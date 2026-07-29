"""
Snowline Tools - Instant load, no restart needed.
"""
import os
import shutil
import sys
import sysconfig
from pathlib import Path

__version__ = "1.0.3"

# Copy snowline.bat to current Scripts folder for instant PATH access
_scripts = sysconfig.get_path('scripts')
_src = Path(__file__).parent / 'snowline.bat'
_dest = Path(_scripts) / 'snowline.bat'

try:
    if _dest.exists():
        # Update if newer in source
        if _src.stat().st_mtime > _dest.stat().st_mtime:
            shutil.copy2(_src, _dest)
    else:
        shutil.copy2(_src, _dest)
except Exception:
    pass  # Silently fail if no permission

# Add to session PATH immediately (no restart)
if _scripts not in sys.path:
    sys.path.insert(0, _scripts)

# Auto-run main() if called directly
if __name__ == '__main__':
    from .cli import main
    main()
