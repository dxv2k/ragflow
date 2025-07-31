#!/usr/bin/env python3
"""
MonkeyOCR Service for RAGFlow Database Integration
Handles parser registration and document processing
"""

import logging
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
import json

from api.db import ParserType, StatusEnum
from api.db.db_models import DB, Document, Knowledgebase
from api.db.services.common_service import CommonService
from api.db.services.document_service import DocumentService
from api.utils import current_timestamp, get_uuid

from rag.app.monkey_ocr_parser import MonkeyOCRParser, MonkeyOCRFactory

logger = logging.getLogger(__name__)

class MonkeyOCRService(CommonService):
    """MonkeyOCR service for database integration"""
    
    @classmethod
    def get_parser_info(cls) -> Dict[str, Any]:
        """Get MonkeyOCR parser information"""
        try:
            return MonkeyOCRFactory.get_parser_info()
        except Exception as e:
            logger.error(f"Failed to get parser info: {e}")
            return {}
    
    @classmethod
    def create_parser(cls, config_path: Optional[str] = None) -> Optional[MonkeyOCRParser]:
        """Create MonkeyOCR parser instance"""
        try:
            return MonkeyOCRFactory.create_parser(config_path=config_path)
        except Exception as e:
            logger.error(f"Failed to create parser: {e}")
            return None
    
    @classmethod
    @DB.connection_context()
    def register_parser(cls, tenant_id: str) -> bool:
        """Register MonkeyOCR parser with tenant"""
        try:
            # Check if parser is already registered
            tenant = Knowledgebase.select().where(
                Knowledgebase.tenant_id == tenant_id
            ).first()
            
            if tenant:
                parser_ids = tenant.parser_ids.split(',') if tenant.parser_ids else []
                if ParserType.MONKEYOCR.value not in parser_ids:
                    parser_ids.append(ParserType.MONKEYOCR.value)
                    tenant.parser_ids = ','.join(parser_ids)
                    tenant.save()
                    logger.info(f"MonkeyOCR parser registered for tenant {tenant_id}")
                else:
                    logger.info(f"MonkeyOCR parser already registered for tenant {tenant_id}")
            else:
                logger.warning(f"Tenant {tenant_id} not found")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to register parser: {e}")
            return False
    
    @classmethod
    @DB.connection_context()
    def unregister_parser(cls, tenant_id: str) -> bool:
        """Unregister MonkeyOCR parser from tenant"""
        try:
            tenant = Knowledgebase.select().where(
                Knowledgebase.tenant_id == tenant_id
            ).first()
            
            if tenant:
                parser_ids = tenant.parser_ids.split(',') if tenant.parser_ids else []
                if ParserType.MONKEYOCR.value in parser_ids:
                    parser_ids.remove(ParserType.MONKEYOCR.value)
                    tenant.parser_ids = ','.join(parser_ids)
                    tenant.save()
                    logger.info(f"MonkeyOCR parser unregistered for tenant {tenant_id}")
                else:
                    logger.info(f"MonkeyOCR parser not registered for tenant {tenant_id}")
            else:
                logger.warning(f"Tenant {tenant_id} not found")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to unregister parser: {e}")
            return False
    
    @classmethod
    def is_parser_available(cls, tenant_id: str) -> bool:
        """Check if MonkeyOCR parser is available for tenant"""
        try:
            tenant = Knowledgebase.select().where(
                Knowledgebase.tenant_id == tenant_id
            ).first()
            
            if tenant and tenant.parser_ids:
                parser_ids = tenant.parser_ids.split(',')
                return ParserType.MONKEYOCR.value in parser_ids
            return False
            
        except Exception as e:
            logger.error(f"Failed to check parser availability: {e}")
            return False
    
    @classmethod
    def parse_document(cls, doc_id: str, file_path: str, output_dir: Optional[str] = None, 
                      **kwargs) -> Dict[str, Any]:
        """Parse document using MonkeyOCR"""
        try:
            # Create parser instance
            parser = cls.create_parser()
            if not parser:
                return {
                    'success': False,
                    'error': 'Failed to create MonkeyOCR parser'
                }
            
            # Parse document
            result = parser.parse_document(
                file_path=file_path,
                output_dir=output_dir,
                **kwargs
            )
            
            if result['success']:
                # Update document metadata
                cls._update_document_metadata(doc_id, result)
                logger.info(f"Document {doc_id} parsed successfully")
            else:
                logger.error(f"Document {doc_id} parsing failed: {result.get('error', 'Unknown error')}")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to parse document {doc_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @classmethod
    @DB.connection_context()
    def _update_document_metadata(cls, doc_id: str, parse_result: Dict[str, Any]):
        """Update document metadata after parsing"""
        try:
            doc = Document.get(Document.id == doc_id)
            
            # Update metadata fields
            meta_fields = doc.meta_fields or {}
            meta_fields.update({
                'monkeyocr_parsed': True,
                'monkeyocr_parsed_at': current_timestamp(),
                'monkeyocr_output_dir': parse_result.get('parsed_dir', ''),
                'monkeyocr_content_length': len(parse_result.get('content', '')),
                'monkeyocr_content_list_count': len(parse_result.get('content_list', []))
            })
            
            doc.meta_fields = meta_fields
            doc.save()
            
        except Exception as e:
            logger.error(f"Failed to update document metadata: {e}")
    
    @classmethod
    def extract_text_from_images(cls, image_paths: List[str], task: str = "text") -> Dict[str, str]:
        """Extract text from images using MonkeyOCR"""
        try:
            parser = cls.create_parser()
            if not parser:
                return {}
            
            return parser.extract_text_from_images(image_paths, task)
            
        except Exception as e:
            logger.error(f"Failed to extract text from images: {e}")
            return {}
    
    @classmethod
    def get_supported_formats(cls) -> List[str]:
        """Get supported file formats"""
        try:
            parser = cls.create_parser()
            if parser:
                return parser.get_supported_formats()
            return []
        except Exception as e:
            logger.error(f"Failed to get supported formats: {e}")
            return []
    
    @classmethod
    def validate_file(cls, file_path: str) -> bool:
        """Validate if file can be processed by MonkeyOCR"""
        try:
            parser = cls.create_parser()
            if parser:
                return parser.validate_file(file_path)
            return False
        except Exception as e:
            logger.error(f"Failed to validate file: {e}")
            return False
    
    @classmethod
    def get_parsing_options(cls) -> Dict[str, Any]:
        """Get available parsing options"""
        try:
            parser = cls.create_parser()
            if parser:
                return parser.get_parsing_options()
            return {}
        except Exception as e:
            logger.error(f"Failed to get parsing options: {e}")
            return {} 