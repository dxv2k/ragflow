#!/usr/bin/env python3
"""
MonkeyOCR Parser for RAGFlow Integration
Integrates CEDD OCR service with RAGFlow document processing
Follows exact flow from cedd_parse.py
"""

import logging
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
import json

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
    
    def parse_document(self, file_path: str, output_dir: Optional[str] = None, 
                      split_pages: bool = False, pred_abandon: bool = False,
                      **kwargs) -> Dict[str, Any]:
        """Parse document using MonkeyOCR"""
        try:
            if output_dir is None:
                output_dir = os.path.join(os.path.dirname(file_path), "parsed_output")
            
            os.makedirs(output_dir, exist_ok=True)
            
            # Use CEDD OCR service to parse the document
            result_dir = parse_file(
                input_file=file_path,
                output_dir=output_dir,
                MonkeyOCR_model=self.monkey_ocr_model,
                split_pages=split_pages,
                pred_abandon=pred_abandon
            )
            
            # Read the parsed content
            content = self._read_parsed_content(result_dir)
            
            return {
                'success': True,
                'parsed_dir': result_dir,
                'content': content,
                'content_list': [content] if content else [],
                'file_path': file_path
            }
            
        except Exception as e:
            logger.error(f"Failed to parse document {file_path}: {e}")
            return {
                'success': False,
                'error': str(e),
                'file_path': file_path
            }
    
    def _read_parsed_content(self, result_dir: str) -> str:
        """Read parsed content from result directory"""
        try:
            # Look for markdown files in the result directory
            md_files = list(Path(result_dir).glob("*.md"))
            if md_files:
                with open(md_files[0], 'r', encoding='utf-8') as f:
                    return f.read()
            
            # Look for text files
            txt_files = list(Path(result_dir).glob("*.txt"))
            if txt_files:
                with open(txt_files[0], 'r', encoding='utf-8') as f:
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
                result_dir = single_task_recognition(
                    input_file=image_path,
                    output_dir=os.path.dirname(image_path),
                    MonkeyOCR_model=self.monkey_ocr_model,
                    task=task
                )
                
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
        return {
            'split_pages': False,
            'pred_abandon': False,
            'extract_images': True,
            'generate_layout_pdf': True,
            'generate_spans_pdf': True
        }


class MonkeyOCRFactory:
    """Factory class for creating MonkeyOCR parser instances"""
    
    @staticmethod
    def get_parser_info() -> Dict[str, Any]:
        """Get MonkeyOCR parser information"""
        return {
            "name": "CEDD OCR Service",
            "version": "1.0.0",
            "description": "Document parsing with CEDD OCR service using cedd_parse.py flow",
            "supported_formats": [".pdf", ".jpg", ".jpeg", ".png", ".tiff", ".bmp"],
            "capabilities": {
                "document_layout_analysis": True,
                "text_extraction": True,
                "formula_recognition": True,
                "table_extraction": True,
                "image_ocr": True,
                "omr_processing": True
            }
        }
    
    @staticmethod
    def create_parser(config_path: Optional[str] = None) -> MonkeyOCRParser:
        """Create MonkeyOCR parser instance"""
        return MonkeyOCRParser(config_path=config_path) 