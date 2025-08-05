#!/usr/bin/env python3
"""
MonkeyOCR Parser for RAGFlow Integration
Integrates CEDD OCR service with RAGFlow document processing
Follows exact flow from cedd_parse.py
"""

import logging
import os
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional, List

# Add monkeyocr to path for CEDD OCR service
import sys

project_root = Path(__file__).parent.parent.parent
monkeyocr_path = project_root / "monkeyocr"
sys.path.insert(0, str(monkeyocr_path))

# Import the actual cedd_parse function
from monkeyocr.cedd_parse import cedd_parse
from monkeyocr.magic_pdf.model.custom_model import MonkeyOCR

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
            # Create a temporary config with absolute paths
            import tempfile
            import yaml
            
            # Read the original config
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # Update the models_dir to use absolute path
            config['models_dir'] = os.path.join(monkeyocr_path, 'model_weight')
            
            # Update chat_config weight_path to use absolute path
            if 'chat_config' in config and 'weight_path' in config['chat_config']:
                config['chat_config']['weight_path'] = os.path.join(monkeyocr_path, 'model_weight', 'Recognition')
            
            # Create a temporary config file with absolute paths
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                yaml.dump(config, f)
                temp_config_path = f.name
            
            self.monkey_ocr_model = MonkeyOCR(temp_config_path)
            logger.info("MonkeyOCR model initialized successfully")
            
            # Clean up temporary file
            os.unlink(temp_config_path)
            
        except Exception as e:
            logger.error(f"Failed to initialize MonkeyOCR model: {e}")
            raise

    def parse_document(self, file_path: str, output_dir: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        Parse document using MonkeyOCR following exact cedd_parse.py flow

        Args:
            file_path: Input file path
            output_dir: Output directory (optional)
            **kwargs: Additional arguments

        Returns:
            Dict with parsing results
        """
        try:
            if output_dir is None:
                # Create temporary output directory
                output_dir = tempfile.mkdtemp(prefix="monkeyocr_")

            logger.info("Starting MonkeyOCR parsing with cedd_parse flow")
            logger.info(f"Input file: {file_path}")
            logger.info(f"Output directory: {output_dir}")

            # Use cedd_parse with 'full' mode (default)
            enhanced_md_path = cedd_parse(input_pdf=file_path, output_dir=output_dir, config_path=self.config_path, MonkeyOCR_model=self.monkey_ocr_model, mode="full")

            # Read the enhanced markdown content
            content = self._read_enhanced_markdown(enhanced_md_path)

            logger.info("MonkeyOCR processing completed successfully")

            return {"success": True, "parsed_dir": output_dir, "enhanced_md_path": enhanced_md_path, "content": content, "content_list": [content] if content else [], "file_path": file_path}

        except Exception as e:
            logger.error(f"Failed to parse document {file_path}: {e}")
            return {"success": False, "error": str(e), "file_path": file_path}

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

    def parse_only(self, file_path: str, output_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Parse only mode - extract images and layout without OCR
        Follows cedd_parse.py parse_only mode
        """
        try:
            if output_dir is None:
                output_dir = tempfile.mkdtemp(prefix="monkeyocr_parse_")

            logger.info("Starting parse_only mode")
            logger.info(f"Input file: {file_path}")
            logger.info(f"Output directory: {output_dir}")

            # Use cedd_parse with parse_only mode
            parsed_dir = cedd_parse(input_pdf=file_path, output_dir=output_dir, config_path=self.config_path, MonkeyOCR_model=self.monkey_ocr_model, mode="parse_only")

            logger.info("Parse only mode completed successfully")

            return {"success": True, "parsed_dir": parsed_dir, "file_path": file_path}

        except Exception as e:
            logger.error(f"Parse only mode failed: {e}")
            return {"success": False, "error": str(e), "file_path": file_path}

    def ocr_only(self, parsed_folder: str, output_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        OCR only mode - run OCR/OMR on already parsed folder
        Follows cedd_parse.py ocr_only mode
        """
        try:
            if output_dir is None:
                output_dir = tempfile.mkdtemp(prefix="monkeyocr_ocr_")

            logger.info(f"Starting ocr_only mode on folder: {parsed_folder}")
            logger.info(f"Parsed folder: {parsed_folder}")
            logger.info(f"Output directory: {output_dir}")

            # Use cedd_parse with ocr_only mode
            enhanced_md_path = cedd_parse(output_dir=output_dir, config_path=self.config_path, MonkeyOCR_model=self.monkey_ocr_model, parsed_folder=parsed_folder, mode="ocr_only")

            # Read the enhanced markdown content
            content = self._read_enhanced_markdown(enhanced_md_path)

            logger.info("OCR only mode completed successfully")

            return {"success": True, "enhanced_md_path": enhanced_md_path, "content": content, "parsed_folder": parsed_folder}

        except Exception as e:
            logger.error(f"OCR only mode failed: {e}")
            return {"success": False, "error": str(e), "parsed_folder": parsed_folder}

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

    try:
        safe_callback(0.1, "Starting MonkeyOCR processing with cedd_parse flow...")

        # Create MonkeyOCR parser instance
        parser = MonkeyOCRParser()

        # Save binary to temporary file if needed
        if binary:
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp_file:
                tmp_file.write(binary)
                temp_path = tmp_file.name
        else:
            temp_path = filename

        safe_callback(0.2, "Validating file format...")

        # Validate file format
        if not parser.validate_file(temp_path):
            safe_callback(-1, f"Unsupported file format: {filename}")
            return []

        safe_callback(0.3, "Processing document with cedd_parse full mode...")

        # Get parser configuration from kwargs
        parser_config = kwargs.get("parser_config", {})
        
        # Use layout_recognize field to determine processing mode
        layout_recognize = parser_config.get("layout_recognize", "MonkeyOCR")
        
        # Parse document using cedd_parse
        result = parser.parse_document(temp_path)

        if result.get("success"):
            safe_callback(0.8, "Converting to RAGFlow chunks...")

            # Convert to RAGFlow format
            try:
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
            except ImportError:
                # Fallback if rag.nlp is not available
                safe_callback(0.9, "Using fallback chunk format...")

                content = result.get("content", f"MonkeyOCR processed: {filename}")

                # Create simple chunk format
                doc = {"docnm_kwd": filename, "title_tks": [filename.replace(".", " ").split()], "doc_type_kwd": "monkeyocr", "content": content, "content_tks": content.split()}

                safe_callback(1.0, "MonkeyOCR processing complete - Fallback mode")

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

if __name__ == "__main__":
    import sys

    def dummy(prog=None, msg=""):
        pass

    chunk(sys.argv[1], from_page=0, to_page=10, callback=dummy)