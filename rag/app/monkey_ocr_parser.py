#!/usr/bin/env python3
"""
MonkeyOCR Parser for RAGFlow Integration
Integrates CEDD OCR service with RAGFlow document processing
Follows exact flow from cedd_parse.py
"""

import logging
import os
import tempfile
import time
from pathlib import Path
from typing import Dict, Any, Optional, List

# Add monkeyocr to path for CEDD OCR service
import sys
import gc

try:
    import torch
except ImportError:
    torch = None

project_root = Path(__file__).parent.parent.parent
monkeyocr_path = project_root / "monkeyocr"
sys.path.insert(0, str(monkeyocr_path))

# Import the actual cedd_parse function
from monkeyocr.cedd_parse import cedd_parse
from monkeyocr.magic_pdf.model.custom_model import MonkeyOCR

# Phase 1: introduce DeepDoc-compatible MonkeyDoc parser scaffolding.
try:
    from monkeydoc.parser import MonkeyDocPdfParser  # type: ignore
except Exception:
    MonkeyDocPdfParser = None  # Fallback if scaffolding not available yet

logger = logging.getLogger(__name__)


class MonkeyOCRParser:
    """MonkeyOCR parser for RAGFlow document processing"""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize MonkeyOCR parser"""
        if config_path is None:
            config_path = os.path.join(monkeyocr_path, "model_configs.yaml")

        self.config_path = config_path

    def _read_enhanced_markdown(self, md_path: str) -> str:
        """Read enhanced markdown content from cedd_parse output"""
        try:
            if os.path.exists(md_path):
                with open(md_path, "r", encoding="utf-8") as f:
                    return f.read()
            else:
                logger.warning(f"Enhanced markdown file not found: {md_path}")
                return ""
        except Exception as e:
            logger.error(f"Failed to read enhanced markdown: {e}")
            return ""

    def get_supported_formats(self) -> List[str]:
        """Get supported file formats"""
        return [".pdf", ".jpg", ".jpeg", ".png", ".tiff", ".bmp"]

    def validate_file(self, file_path: str) -> bool:
        """Validate if file can be processed by MonkeyOCR"""
        try:
            if not os.path.exists(file_path):
                return False

            file_ext = Path(file_path).suffix.lower()
            supported_formats = self.get_supported_formats()
            return file_ext in supported_formats

        except Exception as e:
            logger.error(f"Failed to validate file: {e}")
            return False

    def get_parsing_options(self) -> Dict[str, Any]:
        """Get available parsing options"""
        return {
            "mode": "full",  # full, parse_only, ocr_only
            "split_pages": False,
            "pred_abandon": False,
            "extract_images": True,
            "generate_layout_pdf": True,
            "generate_spans_pdf": True,
        }


def chunk(filename, binary=None, from_page=0, to_page=100000, lang="Chinese", callback=None, **kwargs):
    """
    MonkeyOCR chunk function for RAGFlow integration.
    Follows exact cedd_parse.py flow with 'full' mode.

    Args:
        filename (str): File name
        binary (bytes): File content
        from_page (int): Start page
        to_page (int): End page
        lang (str): Language
        callback (function): Progress callback
        **kwargs: Additional arguments

    Returns:
        list: List of document chunks
    """

    def safe_callback(progress, message):
        if callback:
            callback(progress, message)

    logger.info(f"🔄 MonkeyOCR chunk function started for file: {filename}")
    logger.info(f"📋 Parameters: from_page={from_page}, to_page={to_page}, lang={lang}")
    logger.info(f"📦 Binary size: {len(binary) if binary else 'None'} bytes")
    logger.info(f"⚙️ Parser config: {kwargs.get('parser_config', {})}")

    try:
        safe_callback(0.1, "Starting MonkeyOCR processing with cedd_parse flow...")
        logger.info("✅ Step 1: Starting MonkeyOCR processing")

        # Create MonkeyOCR parser instance
        logger.info("🔧 Creating MonkeyOCR parser instance...")
        parser = MonkeyOCRParser()
        logger.info("✅ MonkeyOCR parser instance created")

        # Save binary to temporary file if needed
        if binary:
            logger.info("💾 Saving binary to temporary file...")
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp_file:
                tmp_file.write(binary)
                temp_path = tmp_file.name
            logger.info(f"✅ Binary saved to temporary file: {temp_path}")
        else:
            temp_path = filename
            logger.info(f"📁 Using existing file path: {temp_path}")

        safe_callback(0.2, "Validating file format...")
        logger.info("🔍 Step 2: Validating file format...")

        # Validate file format
        if not parser.validate_file(temp_path):
            error_msg = f"Unsupported file format: {filename}"
            logger.error(f"❌ {error_msg}")
            safe_callback(-1, error_msg)
            return []
        
        logger.info("✅ File format validation passed")

        safe_callback(0.3, "Processing document with cedd_parse full mode...")
        logger.info("🚀 Step 3: Processing document with cedd_parse full mode...")

        # Get parser configuration from kwargs
        parser_config = kwargs.get("parser_config", {})
        logger.info(f"⚙️ Parser config: {parser_config}")
        
        if MonkeyDocPdfParser is not None:
            safe_callback(0.4, "MonkeyOCR: rendering and layout/OCR...")
            try:
                # Parse with DeepDoc-compatible MonkeyDoc
                pdf_parser = MonkeyDocPdfParser()
                # Determine table HTML flag and whether to return images
                mcfg = parser_config.get("monkeyocr", {}) if isinstance(parser_config, dict) else {}
                return_html = bool(mcfg.get("table_html", True))
                # Default to sections-only (no images) to avoid unnecessary crops
                need_image = bool(mcfg.get("return_images", False))
                # Read MonkeyOCR config flags
                omr_cfg = mcfg.get("omr", {}) if isinstance(mcfg, dict) else {}
                omr_enabled = bool(omr_cfg.get("enabled", True))
                omr_min_area = float(omr_cfg.get("min_area", 500.0))
                omr_max_aspect = float(omr_cfg.get("max_aspect", 10.0))
                chunk_token_num = int(parser_config.get("chunk_token_num", 256))
                sections, tbls = pdf_parser(
                    temp_path,
                    need_image=need_image,
                    zoomin=3,
                    return_html=return_html,
                    omr_enabled=omr_enabled,
                    omr_min_area=omr_min_area,
                    omr_max_aspect=omr_max_aspect
                )
                logger.info(f"🔍 MonkeyOCR: Packing sections: {sections}")
                from monkeydoc.utils import pack_by_token_limit
                sections = pack_by_token_limit(sections, chunk_token_num=chunk_token_num)
                logger.info(f"🔍 MonkeyOCR: Packed sections: {sections}")
                safe_callback(0.7, "MonkeyOCR: building chunks...")
                from rag.nlp import tokenize_chunks, tokenize_table, rag_tokenizer
                import re

                # Base doc metadata
                base_doc = {
                    "docnm_kwd": filename,
                    "title_tks": rag_tokenizer.tokenize(re.sub(r"\.[a-zA-Z]+$", "", filename)),
                    "doc_type_kwd": "monkeyocr",
                }
                eng = lang.lower() == "english"

                # Tokenize sections with position tags; pass parser to crop/remove_tag
                docs_text = tokenize_chunks([s[0] if isinstance(s, tuple) else s for s in sections], base_doc, eng, pdf_parser=pdf_parser)

                # Tokenize tables/figures
                docs_tbls = tokenize_table(tbls, base_doc, eng)

                docs = (docs_text or []) + (docs_tbls or [])
                safe_callback(1.0, f"MonkeyOCR: {len(docs)} chunks ready")

                if binary and os.path.exists(temp_path):
                    os.unlink(temp_path)
                return docs
            except Exception as e:
                logger.warning(f"MonkeyDoc path failed, falling back to enhanced markdown path: {e}")

    except Exception as e:
        error_msg = f"MonkeyOCR processing failed: {str(e)}"
        logger.error(f"❌ {error_msg}")
        logger.exception(f"Exception details for {filename}:")
        safe_callback(-1, error_msg)
        return []
    finally:
        logger.info(f"🏁 MonkeyOCR chunk function finished for file: {filename}")

if __name__ == "__main__":
    import sys

    def dummy(prog=None, msg=""):
        pass

    chunk(sys.argv[1], from_page=0, to_page=10, callback=dummy)