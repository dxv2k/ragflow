#!/usr/bin/env python3
"""
Thin adapter that exposes MonkeyOCR layout and chunking under rag/app.

This module delegates to implementations in the `monkeyocr/` package to avoid
duplicating logic and to keep ownership clear.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional, Tuple


def _should_use_mock(parser_config: Optional[Dict[str, Any]]) -> bool:
    env_flag = os.getenv("MONKEYOCR_USE_MOCK", "0").strip().lower()
    if env_flag in ("1", "true", "yes", "y", "on"):  # env override
        return True
    if isinstance(parser_config, dict) and bool(parser_config.get("use_mock", False)):
        return True
    return False


def parse_layout(
    filename: str,
    binary: Optional[bytes] = None,
    from_page: int = 0,
    to_page: Optional[int] = None,
    callback=None,
    parser_config: Optional[Dict[str, Any]] = None,
    separate_tables_figures: bool = False,
):
    if _should_use_mock(parser_config):
        # Lazy import to avoid heavy deps at import time
        from .monkey_ocr_parser_mock import parse_layout as mock_parse_layout  # type: ignore

        return mock_parse_layout(
            filename=filename,
            binary=binary,
            from_page=from_page,
            to_page=to_page,
            callback=callback,
            parser_config=parser_config,
            separate_tables_figures=separate_tables_figures,
        )
    else:
        from monkeyocr.layout_adapter import parse_layout as real_parse_layout  # type: ignore

        return real_parse_layout(
            filename=filename,
            binary=binary,
            from_page=from_page,
            to_page=to_page,
            callback=callback,
            parser_config=parser_config,
            separate_tables_figures=separate_tables_figures,
        )


def chunk(
    filename: str,
    binary: Optional[bytes] = None,
    from_page: int = 0,
    to_page: int = 100000,
    lang: str = "Chinese",
    callback=None,
    **kwargs,
) -> List[Dict[str, Any]]:
    parser_config = kwargs.get("parser_config")
    if _should_use_mock(parser_config):
        from .monkey_ocr_parser_mock import chunk as mock_chunk  # type: ignore

        return mock_chunk(
            filename=filename,
            binary=binary,
            from_page=from_page,
            to_page=to_page,
            lang=lang,
            callback=callback,
            **kwargs,
        )
    else:
        from monkeyocr.chunk_adapter import chunk as real_chunk  # type: ignore

        return real_chunk(
            filename=filename,
            binary=binary,
            from_page=from_page,
            to_page=to_page,
            lang=lang,
            callback=callback,
            **kwargs,
        )


