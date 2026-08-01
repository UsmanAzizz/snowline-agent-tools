"""
__main__.py - Allow: python -m companion "instruksi"
"""
from .cli import main, task_lock_cli
import sys

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'task':
        task_lock_cli(sys.argv[2:])
    else:
        main()
