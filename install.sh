#!/bin/bash
set -e

echo "❄️ Installing Snowline Agent Tools..."
pip install -e .

# Get Python Scripts path
PYTHON_SCRIPTS_PATH=$(python -c "import os, sysconfig; print(sysconfig.get_path('scripts'))")

# Check if PATH contains the scripts directory
if [[ ":$PATH:" != *":$PYTHON_SCRIPTS_PATH:"* ]]; then
    echo "⚠️ Python Scripts folder is not in your PATH: $PYTHON_SCRIPTS_PATH"
    echo "🔧 You must manually add it to your PATH by adding this line to your ~/.bashrc or ~/.zshrc:"
    echo ""
    echo "export PATH=\"$PYTHON_SCRIPTS_PATH:\$PATH\""
    echo ""
    echo "✅ After adding it, restart your terminal or run 'source ~/.bashrc'."
else
    echo "✅ Python Scripts directory is already in PATH."
    echo "Installation complete! Run 'snowline -h' to test."
fi
