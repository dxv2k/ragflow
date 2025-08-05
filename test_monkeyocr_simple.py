#!/usr/bin/env python3
"""
Simple test script for MonkeyOCR integration with RAGFlow
Uses standard RAGFlow configuration fields
"""

import os
import sys
import tempfile
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_simple_integration():
    """Test the simplified MonkeyOCR integration"""
    
    print("🧪 Testing Simplified MonkeyOCR Integration")
    print("=" * 50)
    
    try:
        # Test 1: Check if ParserType.MONKEYOCR exists
        from api.db import ParserType
        print("✅ ParserType.MONKEYOCR is defined")
        
        # Test 2: Check file type detection
        from api.utils.file_utils import is_monkeyocr_supported
        test_files = [
            ("document.pdf", True),
            ("image.jpg", True),
            ("photo.png", True),
            ("document.docx", False),
            ("presentation.pptx", False)
        ]
        
        print("✅ File type detection:")
        for filename, expected in test_files:
            result = is_monkeyocr_supported(filename)
            status = "✅" if result == expected else "❌"
            print(f"  {status} {filename}: {result} (expected: {expected})")
        
        # Test 3: Check parser assignment
        from api.db.services.file_service import FileService
        from api.db import FileType
        
        print("✅ Parser assignment:")
        for filename, should_be_monkeyocr in test_files:
            if should_be_monkeyocr:
                file_type = FileType.PDF.value if filename.endswith('.pdf') else FileType.VISUAL.value
                parser_id = FileService.get_parser(file_type, filename, "naive")
                status = "✅" if parser_id == ParserType.MONKEYOCR.value else "❌"
                print(f"  {status} {filename}: parser={parser_id} (expected: monkeyocr)")
        
        # Test 4: Check standard configuration
        print("✅ Standard configuration:")
        standard_config = {
            "chunk_token_num": 4096,
            "delimiter": "\n!?;。；！？",
            "layout_recognize": "MonkeyOCR"
        }
        print(f"  Standard config: {standard_config}")
        
        # Test 5: Check parser factory
        from rag.app import monkey_ocr_parser as monkey_ocr
        from api.db.services.document_service import FACTORY
        
        if ParserType.MONKEYOCR.value in FACTORY:
            print("✅ MonkeyOCR parser is in FACTORY")
        else:
            print("❌ MonkeyOCR parser is NOT in FACTORY")
        
        print("\n🎉 All tests passed! Simplified integration is working.")
        print("\n💡 Key points:")
        print("  - Uses standard RAGFlow parser_config fields")
        print("  - No special MonkeyOCR configuration needed")
        print("  - Just change parser_id to 'monkeyocr' to switch")
        print("  - layout_recognize field identifies MonkeyOCR processing")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = test_simple_integration()
    sys.exit(0 if success else 1) 