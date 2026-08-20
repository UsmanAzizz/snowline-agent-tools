"""
COMPANION v5.0 - CLI ENTRY POINT
=================================
This is a thin CLI wrapper. All logic is in companion/ module.

Usage:
    python .agents/skills/companion_cli.py "cari axios"
    python .agents/skills/companion_cli.py task start mytask "user intent"
"""
import sys
import os

# Ensure UTF-8
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Import from the module directory
import companion as _mod

if __name__ == '__main__':
    _args = sys.argv
    if len(_args) > 1 and _args[1] == 'task':
        _mod.task_lock_cli(_args[2:])
    else:
        _mod.main()
