#!/usr/bin/env python3
"""
Complete Integration Test for MonkeyOCR + RAGFlow
Tests all components of the integration
"""

import sys
import logging
import json
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def test_file_structure():
    """Test that all required files exist"""
    logger.info("Testing complete file structure...")

    required_files = [
        # Core integration files
        "deepdoc/vision/monkey_ocr.py",
        "rag/app/monkey_ocr_parser.py",
        "api/db/services/monkeyocr_service.py",
        "api/apps/monkeyocr_app.py",
        # Configuration files
        "conf/monkey_ocr_config.json",
        "requirements_monkeyocr.txt",
        # Docker files
        "Dockerfile.monkeyocr",
        "docker-compose-monkeyocr.yml",
        "docker/init_monkeyocr.sh",
        # MonkeyOCR source
        "monkeyocr/cedd_parse.py",
        "monkeyocr/model_configs.yaml",
        "monkeyocr/requirements.txt",
        # Documentation
        "MONKEYOCR_COMPLETE_INTEGRATION.md",
    ]

    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
        else:
            logger.info(f"✅ Found: {file_path}")

    if missing_files:
        logger.error(f"❌ Missing files: {missing_files}")
        return False

    logger.info("✅ All required files exist")
    return True


def test_database_integration():
    """Test database integration components"""
    logger.info("Testing database integration...")

    try:
        # Test ParserType enum
        from api.db import ParserType

        if hasattr(ParserType, "MONKEYOCR"):
            logger.info(f"✅ ParserType.MONKEYOCR: {ParserType.MONKEYOCR.value}")
        else:
            logger.error("❌ ParserType.MONKEYOCR not found")
            return False

        # Test service import
        from api.db.services.monkeyocr_service import MonkeyOCRService

        logger.info("✅ MonkeyOCRService imported successfully")

        # Test service methods
        service = MonkeyOCRService()
        info = service.get_parser_info()
        logger.info(f"✅ Service info: {info.get('name', 'Unknown')} v{info.get('version', 'Unknown')}")

        return True

    except Exception as e:
        logger.error(f"❌ Database integration test failed: {e}")
        return False


def test_api_integration():
    """Test API integration components"""
    logger.info("Testing API integration...")

    try:
        # Test API app import
        from api.apps.monkeyocr_app import monkeyocr_bp

        logger.info("✅ API app imported successfully")

        # Test blueprint registration
        logger.info(f"✅ Blueprint URL prefix: {monkeyocr_bp.url_prefix}")

        # Test endpoint registration
        routes = [rule.rule for rule in monkeyocr_bp.url_map.iter_rules()]
        expected_routes = [
            "/api/v1/monkeyocr/info",
            "/api/v1/monkeyocr/register",
            "/api/v1/monkeyocr/unregister",
            "/api/v1/monkeyocr/parse",
            "/api/v1/monkeyocr/extract-text",
            "/api/v1/monkeyocr/supported-formats",
            "/api/v1/monkeyocr/validate-file",
            "/api/v1/monkeyocr/parsing-options",
            "/api/v1/monkeyocr/health",
        ]

        for route in expected_routes:
            if route in routes:
                logger.info(f"✅ Found route: {route}")
            else:
                logger.warning(f"⚠️  Missing route: {route}")

        return True

    except Exception as e:
        logger.error(f"❌ API integration test failed: {e}")
        return False


def test_parser_integration():
    """Test parser integration components"""
    logger.info("Testing parser integration...")

    try:
        # Test parser import
        from rag.app.monkey_ocr_parser import MonkeyOCRFactory

        logger.info("✅ Parser components imported successfully")

        # Test factory
        info = MonkeyOCRFactory.get_parser_info()
        logger.info(f"✅ Factory info: {info.get('name', 'Unknown')} v{info.get('version', 'Unknown')}")

        # Test supported formats
        formats = info.get("supported_formats", [])
        expected_formats = [".pdf", ".jpg", ".jpeg", ".png"]
        for fmt in expected_formats:
            if fmt in formats:
                logger.info(f"✅ Supported format: {fmt}")
            else:
                logger.warning(f"⚠️  Missing format: {fmt}")

        return True

    except Exception as e:
        logger.error(f"❌ Parser integration test failed: {e}")
        return False


def test_configuration():
    """Test configuration loading"""
    logger.info("Testing configuration...")

    try:
        # Test main config
        config_path = Path("conf/monkey_ocr_config.json")
        with open(config_path, "r") as f:
            config = json.load(f)

        # Check required sections
        required_sections = ["monkeyocr", "integration"]
        for section in required_sections:
            if section in config:
                logger.info(f"✅ Config section: {section}")
            else:
                logger.error(f"❌ Missing config section: {section}")
                return False

        # Check key settings
        monkeyocr_config = config["monkeyocr"]
        required_keys = ["enabled", "supported_formats", "capabilities", "parsing_options"]
        for key in required_keys:
            if key in monkeyocr_config:
                logger.info(f"✅ Config key: {key}")
            else:
                logger.error(f"❌ Missing config key: {key}")
                return False

        logger.info("✅ Configuration loaded successfully")
        return True

    except Exception as e:
        logger.error(f"❌ Configuration test failed: {e}")
        return False


def test_docker_setup():
    """Test Docker setup files"""
    logger.info("Testing Docker setup...")

    try:
        # Test Dockerfile
        dockerfile_path = Path("Dockerfile.monkeyocr")
        if dockerfile_path.exists():
            with open(dockerfile_path, "r") as f:
                content = f.read()
                if "FROM python:3.10-slim" in content:
                    logger.info("✅ Dockerfile base image correct")
                else:
                    logger.warning("⚠️  Dockerfile base image may need verification")

                if "monkeyocr" in content.lower():
                    logger.info("✅ Dockerfile includes MonkeyOCR")
                else:
                    logger.warning("⚠️  Dockerfile may not include MonkeyOCR")
        else:
            logger.error("❌ Dockerfile.monkeyocr not found")
            return False

        # Test docker-compose
        compose_path = Path("docker-compose-monkeyocr.yml")
        if compose_path.exists():
            with open(compose_path, "r") as f:
                content = f.read()
                if "ragflow:" in content and "monkeyocr" in content.lower():
                    logger.info("✅ Docker Compose includes MonkeyOCR service")
                else:
                    logger.warning("⚠️  Docker Compose may not be properly configured")
        else:
            logger.error("❌ docker-compose-monkeyocr.yml not found")
            return False

        # Test init script
        init_script_path = Path("docker/init_monkeyocr.sh")
        if init_script_path.exists():
            logger.info("✅ MonkeyOCR init script found")
        else:
            logger.error("❌ MonkeyOCR init script not found")
            return False

        return True

    except Exception as e:
        logger.error(f"❌ Docker setup test failed: {e}")
        return False


def test_monkeyocr_source():
    """Test MonkeyOCR source code"""
    logger.info("Testing MonkeyOCR source...")

    try:
        monkeyocr_path = Path("monkeyocr")
        if not monkeyocr_path.exists():
            logger.error("❌ MonkeyOCR directory not found")
            return False

        # Check key files
        required_files = ["cedd_parse.py", "model_configs.yaml", "requirements.txt", "tools/download_model.py"]

        for file_name in required_files:
            file_path = monkeyocr_path / file_name
            if file_path.exists():
                logger.info(f"✅ Found: {file_name}")
            else:
                logger.error(f"❌ Missing: {file_name}")
                return False

        # Check key directories
        required_dirs = ["magic_pdf", "tools"]
        for dir_name in required_dirs:
            dir_path = monkeyocr_path / dir_name
            if dir_path.exists():
                logger.info(f"✅ Found directory: {dir_name}")
            else:
                logger.warning(f"⚠️  Missing directory: {dir_name}")

        return True

    except Exception as e:
        logger.error(f"❌ MonkeyOCR source test failed: {e}")
        return False


def test_code_syntax():
    """Test that all Python files have valid syntax"""
    logger.info("Testing code syntax...")

    python_files = ["deepdoc/vision/monkey_ocr.py", "rag/app/monkey_ocr_parser.py", "api/db/services/monkeyocr_service.py", "api/apps/monkeyocr_app.py", "monkeyocr/cedd_parse.py"]

    for file_path in python_files:
        try:
            with open(file_path, "r") as f:
                compile(f.read(), file_path, "exec")
            logger.info(f"✅ Syntax valid: {file_path}")
        except SyntaxError as e:
            logger.error(f"❌ Syntax error in {file_path}: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Error reading {file_path}: {e}")
            return False

    logger.info("✅ All Python files have valid syntax")
    return True


def main():
    """Run all integration tests"""
    logger.info("🧪 Starting complete MonkeyOCR + RAGFlow integration tests...")

    tests = [
        ("File Structure", test_file_structure),
        ("Database Integration", test_database_integration),
        ("API Integration", test_api_integration),
        ("Parser Integration", test_parser_integration),
        ("Configuration", test_configuration),
        ("Docker Setup", test_docker_setup),
        ("MonkeyOCR Source", test_monkeyocr_source),
        ("Code Syntax", test_code_syntax),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        logger.info(f"\n🔍 Running test: {test_name}")
        try:
            if test_func():
                logger.info(f"✅ {test_name} passed")
                passed += 1
            else:
                logger.error(f"❌ {test_name} failed")
        except Exception as e:
            logger.error(f"❌ {test_name} failed with exception: {e}")

    logger.info(f"\n📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        logger.info("🎉 All tests passed! Complete integration is ready.")
        logger.info("🚀 Ready for Docker deployment!")
        return 0
    else:
        logger.error("❌ Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
