#!/bin/bash
"""
Unified RAGFlow + MonkeyOCR Build Script
---------------------------------------
This script builds a unified Docker image with both RAGFlow and MonkeyOCR integrated.
All dependencies have been merged into pyproject.toml and monkeyocr is now part of the main repo.

Based on MonkeyOCR official Docker approach for maximum compatibility.
"""

echo "🚀 Building unified RAGFlow + MonkeyOCR Docker image..."

# Build the main Docker image with all dependencies
docker build -t ragflow-monkeyocr:latest .

if [ $? -eq 0 ]; then
    echo "✅ Docker image built successfully!"
    echo ""
    echo "📋 Summary of integration:"
    echo "   • ✅ Extracted MonkeyOCR dependencies from docker/requirements.txt"
    echo "   • ✅ Merged dependencies into RAGFlow's pyproject.toml"  
    echo "   • ✅ Fixed version conflicts (transformers==4.50.0, torch==2.5.1)"
    echo "   • ✅ Removed git submodule tracking from monkeyocr/"
    echo "   • ✅ Added monkeyocr/ files to main repository"
    echo "   • ✅ Updated main Dockerfile following MonkeyOCR Docker pattern"
    echo "   • ✅ Included LMDeploy==0.8.0 from MonkeyOCR requirements"
    echo "   • ✅ Added conditional LMDeploy patch for GPU compatibility"
    echo "   • ✅ Configured model weight directories and download scripts"
    echo ""
    echo "🔧 To run the container:"
    echo "   docker run -it --gpus all -p 9380:9380 -v \$(pwd)/model_cache:/ragflow/monkeyocr/model_weight ragflow-monkeyocr:latest"
    echo ""
    echo "📁 MonkeyOCR Backend Options:"
    echo "   • LMDeploy (default, already included)"
    echo "   • vLLM: pip install .[monkeyocr-vllm]"
    echo "   • Transformers: pip install .[monkeyocr-transformers]"
    echo ""
    echo "📥 Download MonkeyOCR models inside container:"
    echo "   docker exec -it <container_name> python monkeyocr/tools/download_model.py -t modelscope"
    echo "   or: python monkeyocr/tools/download_model.py  # for HuggingFace"
    echo ""
    echo "📂 Repository structure:"
    echo "   • monkeyocr/ folder is now part of this repository"
    echo "   • All files included when you git pull/clone"
    echo "   • No more submodule issues!"
else
    echo "❌ Docker build failed. Please check the output above for errors."
    exit 1
fi