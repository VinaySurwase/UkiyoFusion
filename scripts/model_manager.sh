#!/bin/bash

echo "🤖 UkiyoeFusion Model Manager"
echo "============================"

MODELS_DIR="models"

# Create models directory if it doesn't exist
mkdir -p "$MODELS_DIR"

show_help() {
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  list          List all available models"
    echo "  download      Download a model from Hugging Face"
    echo "  remove        Remove a local model"
    echo "  info          Show model information"
    echo "  help          Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 list"
    echo "  $0 download stabilityai/stable-diffusion-2-1"
    echo "  $0 remove my-custom-model"
}

list_models() {
    echo "📋 Available Models:"
    echo "==================="
    
    echo ""
    echo "🌐 Online Models (automatically available):"
    echo "  - runwayml/stable-diffusion-v1-5"
    echo "  - stabilityai/stable-diffusion-2-1"
    echo "  - Any other Hugging Face diffusers model"
    
    echo ""
    echo "💾 Local Models:"
    if [ -d "$MODELS_DIR" ] && [ "$(ls -A $MODELS_DIR 2>/dev/null)" ]; then
        for model in "$MODELS_DIR"/*; do
            if [ -d "$model" ]; then
                model_name=$(basename "$model")
                if [ -f "$model/model_index.json" ]; then
                    echo "  ✅ $model_name (valid)"
                else
                    echo "  ❌ $model_name (invalid - missing model_index.json)"
                fi
            fi
        done
    else
        echo "  (No local models found)"
    fi
    
    echo ""
    echo "💡 To add a custom model:"
    echo "  1. Place your model files in the models/ directory"
    echo "  2. Ensure it has a model_index.json file"
    echo "  3. Restart the application"
}

download_model() {
    if [ -z "$1" ]; then
        echo "❌ Please specify a model to download"
        echo "Example: $0 download stabilityai/stable-diffusion-2-1"
        return 1
    fi
    
    model_id="$1"
    model_name=$(echo "$model_id" | sed 's/\//_/g')
    model_path="$MODELS_DIR/$model_name"
    
    echo "📥 Downloading model: $model_id"
    echo "📁 Destination: $model_path"
    
    # Activate virtual environment if it exists
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi
    
    # Download using huggingface_hub
    python3 -c "
from huggingface_hub import snapshot_download
import os

try:
    snapshot_download(
        repo_id='$model_id',
        local_dir='$model_path',
        local_dir_use_symlinks=False
    )
    print('✅ Model downloaded successfully!')
except Exception as e:
    print(f'❌ Download failed: {e}')
    exit(1)
"
    
    if [ $? -eq 0 ]; then
        echo "✅ Model '$model_id' downloaded to '$model_path'"
        echo "🔄 Restart the application to use the new model"
    else
        echo "❌ Failed to download model"
    fi
}

remove_model() {
    if [ -z "$1" ]; then
        echo "❌ Please specify a model to remove"
        echo "Example: $0 remove my-custom-model"
        return 1
    fi
    
    model_name="$1"
    model_path="$MODELS_DIR/$model_name"
    
    if [ ! -d "$model_path" ]; then
        echo "❌ Model '$model_name' not found in local models"
        return 1
    fi
    
    echo "🗑️  Removing model: $model_name"
    echo "📁 Path: $model_path"
    
    read -p "Are you sure you want to remove this model? (y/N): " confirm
    
    if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
        rm -rf "$model_path"
        echo "✅ Model '$model_name' removed successfully"
    else
        echo "❌ Operation cancelled"
    fi
}

show_model_info() {
    if [ -z "$1" ]; then
        echo "❌ Please specify a model name"
        echo "Example: $0 info my-custom-model"
        return 1
    fi
    
    model_name="$1"
    model_path="$MODELS_DIR/$model_name"
    
    if [ ! -d "$model_path" ]; then
        echo "❌ Model '$model_name' not found in local models"
        return 1
    fi
    
    echo "📊 Model Information: $model_name"
    echo "================================="
    echo "📁 Path: $model_path"
    
    if [ -f "$model_path/model_index.json" ]; then
        echo "✅ Status: Valid diffusers model"
        echo "📄 Configuration:"
        cat "$model_path/model_index.json" | python3 -m json.tool 2>/dev/null || echo "Invalid JSON"
    else
        echo "❌ Status: Invalid (missing model_index.json)"
    fi
    
    # Show disk usage
    if command -v du >/dev/null 2>&1; then
        size=$(du -sh "$model_path" 2>/dev/null | cut -f1)
        echo "💾 Size: $size"
    fi
}

# Main script logic
case "$1" in
    "list")
        list_models
        ;;
    "download")
        download_model "$2"
        ;;
    "remove")
        remove_model "$2"
        ;;
    "info")
        show_model_info "$2"
        ;;
    "help"|"")
        show_help
        ;;
    *)
        echo "❌ Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
