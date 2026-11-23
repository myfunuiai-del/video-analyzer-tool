#!/bin/bash
# install.sh - Setup dependencies and models for Video Analyzer Tool on Termux / Linux

set -e

echo "=== [1/4] Installing Required Packages ==="
if command -v pkg &> /dev/null; then
    pkg update -y || true
    pkg install -y python ffmpeg git jq curl
elif command -v apt-get &> /dev/null; then
    sudo apt-get update -y || true
    sudo apt-get install -y python3 python3-pip ffmpeg git jq curl
fi

echo "=== [2/4] Installing Python Packages (yt-dlp) ==="
python3 -m pip install -U yt-dlp || pip install -U yt-dlp || true

echo "=== [3/4] Preparing whisper.cpp & models directory ==="
MODELS_DIR="$HOME/tools/whisper.cpp/models"
mkdir -p "$MODELS_DIR"

# 1. Download Base model (~148MB) - Used for language detection and lightweight usage
BASE_MODEL="$MODELS_DIR/ggml-base.bin"
if [ ! -f "$BASE_MODEL" ]; then
    echo "[*] Downloading Whisper Base Model (ggml-base.bin)..."
    curl -L -o "$BASE_MODEL" "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.bin" || true
else
    echo "[✓] Whisper Base model already exists."
fi

# 2. Download Large v3 Turbo model (~574MB) - Recommended for English & Banglish
TURBO_MODEL="$MODELS_DIR/ggml-large-v3-turbo-q5_0.bin"
if [ ! -f "$TURBO_MODEL" ]; then
    echo "[*] Downloading Whisper Turbo Model (ggml-large-v3-turbo-q5_0.bin)..."
    curl -L -o "$TURBO_MODEL" "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v3-turbo-q5_0.bin" || true
else
    echo "[✓] Whisper Turbo model already exists."
fi

# 3. Download Bengali fine-tuned medium model (~539MB) - Recommended for pure Bengali
BN_MODEL="$MODELS_DIR/ggml-bn-medium-q5_0.bin"
if [ ! -f "$BN_MODEL" ]; then
    echo "[*] Checking Bengali Fine-Tuned Model (ggml-bn-medium-q5_0.bin)..."
    # If file exists in local storage tools, copy it, else notify download
    if [ -f "/data/user/0/ai.antigem/files/home/tools/whisper.cpp/models/ggml-bn-medium-q5_0.bin" ]; then
        cp "/data/user/0/ai.antigem/files/home/tools/whisper.cpp/models/ggml-bn-medium-q5_0.bin" "$BN_MODEL"
        echo "[✓] Copied local Bengali model."
    fi
fi

echo "=== [4/4] Linking video-analyzer to PATH ==="
chmod +x "$(dirname "$0")/video_analyzer.py"

if [ -d "/data/user/0/ai.antigem/files/usr/bin" ]; then
    TARGET_BIN="/data/user/0/ai.antigem/files/usr/bin/video-analyzer"
elif [ -d "$PREFIX/bin" ]; then
    TARGET_BIN="$PREFIX/bin/video-analyzer"
elif [ -d "$HOME/.local/bin" ]; then
    mkdir -p "$HOME/.local/bin"
    TARGET_BIN="$HOME/.local/bin/video-analyzer"
else
    TARGET_BIN="/usr/local/bin/video-analyzer"
fi

cp "$(dirname "$0")/video_analyzer.py" "$TARGET_BIN"
chmod +x "$TARGET_BIN"

echo "=========================================="
echo " [✓] Installation complete!"
echo " You can now run: video-analyzer <URL_OR_FILE>"
echo "=========================================="
