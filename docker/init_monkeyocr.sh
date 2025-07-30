#!/bin/bash

# MonkeyOCR Initialization Script for Docker
set -e

echo "🚀 Starting MonkeyOCR initialization..."

# Set paths
MONKEYOCR_DIR="/app/monkeyocr"
MODEL_DIR="$MONKEYOCR_DIR/model_weight"
CACHE_DIR="$MONKEYOCR_DIR/cache"
CONFIG_FILE="/app/conf/monkey_ocr_config.json"

# Create necessary directories
mkdir -p "$MODEL_DIR" "$CACHE_DIR" /app/logs /app/data /app/cache

echo "📁 Created directories:"
echo "  - Model directory: $MODEL_DIR"
echo "  - Cache directory: $CACHE_DIR"

# Check if models exist
if [ ! -d "$MODEL_DIR/Recognition" ] || [ ! -d "$MODEL_DIR/Structure" ] || [ ! -d "$MODEL_DIR/Relation" ]; then
    echo "📥 Downloading MonkeyOCR models..."
    cd "$MONKEYOCR_DIR/tools"
    
    # Download models with retry logic
    MAX_RETRIES=3
    RETRY_COUNT=0
    
    while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
        if python download_model.py --type huggingface --name MonkeyOCR; then
            echo "✅ Models downloaded successfully"
            break
        else
            RETRY_COUNT=$((RETRY_COUNT + 1))
            echo "⚠️  Download attempt $RETRY_COUNT failed, retrying..."
            sleep 10
        fi
    done
    
    if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
        echo "❌ Failed to download models after $MAX_RETRIES attempts"
        echo "💡 Models will be downloaded at runtime when needed"
    fi
else
    echo "✅ MonkeyOCR models already exist"
fi

# Verify configuration
if [ -f "$CONFIG_FILE" ]; then
    echo "✅ Configuration file found: $CONFIG_FILE"
else
    echo "⚠️  Configuration file not found, creating default..."
    cat > "$CONFIG_FILE" << 'EOF'
{
  "monkeyocr": {
    "enabled": true,
    "config_path": "/app/monkeyocr/model_configs.yaml",
    "model_weights_path": "/app/monkeyocr/model_weight",
    "supported_formats": [".pdf", ".jpg", ".jpeg", ".png"],
    "max_image_dimension": 1280,
    "default_dpi": 150,
    "batch_size": 2,
    "device": "cpu",
    "capabilities": {
      "document_layout_analysis": true,
      "text_extraction": true,
      "formula_recognition": true,
      "table_extraction": true,
      "image_ocr": true,
      "omr_processing": true
    },
    "parsing_options": {
      "split_pages": false,
      "pred_abandon": false,
      "extract_images": true,
      "generate_layout_pdf": true,
      "generate_spans_pdf": true
    },
    "performance": {
      "enable_caching": true,
      "cache_dir": "/app/monkeyocr/cache",
      "max_cache_size": "1GB",
      "enable_parallel_processing": true,
      "max_workers": 4
    },
    "logging": {
      "level": "INFO",
      "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
      "file": "/app/logs/monkeyocr.log"
    }
  },
  "integration": {
    "ragflow_parser_registry": true,
    "auto_register": true,
    "priority": 10,
    "fallback_parser": "default"
  }
}
EOF
fi

# Update MonkeyOCR config for Docker environment
MONKEYOCR_CONFIG="$MONKEYOCR_DIR/model_configs.yaml"
if [ -f "$MONKEYOCR_CONFIG" ]; then
    echo "🔧 Updating MonkeyOCR configuration for Docker..."
    
    # Update device to CPU for Docker (can be overridden with GPU setup)
    sed -i 's/device: cuda/device: cpu/' "$MONKEYOCR_CONFIG"
    
    # Update model paths
    sed -i 's|models_dir: model_weight|models_dir: /app/monkeyocr/model_weight|' "$MONKEYOCR_CONFIG"
    
    echo "✅ MonkeyOCR configuration updated"
else
    echo "⚠️  MonkeyOCR config file not found: $MONKEYOCR_CONFIG"
fi

# Set permissions
chmod -R 755 "$MODEL_DIR" "$CACHE_DIR"
chown -R 1000:1000 "$MODEL_DIR" "$CACHE_DIR" /app/logs /app/data /app/cache

# Test MonkeyOCR import
echo "🧪 Testing MonkeyOCR import..."
cd /app
python -c "
import sys
sys.path.insert(0, '/app/monkeyocr')
try:
    from rag.app.monkey_ocr_parser import MonkeyOCRFactory
    info = MonkeyOCRFactory.get_parser_info()
    print(f'✅ MonkeyOCR import successful: {info[\"name\"]} v{info[\"version\"]}')
except Exception as e:
    print(f'❌ MonkeyOCR import failed: {e}')
    sys.exit(1)
"

echo "🎉 MonkeyOCR initialization completed!"
echo ""
echo "📋 Summary:"
echo "  - Models directory: $MODEL_DIR"
echo "  - Cache directory: $CACHE_DIR"
echo "  - Configuration: $CONFIG_FILE"
echo "  - Logs: /app/logs/monkeyocr.log"
echo ""
echo "🚀 Ready to start RAGFlow with MonkeyOCR integration!" 