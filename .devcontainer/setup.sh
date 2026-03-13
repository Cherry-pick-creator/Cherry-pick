#!/bin/bash
set -e

echo "🔧 Installing system dependencies..."
sudo apt-get update && sudo apt-get install -y ffmpeg && sudo apt-get clean

echo "🐍 Installing Python dependencies..."
if [ -f backend/requirements.txt ]; then
    pip install -r backend/requirements.txt
fi

echo "📦 Installing frontend dependencies..."
if [ -f frontend/package.json ]; then
    cd frontend && npm install && cd ..
fi

echo "✅ Setup complete. Run 'claude' to start Claude Code."
