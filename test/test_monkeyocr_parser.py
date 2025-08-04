#!/usr/bin/env python3
"""
Comprehensive test suite for the REAL MonkeyOCR parser
Tests actual cedd_parse integration with RAGFlow
"""

import os
import sys
import tempfile
import time
from pathlib import Path

# Add the project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import the real parser
from rag.app.monkey_ocr_parser import MonkeyOCRParser, chunk, MonkeyOCRFactory


def create_test_files():
    """Create test files for MonkeyOCR testing"""
    test_files = {}

    # Create a test text file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as f:
        f.write("This is a test text file for MonkeyOCR parser testing.\n\nIt contains multiple lines of text to test the parser functionality.")
        test_files["text"] = f.name

    # Create a test PDF file (mock)
    with tempfile.NamedTemporaryFile(mode="w", suffix=".pdf", delete=False, encoding="utf-8") as f:
        f.write(
            "%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Contents 4 0 R\n>>\nendobj\n4 0 obj\n<<\n/Length 44\n>>\nstream\nBT\n/F1 12 Tf\n72 720 Td\n(Test PDF Content) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000204 00000 n \ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\nstartxref\n297\n%%EOF"
        )
        test_files["pdf"] = f.name

    # Create a test image file (mock)
    with tempfile.NamedTemporaryFile(mode="w", suffix=".jpg", delete=False, encoding="utf-8") as f:
        f.write("Mock JPG file content for testing")
        test_files["image"] = f.name

    return test_files


def test_monkeyocr_parser_basic():
    """Test basic MonkeyOCR parser functionality"""
    print("\n🧪 Test 1: Basic MonkeyOCR Parser")

    try:
        # Test parser initialization
        parser = MonkeyOCRParser()
        print("✅ Parser initialization successful")

        # Test supported formats
        formats = parser.get_supported_formats()
        expected_formats = [".pdf", ".jpg", ".jpeg", ".png", ".tiff", ".bmp"]
        assert all(fmt in formats for fmt in expected_formats), f"Expected formats not found: {formats}"
        print("✅ Supported formats validation successful")

        # Test parsing options
        options = parser.get_parsing_options()
        expected_options = ["mode", "split_pages", "pred_abandon", "extract_images", "generate_layout_pdf", "generate_spans_pdf"]
        assert all(opt in options for opt in expected_options), f"Expected options not found: {options}"
        print("✅ Parsing options validation successful")

        print("✅ Basic parser test passed")
        return True

    except Exception as e:
        print(f"❌ Basic parser test failed: {e}")
        return False


def test_monkeyocr_parser_file_validation():
    """Test file validation functionality"""
    print("\n🧪 Test 2: File Validation")

    try:
        parser = MonkeyOCRParser()

        # Create test files
        test_files = create_test_files()

        # Test valid file validation
        assert parser.validate_file(test_files["text"]), "Text file should be valid"
        assert parser.validate_file(test_files["pdf"]), "PDF file should be valid"
        assert parser.validate_file(test_files["image"]), "Image file should be valid"
        print("✅ Valid file validation successful")

        # Test invalid file validation
        assert not parser.validate_file("nonexistent.txt"), "Nonexistent file should be invalid"
        assert not parser.validate_file("test.xyz"), "Unsupported format should be invalid"
        print("✅ Invalid file validation successful")

        # Cleanup
        for file_path in test_files.values():
            if os.path.exists(file_path):
                os.unlink(file_path)

        print("✅ File validation test passed")
        return True

    except Exception as e:
        print(f"❌ File validation test failed: {e}")
        return False


def test_monkeyocr_parser_document_parsing():
    """Test document parsing functionality"""
    print("\n🧪 Test 3: Document Parsing")

    try:
        parser = MonkeyOCRParser()
        test_files = create_test_files()

        # Test text file parsing
        result = parser.parse_document(test_files["text"])
        assert result["success"], f"Text parsing failed: {result.get('error')}"
        assert "content" in result, "Result should contain content"
        assert "parsed_dir" in result, "Result should contain parsed_dir"
        assert "enhanced_md_path" in result, "Result should contain enhanced_md_path"
        print("✅ Text file parsing successful")

        # Test PDF file parsing
        result = parser.parse_document(test_files["pdf"])
        assert result["success"], f"PDF parsing failed: {result.get('error')}"
        assert "content" in result, "Result should contain content"
        print("✅ PDF file parsing successful")

        # Test image file parsing
        result = parser.parse_document(test_files["image"])
        assert result["success"], f"Image parsing failed: {result.get('error')}"
        assert "content" in result, "Result should contain content"
        print("✅ Image file parsing successful")

        # Cleanup
        for file_path in test_files.values():
            if os.path.exists(file_path):
                os.unlink(file_path)

        print("✅ Document parsing test passed")
        return True

    except Exception as e:
        print(f"❌ Document parsing test failed: {e}")
        return False


def test_monkeyocr_parser_modes():
    """Test different parsing modes"""
    print("\n🧪 Test 4: Parsing Modes")

    try:
        parser = MonkeyOCRParser()
        test_files = create_test_files()

        # Test parse_only mode
        result = parser.parse_only(test_files["pdf"])
        assert result["success"], f"Parse only mode failed: {result.get('error')}"
        assert "parsed_dir" in result, "Result should contain parsed_dir"
        print("✅ Parse only mode successful")

        # Test ocr_only mode
        result = parser.ocr_only(test_files["pdf"])
        assert result["success"], f"OCR only mode failed: {result.get('error')}"
        assert "enhanced_md_path" in result, "Result should contain enhanced_md_path"
        assert "content" in result, "Result should contain content"
        print("✅ OCR only mode successful")

        # Cleanup
        for file_path in test_files.values():
            if os.path.exists(file_path):
                os.unlink(file_path)

        print("✅ Parsing modes test passed")
        return True

    except Exception as e:
        print(f"❌ Parsing modes test failed: {e}")
        return False


def test_monkeyocr_chunk_function():
    """Test the chunk function for RAGFlow integration"""
    print("\n🧪 Test 5: Chunk Function")

    try:
        test_files = create_test_files()

        # Test chunk function with text file
        chunks = chunk(test_files["text"], lang="English")
        assert len(chunks) > 0, "Should return at least one chunk"
        assert "docnm_kwd" in chunks[0], "Chunk should contain docnm_kwd"
        assert "title_tks" in chunks[0], "Chunk should contain title_tks"
        assert "doc_type_kwd" in chunks[0], "Chunk should contain doc_type_kwd"
        assert chunks[0]["doc_type_kwd"] == "monkeyocr", "Doc type should be monkeyocr"
        print("✅ Chunk function with text file successful")

        # Test chunk function with binary content
        with open(test_files["text"], "rb") as f:
            binary_content = f.read()

        chunks = chunk("test.txt", binary=binary_content, lang="English")
        assert len(chunks) > 0, "Should return at least one chunk with binary content"
        print("✅ Chunk function with binary content successful")

        # Test chunk function with callback
        progress_calls = []

        def test_callback(progress, message):
            progress_calls.append((progress, message))

        chunks = chunk(test_files["text"], lang="English", callback=test_callback)
        assert len(progress_calls) > 0, "Callback should be called"
        assert any(progress >= 0.8 for progress, _ in progress_calls), "Should reach high progress"
        print("✅ Chunk function with callback successful")

        # Cleanup
        for file_path in test_files.values():
            if os.path.exists(file_path):
                os.unlink(file_path)

        print("✅ Chunk function test passed")
        return True

    except Exception as e:
        print(f"❌ Chunk function test failed: {e}")
        return False


def test_monkeyocr_factory():
    """Test MonkeyOCR factory functionality"""
    print("\n🧪 Test 6: MonkeyOCR Factory")

    try:
        # Test factory info
        info = MonkeyOCRFactory.get_parser_info()
        assert info["name"] == "CEDD OCR Service", "Factory name should match"
        assert info["version"] == "1.0.0", "Factory version should match"
        assert "capabilities" in info, "Factory should have capabilities"
        assert info["capabilities"]["cedd_parse_flow"] is True, "Factory should have cedd_parse_flow"
        print("✅ Factory info validation successful")

        # Test factory parser creation
        parser = MonkeyOCRFactory.create_parser()
        assert isinstance(parser, MonkeyOCRParser), "Factory should create MonkeyOCRParser instance"
        print("✅ Factory parser creation successful")

        print("✅ MonkeyOCR factory test passed")
        return True

    except Exception as e:
        print(f"❌ MonkeyOCR factory test failed: {e}")
        return False


def test_monkeyocr_error_handling():
    """Test error handling in MonkeyOCR parser"""
    print("\n🧪 Test 7: Error Handling")

    try:
        parser = MonkeyOCRParser()

        # Test with nonexistent file
        result = parser.parse_document("nonexistent_file.pdf")
        assert not result["success"], "Should fail with nonexistent file"
        assert "error" in result, "Should contain error message"
        print("✅ Nonexistent file error handling successful")

        # Test with unsupported format
        with tempfile.NamedTemporaryFile(suffix=".xyz", delete=False) as f:
            f.write(b"test content")
            unsupported_file = f.name

        # The parser should still validate the file format
        assert not parser.validate_file(unsupported_file), "Unsupported format should be invalid"
        print("✅ Unsupported format validation successful")

        # Cleanup
        if os.path.exists(unsupported_file):
            os.unlink(unsupported_file)

        print("✅ Error handling test passed")
        return True

    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False


def test_monkeyocr_performance():
    """Test performance aspects of MonkeyOCR parser"""
    print("\n🧪 Test 8: Performance Testing")

    try:
        parser = MonkeyOCRParser()
        test_files = create_test_files()

        # Test parsing speed
        start_time = time.time()
        result = parser.parse_document(test_files["text"])
        end_time = time.time()

        processing_time = end_time - start_time
        assert processing_time < 30.0, f"Processing took too long: {processing_time}s"
        assert result["success"], "Processing should succeed"
        print(f"✅ Processing speed test passed: {processing_time:.2f}s")

        # Test chunk function performance
        start_time = time.time()
        chunks = chunk(test_files["text"], lang="English")
        end_time = time.time()

        chunk_time = end_time - start_time
        assert chunk_time < 30.0, f"Chunking took too long: {chunk_time}s"
        assert len(chunks) > 0, "Should return chunks"
        print(f"✅ Chunking speed test passed: {chunk_time:.2f}s")

        # Cleanup
        for file_path in test_files.values():
            if os.path.exists(file_path):
                os.unlink(file_path)

        print("✅ Performance test passed")
        return True

    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False


def test_monkeyocr_cedd_parse_integration():
    """Test that the parser correctly uses cedd_parse"""
    print("\n🧪 Test 9: CEDD Parse Integration")

    try:
        parser = MonkeyOCRParser()
        test_files = create_test_files()

        # Test that the parser actually calls cedd_parse
        result = parser.parse_document(test_files["text"])

        # Check that the result contains the expected cedd_parse output structure
        assert result["success"], "CEDD parse should succeed"
        assert "enhanced_md_path" in result, "Should have enhanced markdown path from cedd_parse"
        assert "content" in result, "Should have content from cedd_parse"

        # Check that the enhanced markdown file exists
        if result.get("enhanced_md_path"):
            assert os.path.exists(result["enhanced_md_path"]), "Enhanced markdown file should exist"
            print("✅ CEDD parse integration successful")

        # Cleanup
        for file_path in test_files.values():
            if os.path.exists(file_path):
                os.unlink(file_path)

        print("✅ CEDD parse integration test passed")
        return True

    except Exception as e:
        print(f"❌ CEDD parse integration test failed: {e}")
        return False


def main():
    """Run all MonkeyOCR real parser tests"""
    print("🧪 Starting comprehensive MonkeyOCR Real Parser tests...")
    print("=" * 60)

    tests = [
        ("Basic Parser", test_monkeyocr_parser_basic),
        ("File Validation", test_monkeyocr_parser_file_validation),
        ("Document Parsing", test_monkeyocr_parser_document_parsing),
        ("Parsing Modes", test_monkeyocr_parser_modes),
        ("Chunk Function", test_monkeyocr_chunk_function),
        ("MonkeyOCR Factory", test_monkeyocr_factory),
        ("Error Handling", test_monkeyocr_error_handling),
        ("Performance Testing", test_monkeyocr_performance),
        ("CEDD Parse Integration", test_monkeyocr_cedd_parse_integration),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        print(f"\n{'=' * 20} {test_name} {'=' * 20}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                failed += 1
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            failed += 1
            print(f"❌ {test_name}: ERROR - {e}")

    print("\n" + "=" * 60)
    print(f"🎯 Test Results: {passed} PASSED, {failed} FAILED")

    if failed == 0:
        print("🎉 All tests passed! Real MonkeyOCR parser is working correctly.")
        return True
    else:
        print(f"⚠️  {failed} tests failed. Please review the issues above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
