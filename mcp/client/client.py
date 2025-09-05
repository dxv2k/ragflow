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
import sys
from datetime import datetime
from typing import Optional, Dict, Any, List

from mcp.client.session import ClientSession
from mcp.client.sse import sse_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class RAGFlowMCPClient:
    def __init__(self, server_url: str, auth_token: str):
        self.server_url = server_url
        self.auth_token = auth_token
        self.session: Optional[ClientSession] = None
        self.tools: List[Any] = []

    def print_banner(self):
        print("\n" + "=" * 80)
        print("🚀 RAGFlow Enhanced MCP Client - Interactive Tool Tester")
        print("=" * 80)
        print(f"📡 Server: {self.server_url}")
        print(f"🔑 Token: {self.auth_token[:20]}...")
        print("=" * 80 + "\n")

    def print_separator(self, title: str, emoji: str = "🔧"):
        print(f"\n{'-' * 60}")
        print(f"{emoji} {title.upper()}")
        print("-" * 60)

    def format_tool_arguments(self, arguments: Dict[str, Any]) -> str:
        """Pretty format tool arguments for logging"""
        formatted = []
        for key, value in arguments.items():
            if isinstance(value, str):
                formatted.append(f'  {key}: "{value}"')
            elif isinstance(value, list):
                if len(value) == 0:
                    formatted.append(f'  {key}: []')
                else:
                    items_str = ", ".join([f'"{v}"' for v in value])
                    formatted.append(f'  {key}: [{items_str}]')
            else:
                formatted.append(f'  {key}: {value}')
        return "{\n" + ",\n".join(formatted) + "\n}"

    def _print_full_calltool_result(self, response: Any, label: str = "Full Response") -> None:
        """Print the full CallToolResult including all content fields for debugging."""
        try:
            print(f"\n🔎 {label} (model_dump):")
            if hasattr(response, "model_dump"):
                dumped = response.model_dump(by_alias=True, exclude_none=False)
                print(json.dumps(dumped, indent=2, ensure_ascii=False))
            else:
                # Fallback if not a Pydantic model
                print(str(response))

            # Print each content item in detail as well
            if getattr(response, "content", None):
                print("\n🧩 Content Items (detailed):")
                for idx, content in enumerate(response.content, 1):
                    print(f"\n  • Item {idx} type={getattr(content, 'type', 'unknown')}")
                    try:
                        if hasattr(content, "model_dump"):
                            cdump = content.model_dump(by_alias=True, exclude_none=False)
                            print(json.dumps(cdump, indent=2, ensure_ascii=False))
                        else:
                            # Best-effort dump of attributes
                            attrs = {k: getattr(content, k) for k in dir(content) if not k.startswith("_")}
                            print(json.dumps(attrs, indent=2, default=str, ensure_ascii=False))
                    except Exception as e:  # pragma: no cover - best effort
                        print(f"    (Failed to dump content item: {e})")
        except Exception as e:  # pragma: no cover - best effort
            print(f"(Failed to print full response: {e})")

    def _print_text_as_pretty_json(self, text: str, label: str = "JSON") -> None:
        """Try to parse a text blob as JSON and pretty-print it; fallback to raw text."""
        try:
            obj = json.loads(text)
            print(f"\n🔎 {label} (pretty):")
            print(json.dumps(obj, indent=2, ensure_ascii=False))
        except Exception:
            print(text)

    async def initialize_session(self):
        """Initialize MCP session with verbose logging"""
        logger.info("🔌 Attempting to connect to MCP server...")
        
        try:
            async with sse_client(
                self.server_url,
                headers={"Authorization": f"Bearer {self.auth_token}"}
            ) as streams:
                logger.info("✅ Successfully connected to MCP server via SSE")
                logger.info(f"📊 Streams established: {len(streams)} streams")

                logger.info("🤝 Initializing client session...")
                async with ClientSession(streams[0], streams[1]) as session:
                    self.session = session
                    logger.info("✅ Client session created successfully")
                    
                    logger.info("🔧 Initializing session...")
                    await session.initialize()
                    logger.info("✅ Session initialization completed")
                    
                    await self.discover_tools()
                    await self.run_interactive_session()

        except Exception as e:
            logger.error("❌ Error occurred during MCP client execution")
            logger.error(f"🔍 Error type: {type(e).__name__}")
            logger.error(f"💬 Error message: {str(e)}")
            logger.error("📚 Full error details:", exc_info=True)
            raise

    async def discover_tools(self):
        """Discover available tools with detailed logging"""
        self.print_separator("Tool Discovery", "🔍")
        
        logger.info("🔍 Discovering available tools...")
        tools_response = await self.session.list_tools()
        self.tools = tools_response.tools
        
        logger.info(f"📋 Found {len(self.tools)} available tools:")
        print("\nAvailable Tools:")
        for i, tool in enumerate(self.tools, 1):
            print(f"\n{i}. 🛠️  **{tool.name}**")
            print(f"   📝 Description: {tool.description[:100]}...")
            if hasattr(tool, 'inputSchema') and tool.inputSchema:
                required_fields = tool.inputSchema.get('required', [])
                properties = tool.inputSchema.get('properties', {})
                if required_fields:
                    print(f"   📋 Required: {', '.join(required_fields)}")
                if properties:
                    optional_fields = [k for k in properties.keys() if k not in required_fields]
                    if optional_fields:
                        print(f"   🔧 Optional: {', '.join(optional_fields)}")

    async def test_list_datasets(self):
        """Test list_datasets tool with verbose output"""
        self.print_separator("Testing list_datasets Tool", "📚")
        
        print("🧪 Testing list_datasets tool...")
        
        # Test with default parameters
        arguments = {}
        print(f"📤 Input Arguments: {self.format_tool_arguments(arguments)}")
        
        start_time = datetime.now()
        response = await self.session.call_tool(
            name="list_datasets",
            arguments=arguments
        )
        end_time = datetime.now()
        
        print(f"⏱️  Execution time: {(end_time - start_time).total_seconds():.2f} seconds")
        print(f"📥 Response type: {type(response).__name__}")
        
        if hasattr(response, 'content') and response.content:
            print("\n📄 Response Content:")
            for content in response.content:
                if hasattr(content, 'text'):
                    print(content.text)
        else:
            print(f"📄 Raw Response: {response}")

        # Always show full response for verification
        self._print_full_calltool_result(response, label="list_datasets: Full CallToolResult")

        # Test with pagination
        print(f"\n{'-' * 40}")
        print("🧪 Testing list_datasets with pagination...")
        
        arguments = {"page": 1, "page_size": 5}
        print(f"📤 Input Arguments: {self.format_tool_arguments(arguments)}")
        
        start_time = datetime.now()
        response = await self.session.call_tool(
            name="list_datasets",
            arguments=arguments
        )
        end_time = datetime.now()
        
        print(f"⏱️  Execution time: {(end_time - start_time).total_seconds():.2f} seconds")
        if hasattr(response, 'content') and response.content:
            print("\n📄 Paginated Response:")
            for content in response.content:
                if hasattr(content, 'text'):
                    print(content.text)

        # Full paginated response
        self._print_full_calltool_result(response, label="list_datasets (paginated): Full CallToolResult")

        return response

    async def test_list_documents(self, dataset_id: Optional[str] = None):
        """Test list_documents tool with verbose output"""
        self.print_separator("Testing list_documents Tool", "📁")
        
        if not dataset_id:
            print("⚠️  No dataset_id provided. Using a test dataset ID...")
            # Try to get a dataset ID from previous list_datasets call
            dataset_response = await self.session.call_tool("list_datasets", {})
            dataset_id = "test_dataset_id"  # Fallback
        
        print(f"🧪 Testing list_documents tool with dataset_id: {dataset_id}")
        
        # Test with basic parameters
        arguments = {"dataset_id": dataset_id}
        print(f"📤 Input Arguments: {self.format_tool_arguments(arguments)}")
        
        start_time = datetime.now()
        try:
            response = await self.session.call_tool(
                name="list_documents",
                arguments=arguments
            )
            end_time = datetime.now()
            
            print(f"⏱️  Execution time: {(end_time - start_time).total_seconds():.2f} seconds")
            print(f"📥 Response type: {type(response).__name__}")
            
            if hasattr(response, 'content') and response.content:
                print("\n📄 Response Content:")
                for content in response.content:
                    if hasattr(content, 'text'):
                        print(content.text)
            else:
                print(f"📄 Raw Response: {response}")
            # Full response
            self._print_full_calltool_result(response, label="list_documents: Full CallToolResult")
                
        except Exception as e:
            print(f"❌ Error testing list_documents: {str(e)}")
            
        # Test with additional filters
        print(f"\n{'-' * 40}")
        print("🧪 Testing list_documents with keyword filter...")
        
        arguments = {
            "dataset_id": dataset_id,
            "keywords": "test",
            "page_size": 10
        }
        print(f"📤 Input Arguments: {self.format_tool_arguments(arguments)}")
        
        try:
            start_time = datetime.now()
            response = await self.session.call_tool(
                name="list_documents",
                arguments=arguments
            )
            end_time = datetime.now()
            
            print(f"⏱️  Execution time: {(end_time - start_time).total_seconds():.2f} seconds")
            if hasattr(response, 'content') and response.content:
                print("\n📄 Filtered Response:")
                for content in response.content:
                    if hasattr(content, 'text'):
                        print(content.text)
            # Full filtered response
            self._print_full_calltool_result(response, label="list_documents (filtered): Full CallToolResult")
        except Exception as e:
            print(f"❌ Error testing filtered list_documents: {str(e)}")

        return response

    async def test_knowledge_base_retrieval(self, dataset_ids: List[str] = None, question: str = None):
        """Test knowledge_base_retrieval tool with verbose output"""
        self.print_separator("Testing knowledge_base_retrieval Tool", "🔍")
        
        if not question:
            question = "What documents are required for construction project approval in Hong Kong?"
        
        print(f"🧪 Testing knowledge_base_retrieval tool...")
        print(f"❓ Question: {question}")
        
        # Test with auto-dataset discovery (no dataset_ids)
        arguments = {
            "question": question
        }
        print(f"📤 Input Arguments (Auto-discovery): {self.format_tool_arguments(arguments)}")
        
        start_time = datetime.now()
        try:
            response = await self.session.call_tool(
                name="knowledge_base_retrieval",
                arguments=arguments
            )
            end_time = datetime.now()
            
            print(f"⏱️  Execution time: {(end_time - start_time).total_seconds():.2f} seconds")
            print(f"📥 Response type: {type(response).__name__}")
            
            if hasattr(response, 'content') and response.content:
                # Expect a single JSON content item
                print("\n📄 Retrieval JSON Response:")
                for content in response.content:
                    if hasattr(content, 'text') and content.text:
                        self._print_text_as_pretty_json(content.text, label="knowledge_base_retrieval")
            else:
                print(f"📄 Raw Response: {response}")
                
        except Exception as e:
            print(f"❌ Error testing auto-discovery retrieval: {str(e)}")

        # Test with specific dataset IDs
        if dataset_ids:
            print(f"\n{'-' * 40}")
            print("🧪 Testing knowledge_base_retrieval with specific datasets...")
            
            arguments = {
                "dataset_ids": dataset_ids,
                "question": question
            }
            print(f"📤 Input Arguments (Specific datasets): {self.format_tool_arguments(arguments)}")
            
            try:
                start_time = datetime.now()
                response = await self.session.call_tool(
                    name="knowledge_base_retrieval",
                    arguments=arguments
                )
                end_time = datetime.now()
                
                print(f"⏱️  Execution time: {(end_time - start_time).total_seconds():.2f} seconds")
                if hasattr(response, 'content') and response.content:
                    print("\n📄 Retrieval JSON Response (specific):")
                    for content in response.content:
                        if hasattr(content, 'text') and content.text:
                            self._print_text_as_pretty_json(content.text, label="knowledge_base_retrieval")
            except Exception as e:
                print(f"❌ Error testing specific dataset retrieval: {str(e)}")

        return response

    async def run_comprehensive_tests(self):
        """Run all tools with comprehensive testing"""
        self.print_separator("Comprehensive Tool Testing", "🧪")
        
        # Test 1: List datasets
        datasets_response = await self.test_list_datasets()
        
        # Extract a dataset ID for further testing
        test_dataset_id = None
        if hasattr(datasets_response, 'content') and datasets_response.content:
            try:
                # Try to extract dataset ID from response text
                response_text = datasets_response.content[0].text if datasets_response.content else ""
                if "ID: `" in response_text:
                    import re
                    match = re.search(r'ID: `([^`]+)`', response_text)
                    if match:
                        test_dataset_id = match.group(1)
                        print(f"\n🎯 Extracted dataset ID for testing: {test_dataset_id}")
            except:
                pass
        
        # Test 2: List documents
        await self.test_list_documents(test_dataset_id)
        
        # Test 3: Knowledge base retrieval
        dataset_ids = [test_dataset_id] if test_dataset_id else []
        await self.test_knowledge_base_retrieval(dataset_ids)

    async def run_interactive_session(self):
        """Run interactive session for tool testing"""
        self.print_separator("Interactive Session", "🎮")
        
        while True:
            print("\n" + "=" * 50)
            print("🎮 Interactive MCP Client Menu")
            print("=" * 50)
            print("1. 🧪 Run comprehensive tests (all tools)")
            print("2. 📚 Test list_datasets")
            print("3. 📁 Test list_documents")
            print("4. 🔍 Test knowledge_base_retrieval")
            print("5. 🔎 Read chunk by ID")
            print("6. 🛠️  Show available tools")
            print("7. 🔄 Custom tool call")
            print("8. ❌ Exit")
            print("=" * 50)
            
            try:
                choice = input("Enter your choice (1-7): ").strip()
                
                if choice == "1":
                    await self.run_comprehensive_tests()
                    
                elif choice == "2":
                    await self.test_list_datasets()
                    
                elif choice == "3":
                    dataset_id = input("Enter dataset_id (or press Enter for auto): ").strip()
                    if not dataset_id:
                        dataset_id = None
                    await self.test_list_documents(dataset_id)
                    
                elif choice == "4":
                    question = input("Enter your question (or press Enter for default): ").strip()
                    dataset_ids_input = input("Enter dataset_ids (comma-separated, or press Enter for auto): ").strip()
                    dataset_ids = [id.strip() for id in dataset_ids_input.split(",")] if dataset_ids_input else []
                    await self.test_knowledge_base_retrieval(dataset_ids if dataset_ids else None, question if question else None)
                    
                elif choice == "5":
                    await self.test_read_chunk()
                    
                elif choice == "6":
                    await self.discover_tools()
                    
                elif choice == "7":
                    await self.custom_tool_call()
                    
                elif choice == "8":
                    print("👋 Goodbye!")
                    break
                    
                else:
                    print("❌ Invalid choice. Please select 1-8.")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {str(e)}")

    async def custom_tool_call(self):
        """Allow custom tool calls with user input"""
        print("\n🔄 Custom Tool Call")
        print("-" * 30)
        
        # Show available tools
        if self.tools:
            print("Available tools:")
            for i, tool in enumerate(self.tools):
                print(f"{i+1}. {tool.name}")
        
        tool_name = input("Enter tool name: ").strip()
        if not tool_name:
            print("❌ Tool name cannot be empty")
            return
        
        print("Enter arguments as JSON (or press Enter for empty arguments):")
        args_input = input("Arguments: ").strip()
        
        try:
            arguments = json.loads(args_input) if args_input else {}
        except json.JSONDecodeError:
            print("❌ Invalid JSON format")
            return
        
        print(f"\n🛠️  Calling tool: {tool_name}")
        print(f"📤 Arguments: {self.format_tool_arguments(arguments)}")
        
        try:
            start_time = datetime.now()
            response = await self.session.call_tool(tool_name, arguments)
            end_time = datetime.now()
            
            print(f"⏱️  Execution time: {(end_time - start_time).total_seconds():.2f} seconds")
            print(f"📥 Response type: {type(response).__name__}")
            
            if hasattr(response, 'content') and response.content:
                print("\n📄 Response Content:")
                for content in response.content:
                    if hasattr(content, 'text') and content.text:
                        # Try to pretty print JSON if present
                        self._print_text_as_pretty_json(content.text, label=tool_name)
                    else:
                        print(content)
            else:
                print(f"📄 Raw Response: {response}")
            # Full custom call response
            self._print_full_calltool_result(response, label=f"{tool_name}: Full CallToolResult (custom)")
                
        except Exception as e:
            print(f"❌ Error calling tool: {str(e)}")

    async def test_read_chunk(self):
        """Test read_chunk tool: prompts for IDs and pretty-prints JSON."""
        self.print_separator("Testing read_chunk Tool", "🔎")
        try:
            # Dataset ID prompt with optional listing
            dataset_id = input("Enter dataset_id (press Enter to list): ").strip()
            if not dataset_id:
                print("\n📚 Listing datasets to help you choose...")
                ds_resp = await self.session.call_tool("list_datasets", {})
                if hasattr(ds_resp, 'content') and ds_resp.content:
                    for c in ds_resp.content:
                        if hasattr(c, 'text') and c.text:
                            print(c.text)
                dataset_id = input("\nEnter dataset_id (or 'q' to cancel): ").strip()
                if not dataset_id or dataset_id.lower() == 'q':
                    print("↩️  Cancelled. Returning to menu.")
                    return

            # Document ID prompt with optional listing
            document_id = input("Enter document_id (press Enter to list): ").strip()
            if not document_id:
                print("\n📁 Listing documents in the dataset...")
                docs_resp = await self.session.call_tool("list_documents", {"dataset_id": dataset_id, "page_size": 20})
                if hasattr(docs_resp, 'content') and docs_resp.content:
                    for c in docs_resp.content:
                        if hasattr(c, 'text') and c.text:
                            print(c.text)
                document_id = input("\nEnter document_id (or 'q' to cancel): ").strip()
                if not document_id or document_id.lower() == 'q':
                    print("↩️  Cancelled. Returning to menu.")
                    return

            # Chunk selection with paging
            page = 1
            page_size = 20
            selected_chunk_id = None
            while True:
                print(f"\n🧩 Fetching chunks (page {page})...")
                chunks_resp = await self.session.call_tool(
                    "list_chunks",
                    {"dataset_id": dataset_id, "document_id": document_id, "page": page, "page_size": page_size}
                )
                chunks_json = None
                if hasattr(chunks_resp, 'content') and chunks_resp.content and hasattr(chunks_resp.content[0], 'text'):
                    try:
                        chunks_json = json.loads(chunks_resp.content[0].text)
                    except Exception:
                        print("❌ Failed to parse chunks JSON. Raw:")
                        print(chunks_resp.content[0].text)
                        return
                if not chunks_json:
                    print("❌ No chunk data returned.")
                    return
                chunks = chunks_json.get("chunks", [])
                total = chunks_json.get("total", 0)
                if not chunks:
                    print("⚠️  No chunks on this page.")
                else:
                    print("\nAvailable chunks:")
                    for idx, ch in enumerate(chunks, 1):
                        cid = ch.get("id") or ch.get("chunk_id")
                        preview = (ch.get("content") or "").replace("\n", " ")
                        preview = (preview[:200] + "...") if len(preview) > 200 else preview
                        print(f"{idx}. {cid} — {preview}")
                max_page = (total + page_size - 1) // page_size if page_size else 1
                nav = input(f"\nSelect chunk number, 'n' next, 'p' prev, 'q' quit (page {page}/{max_page}): ").strip().lower()
                if nav == 'q':
                    print("↩️  Cancelled. Returning to menu.")
                    return
                if nav == 'n':
                    if page < max_page:
                        page += 1
                    else:
                        print("⚠️  Already at last page.")
                    continue
                if nav == 'p':
                    if page > 1:
                        page -= 1
                    else:
                        print("⚠️  Already at first page.")
                    continue
                try:
                    sel = int(nav)
                    if 1 <= sel <= len(chunks):
                        selected_chunk_id = chunks[sel - 1].get("id") or chunks[sel - 1].get("chunk_id")
                        break
                    else:
                        print("❌ Invalid selection.")
                except ValueError:
                    print("❌ Please enter a number, 'n', 'p', or 'q'.")

            arguments = {"dataset_id": dataset_id, "document_id": document_id, "chunk_id": selected_chunk_id}
            print(f"📤 Input Arguments: {self.format_tool_arguments(arguments)}")

            start_time = datetime.now()
            response = await self.session.call_tool("read_chunk", arguments)
            end_time = datetime.now()

            print(f"⏱️  Execution time: {(end_time - start_time).total_seconds():.2f} seconds")
            if hasattr(response, 'content') and response.content:
                for content in response.content:
                    if hasattr(content, 'text') and content.text:
                        self._print_text_as_pretty_json(content.text, label="read_chunk")
                    else:
                        print(content)
            else:
                print(f"📄 Raw Response: {response}")
        except KeyboardInterrupt:
            print("\n↩️  Cancelled. Returning to menu.")
            return
        except Exception as e:
            print(f"❌ Error calling read_chunk: {str(e)}")


async def main():
    # Configuration
    # server_url = "https://wise-gibbon-delicate.ngrok-free.app/mcp/sse"
    server_url = "http://localhost:9383/sse"  # For local testing
    
    auth_token = "ragflow-Q2NmRkMzY4Nzc0MjExZjBhMWNhMDI0Mm"
    
    client = RAGFlowMCPClient(server_url, auth_token)
    client.print_banner()
    
    try:
        await client.initialize_session()
    except Exception as e:
        logger.error(f"💥 Application failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    from anyio import run
    
    try:
        run(main)
        logger.info("🎉 MCP client application completed successfully")
    except KeyboardInterrupt:
        logger.info("⏹️  Application interrupted by user")
    except Exception as e:
        logger.error(f"💥 Application failed: {e}")
        sys.exit(1)
