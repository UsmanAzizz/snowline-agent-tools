"""
Snowline Tools - Instant load, no restart needed.
"""
import os
import shutil
import sys
import sysconfig
import subprocess
from pathlib import Path

__version__ = "1.0.5"

_scripts = sysconfig.get_path('scripts')
_python_exe = sys.executable

# 1. Copy snowline.bat wrapper to Scripts folder
_src = Path(__file__).parent / 'snowline.bat'
_dest = Path(_scripts) / 'snowline.bat'

try:
    if _src.exists():
        if _dest.exists():
            if _src.stat().st_mtime > _dest.stat().st_mtime:
                shutil.copy2(_src, _dest)
        else:
            shutil.copy2(_src, _dest)
except Exception:
    pass

# 2. Add Scripts to current process PATH (works immediately)
_current_path = os.environ.get('PATH', '')
if _scripts not in _current_path:
    os.environ['PATH'] = _scripts + os.pathsep + _current_path

# 3. Update Windows registry PATH for future terminals (if has permission)
try:
    import winreg
    _user_path_key = r"Environment"
    _key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, _user_path_key, 0, winreg.KEY_READ)
    _user_path, _ = winreg.QueryValueEx(_key, "Path")
    winreg.CloseKey(_key)

    if _scripts not in _user_path:
        _key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, _user_path_key, 0, winreg.KEY_WRITE)
        winreg.SetValueEx(_key, "Path", 0, winreg.REG_EXPAND_SZ, _user_path + ";" + _scripts)
        winreg.CloseKey(_key)
        # Broadcast WM_SETTINGCHANGE so other processes update
        try:
            import ctypes
            HWND_BROADCAST = 0xFFFF
            WM_SETTINGCHANGE = 0x1A
            ctypes.windll.user32.SendMessageW(HWND_BROADCAST, WM_SETTINGCHANGE, 0, "Environment")
        except Exception:
            pass
except Exception:
    pass  # Silently fail if no permission to modify registry

# Auto-run main() if called directly
if __name__ == '__main__':
    from .cli import main
    main()
