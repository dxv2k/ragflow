#!/usr/bin/env python3
"""
MonkeyOCR API Endpoints for RAGFlow
Provides REST API endpoints for MonkeyOCR functionality
"""

import logging
import os
from pathlib import Path
import tempfile

from flask import request, jsonify

from api.db.services.monkeyocr_service import MonkeyOCRService
from api.utils import get_uuid

logger = logging.getLogger(__name__)


@manager.route("/info", methods=["GET"])  # noqa: F821
# @login_required
def get_parser_info():
    """Get MonkeyOCR parser information"""
    try:
        info = MonkeyOCRService.get_parser_info()
        return jsonify({"success": True, "data": info})
    except Exception as e:
        logger.error(f"Failed to get parser info: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@manager.route("/register", methods=["POST"])  # noqa: F821
# @login_required
def register_parser():
    """Register MonkeyOCR parser with tenant"""
    try:
        data = request.get_json()
        tenant_id = data.get("tenant_id")

        if not tenant_id:
            return jsonify({"success": False, "error": "tenant_id is required"}), 400

        success = MonkeyOCRService.register_parser(tenant_id)

        return jsonify({"success": success, "message": "Parser registered successfully" if success else "Failed to register parser"})

    except Exception as e:
        logger.error(f"Failed to register parser: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@manager.route("/unregister", methods=["POST"])  # noqa: F821
# @login_required
def unregister_parser():
    """Unregister MonkeyOCR parser from tenant"""
    try:
        data = request.get_json()
        tenant_id = data.get("tenant_id")

        if not tenant_id:
            return jsonify({"success": False, "error": "tenant_id is required"}), 400

        success = MonkeyOCRService.unregister_parser(tenant_id)

        return jsonify({"success": success, "message": "Parser unregistered successfully" if success else "Failed to unregister parser"})

    except Exception as e:
        logger.error(f"Failed to unregister parser: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@manager.route("/available/<tenant_id>", methods=["GET"])  # noqa: F821
# @login_required
def check_parser_availability(tenant_id):
    """Check if MonkeyOCR parser is available for tenant"""
    try:
        available = MonkeyOCRService.is_parser_available(tenant_id)

        return jsonify({"success": True, "data": {"tenant_id": tenant_id, "available": available}})

    except Exception as e:
        logger.error(f"Failed to check parser availability: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@manager.route("/parse", methods=["POST"])  # noqa: F821
# @login_required
def parse_document():
    """Parse document using MonkeyOCR"""
    try:
        # Check if file was uploaded
        if "file" not in request.files:
            return jsonify({"success": False, "error": "No file uploaded"}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"success": False, "error": "No file selected"}), 400

        # Get parsing options
        split_pages = request.form.get("split_pages", "false").lower() == "true"
        pred_abandon = request.form.get("pred_abandon", "false").lower() == "true"

        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp_file:
            file.save(tmp_file.name)
            file_path = tmp_file.name

        try:
            # Generate document ID
            doc_id = get_uuid()

            # Parse document
            result = MonkeyOCRService.parse_document(doc_id=doc_id, file_path=file_path, split_pages=split_pages, pred_abandon=pred_abandon)

            # Clean up temporary file
            os.unlink(file_path)

            return jsonify(result)

        except Exception as e:
            # Clean up temporary file on error
            if os.path.exists(file_path):
                os.unlink(file_path)
            raise e

    except Exception as e:
        logger.error(f"Failed to parse document: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@manager.route("/extract-text", methods=["POST"])  # noqa: F821
# @login_required
def extract_text_from_images():
    """Extract text from images using MonkeyOCR"""
    try:
        data = request.get_json()
        image_paths = data.get("image_paths", [])
        task = data.get("task", "text")

        if not image_paths:
            return jsonify({"success": False, "error": "image_paths is required"}), 400

        # Validate image paths
        for path in image_paths:
            if not os.path.exists(path):
                return jsonify({"success": False, "error": f"Image file not found: {path}"}), 400

        # Extract text
        results = MonkeyOCRService.extract_text_from_images(image_paths, task)

        return jsonify({"success": True, "data": results})

    except Exception as e:
        logger.error(f"Failed to extract text from images: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@manager.route("/supported-formats", methods=["GET"])  # noqa: F821
# @login_required
def get_supported_formats():
    """Get supported file formats"""
    try:
        formats = MonkeyOCRService.get_supported_formats()

        return jsonify({"success": True, "data": formats})

    except Exception as e:
        logger.error(f"Failed to get supported formats: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@manager.route("/validate-file", methods=["POST"])  # noqa: F821
# @login_required
def validate_file():
    """Validate if file can be processed by MonkeyOCR"""
    try:
        data = request.get_json()
        file_path = data.get("file_path")

        if not file_path:
            return jsonify({"success": False, "error": "file_path is required"}), 400

        if not os.path.exists(file_path):
            return jsonify({"success": False, "error": "File not found"}), 400

        valid = MonkeyOCRService.validate_file(file_path)

        return jsonify({"success": True, "data": {"file_path": file_path, "valid": valid}})

    except Exception as e:
        logger.error(f"Failed to validate file: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@manager.route("/parsing-options", methods=["GET"])  # noqa: F821
# @login_required
def get_parsing_options():
    """Get available parsing options"""
    try:
        options = MonkeyOCRService.get_parsing_options()

        return jsonify({"success": True, "data": options})

    except Exception as e:
        logger.error(f"Failed to get parsing options: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@manager.route("/health", methods=["GET"])  # noqa: F821
def health_check():
    """Health check endpoint"""
    try:
        # Basic health check
        info = MonkeyOCRService.get_parser_info()

        return jsonify({"success": True, "data": {"status": "healthy", "parser_info": info}})

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# MonkeyOCR API endpoints are automatically registered by RAGFlow app discovery
