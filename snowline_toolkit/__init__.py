"""
Snowline Tools - Instant load, no restart needed.
"""
import os
import shutil
import sys
import sysconfig
from pathlib import Path
import winreg

__version__ = "1.0.5"

_scripts = sysconfig.get_path('scripts')

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

# 2. Add Scripts to current process PATH
if _scripts not in os.environ.get('PATH', ''):
    os.environ['PATH'] = _scripts + os.pathsep + os.environ.get('PATH', '')

# 3. Update PowerShell profile for instant access in current terminal
def _update_ps_profile():
    profiles = [
        Path.home() / "Documents" / "PowerShell" / "Microsoft.PowerShell_profile.ps1",
        Path.home() / "Documents" / "WindowsPowerShell" / "Microsoft.PowerShell_profile.ps1",
    ]

    add_line = f'$env:PATH = "{_scripts};$env:PATH"'

    for profile in profiles:
        try:
            profile.parent.mkdir(parents=True, exist_ok=True)
            if profile.exists():
                content = profile.read_text(encoding='utf-8')
                if _scripts not in content:
                    content += f"\n# Snowline PATH\n{add_line}\n"
                    profile.write_text(content, encoding='utf-8')
            else:
                profile.write_text(f"# Snowline PATH\n{add_line}\n", encoding='utf-8')
        except Exception:
            pass

# 4. Update Windows registry PATH for future terminals
try:
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment", 0, winreg.KEY_READ)
    user_path, _ = winreg.QueryValueEx(key, "Path")
    winreg.CloseKey(key)

    if _scripts not in user_path:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment", 0, winreg.KEY_WRITE)
        winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, user_path + ";" + _scripts)
        winreg.CloseKey(key)

        # Update PowerShell profile
        _update_ps_profile()

        # Broadcast change
        try:
            import ctypes
            HWND_BROADCAST = 0xFFFF
            WM_SETTINGCHANGE = 0x1A
            ctypes.windll.user32.SendMessageW(HWND_BROADCAST, WM_SETTINGCHANGE, 0, "Environment")
        except Exception:
            pass
except Exception:
    pass

# Auto-run main() if called directly
if __name__ == '__main__':
    from .cli import main
    main()
