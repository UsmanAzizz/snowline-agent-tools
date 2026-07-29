"""
Snowline Tools - Instant load, no restart needed.
"""
import os
import shutil
import sys
import sysconfig
from pathlib import Path
import winreg
import subprocess

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

# 3. Update PowerShell profile for instant and future access
def _update_ps_profile():
    """Update PowerShell profile to add Scripts to PATH"""
    profiles = [
        Path.home() / 'Documents' / 'PowerShell' / 'Microsoft.PowerShell_profile.ps1',
        Path.home() / 'Documents' / 'WindowsPowerShell' / 'Microsoft.PowerShell_profile.ps1',
    ]

    # Use raw string to avoid escape issues
    scripts_escaped = _scripts.replace('\\', '\\\\')
    add_line = f'$env:PATH = "{scripts_escaped};$env:PATH"'
    marker = "# SNOWLINE_PATH_AUTO"

    for profile in profiles:
        try:
            profile.parent.mkdir(parents=True, exist_ok=True)
            content = ""
            if profile.exists():
                content = profile.read_text(encoding='utf-8')

            # Check if already configured
            if scripts_escaped.replace('\\\\', '\\') in content:
                continue

            # Add snowline PATH block
            new_content = f"# SNOWLINE_PATH_AUTO\n{add_line}\n\n"
            if marker in content:
                # Update existing block
                lines = content.split('\n')
                result = []
                skip_until_next_hash = False
                for line in lines:
                    if line.strip() == marker:
                        skip_until_next_hash = True
                        result.append(new_content)
                    elif skip_until_next_hash and line.startswith('# '):
                        skip_until_next_hash = False
                    if not skip_until_next_hash or not line.startswith('#'):
                        if line.strip() != marker:
                            result.append(line)
                content = '\n'.join(result)
            else:
                content = new_content + content

            profile.write_text(content, encoding='utf-8')
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

        # Broadcast change to all windows
        try:
            import ctypes
            HWND_BROADCAST = 0xFFFF
            WM_SETTINGCHANGE = 0x1A
            ctypes.windll.user32.SendMessageW(HWND_BROADCAST, WM_SETTINGCHANGE, 0, "Environment")
        except Exception:
            pass
except Exception:
    pass

# 5. For instant access in current PowerShell session: run reload command
# This is picked up by cli.py to inform user
if os.environ.get('PSModulePath'):
    # We're likely in PowerShell, try to update current session
    try:
        # Read registry PATH and set it
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment", 0, winreg.KEY_READ)
        user_path, _ = winreg.QueryValueEx(key, "Path")
        winreg.CloseKey(key)
        os.environ['PATH'] = user_path + os.pathsep + os.environ.get('PATH', '')
    except Exception:
        pass

# Auto-run main() if called directly
if __name__ == '__main__':
    from .cli import main
    main()
