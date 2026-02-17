#!/bin/bash
# Auggie Voice Assistant Launcher

SCRIPT_DIR="$(dirname "$0")"
WORKSPACE="${1:-$(pwd)}"

echo "=================================="
echo "🎙️  AUGGIE VOICE ASSISTANT"
echo "=================================="
echo ""
echo "Installing dependencies..."
pip3 install openai-whisper sounddevice numpy -q 2>/dev/null

echo ""
echo "Starting voice assistant..."
echo "Workspace: $WORKSPACE"
echo ""
python3 "$SCRIPT_DIR/voice_chat.py" "$WORKSPACE"

