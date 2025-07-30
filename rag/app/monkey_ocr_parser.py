#!/usr/bin/env python3
"""
MonkeyOCR Parser for RAGFlow
Integrates MonkeyOCR functionality with RAGFlow's parser system
"""

import os
import sys
import logging
import tempfile
from pathlib import Path
from typing import Optional, Dict, List, Union, Any
import json

# Add monkeyocr to path
monkeyocr_path = Path(__file__).parent.parent.parent / "monkeyocr"
if str(monkeyocr_path) not in sys.path:
    sys.path.insert(0, str(monkeyocr_path))

try:
    from deepdoc.vision.monkey_ocr import MonkeyOCRProcessor
except ImportError as e:
    logging.error(f"Failed to import MonkeyOCR processor: {e}")
    raise

logger = logging.getLogger(__name__)

class MonkeyOCRParser:
    """
    MonkeyOCR parser for RAGFlow integration
    Handles document parsing and content extraction for RAG applications
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize MonkeyOCR parser
        
        Args:
            config_path: Path to MonkeyOCR config file
        """
        self.config_path = config_path
        self.processor = None
        self._initialize_processor()
        
    def _initialize_processor(self):
        """Initialize the MonkeyOCR processor"""
        try:
            self.processor = MonkeyOCRProcessor(config_path=self.config_path)
            logger.info("MonkeyOCR parser initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize MonkeyOCR parser: {e}")
            raise RuntimeError(f"MonkeyOCR parser initialization failed: {e}")
    
    def parse_document(self, 
                      file_path: Union[str, Path],
                      output_dir: Optional[str] = None,
                      **kwargs) -> Dict[str, Any]:
        """
        Parse document and extract content for RAG
        
        Args:
            file_path: Path to document file
            output_dir: Output directory for results
            **kwargs: Additional parsing options
            
        Returns:
            Dictionary containing parsed content and metadata
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Document file does not exist: {file_path}")
        
        # Create output directory if not provided
        if output_dir is None:
            output_dir = tempfile.mkdtemp(prefix="ragflow_monkeyocr_")
        
        logger.info(f"Parsing document: {file_path}")
        logger.info(f"Output directory: {output_dir}")
        
        try:
            # Parse document using MonkeyOCR
            parsed_dir = self.processor.parse_document(
                input_file=file_path,
                output_dir=output_dir,
                split_pages=kwargs.get('split_pages', False),
                pred_abandon=kwargs.get('pred_abandon', False)
            )
            
            # Extract structured content
            content_data = self.processor.get_parsed_content(parsed_dir)
            
            # Prepare RAGFlow compatible result
            result = {
                'success': True,
                'parsed_dir': parsed_dir,
                'content': content_data['markdown_content'],
                'content_list': content_data['content_list'],
                'metadata': {
                    'file_path': str(file_path),
                    'file_name': file_path.name,
                    'file_size': file_path.stat().st_size,
                    'parser': 'monkeyocr',
                    'parsed_at': str(Path(parsed_dir).stat().st_mtime)
                }
            }
            
            logger.info(f"Document parsing completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Document parsing failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'file_path': str(file_path)
            }
    
    def extract_text_from_images(self, 
                                image_paths: List[Union[str, Path]],
                                task: str = "text") -> Dict[str, str]:
        """
        Extract text from images using OCR
        
        Args:
            image_paths: List of image file paths
            task: Task type ('text', 'formula', 'table')
            
        Returns:
            Dictionary mapping filename to extracted text
        """
        try:
            return self.processor.extract_text_from_images(image_paths, task)
        except Exception as e:
            logger.error(f"Text extraction from images failed: {e}")
            return {}
    
    def get_supported_formats(self) -> List[str]:
        """
        Get list of supported file formats
        
        Returns:
            List of supported file extensions
        """
        return ['.pdf', '.jpg', '.jpeg', '.png']
    
    def get_parser_info(self) -> Dict[str, Any]:
        """
        Get parser information
        
        Returns:
            Dictionary containing parser metadata
        """
        return {
            'name': 'monkeyocr',
            'version': '1.0.0',
            'description': 'MonkeyOCR parser for document analysis and OCR',
            'supported_formats': self.get_supported_formats(),
            'capabilities': [
                'document_layout_analysis',
                'text_extraction',
                'formula_recognition',
                'table_extraction',
                'image_ocr'
            ]
        }
    
    def validate_file(self, file_path: Union[str, Path]) -> bool:
        """
        Validate if file can be processed by this parser
        
        Args:
            file_path: Path to file to validate
            
        Returns:
            True if file can be processed, False otherwise
        """
        file_path = Path(file_path)
        if not file_path.exists():
            return False
        
        # Check file extension
        supported_extensions = self.get_supported_formats()
        return file_path.suffix.lower() in supported_extensions
    
    def get_parsing_options(self) -> Dict[str, Any]:
        """
        Get available parsing options
        
        Returns:
            Dictionary of parsing options and their descriptions
        """
        return {
            'split_pages': {
                'type': 'bool',
                'default': False,
                'description': 'Split results by pages'
            },
            'pred_abandon': {
                'type': 'bool',
                'default': False,
                'description': 'Predict abandon elements'
            }
        }


class MonkeyOCRFactory:
    """
    Factory class for creating MonkeyOCR parser instances
    """
    
    @staticmethod
    def create_parser(config_path: Optional[str] = None) -> MonkeyOCRParser:
        """
        Create a new MonkeyOCR parser instance
        
        Args:
            config_path: Path to MonkeyOCR config file
            
        Returns:
            MonkeyOCR parser instance
        """
        return MonkeyOCRParser(config_path=config_path)
    
    @staticmethod
    def get_parser_info() -> Dict[str, Any]:
        """
        Get information about the MonkeyOCR parser
        
        Returns:
            Dictionary containing parser information
        """
        return {
            'name': 'monkeyocr',
            'version': '1.0.0',
            'description': 'MonkeyOCR parser for document analysis and OCR',
            'supported_formats': ['.pdf', '.jpg', '.jpeg', '.png'],
            'capabilities': [
                'document_layout_analysis',
                'text_extraction',
                'formula_recognition',
                'table_extraction',
                'image_ocr'
            ],
            'requirements': [
                'monkeyocr',
                'opencv-python',
                'pdf2image',
                'PIL'
            ]
        } 