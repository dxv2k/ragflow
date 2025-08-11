#!/usr/bin/env python3
"""
MonkeyOCR layout adapter that returns DeepDoc-compatible triples.
"""

from __future__ import annotations

import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .adapter_common import MonkeyOCRParser


def parse_layout(
    filename: str,
    binary: Optional[bytes] = None,
    from_page: int = 0,
    to_page: Optional[int] = None,
    callback=None,
    parser_config: Optional[Dict[str, Any]] = None,
    separate_tables_figures: bool = False,
) -> Tuple[List[Tuple[str, str]], List[Tuple[Tuple[Optional[Any], str], str]], Optional[List[Any]]]:
    """Parse layout-only view; prefer normalized layout.json when available.

    Returns (sections, tables, figures|None) matching DeepDoc contract.
    """

    def make_tag(pn: Optional[int]) -> str:
        return f"@@{pn}\t0\t0\t0\t0##" if pn is not None else ""

    def is_table_block(lines_block: List[str]) -> bool:
        has_pipe = any("|" in ln for ln in lines_block)
        has_sep = any(re.search(r"\|?\s*:?[-]{3,}\s*:?\s*\|", ln) for ln in lines_block)
        return has_pipe and has_sep

    # Write temp file if binary provided
    if binary:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp:
            tmp.write(binary)
            file_path = tmp.name
    else:
        file_path = filename

    try:
        parser = MonkeyOCRParser()
        result = parser.parse_document(file_path)
        if not result.get("success"):
            return [], [], ([] if separate_tables_figures else None)

        enhanced_md_path = result.get("enhanced_md_path")
        layout_sections: List[Tuple[str, str]] = []
        layout_tables: List[Tuple[Tuple[Optional[Any], str], str]] = []
        layout_figures: Optional[List[Any]] = [] if separate_tables_figures else None

        if enhanced_md_path:
            enhanced_path = Path(enhanced_md_path)
            local_md_dir = enhanced_path.parent
            stem = enhanced_path.stem
            base_stem = stem[:-5] if stem.endswith("_cedd") else stem
            layout_json_path = local_md_dir / f"{base_stem}_layout.json"
            if layout_json_path.exists():
                with open(layout_json_path, "r", encoding="utf-8") as f:
                    payload = json.load(f)
                for sec in payload.get("sections", []) or []:
                    if isinstance(sec, (list, tuple)) and len(sec) >= 2:
                        layout_sections.append((str(sec[0]), str(sec[1])))
                for tbl in payload.get("tables", []) or []:
                    if isinstance(tbl, (list, tuple)) and len(tbl) >= 2:
                        pair, tag = tbl[0], tbl[1]
                        image_or_none = None
                        html = ""
                        if isinstance(pair, (list, tuple)) and len(pair) >= 2:
                            image_or_none = pair[0]
                            html = pair[1]
                        layout_tables.append(((image_or_none, html), str(tag)))
                figs = payload.get("figures", None)
                if separate_tables_figures:
                    layout_figures = figs if isinstance(figs, list) else []
                else:
                    layout_figures = None
                return layout_sections, layout_tables, layout_figures

        # Fallback: parse enhanced markdown heuristically
        content = result.get("content", "") or ""
        if not content.strip():
            return [], [], ([] if separate_tables_figures else None)

        to_page_eff = to_page if to_page is not None else 1_000_000_000
        lines = content.splitlines()
        current_page: Optional[int] = None
        seen_page = False
        sections: List[Tuple[str, str]] = []
        tables: List[Tuple[Tuple[Optional[Any], str], str]] = []
        figures: Optional[List[Any]] = [] if separate_tables_figures else None
        block: List[str] = []

        def flush_block():
            nonlocal block, current_page
            if not block:
                return
            blk = "\n".join(block).strip()
            if not blk:
                block = []
                return
            if is_table_block(block):
                try:
                    from markdown import markdown as md_to_html
                    html = md_to_html(blk, extensions=["markdown.extensions.tables"])  # type: ignore
                except Exception:
                    html = blk
                tables.append(((None, html), make_tag(current_page)))
            else:
                sections.append((blk, make_tag(current_page)))
            block = []

        for ln in lines:
            m = re.match(r"^\s*(?:#+\s*)?(?:Page|PAGE|page)\s+(\d+)\b", ln)
            m2 = re.search(r"\[\[page=(\d+)]]", ln)
            if m or m2:
                flush_block()
                pn = int((m or m2).group(1))
                seen_page = True
                current_page = pn
                continue
            if "\f" in ln:
                flush_block()
                current_page = (current_page + 1) if current_page is not None else 1
                seen_page = True
                ln = ln.replace("\f", "")
                if not ln.strip():
                    continue
            if not ln.strip():
                flush_block()
                continue
            block.append(ln)

        flush_block()

        if seen_page:
            def within(tag: str) -> bool:
                if not tag:
                    return False
                try:
                    pn = int(tag.lstrip("@@").split("\t")[0])
                    return from_page <= pn <= to_page_eff
                except Exception:
                    return True

            sections = [(t, tg) for (t, tg) in sections if within(tg)]
            tables = [tbl for tbl in tables if within(tbl[1])]

        return sections, tables, figures
    finally:
        try:
            if binary and os.path.exists(file_path):
                os.unlink(file_path)
        except Exception:
            pass


