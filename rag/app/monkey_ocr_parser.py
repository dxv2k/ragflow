#!/usr/bin/env python3
"""
MonkeyOCR Parser for RAGFlow Integration
Integrates CEDD OCR service with RAGFlow document processing
"""

import logging
import os
from pathlib import Path
from typing import Dict, Any, Optional, List

# Add monkeyocr to path for CEDD OCR service
monkeyocr_path = Path(__file__).parent.parent / "monkeyocr"

from monkeyocr.magic_pdf.model.custom_model import MonkeyOCR
from monkeyocr.parse import parse_file, single_task_recognition

logger = logging.getLogger(__name__)


class MonkeyOCRParser:
    """MonkeyOCR parser for RAGFlow document processing"""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize MonkeyOCR parser"""
        if config_path is None:
            config_path = os.path.join(monkeyocr_path, "model_configs.yaml")

        self.config_path = config_path
        self.monkey_ocr_model = None
        self._initialize_model()

    def _initialize_model(self):
        """Initialize the MonkeyOCR model"""
        try:
            self.monkey_ocr_model = MonkeyOCR(self.config_path)
            logger.info("MonkeyOCR model initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize MonkeyOCR model: {e}")
            raise

    def parse_document(self, file_path: str, output_dir: Optional[str] = None, split_pages: bool = False, pred_abandon: bool = False, **kwargs) -> Dict[str, Any]:
        """Parse document using MonkeyOCR"""
        try:
            if output_dir is None:
                output_dir = os.path.join(os.path.dirname(file_path), "parsed_output")

            os.makedirs(output_dir, exist_ok=True)

            # Use CEDD OCR service to parse the document
            result_dir = parse_file(input_file=file_path, output_dir=output_dir, MonkeyOCR_model=self.monkey_ocr_model, split_pages=split_pages, pred_abandon=pred_abandon)

            # Read the parsed content
            content = self._read_parsed_content(result_dir)

            return {"success": True, "parsed_dir": result_dir, "content": content, "content_list": [content] if content else [], "file_path": file_path}

        except Exception as e:
            logger.error(f"Failed to parse document {file_path}: {e}")
            return {"success": False, "error": str(e), "file_path": file_path}

    def _read_parsed_content(self, result_dir: str) -> str:
        """Read parsed content from result directory"""
        try:
            # Look for markdown files in the result directory
            md_files = list(Path(result_dir).glob("*.md"))
            if md_files:
                with open(md_files[0], "r", encoding="utf-8") as f:
                    return f.read()

            # Look for text files
            txt_files = list(Path(result_dir).glob("*.txt"))
            if txt_files:
                with open(txt_files[0], "r", encoding="utf-8") as f:
                    return f.read()

            return ""

        except Exception as e:
            logger.error(f"Failed to read parsed content: {e}")
            return ""

    def extract_text_from_images(self, image_paths: List[str], task: str = "text") -> Dict[str, str]:
        """Extract text from images using MonkeyOCR"""
        try:
            results = {}
            for image_path in image_paths:
                if not os.path.exists(image_path):
                    logger.warning(f"Image file not found: {image_path}")
                    continue

                # Use single task recognition for text extraction
                result_dir = single_task_recognition(input_file=image_path, output_dir=os.path.dirname(image_path), MonkeyOCR_model=self.monkey_ocr_model, task=task)

                content = self._read_parsed_content(result_dir)
                results[image_path] = content

            return results

        except Exception as e:
            logger.error(f"Failed to extract text from images: {e}")
            return {}

    def get_supported_formats(self) -> List[str]:
        """Get supported file formats"""
        return [".pdf", ".jpg", ".jpeg", ".png", ".tiff", ".bmp"]

    def validate_file(self, file_path: str) -> bool:
        """Validate if file can be processed by MonkeyOCR"""
        try:
            if not os.path.exists(file_path):
                return False

            file_ext = Path(file_path).suffix.lower()
            return file_ext in self.get_supported_formats()

        except Exception as e:
            logger.error(f"Failed to validate file: {e}")
            return False

    def get_parsing_options(self) -> Dict[str, Any]:
        """Get available parsing options"""
        return {"split_pages": False, "pred_abandon": False, "extract_images": True, "generate_layout_pdf": True, "generate_spans_pdf": True}


def chunk(filename, binary=None, from_page=0, to_page=100000, lang="Chinese", callback=None, **kwargs):
    """
    MonkeyOCR chunk function for RAGFlow integration.

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

    try:
        safe_callback(0.1, "Starting MonkeyOCR processing...")

        # Create MonkeyOCR parser instance
        parser = MonkeyOCRParser()

        # Save binary to temporary file if needed
        if binary:
            import tempfile

            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp_file:
                tmp_file.write(binary)
                temp_path = tmp_file.name
        else:
            temp_path = filename

        safe_callback(0.3, "Processing document with MonkeyOCR...")

        # Parse document
        result = parser.parse_document(temp_path)

        if result.get("success"):
            safe_callback(0.8, "Converting to RAGFlow chunks...")

            # Convert to RAGFlow format
            from rag.nlp import tokenize, rag_tokenizer
            import re

            content = result.get("content", "")
            if not content:
                content = f"MonkeyOCR processed: {filename}"

            # Create RAGFlow chunk
            doc = {"docnm_kwd": filename, "title_tks": rag_tokenizer.tokenize(re.sub(r"\.[a-zA-Z]+$", "", filename)), "doc_type_kwd": "monkeyocr"}

            # Tokenize content
            eng = lang.lower() == "english"
            tokenize(doc, content, eng)

            safe_callback(1.0, "MonkeyOCR processing complete")

            # Cleanup temporary file
            if binary and os.path.exists(temp_path):
                os.unlink(temp_path)

            return [doc]
        else:
            safe_callback(-1, f"MonkeyOCR failed: {result.get('error', 'Unknown error')}")
            return []

    except Exception as e:
        safe_callback(-1, f"MonkeyOCR processing failed: {str(e)}")
        logger.error(f"Error processing {filename}: {e}")
        return []


class MonkeyOCRFactory:
    """Factory class for creating MonkeyOCR parser instances"""

    @staticmethod
    def get_parser_info() -> Dict[str, Any]:
        """Get MonkeyOCR parser information"""
        return {
            "name": "CEDD OCR Service",
            "version": "1.0.0",
            "description": "Document parsing with CEDD OCR service",
            "supported_formats": [".pdf", ".jpg", ".jpeg", ".png", ".tiff", ".bmp"],
            "capabilities": {"document_layout_analysis": True, "text_extraction": True, "formula_recognition": True, "table_extraction": True, "image_ocr": True, "omr_processing": True},
        }

    @staticmethod
    def create_parser(config_path: Optional[str] = None) -> MonkeyOCRParser:
        """Create MonkeyOCR parser instance"""
        return MonkeyOCRParser(config_path=config_path)
