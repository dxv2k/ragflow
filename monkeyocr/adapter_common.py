#!/usr/bin/env python3
"""
Common MonkeyOCR adapter utilities: Parser wrapper used by layout/chunk adapters.
"""

import logging
import os
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, Optional

import gc

try:
    import torch  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    torch = None

from .cedd_parse import cedd_parse
from .magic_pdf.model.custom_model import MonkeyOCR  # type: ignore

logger = logging.getLogger(__name__)


class MonkeyOCRParser:
    """MonkeyOCR parser for RAGFlow document processing."""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize MonkeyOCR parser."""
        project_root = Path(__file__).resolve().parents[1]
        default_cfg = project_root / "monkeyocr" / "model_configs.yaml"
        self.config_path = str(default_cfg if config_path is None else config_path)

    def parse_document(self, file_path: str, output_dir: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Parse a document via MonkeyOCR and return enhanced markdown results.

        Returns a dict containing success flag, paths, and content.
        """
        logger.info(f"[MonkeyOCRParser] parse_document: file={file_path}")

        # Lazy import to avoid heavy deps at module import time
        from .magic_pdf.model.custom_model import get_memory_usage  # type: ignore
        from .magic_pdf.model.sub_modules.model_init import AtomModelSingleton  # type: ignore

        model = None
        try:
            if output_dir is None:
                output_dir = tempfile.mkdtemp(prefix="monkeyocr_")

            start_time = time.time()
            model = MonkeyOCR(self.config_path)
            logger.info(f"[MonkeyOCRParser] Model loaded in {time.time() - start_time:.2f}s")

            enhanced_md_path = cedd_parse(
                input_pdf=file_path,
                output_dir=output_dir,
                config_path=self.config_path,
                MonkeyOCR_model=model,
                mode="full",
            )

            if not enhanced_md_path or not os.path.exists(enhanced_md_path):
                return {
                    "success": False,
                    "error": f"Enhanced markdown path missing: {enhanced_md_path}",
                    "file_path": file_path,
                    "parsed_dir": output_dir,
                }

            content = self._read_enhanced_markdown(enhanced_md_path)
            if not content or not content.strip():
                return {
                    "success": False,
                    "error": "Enhanced markdown content is empty",
                    "file_path": file_path,
                    "parsed_dir": output_dir,
                    "enhanced_md_path": enhanced_md_path,
                }

            return {
                "success": True,
                "parsed_dir": output_dir,
                "enhanced_md_path": enhanced_md_path,
                "content": content,
                "content_list": [content],
                "file_path": file_path,
            }
        except Exception as e:  # pragma: no cover - safety
            logger.exception("[MonkeyOCRParser] Exception in parse_document")
            return {"success": False, "error": str(e), "file_path": file_path}
        finally:
            try:
                if model is not None:
                    model.cleanup()  # type: ignore[attr-defined]
                    del model
                    model = None
                if torch and torch.cuda.is_available():
                    torch.cuda.empty_cache()
                    torch.cuda.synchronize()
                gc.collect()
                # Clean temp handled by caller if needed
            except Exception:  # pragma: no cover - best effort cleanup
                pass

    @staticmethod
    def _read_enhanced_markdown(md_path: str) -> str:
        try:
            if os.path.exists(md_path):
                with open(md_path, "r", encoding="utf-8") as f:
                    return f.read()
            return ""
        except Exception:
            return ""


