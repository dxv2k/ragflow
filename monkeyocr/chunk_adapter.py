#!/usr/bin/env python3
"""
MonkeyOCR chunking adapter that uses the layout adapter and rag.nlp utilities.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from .layout_adapter import parse_layout


def chunk(
    filename: str,
    binary: Optional[bytes] = None,
    from_page: int = 0,
    to_page: int = 100000,
    lang: str = "Chinese",
    callback=None,
    **kwargs,
) -> List[Dict[str, Any]]:
    from rag.nlp import rag_tokenizer, naive_merge, tokenize_chunks, tokenize

    parser_config = kwargs.get("parser_config", {})
    is_english = lang.lower() == "english"

    doc = {
        "docnm_kwd": filename,
        "title_tks": rag_tokenizer.tokenize(__import__("re").sub(r"\.[a-zA-Z]+$", "", filename)),
        "doc_type_kwd": "monkeyocr",
    }
    doc["title_sm_tks"] = rag_tokenizer.fine_grained_tokenize(doc["title_tks"])  # type: ignore[attr-defined]

    chunk_token_num = parser_config.get("chunk_token_num")
    delimiter = parser_config.get("delimiter") or "\n!?。；！？"
    split_pages_flag = bool(parser_config.get("split_pages", False))

    # End-to-end default if token limit not set
    if not (isinstance(chunk_token_num, int) and chunk_token_num > 0):
        # Minimal path: tokenize entire doc as one chunk
        # A richer path could call adapter_common.MonkeyOCRParser and reuse content
        tokenize(doc, f"MonkeyOCR processed: {filename}", is_english)
        return [doc]

    # Layout-aware path
    sections, _tables, _figures = parse_layout(
        filename=filename,
        binary=binary,
        from_page=from_page,
        to_page=to_page,
        callback=callback,
        parser_config=parser_config,
        separate_tables_figures=False,
    )

    if not sections:
        tokenize(doc, f"MonkeyOCR processed: {filename}", is_english)
        return [doc]

    def _extract_pn(tag: str) -> int:
        try:
            return int(tag.lstrip("@@").split("\t")[0])
        except Exception:
            return 0

    if split_pages_flag:
        page_to_sections: Dict[int, List[Tuple[str, str]]] = {}
        for text_i, tag_i in sections:
            pn = _extract_pn(tag_i) if tag_i else 0
            page_to_sections.setdefault(pn, []).append((text_i, tag_i))
        all_chunks = []
        for pn in sorted(page_to_sections.keys()):
            subset = page_to_sections[pn]
            if not subset:
                continue
            chs = naive_merge(subset, int(chunk_token_num), delimiter)
            all_chunks.extend(chs)
        return tokenize_chunks(all_chunks, doc, is_english, pdf_parser=None)

    chunks = naive_merge(sections, int(chunk_token_num), delimiter)
    return tokenize_chunks(chunks, doc, is_english, pdf_parser=None)


