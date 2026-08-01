"""
COMPANION v5.0 - CLI ENTRY POINT (ROOT)
========================================
This is the CLI entry point at project root.
It delegates to .agents/skills/companion_cli.py

Usage:
    python companion.py "instruksi"
    python companion.py task start mytask "user intent"
"""
import subprocess
import sys
import os

# Path to actual CLI
cli_path = os.path.join(os.getcwd(), '.agents', 'skills', 'companion_cli.py')

# Ensure UTF-8
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Delegate to the actual CLI
result = subprocess.run(
    [sys.executable, '-X', 'utf8', cli_path] + sys.argv[1:],
    cwd=os.getcwd()
)
sys.exit(result.returncode)
