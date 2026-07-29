"""
Snowline Toolkit
Auto-creates snowline.bat in Scripts folder on import.
"""
import os
import sys
import shutil
import sysconfig

__version__ = "1.0.2"

def _copy_bat():
    """Copy snowline.bat to Scripts folder."""
    scripts = sysconfig.get_path('scripts')
    src = os.path.join(os.path.dirname(__file__), '..', 'scripts', 'snowline.bat')
    dest = os.path.join(scripts, 'snowline.bat')

    try:
        shutil.copy2(src, dest)
        print("[OK] snowline.bat ->", scripts)
    except Exception as e:
        print("[WARN] Could not copy snowline.bat:", e)

# Run on import
_copy_bat()
