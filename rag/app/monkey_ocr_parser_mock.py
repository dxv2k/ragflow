#!/usr/bin/env python3
"""
MonkeyOCR Parser for RAGFlow Integration - MOCK VERSION FOR TESTING
Integrates CEDD OCR service with RAGFlow document processing
Follows exact flow from cedd_parse.py (MOCK IMPLEMENTATION)
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
sys.path.insert(0, str(project_root))

# Mock imports - don't actually import the heavy modules
from monkeyocr.magic_pdf.model.custom_model import MonkeyOCR
from monkeyocr.cedd_parse import cedd_parse

logger = logging.getLogger(__name__)


class MonkeyOCRParserMock:
    """MonkeyOCR parser for RAGFlow document processing - MOCK VERSION"""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize MonkeyOCR parser (MOCK VERSION)"""
        if config_path is None:
            config_path = os.path.join(monkeyocr_path, "model_configs.yaml")

        self.config_path = config_path
        self.monkey_ocr_model = None
        self._initialize_model()

    def _initialize_model(self):
        """Initialize the MonkeyOCR model (MOCK VERSION FOR TESTING)"""
        try:
            print("🔄 [MOCK] Loading MonkeyOCR model...")
            print(f"🔄 [MOCK] Config path: {self.config_path}")
            print("🔄 [MOCK] Model loading phase completed")
            
            # Mock model object for testing
            self.monkey_ocr_model = type('MockMonkeyOCR', (), {
                'config_path': self.config_path,
                'is_loaded': True
            })()
            
            logger.info("MonkeyOCR model initialized successfully (MOCK)")
            print("✅ [MOCK] MonkeyOCR model initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize MonkeyOCR model: {e}")
            print(f"❌ [MOCK] Failed to initialize MonkeyOCR model: {e}")
            raise

    def parse_document(self, file_path: str, output_dir: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        Parse document using MonkeyOCR following exact cedd_parse.py flow (MOCK VERSION FOR TESTING)
        
        Args:
            file_path: Input file path
            output_dir: Output directory (optional)
            **kwargs: Additional arguments
            
        Returns:
            Dict with parsing results
        """
        try:
            # Check if file exists first
            if not os.path.exists(file_path):
                return {"success": False, "error": f"File not found: {file_path}", "file_path": file_path}
            
            if output_dir is None:
                # Create temporary output directory
                output_dir = tempfile.mkdtemp(prefix="monkeyocr_")
            
            print("🔄 [MOCK] Starting MonkeyOCR parsing with cedd_parse flow")
            print(f"🔄 [MOCK] Input file: {file_path}")
            print(f"🔄 [MOCK] Output directory: {output_dir}")
            
            # Mock the cedd_parse flow without actually calling it
            print("🔄 [MOCK] Step 1: Parsing PDF and extracting images...")
            print("🔄 [MOCK] Step 2: Classifying images (text vs OMR forms)...")
            print("🔄 [MOCK] Step 3: Running OCR on text images...")
            print("🔄 [MOCK] Step 4: Running OMR on form images...")
            print("🔄 [MOCK] Step 5: Generating enhanced markdown...")
            
            # Instead of calling cedd_parse, just read the original file content
            content = self._read_file_content(file_path)
            
            # Create mock enhanced markdown path
            enhanced_md_path = os.path.join(output_dir, f"{Path(file_path).stem}_cedd.md")
            
            # Write mock content to the enhanced markdown file
            with open(enhanced_md_path, "w", encoding="utf-8") as f:
                f.write(content)
            
            print("✅ [MOCK] MonkeyOCR processing completed successfully")
            
            return {
                "success": True,
                "parsed_dir": output_dir,
                "enhanced_md_path": enhanced_md_path,
                "content": content,
                "content_list": [content] if content else [],
                "file_path": file_path
            }

        except Exception as e:
            print(f"❌ [MOCK] Failed to parse document {file_path}: {e}")
            logger.error(f"Failed to parse document {file_path}: {e}")
            return {"success": False, "error": str(e), "file_path": file_path}

    def _read_file_content(self, file_path: str) -> str:
        """Read file content directly (MOCK VERSION FOR TESTING)"""
        try:
            print(f"📖 [MOCK] Reading file content: {file_path}")
            
            if os.path.exists(file_path):
                # Try to read as text first
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        print(f"📖 [MOCK] Successfully read text file: {len(content)} characters")
                        return content
                except UnicodeDecodeError:
                    # If it's a binary file, return a mock OCR result
                    print(f"📖 [MOCK] Binary file detected, returning mock OCR content")
                    return f"[MOCK OCR RESULT] Content extracted from {Path(file_path).name}\n\nThis is a mock OCR result for testing purposes. The actual file would be processed by MonkeyOCR with full OCR and OMR capabilities.\n\nFile: {file_path}\nSize: {os.path.getsize(file_path)} bytes\nType: {Path(file_path).suffix}"
            else:
                print(f"❌ [MOCK] File not found: {file_path}")
                return f"[MOCK OCR RESULT] File not found: {file_path}"
                
        except Exception as e:
            print(f"❌ [MOCK] Failed to read file content: {e}")
            logger.error(f"Failed to read file content: {e}")
            return f"[MOCK OCR RESULT] Error reading file: {str(e)}"

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
        Parse only mode - extract images and layout without OCR (MOCK VERSION FOR TESTING)
        Follows cedd_parse.py parse_only mode
        """
        try:
            if output_dir is None:
                output_dir = tempfile.mkdtemp(prefix="monkeyocr_parse_")
            
            print("🔄 [MOCK] Starting parse_only mode")
            print(f"🔄 [MOCK] Input file: {file_path}")
            print(f"🔄 [MOCK] Output directory: {output_dir}")
            
            # Mock parse_only flow
            print("🔄 [MOCK] Step 1: Extracting images from PDF...")
            print("🔄 [MOCK] Step 2: Analyzing document layout...")
            print("🔄 [MOCK] Step 3: Generating layout PDF...")
            print("🔄 [MOCK] Step 4: Saving parsed results...")
            
            # Create mock parsed directory structure
            parsed_dir = os.path.join(output_dir, Path(file_path).stem)
            os.makedirs(parsed_dir, exist_ok=True)
            
            print("✅ [MOCK] Parse only mode completed successfully")
            
            return {
                "success": True,
                "parsed_dir": parsed_dir,
                "file_path": file_path
            }
            
        except Exception as e:
            print(f"❌ [MOCK] Parse only mode failed: {e}")
            logger.error(f"Parse only mode failed: {e}")
            return {"success": False, "error": str(e), "file_path": file_path}

    def ocr_only(self, parsed_folder: str, output_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        OCR only mode - run OCR/OMR on already parsed folder (MOCK VERSION FOR TESTING)
        Follows cedd_parse.py ocr_only mode
        """
        try:
            if output_dir is None:
                output_dir = tempfile.mkdtemp(prefix="monkeyocr_ocr_")
            
            print("🔄 [MOCK] Starting ocr_only mode on folder: {parsed_folder}")
            print(f"🔄 [MOCK] Parsed folder: {parsed_folder}")
            print(f"🔄 [MOCK] Output directory: {output_dir}")
            
            # Mock ocr_only flow
            print("🔄 [MOCK] Step 1: Reading parsed folder...")
            print("🔄 [MOCK] Step 2: Running OCR on text images...")
            print("🔄 [MOCK] Step 3: Running OMR on form images...")
            print("🔄 [MOCK] Step 4: Generating enhanced markdown...")
            
            # Create mock enhanced markdown
            enhanced_md_path = os.path.join(output_dir, f"{Path(parsed_folder).stem}_cedd.md")
            content = f"[MOCK OCR RESULT] Enhanced content from {parsed_folder}\n\nThis is a mock OCR result for testing purposes."
            
            with open(enhanced_md_path, "w", encoding="utf-8") as f:
                f.write(content)
            
            print("✅ [MOCK] OCR only mode completed successfully")
            
            return {
                "success": True,
                "enhanced_md_path": enhanced_md_path,
                "content": content,
                "parsed_folder": parsed_folder
            }
            
        except Exception as e:
            print(f"❌ [MOCK] OCR only mode failed: {e}")
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
            "generate_spans_pdf": True
        }


def chunk(filename, binary=None, from_page=0, to_page=100000, lang="Chinese", callback=None, **kwargs):
    """
    MonkeyOCR chunk function for RAGFlow integration - MOCK VERSION.
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
        safe_callback(0.1, "Starting MonkeyOCR processing with cedd_parse flow (MOCK)...")

        # Create MonkeyOCR parser instance (MOCK)
        parser = MonkeyOCRParserMock()

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

        safe_callback(0.3, "Processing document with cedd_parse full mode (MOCK)...")

        # Parse document using cedd_parse full mode (MOCK)
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
                doc = {
                    "docnm_kwd": filename, 
                    "title_tks": rag_tokenizer.tokenize(re.sub(r"\.[a-zA-Z]+$", "", filename)), 
                    "doc_type_kwd": "monkeyocr"
                }

                # Tokenize content
                eng = lang.lower() == "english"
                tokenize(doc, content, eng)

                safe_callback(1.0, "MonkeyOCR processing complete (MOCK)")

                # Cleanup temporary file
                if binary and os.path.exists(temp_path):
                    os.unlink(temp_path)

                return [doc]
            except ImportError:
                # Fallback if rag.nlp is not available
                safe_callback(0.9, "Using fallback chunk format...")
                
                content = result.get("content", f"MonkeyOCR processed: {filename}")
                
                # Create simple chunk format
                doc = {
                    "docnm_kwd": filename,
                    "title_tks": [filename.replace(".", " ").split()],
                    "doc_type_kwd": "monkeyocr",
                    "content": content,
                    "content_tks": content.split()
                }
                
                safe_callback(1.0, "MonkeyOCR processing complete (MOCK) - Fallback mode")
                
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


class MonkeyOCRFactoryMock:
    """Factory class for creating MonkeyOCR parser instances (MOCK VERSION)"""

    @staticmethod
    def get_parser_info() -> Dict[str, Any]:
        """Get MonkeyOCR parser information"""
        return {
            "name": "CEDD OCR Service (MOCK)",
            "version": "1.0.0-MOCK",
            "description": "Document parsing with CEDD OCR service using cedd_parse.py flow (MOCK VERSION FOR TESTING)",
            "supported_formats": [".pdf", ".jpg", ".jpeg", ".png", ".tiff", ".bmp"],
            "capabilities": {
                "document_layout_analysis": True, 
                "text_extraction": True, 
                "formula_recognition": True, 
                "table_extraction": True, 
                "image_ocr": True, 
                "omr_processing": True,
                "cedd_parse_flow": True,
                "mock_mode": True
            },
            "modes": ["full", "parse_only", "ocr_only"]
        }

    @staticmethod
    def create_parser(config_path: Optional[str] = None) -> MonkeyOCRParserMock:
        """Create MonkeyOCR parser instance (MOCK)"""
        return MonkeyOCRParserMock(config_path=config_path) 