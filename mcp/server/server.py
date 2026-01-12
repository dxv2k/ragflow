#
#  Copyright 2025 The InfiniFlow Authors. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

import json
import logging
import re
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from functools import wraps
from typing import Any, Dict

import click
import requests
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Mount, Route
from strenum import StrEnum

import mcp.types as types
from mcp.server.lowlevel import Server


class LaunchMode(StrEnum):
    SELF_HOST = "self-host"
    HOST = "host"


class Transport(StrEnum):
    SSE = "sse"
    STEAMABLE_HTTP = "streamable-http"


BASE_URL = "http://127.0.0.1:9380"
HOST = "127.0.0.1"
PORT = "9382"
HOST_API_KEY = ""
MODE = ""
TRANSPORT_SSE_ENABLED = True
TRANSPORT_STREAMABLE_HTTP_ENABLED = False
JSON_RESPONSE = True


class RAGFlowConnector:
    def __init__(self, base_url: str, version="v1"):
        self.base_url = base_url
        self.version = version
        self.api_url = f"{self.base_url}/api/{self.version}"

    def bind_api_key(self, api_key: str):
        self.api_key = api_key
        self.authorization_header = {"Authorization": "{} {}".format("Bearer", self.api_key)}

    def _post(self, path, json=None, stream=False, files=None):
        if not self.api_key:
            return None
        res = requests.post(url=self.api_url + path, json=json, headers=self.authorization_header, stream=stream, files=files)
        return res

    def _get(self, path, params=None, json=None):
        res = requests.get(url=self.api_url + path, params=params, headers=self.authorization_header, json=json)
        return res

    def list_datasets(self, page: int = 1, page_size: int = 1000, orderby: str = "create_time", desc: bool = True, id: str | None = None, name: str | None = None):
        res = self._get("/datasets", {"page": page, "page_size": page_size, "orderby": orderby, "desc": desc, "id": id, "name": name})
        if not res:
            raise Exception([types.TextContent(type="text", text=res.get("Cannot process this operation."))])

        res = res.json()
        if res.get("code") == 0:
            result_list = []
            for data in res["data"]:
                # Return richer dataset information
                d = {
                    "id": data["id"],
                    "name": data.get("name", ""),
                    "description": data.get("description", ""),
                    "chunk_count": data.get("chunk_num", 0),
                    "document_count": data.get("doc_num", 0),
                    "token_count": data.get("token_num", 0),
                    "embedding_model": data.get("embd_id", ""),
                    "chunk_method": data.get("parser_id", ""),
                    "create_time": data.get("create_time", ""),
                    "update_time": data.get("update_time", "")
                }
                result_list.append(json.dumps(d, ensure_ascii=False))
            return "\n".join(result_list)
        return ""

    def list_documents(self, dataset_id: str, page: int = 1, page_size: int = 30, orderby: str = "create_time", desc: bool = True, keywords: str = "", id: str | None = None, name: str | None = None):
        params = {"page": page, "page_size": page_size, "orderby": orderby, "desc": desc}
        if keywords:
            params["keywords"] = keywords
        if id:
            params["id"] = id
        if name:
            params["name"] = name
            
        res = self._get(f"/datasets/{dataset_id}/documents", params)
        if not res:
            raise Exception([types.TextContent(type="text", text="Cannot process this operation.")])

        res = res.json()
        if res.get("code") == 0:
            return res["data"]
        raise Exception([types.TextContent(type="text", text=res.get("message", "Failed to list documents"))])

    def list_chunks(self, dataset_id: str, document_id: str, page: int = 1, page_size: int = 30, id: str | None = None, keywords: str | None = None):
        params = {"page": page, "page_size": page_size}
        if id:
            params["id"] = id
        if keywords:
            params["keywords"] = keywords

        res = self._get(f"/datasets/{dataset_id}/documents/{document_id}/chunks", params)
        if not res:
            raise Exception([types.TextContent(type="text", text="Cannot process this operation.")])

        res = res.json()
        if res.get("code") == 0:
            data = res.get("data", {}) or {}
            data.setdefault("total", 0)
            data.setdefault("chunks", [])
            data.setdefault("doc", {})
            return data
        raise Exception([types.TextContent(type="text", text=res.get("message", "Failed to list chunks"))])

    def read_chunk(self, dataset_id: str, document_id: str, chunk_id: str):
        params = {"id": chunk_id}
        res = self._get(f"/datasets/{dataset_id}/documents/{document_id}/chunks", params)
        if not res:
            raise Exception([types.TextContent(type="text", text="Cannot process this operation.")])

        res = res.json()
        if res.get("code") == 0:
            data = res.get("data", {}) or {}
            # Normalize keys to ensure expected structure
            data.setdefault("total", 0)
            data.setdefault("chunks", [])
            data.setdefault("doc", {})
            return data
        raise Exception([types.TextContent(type="text", text=res.get("message", "Failed to read chunk"))])

    def retrieval(
        self, dataset_ids, document_ids=None, question="", page=1, page_size=30, similarity_threshold=0.2, vector_similarity_weight=0.3, top_k=1024, rerank_id: str | None = None, keyword: bool = False, search_mode: str | None = None
    ) -> dict:
        if document_ids is None:
            document_ids = []
        data_json = {
            "page": page,
            "page_size": page_size,
            "similarity_threshold": similarity_threshold,
            "vector_similarity_weight": vector_similarity_weight,
            "top_k": top_k,
            "rerank_id": rerank_id,
            "keyword": keyword,
            "question": question,
            "dataset_ids": dataset_ids,
            "document_ids": document_ids,
        }
        # Add search_mode to data_json for routing
        if search_mode is not None:
            data_json["search_mode"] = search_mode

        # Send a POST request to the backend service
        res = self._post("/retrieval", json=data_json)
        if not res:
            raise Exception([types.TextContent(type="text", text=res.get("Cannot process this operation."))])

        res = res.json()
        if res.get("code") == 0:
            data = res.get("data", {}) or {}
            # Ensure keys exist
            data.setdefault("chunks", [])
            data.setdefault("doc_aggs", [])
            data.setdefault("total", 0)
            return data
        # Bubble up backend message as TextContent
        raise Exception([types.TextContent(type="text", text=res.get("message", "Retrieval failed"))])

    def iter_documents(self, dataset_id: str, page_size: int = 200):
        """Yield all documents metadata in a dataset using pagination."""
        page = 1
        while True:
            data = self.list_documents(dataset_id=dataset_id, page=page, page_size=page_size)
            docs = data.get("docs", [])
            if not docs:
                break
            for d in docs:
                yield d
            total = int(data.get("total", len(docs)))
            if page * page_size >= total:
                break
            page += 1

    def iter_chunks(self, dataset_id: str, document_id: str, page_size: int = 200):
        """Yield all chunks for a document using pagination."""
        page = 1
        while True:
            data = self.list_chunks(dataset_id=dataset_id, document_id=document_id, page=page, page_size=page_size)
            chunks = data.get("chunks", [])
            if not chunks:
                break
            for c in chunks:
                yield c, data.get("doc", {})
            total = int(data.get("total", len(chunks)))
            if page * page_size >= total:
                break
            page += 1


class RAGFlowCtx:
    def __init__(self, connector: RAGFlowConnector):
        self.conn = connector


@asynccontextmanager
async def sse_lifespan(server: Server) -> AsyncIterator[dict]:
    ctx = RAGFlowCtx(RAGFlowConnector(base_url=BASE_URL))

    logging.info("Legacy SSE application started with StreamableHTTP session manager!")
    try:
        yield {"ragflow_ctx": ctx}
    finally:
        logging.info("Legacy SSE application shutting down...")


app = Server("ragflow-mcp-server", lifespan=sse_lifespan)


def with_api_key(required=True):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            ctx = app.request_context
            ragflow_ctx = ctx.lifespan_context.get("ragflow_ctx")
            if not ragflow_ctx:
                raise ValueError("Get RAGFlow Context failed")

            connector = ragflow_ctx.conn

            if MODE == LaunchMode.HOST:
                headers = ctx.session._init_options.capabilities.experimental.get("headers", {})
                token = None

                # lower case here, because of Starlette conversion
                auth = headers.get("authorization", "")
                if auth.startswith("Bearer "):
                    token = auth.removeprefix("Bearer ").strip()
                elif "api_key" in headers:
                    token = headers["api_key"]

                # Verbose auth logging (masked)
                masked = None
                if auth:
                    masked = f"{auth.split(' ')[0]} ****{auth[-8:]}" if len(auth) > 8 else f"{auth.split(' ')[0]} ****"
                logging.info(
                    "[AUTH] mode=host headers_keys=%s auth_present=%s x-forwarded-prefix=%s",
                    sorted(list(headers.keys())),
                    bool(auth) or ("api_key" in headers),
                    headers.get("x-forwarded-prefix"),
                )
                if masked:
                    logging.info("[AUTH] authorization(masked)=%s", masked)

                if required and not token:
                    raise ValueError("RAGFlow API key or Bearer token is required.")

                connector.bind_api_key(token)
            else:
                connector.bind_api_key(HOST_API_KEY)

            return await func(*args, connector=connector, **kwargs)

        return wrapper

    return decorator


def _normalize_audio_json(raw_text: str) -> str:
    """Convert WhisperX audio JSON blobs into speaker-aware plain text."""
    if not isinstance(raw_text, str):
        return raw_text

    candidate = raw_text.strip()
    if not candidate or not candidate.startswith("{"):
        return raw_text
    if "segments" not in candidate and "word_segments" not in candidate:
        return raw_text

    try:
        data: Dict[str, Any] = json.loads(candidate)
    except (json.JSONDecodeError, TypeError):
        return raw_text

    segments = data.get("segments")
    if not isinstance(segments, list):
        return raw_text

    lines: list[str] = []
    for seg in segments:
        if not isinstance(seg, dict):
            continue
        seg_text = (seg.get("text") or "").strip()
        if not seg_text:
            continue
        speaker = seg.get("speaker")
        if speaker:
            lines.append(f"[{speaker}] {seg_text}")
        else:
            lines.append(seg_text)

    if not lines:
        return raw_text
    return " ".join(lines)


def _normalize_chunk_dict(chunk: Dict[str, Any]) -> Dict[str, Any]:
    """Ensure chunk text fields are plain text before sending to clients."""
    if not isinstance(chunk, dict):
        return chunk

    for key in ("content", "content_with_weight", "highlight"):
        value = chunk.get(key)
        if isinstance(value, str):
            chunk[key] = _normalize_audio_json(value)
    return chunk


@app.list_tools()
@with_api_key(required=True)
async def list_tools(*, connector) -> list[types.Tool]:
    dataset_description = connector.list_datasets()

    return [
        types.Tool(
            name="grep",
            description=(
                "Local full-text search (substring) over all chunks in a dataset. "
                "Does NOT use semantic retrieval; purely scans chunk text and returns the best matches. "
                "Provide a dataset_id and query. Optionally limit by document_ids. Top_k is capped at 10.\n\n"
                "Available datasets (id, name, desc, counts):\n" + dataset_description
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "dataset_id": {"type": "string", "description": "Target dataset (knowledge base) ID"},
                    "query": {"type": "string", "description": "Text to search (literal substring)"},
                    "document_ids": {"type": "array", "items": {"type": "string"}, "description": "Optional: restrict search to specific document IDs"},
                    "case_sensitive": {"type": "boolean", "description": "Case sensitive matching (default false)", "default": False},
                    "top_k": {"type": "integer", "description": "Max number of chunks to return (<=10)", "default": 10}
                },
                "required": ["dataset_id", "query"],
            },
        ),
        types.Tool(
            name="re_search",
            description=(
                "Regular expression (regex) search over all chunks in a dataset. "
                "Does NOT use semantic retrieval; purely scans chunk text using regex patterns and returns the best matches. "
                "Provide a dataset_id and regex pattern. Optionally limit by document_ids. Top_k is capped at 10.\n"
                "Supports full regex syntax (e.g., 'video.*analytics', '\\bword\\b', 'pattern\\d+', etc.).\n\n"
                "Available datasets (id, name, desc, counts):\n" + dataset_description
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "dataset_id": {"type": "string", "description": "Target dataset (knowledge base) ID"},
                    "pattern": {"type": "string", "description": "Regular expression pattern to search for"},
                    "document_ids": {"type": "array", "items": {"type": "string"}, "description": "Optional: restrict search to specific document IDs"},
                    "case_sensitive": {"type": "boolean", "description": "Case sensitive matching (default false)", "default": False},
                    "top_k": {"type": "integer", "description": "Max number of chunks to return (<=10)", "default": 10}
                },
                "required": ["dataset_id", "pattern"],
            },
        ),
        types.Tool(
            name="knowledge_base_retrieval",
            description="Retrieve relevant chunks from the RAGFlow retrieve interface based on the question. You can optionally specify dataset_ids to search only specific datasets, or omit dataset_ids entirely to search across ALL available datasets. You can also optionally specify document_ids to search within specific documents. When dataset_ids is not provided or is empty, the system will automatically search across all available datasets. Below is the list of all available datasets, including their descriptions and IDs:"
            + dataset_description,
            inputSchema={
                "type": "object",
                "properties": {
                    "dataset_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional array of dataset IDs to search. If not provided or empty, all datasets will be searched."
                    },
                    "document_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional array of document IDs to search within."
                    },
                    "question": {"type": "string", "description": "The question or query to search for."},
                },
                "required": ["question"],
            },
        ),
        types.Tool(
            name="read_chunk",
            description="Read a single chunk by IDs and return its structured JSON (with document and dataset references).",
            inputSchema={
                "type": "object",
                "properties": {
                    "dataset_id": {"type": "string", "description": "Dataset ID (kb_id) that owns the document"},
                    "document_id": {"type": "string", "description": "Document ID that owns the chunk"},
                    "chunk_id": {"type": "string", "description": "Chunk ID to read"},
                },
                "required": ["dataset_id", "document_id", "chunk_id"],
            },
        ),
        types.Tool(
            name="list_chunks",
            description="List chunks for a given document in a dataset. Returns JSON with total, chunks, and doc.",
            inputSchema={
                "type": "object",
                "properties": {
                    "dataset_id": {"type": "string", "description": "Dataset ID (kb_id)"},
                    "document_id": {"type": "string", "description": "Document ID"},
                    "page": {"type": "integer", "description": "Page number", "default": 1},
                    "page_size": {"type": "integer", "description": "Items per page", "default": 20},
                    "keywords": {"type": "string", "description": "Optional keyword filter"}
                },
                "required": ["dataset_id", "document_id"],
            },
        ),
        types.Tool(
            name="list_datasets",
            description="List all available datasets with detailed information including names, descriptions, document counts, chunk counts, embedding models, and creation times. This provides a comprehensive overview of all knowledge bases available for querying.",
            inputSchema={
                "type": "object",
                "properties": {
                    "page": {
                        "type": "integer",
                        "description": "Page number for pagination (default: 1)",
                        "default": 1
                    },
                    "page_size": {
                        "type": "integer", 
                        "description": "Number of datasets per page (default: 30)",
                        "default": 30
                    },
                    "name": {
                        "type": "string",
                        "description": "Filter datasets by name"
                    }
                },
                "required": [],
            },
        ),
        types.Tool(
            name="list_documents",
            description="List all documents/files within a specific dataset. Shows document names, processing status, chunk counts, token counts, and file information. Useful for understanding what content is available in a knowledge base before querying.",
            inputSchema={
                "type": "object",
                "properties": {
                    "dataset_id": {
                        "type": "string",
                        "description": "ID of the dataset to list documents from"
                    },
                    "page": {
                        "type": "integer",
                        "description": "Page number for pagination (default: 1)",
                        "default": 1
                    },
                    "page_size": {
                        "type": "integer",
                        "description": "Number of documents per page (default: 30)", 
                        "default": 30
                    },
                    "keywords": {
                        "type": "string",
                        "description": "Filter documents by keywords in their names"
                    },
                    "name": {
                        "type": "string", 
                        "description": "Filter by exact document name"
                    }
                },
                "required": ["dataset_id"],
            },
        ),
        types.Tool(
            name="bm25_search",
            description=(
                "Pure BM25/full-text search using Elasticsearch's custom BM25 scoring. "
                "Uses tokenized text matching without vector embeddings - faster than semantic search "
                "and better for exact keyword/phrase matching. "
                "Provide dataset_ids and a query. Optionally filter by document_ids.\n\n"
                "Available datasets:\n" + dataset_description
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "dataset_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Dataset IDs to search (leave empty to search all)"
                    },
                    "document_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional: restrict to specific documents"
                    },
                    "query": {
                        "type": "string",
                        "description": "Search query (will be tokenized)"
                    },
                    "keyword_extraction": {
                        "type": "boolean",
                        "description": "Use LLM to extract additional keywords (default: false)",
                        "default": False
                    },
                    "rerank_id": {
                        "type": "string",
                        "description": "use rerank model 'BAAI/bge-reranker-v2-m3'"
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "Max results to return (default: 30)",
                        "default": 30
                    },
                    "similarity_threshold": {
                        "type": "number",
                        "description": "Minimum score threshold 0-1 (default: 0.0)",
                        "default": 0.0
                    },
                    "search_mode": {
                        "type": "string",
                        "description": "Search mode: 'bm25' for pure BM25 full-text, or null/omit for hybrid (default: null)",
                        "enum": ["bm25", None],
                        "default": None
                    }
                },
                "required": ["query"]
            },
        ),
    ]


def format_retrieval_response(chunks_data):
    """Format retrieval response for better readability.

    Accepts a list of chunk dicts or JSON strings. Produces a human-friendly
    summary including basic references when available.
    """
    if not chunks_data or not isinstance(chunks_data, list):
        return [types.TextContent(type="text", text="No results found.")]

    summary_parts = [f"📊 **Search Results: {len(chunks_data)} chunks found**\n"]

    for i, chunk in enumerate(chunks_data, 1):
        try:
            chunk_obj = json.loads(chunk) if isinstance(chunk, str) else chunk

            text = _normalize_audio_json(chunk_obj.get("content", "") or "")
            content = (text[:200] + "...") if len(text) > 200 else text
            highlight = _normalize_audio_json(chunk_obj.get("highlight") or "")
            doc_name = (
                chunk_obj.get("document_keyword")
                or chunk_obj.get("doc_name")
                or "Unknown Document"
            )
            similarity = round(float(chunk_obj.get("similarity", 0)) * 100, 1)

            # IDs for reference
            chunk_id = chunk_obj.get("id")
            doc_id = chunk_obj.get("document_id") or chunk_obj.get("doc_id")
            kb_id = chunk_obj.get("kb_id")

            summary_parts.append(f"\n**Result {i}** ({similarity}% relevance)")
            summary_parts.append(f"📄 **Source:** {doc_name}")

            if highlight:
                summary_parts.append(f"🔍 **Key Information:** {highlight[:300]}...")
            else:
                summary_parts.append(f"📝 **Content:** {content}")

            refs = []
            if doc_id:
                refs.append(f"doc_id={doc_id}")
            if chunk_id:
                refs.append(f"chunk_id={chunk_id}")
            if kb_id:
                refs.append(f"kb_id={kb_id}")
            if refs:
                summary_parts.append("🔗 " + ", ".join(refs))

            summary_parts.append("---")
        except (json.JSONDecodeError, KeyError, TypeError):
            summary_parts.append(f"\n**Result {i}** (Raw data)")
            summary_parts.append(str(chunk)[:200] + "...")
            summary_parts.append("---")

    formatted_text = "\n".join(summary_parts)

    return [types.TextContent(type="text", text=formatted_text)]

def format_datasets_response(datasets_str):
    """Format datasets response for better readability"""
    if not datasets_str:
        return [types.TextContent(type="text", text="No datasets found.")]
    
    datasets = []
    for line in datasets_str.strip().split('\n'):
        if line.strip():
            try:
                datasets.append(json.loads(line.strip()))
            except json.JSONDecodeError:
                continue
    
    if not datasets:
        return [types.TextContent(type="text", text="No datasets found.")]
    
    # Create readable summary
    summary_parts = [f"📚 **Available Datasets: {len(datasets)} found**\n"]
    
    for dataset in datasets:
        summary_parts.append(f"**{dataset.get('name', 'Unnamed Dataset')}**")
        summary_parts.append(f"🆔 ID: `{dataset.get('id', 'N/A')}`")
        summary_parts.append(f"📖 Description: {dataset.get('description', 'No description')}")
        summary_parts.append(f"📄 Documents: {dataset.get('document_count', 0)}")
        summary_parts.append(f"🧩 Chunks: {dataset.get('chunk_count', 0)}")
        summary_parts.append(f"🔤 Tokens: {dataset.get('token_count', 0)}")
        if dataset.get('embedding_model'):
            summary_parts.append(f"🤖 Model: {dataset.get('embedding_model')}")
        summary_parts.append("---")
    
    return [
        types.TextContent(
            type="text",
            text="\n".join(summary_parts)
        )
    ]

def format_documents_response(docs_data):
    """Format documents response for better readability"""
    if not docs_data:
        return [types.TextContent(type="text", text="No documents found in this dataset.")]
    
    docs = docs_data.get("docs", [])
    total = docs_data.get("total", len(docs))
    
    if not docs:
        return [types.TextContent(type="text", text="No documents found in this dataset.")]
    
    # Create readable summary
    summary_parts = [f"📁 **Documents in Dataset: {len(docs)} of {total} total**\n"]
    
    for doc in docs:
        status_emoji = {"DONE": "✅", "RUNNING": "⏳", "UNSTART": "⏸️", "FAIL": "❌"}.get(doc.get("run", ""), "❓")
        
        summary_parts.append(f"**{doc.get('name', 'Unnamed Document')}** {status_emoji}")
        summary_parts.append(f"🆔 ID: `{doc.get('id', 'N/A')}`")
        summary_parts.append(f"🧩 Chunks: {doc.get('chunk_count', 0)}")
        summary_parts.append(f"🔤 Tokens: {doc.get('token_count', 0)}")
        summary_parts.append(f"⚙️ Method: {doc.get('chunk_method', 'unknown')}")
        summary_parts.append(f"📊 Status: {doc.get('run', 'unknown')}")
        summary_parts.append("---")
    
    return [
        types.TextContent(
            type="text",
            text="\n".join(summary_parts)
        )
    ]

@app.call_tool()
@with_api_key(required=True)
async def call_tool(name: str, arguments: dict, *, connector) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    if name == "grep":
        dataset_id = arguments.get("dataset_id")
        query = arguments.get("query")
        case_sensitive = bool(arguments.get("case_sensitive", False))
        document_ids = arguments.get("document_ids", []) or []
        if not dataset_id or not query:
            return [types.TextContent(type="text", text="Error: dataset_id and query are required.")]

        try:
            # Gather chunks across dataset (optionally restricted to documents)
            target_docs = set(document_ids) if document_ids else None
            all_matches = []

            def norm(s: str) -> str:
                return s if case_sensitive else s.lower()

            qn = norm(query)

            for doc in connector.iter_documents(dataset_id):
                doc_id = doc.get("id")
                if target_docs and doc_id not in target_docs:
                    continue
                doc_name = doc.get("name") or doc.get("document_keyword") or "Unknown Document"
                for chunk, doc_meta in connector.iter_chunks(dataset_id, doc_id):
                    # Extract text
                    text = chunk.get("content") or chunk.get("text") or ""
                    if not isinstance(text, str):
                        try:
                            text = json.dumps(text, ensure_ascii=False)
                        except Exception:
                            text = str(text)

                    tn = norm(text)
                    count = tn.count(qn) if qn else 0
                    if count <= 0:
                        continue

                    first_idx = tn.find(qn)
                    # Build a simple highlight snippet around first match
                    start = max(0, first_idx - 80)
                    end = min(len(text), first_idx + len(query) + 120)
                    snippet = ("..." if start > 0 else "") + text[start:end].strip() + ("..." if end < len(text) else "")

                    out = {
                        **chunk,
                        "document_id": chunk.get("document_id") or chunk.get("doc_id") or doc_id,
                        "kb_id": chunk.get("kb_id") or dataset_id,
                        "document_keyword": doc_name,
                        "doc_name": doc_name,
                        "highlight": snippet,
                        "_match_count": count,
                        "_first_pos": first_idx,
                    }
                    all_matches.append(out)

            if not all_matches:
                return [types.TextContent(type="text", text=json.dumps({
                    "request": {
                        "dataset_id": dataset_id,
                        "document_ids": document_ids,
                        "query": query,
                        "mode": "fulltext-local"
                    },
                    "response": "No results found.",
                    "chunks": [],
                    "documents": [],
                    "total": 0
                }, ensure_ascii=False, indent=2))]

            # Sort by match strength, then by earliest position, then shorter content
            def sort_key(c):
                content = c.get("content") or ""
                clen = len(content) if isinstance(content, str) else 0
                return (-int(c.get("_match_count", 0)), int(c.get("_first_pos", 0)), clen)

            all_matches.sort(key=sort_key)

            # Cap top_k to 10
            try:
                req_top_k = int(arguments.get("top_k", 10))
            except Exception:
                req_top_k = 10
            top_k = max(1, min(10, req_top_k))

            top_matches = all_matches[:top_k]

            # Normalize similarity (0..1) based on match_count
            max_count = max((m.get("_match_count", 0) for m in top_matches), default=1) or 1
            for m in top_matches:
                try:
                    m["similarity"] = float(m.get("_match_count", 0)) / float(max_count)
                except Exception:
                    m["similarity"] = 0.0
                # Remove internal keys
                m.pop("_match_count", None)
                m.pop("_first_pos", None)

            for match in top_matches:
                _normalize_chunk_dict(match)

            formatted = format_retrieval_response(top_matches)
            summary_text = ""
            try:
                if formatted and isinstance(formatted[0], types.TextContent):
                    summary_text = formatted[0].text or ""
            except Exception:
                summary_text = ""

            payload = {
                "request": {
                    "dataset_id": dataset_id,
                    "document_ids": document_ids,
                    "query": query,
                    "case_sensitive": case_sensitive,
                    "mode": "fulltext-local",
                    "top_k": top_k,
                },
                "response": summary_text,
                "chunks": top_matches,
                "documents": [],
                "total": len(all_matches),
            }

            return [types.TextContent(type="text", text=json.dumps(payload, ensure_ascii=False, indent=2))]
        except Exception as e:
            try:
                if getattr(e, "args", None) and isinstance(e.args[0], list):
                    return e.args[0]
            except Exception:
                pass
            return [types.TextContent(type="text", text=f"Error during grep: {str(e)}")]

    elif name == "re_search":
        """
        Regular expression search tool - searches chunks using regex patterns.

        Args:
            dataset_id: Target dataset ID
            pattern: Regex pattern to search for
            document_ids: Optional list of document IDs to restrict search
            case_sensitive: Whether to use case-sensitive matching (default False)
            top_k: Maximum number of results to return (capped at 10)

        Returns:
            JSON response with matched chunks, sorted by match count and position
        """
        dataset_id = arguments.get("dataset_id")
        pattern = arguments.get("pattern")
        case_sensitive = bool(arguments.get("case_sensitive", False))
        document_ids = arguments.get("document_ids", []) or []
        if not dataset_id or not pattern:
            return [types.TextContent(type="text", text="Error: dataset_id and pattern are required.")]

        try:
            # Compile regex pattern
            try:
                flags = 0 if case_sensitive else re.IGNORECASE
                regex_pattern = re.compile(pattern, flags)
            except re.error as e:
                return [types.TextContent(type="text", text=f"Error: Invalid regex pattern: {str(e)}")]

            # Gather chunks across dataset (optionally restricted to documents)
            target_docs = set(document_ids) if document_ids else None
            all_matches = []

            for doc in connector.iter_documents(dataset_id):
                doc_id = doc.get("id")
                if target_docs and doc_id not in target_docs:
                    continue
                doc_name = doc.get("name") or doc.get("document_keyword") or "Unknown Document"
                for chunk, doc_meta in connector.iter_chunks(dataset_id, doc_id):
                    # Extract text
                    text = chunk.get("content") or chunk.get("text") or ""
                    if not isinstance(text, str):
                        try:
                            text = json.dumps(text, ensure_ascii=False)
                        except Exception:
                            text = str(text)

                    # Match using regex
                    matches = list(regex_pattern.finditer(text))
                    count = len(matches)
                    if count <= 0:
                        continue

                    first_match = matches[0]
                    first_idx = first_match.start()
                    match_len = first_match.end() - first_match.start()

                    # Build a simple highlight snippet around first match
                    start = max(0, first_idx - 80)
                    end = min(len(text), first_idx + match_len + 120)
                    snippet = ("..." if start > 0 else "") + text[start:end].strip() + ("..." if end < len(text) else "")

                    out = {
                        **chunk,
                        "document_id": chunk.get("document_id") or chunk.get("doc_id") or doc_id,
                        "kb_id": chunk.get("kb_id") or dataset_id,
                        "document_keyword": doc_name,
                        "doc_name": doc_name,
                        "highlight": snippet,
                        "_match_count": count,
                        "_first_pos": first_idx,
                    }
                    all_matches.append(out)

            if not all_matches:
                return [types.TextContent(type="text", text=json.dumps({
                    "request": {
                        "dataset_id": dataset_id,
                        "document_ids": document_ids,
                        "pattern": pattern,
                        "case_sensitive": case_sensitive,
                        "mode": "regex"
                    },
                    "response": "No results found.",
                    "chunks": [],
                    "documents": [],
                    "total": 0
                }, ensure_ascii=False, indent=2))]

            # Sort by match strength, then by earliest position, then shorter content
            def sort_key(c):
                content = c.get("content") or ""
                clen = len(content) if isinstance(content, str) else 0
                return (-int(c.get("_match_count", 0)), int(c.get("_first_pos", 0)), clen)

            all_matches.sort(key=sort_key)

            # Cap top_k to 10
            try:
                req_top_k = int(arguments.get("top_k", 10))
            except Exception:
                req_top_k = 10
            top_k = max(1, min(10, req_top_k))

            top_matches = all_matches[:top_k]

            # Normalize similarity (0..1) based on match_count
            max_count = max((m.get("_match_count", 0) for m in top_matches), default=1) or 1
            for m in top_matches:
                try:
                    m["similarity"] = float(m.get("_match_count", 0)) / float(max_count)
                except Exception:
                    m["similarity"] = 0.0
                # Remove internal keys
                m.pop("_match_count", None)
                m.pop("_first_pos", None)

            formatted = format_retrieval_response(top_matches)
            summary_text = ""
            try:
                if formatted and isinstance(formatted[0], types.TextContent):
                    summary_text = formatted[0].text or ""
            except Exception:
                summary_text = ""

            payload = {
                "request": {
                    "dataset_id": dataset_id,
                    "document_ids": document_ids,
                    "pattern": pattern,
                    "case_sensitive": case_sensitive,
                    "mode": "regex",
                    "top_k": top_k,
                },
                "response": summary_text,
                "chunks": top_matches,
                "documents": [],
                "total": len(all_matches),
            }

            return [types.TextContent(type="text", text=json.dumps(payload, ensure_ascii=False, indent=2))]
        except Exception as e:
            try:
                if getattr(e, "args", None) and isinstance(e.args[0], list):
                    return e.args[0]
            except Exception:
                pass
            return [types.TextContent(type="text", text=f"Error during re_search: {str(e)}")]

    elif name == "knowledge_base_retrieval":
        document_ids = arguments.get("document_ids", [])
        dataset_ids = arguments.get("dataset_ids", [])
        # Simplified output: always return a single JSON object
        
        # If no dataset_ids provided or empty list, get all available dataset IDs
        if not dataset_ids:
            dataset_list_str = connector.list_datasets()
            dataset_ids = []
            
            # Parse the dataset list to extract IDs
            if dataset_list_str:
                for line in dataset_list_str.strip().split('\n'):
                    if line.strip():
                        try:
                            dataset_info = json.loads(line.strip())
                            dataset_ids.append(dataset_info["id"])
                        except (json.JSONDecodeError, KeyError):
                            # Skip malformed lines
                            continue
        
        try:
            data = connector.retrieval(
                dataset_ids=dataset_ids,
                document_ids=document_ids,
                question=arguments["question"],
            )

            # Build formatted summary from chunks (pass dicts directly)
            chunks_list = data.get("chunks", [])
            for chunk in chunks_list:
                _normalize_chunk_dict(chunk)
            formatted = format_retrieval_response(chunks_list)  # returns [TextContent]
            summary_text = ""
            try:
                if formatted and isinstance(formatted[0], types.TextContent):
                    summary_text = formatted[0].text or ""
            except Exception:
                summary_text = ""

            payload = {
                "request": {
                    "dataset_ids": dataset_ids,
                    "document_ids": document_ids,
                    "question": arguments.get("question", ""),
                },
                "response": summary_text,
                "chunks": data.get("chunks", []),
                "documents": data.get("doc_aggs", []),
                "total": data.get("total", 0),
            }

            return [
                types.TextContent(
                    type="text",
                    text=json.dumps(payload, ensure_ascii=False, indent=2),
                )
            ]
        except Exception as e:
            # Unwrap server-side content if exception carried it as args[0]
            try:
                if getattr(e, "args", None) and isinstance(e.args[0], list):
                    return e.args[0]
            except Exception:
                pass
            return [types.TextContent(type="text", text=f"Error during retrieval: {str(e)}")]
    
    elif name == "read_chunk":
        dataset_id = arguments.get("dataset_id")
        document_id = arguments.get("document_id")
        chunk_id = arguments.get("chunk_id")
        if not all([dataset_id, document_id, chunk_id]):
            return [types.TextContent(type="text", text="Error: dataset_id, document_id, and chunk_id are required.")]
        try:
            data = connector.read_chunk(dataset_id=dataset_id, document_id=document_id, chunk_id=chunk_id)
            for chunk in data.get("chunks", []):
                _normalize_chunk_dict(chunk)
            return [
                types.TextContent(
                    type="text",
                    text=json.dumps(data, ensure_ascii=False, indent=2),
                )
            ]
        except Exception as e:
            try:
                if getattr(e, "args", None) and isinstance(e.args[0], list):
                    return e.args[0]
            except Exception:
                pass
            return [types.TextContent(type="text", text=f"Error reading chunk: {str(e)}")]

    elif name == "list_chunks":
        dataset_id = arguments.get("dataset_id")
        document_id = arguments.get("document_id")
        if not all([dataset_id, document_id]):
            return [types.TextContent(type="text", text="Error: dataset_id and document_id are required.")]
        try:
            data = connector.list_chunks(
                dataset_id=dataset_id,
                document_id=document_id,
                page=arguments.get("page", 1),
                page_size=arguments.get("page_size", 20),
                keywords=arguments.get("keywords"),
            )
            for chunk in data.get("chunks", []):
                _normalize_chunk_dict(chunk)
            return [
                types.TextContent(
                    type="text",
                    text=json.dumps(data, ensure_ascii=False, indent=2),
                )
            ]
        except Exception as e:
            try:
                if getattr(e, "args", None) and isinstance(e.args[0], list):
                    return e.args[0]
            except Exception:
                pass
            return [types.TextContent(type="text", text=f"Error listing chunks: {str(e)}")]
    
    elif name == "list_datasets":
        try:
            datasets_str = connector.list_datasets(
                page=arguments.get("page", 1),
                page_size=arguments.get("page_size", 30),
                name=arguments.get("name")
            )
            return format_datasets_response(datasets_str)
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error listing datasets: {str(e)}")]
    
    elif name == "list_documents":
        dataset_id = arguments.get("dataset_id")
        if not dataset_id:
            return [types.TextContent(type="text", text="Error: dataset_id is required.")]
        
        try:
            docs_data = connector.list_documents(
                dataset_id=dataset_id,
                page=arguments.get("page", 1),
                page_size=arguments.get("page_size", 30),
                keywords=arguments.get("keywords", ""),
                name=arguments.get("name")
            )
            return format_documents_response(docs_data)
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error listing documents: {str(e)}")]

    elif name == "bm25_search":
        query = arguments.get("query")
        if not query:
            return [types.TextContent(type="text", text="Error: query is required.")]

        dataset_ids = arguments.get("dataset_ids", [])
        # If no dataset_ids provided, get all available datasets
        if not dataset_ids:
            dataset_list_str = connector.list_datasets()
            if dataset_list_str:
                for line in dataset_list_str.strip().split('\n'):
                    if line.strip():
                        try:
                            dataset_info = json.loads(line.strip())
                            dataset_ids.append(dataset_info["id"])
                        except (json.JSONDecodeError, KeyError):
                            continue

        try:
            data = connector.retrieval(
                dataset_ids=dataset_ids,
                document_ids=arguments.get("document_ids", []),
                question=query,
                page=1,
                page_size=arguments.get("top_k", 60),
                similarity_threshold=arguments.get("similarity_threshold", 0.0),
                vector_similarity_weight=0.0,  # Pure BM25 - no vector search
                top_k=1024,
                keyword=arguments.get("keyword_extraction", False),
                rerank_id=arguments.get("rerank_id", "BAAI/bge-reranker-v2-m3"),  # Add rerank always support
                search_mode=arguments.get("search_mode", None)  # Route to pure BM25 if "bm25"
            )

            # Format response
            chunks_list = data.get("chunks", [])
            formatted = format_retrieval_response(chunks_list)
            summary_text = ""
            try:
                if formatted and isinstance(formatted[0], types.TextContent):
                    summary_text = formatted[0].text or ""
            except Exception:
                summary_text = ""

            payload = {
                "request": {
                    "dataset_ids": dataset_ids,
                    "document_ids": arguments.get("document_ids", []),
                    "query": query,
                    "mode": "bm25",
                    "vector_similarity_weight": 0.0,
                    "rerank_id": arguments.get("rerank_id"),
                },
                "response": summary_text,
                "chunks": chunks_list,
                "documents": data.get("doc_aggs", []),
                "total": data.get("total", 0),
            }

            return [types.TextContent(type="text", text=json.dumps(payload, ensure_ascii=False, indent=2))]
        except Exception as e:
            try:
                if getattr(e, "args", None) and isinstance(e.args[0], list):
                    return e.args[0]
            except Exception:
                pass
            return [types.TextContent(type="text", text=f"Error during BM25 search: {str(e)}")]
    
    raise ValueError(f"Tool not found: {name}")


def create_starlette_app():
    routes = []
    middleware = None
    if MODE == LaunchMode.HOST:
        from starlette.types import ASGIApp, Receive, Scope, Send

        class AuthMiddleware:
            def __init__(self, app: ASGIApp):
                self.app = app

            async def __call__(self, scope: Scope, receive: Receive, send: Send):
                if scope["type"] != "http":
                    await self.app(scope, receive, send)
                    return

                path = scope["path"]
                if path.startswith("/messages/") or path.startswith("/sse") or path.startswith("/mcp"):
                    headers = dict(scope["headers"])
                    token = None
                    auth_header = headers.get(b"authorization")
                    if auth_header and auth_header.startswith(b"Bearer "):
                        token = auth_header.removeprefix(b"Bearer ").strip()
                    elif b"api_key" in headers:
                        token = headers[b"api_key"]

                    if not token:
                        response = JSONResponse({"error": "Missing or invalid authorization header"}, status_code=401)
                        await response(scope, receive, send)
                        return

                await self.app(scope, receive, send)

        middleware = [Middleware(AuthMiddleware)]

    # Request/Response verbose logger (ASGI-safe for streaming)
    class RequestLoggerMiddleware:
        def __init__(self, app):
            self.app = app

        async def __call__(self, scope, receive, send):
            if scope.get("type") != "http":
                return await self.app(scope, receive, send)

            path = scope.get("path", "")
            try:
                headers = {k.decode(): v.decode() for k, v in scope.get("headers", [])}
                masked_headers = {}
                for k, v in headers.items():
                    if k.lower() in {"authorization", "api_key", "cookie"}:
                        suffix = v[-8:] if isinstance(v, str) and len(v) > 8 else ""
                        masked_headers[k] = f"***{suffix}"
                    else:
                        masked_headers[k] = v
                logging.info("[REQ] %s %s qs=%s headers=%s", scope.get("method"), path, scope.get("query_string"), masked_headers)
            except Exception as e:
                logging.warning("[REQ] log failed: %s", e)

            # Wrap send to log response status without buffering body
            async def send_wrapper(message):
                if message.get("type") == "http.response.start":
                    status = message.get("status")
                    logging.info("[RES] %s %s -> %s", scope.get("method"), path, status)
                await send(message)

            return await self.app(scope, receive, send_wrapper)

    if middleware is None:
        middleware = []
    middleware.insert(0, Middleware(RequestLoggerMiddleware))

    # Add SSE routes if enabled
    if TRANSPORT_SSE_ENABLED:
        from mcp.server.sse import SseServerTransport

        # Instantiate once; we keep the transport mounted at /messages/.
        # Nginx handles any external prefix (e.g., /mcp) and proxies to this path.
        sse_transport = SseServerTransport("/messages/")

        async def handle_sse(request):
            # Normalize headers to lowercase so downstream code can reliably read 'authorization'
            headers = {k.lower(): v for k, v in dict(request.headers).items()}
            prefix = headers.get("x-forwarded-prefix", "").rstrip("/")
            messages_path = "/messages/" if not prefix else f"{prefix}/messages/"

            logging.info(
                "[SSE] connected path=%s prefix=%s computed_messages_path=%s headers_keys=%s",
                request.url.path,
                prefix,
                messages_path,
                sorted(list(headers.keys())),
            )

            # Use the pre-mounted transport; nginx maps prefixed paths to /messages/ upstream.
            async with sse_transport.connect_sse(request.scope, request.receive, request._send) as streams:
                await app.run(
                    streams[0],
                    streams[1],
                    app.create_initialization_options(experimental_capabilities={"headers": headers}),
                )
            return Response()

        routes.extend(
            [
                Route("/sse", endpoint=handle_sse, methods=["GET"]),
                Mount("/messages/", app=sse_transport.handle_post_message),
            ]
        )

    # Add streamable HTTP route if enabled
    streamablehttp_lifespan = None
    if TRANSPORT_STREAMABLE_HTTP_ENABLED:
        from starlette.types import Receive, Scope, Send

        from mcp.server.streamable_http_manager import StreamableHTTPSessionManager

        session_manager = StreamableHTTPSessionManager(
            app=app,
            event_store=None,
            json_response=JSON_RESPONSE,
            stateless=True,
        )

        async def handle_streamable_http(scope: Scope, receive: Receive, send: Send) -> None:
            await session_manager.handle_request(scope, receive, send)

        @asynccontextmanager
        async def streamablehttp_lifespan(app: Starlette) -> AsyncIterator[None]:
            async with session_manager.run():
                logging.info("StreamableHTTP application started with StreamableHTTP session manager!")
                try:
                    yield
                finally:
                    logging.info("StreamableHTTP application shutting down...")

        routes.append(Mount("/mcp", app=handle_streamable_http))

    return Starlette(
        debug=True,
        routes=routes,
        middleware=middleware,
        lifespan=streamablehttp_lifespan,
    )


@click.command()
@click.option("--base-url", type=str, default="http://127.0.0.1:9380", help="API base URL for RAGFlow backend")
@click.option("--host", type=str, default="127.0.0.1", help="Host to bind the RAGFlow MCP server")
@click.option("--port", type=int, default=9383, help="Port to bind the RAGFlow MCP server")
@click.option(
    "--mode",
    type=click.Choice(["self-host", "host"]),
    default="host",
    help=("Launch mode:\n  self-host: run MCP for a single tenant (requires --api-key)\n  host: multi-tenant mode, users must provide Authorization headers"),
)
@click.option("--api-key", type=str, default="", help="API key to use when in self-host mode")
@click.option(
    "--root-path",
    type=str,
    default="",
    help="ASGI root_path for subpath deployments behind reverse proxies (e.g., /mcp)",
)
@click.option(
    "--transport-sse-enabled/--no-transport-sse-enabled",
    default=True,
    help="Enable or disable legacy SSE transport mode (default: enabled)",
)
@click.option(
    "--transport-streamable-http-enabled/--no-transport-streamable-http-enabled",
    default=False,
    help="Enable or disable streamable-http transport mode (default: disabled)",
)
@click.option(
    "--json-response/--no-json-response",
    default=True,
    help="Enable or disable JSON response mode for streamable-http (default: enabled)",
)
def main(base_url, host, port, mode, api_key, transport_sse_enabled, transport_streamable_http_enabled, json_response, root_path):
    import os

    import uvicorn
    from dotenv import load_dotenv

    load_dotenv()

    def parse_bool_flag(key: str, default: bool) -> bool:
        val = os.environ.get(key, str(default))
        return str(val).strip().lower() in ("1", "true", "yes", "on")

    global BASE_URL, HOST, PORT, MODE, HOST_API_KEY, TRANSPORT_SSE_ENABLED, TRANSPORT_STREAMABLE_HTTP_ENABLED, JSON_RESPONSE
    BASE_URL = os.environ.get("RAGFLOW_MCP_BASE_URL", base_url)
    HOST = os.environ.get("RAGFLOW_MCP_HOST", host)
    PORT = os.environ.get("RAGFLOW_MCP_PORT", str(port))
    MODE = os.environ.get("RAGFLOW_MCP_LAUNCH_MODE", mode)
    HOST_API_KEY = os.environ.get("RAGFLOW_MCP_HOST_API_KEY", api_key)
    TRANSPORT_SSE_ENABLED = parse_bool_flag("RAGFLOW_MCP_TRANSPORT_SSE_ENABLED", transport_sse_enabled)
    TRANSPORT_STREAMABLE_HTTP_ENABLED = parse_bool_flag("RAGFLOW_MCP_TRANSPORT_STREAMABLE_ENABLED", transport_streamable_http_enabled)
    JSON_RESPONSE = parse_bool_flag("RAGFLOW_MCP_JSON_RESPONSE", json_response)
    ROOT_PATH = os.environ.get("RAGFLOW_MCP_ROOT_PATH", root_path)

    if MODE == LaunchMode.SELF_HOST and not HOST_API_KEY:
        raise click.UsageError("--api-key is required when --mode is 'self-host'")

    if TRANSPORT_STREAMABLE_HTTP_ENABLED and MODE == LaunchMode.HOST:
        raise click.UsageError("The --host mode is not supported with streamable-http transport yet.")

    if not TRANSPORT_STREAMABLE_HTTP_ENABLED and JSON_RESPONSE:
        JSON_RESPONSE = False

    print(
        r"""
__  __  ____ ____       ____  _____ ______     _______ ____
|  \/  |/ ___|  _ \     / ___|| ____|  _ \ \   / / ____|  _ \
| |\/| | |   | |_) |    \___ \|  _| | |_) \ \ / /|  _| | |_) |
| |  | | |___|  __/      ___) | |___|  _ < \ V / | |___|  _ <
|_|  |_|\____|_|        |____/|_____|_| \_\ \_/  |_____|_| \_\
        """,
        flush=True,
    )
    print(f"MCP launch mode: {MODE}", flush=True)
    print(f"MCP host: {HOST}", flush=True)
    print(f"MCP port: {PORT}", flush=True)
    print(f"MCP base_url: {BASE_URL}", flush=True)
    if ROOT_PATH:
        print(f"MCP root_path: {ROOT_PATH}", flush=True)

    if not any([TRANSPORT_SSE_ENABLED, TRANSPORT_STREAMABLE_HTTP_ENABLED]):
        print("At least one transport should be enabled, enable streamable-http automatically", flush=True)
        TRANSPORT_STREAMABLE_HTTP_ENABLED = True

    if TRANSPORT_SSE_ENABLED:
        print("SSE transport enabled: yes", flush=True)
        print("SSE endpoint available at /sse", flush=True)
    else:
        print("SSE transport enabled: no", flush=True)

    if TRANSPORT_STREAMABLE_HTTP_ENABLED:
        print("Streamable HTTP transport enabled: yes", flush=True)
        print("Streamable HTTP endpoint available at /mcp", flush=True)
        if JSON_RESPONSE:
            print("Streamable HTTP mode: JSON response enabled", flush=True)
        else:
            print("Streamable HTTP mode: SSE over HTTP enabled", flush=True)
    else:
        print("Streamable HTTP transport enabled: no", flush=True)
        if JSON_RESPONSE:
            print("Warning: --json-response ignored because streamable transport is disabled.", flush=True)

    uvicorn.run(
        create_starlette_app(),
        host=HOST,
        port=int(PORT),
        root_path=ROOT_PATH or "", # NOTE: uvicorn require this "" 
    )


if __name__ == "__main__":
    """
    Launch examples:

    1. Self-host mode with both SSE and Streamable HTTP (in JSON response mode) enabled (default):
        uv run mcp/server/server.py --host=127.0.0.1 --port=9382 \
            --base-url=http://127.0.0.1:9380 \
            --mode=self-host --api-key=ragflow-xxxxx

    2. Host mode (multi-tenant, self-host only, clients must provide Authorization headers):
        uv run mcp/server/server.py --host=127.0.0.1 --port=9382 \
            --base-url=http://127.0.0.1:9380 \
            --mode=host

    3. Disable legacy SSE (only streamable HTTP will be active):
        uv run mcp/server/server.py --no-transport-sse-enabled \
            --mode=self-host --api-key=ragflow-xxxxx

    4. Disable streamable HTTP (only legacy SSE will be active):
        uv run mcp/server/server.py --no-transport-streamable-http-enabled \
            --mode=self-host --api-key=ragflow-xxxxx

    5. Use streamable HTTP with SSE-style events (disable JSON response):
        uv run mcp/server/server.py --transport-streamable-http-enabled --no-json-response \
            --mode=self-host --api-key=ragflow-xxxxx

    6. Disable both transports (for testing):
        uv run mcp/server/server.py --no-transport-sse-enabled --no-transport-streamable-http-enabled \
            --mode=self-host --api-key=ragflow-xxxxx
    """
    main()
