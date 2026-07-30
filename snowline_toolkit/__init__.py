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

# 3. Update profiles for instant access
def _update_profiles():
    """Update PowerShell and Bash profiles to add Scripts to PATH"""

    # PowerShell profiles
    ps_profiles = [
        Path.home() / 'Documents' / 'PowerShell' / 'Microsoft.PowerShell_profile.ps1',
        Path.home() / 'Documents' / 'WindowsPowerShell' / 'Microsoft.PowerShell_profile.ps1',
    ]

    # Bash profile (for Git Bash, WSL, etc.)
    bash_profiles = [
        Path.home() / '.bashrc',
        Path.home() / '.bash_profile',
        Path.home() / '.zshrc',
    ]

    scripts_escaped = _scripts.replace('\\', '\\\\')
    ps_add_line = f'$env:PATH = "{scripts_escaped};$env:PATH"'
    bash_add_line = f'export PATH="{_scripts}:$PATH"'
    ps_marker = "# SNOWLINE_PATH_AUTO"
    bash_marker = "# SNOWLINE_PATH_AUTO"

    # Update PowerShell profiles
    for profile in ps_profiles:
        try:
            profile.parent.mkdir(parents=True, exist_ok=True)
            content = ""
            if profile.exists():
                content = profile.read_text(encoding='utf-8')

            if scripts_escaped.replace('\\\\', '\\') in content:
                continue

            new_content = f"# SNOWLINE_PATH_AUTO\n{ps_add_line}\n\n"
            if ps_marker in content:
                lines = content.split('\n')
                result = []
                skip_block = False
                for line in lines:
                    if line.strip() == ps_marker:
                        skip_block = True
                        result.append(new_content)
                    elif skip_block and (line.startswith('# ') or line.strip() == ''):
                        skip_block = False
                    if not skip_block:
                        result.append(line)
                content = '\n'.join(result)
            else:
                content = new_content + content

            profile.write_text(content, encoding='utf-8')
        except Exception:
            pass

    # Update Bash profiles
    for profile in bash_profiles:
        try:
            profile.parent.mkdir(parents=True, exist_ok=True)
            content = ""
            if profile.exists():
                content = profile.read_text(encoding='utf-8')

            if _scripts in content:
                continue

            new_content = f"# SNOWLINE_PATH_AUTO\nexport PATH=\"{_scripts}:$PATH\"\n\n"

            if bash_marker in content:
                lines = content.split('\n')
                result = []
                skip_block = False
                for line in lines:
                    if line.strip() == bash_marker:
                        skip_block = True
                        result.append(new_content)
                    elif skip_block and line.startswith('export PATH='):
                        continue
                    elif skip_block and (line.startswith('# ') or line.strip() == ''):
                        skip_block = False
                    if not skip_block:
                        result.append(line)
                content = '\n'.join(result)
            else:
                content = new_content + content

            profile.write_text(content, encoding='utf-8')
        except Exception:
            pass

# 4. Update Windows registry PATH for future terminals (with consent)
try:
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment", 0, winreg.KEY_READ)
    user_path, _ = winreg.QueryValueEx(key, "Path")
    winreg.CloseKey(key)

    if _scripts not in user_path:
        print("")
        print("[?] Add Python Scripts folder to Windows PATH? (Y/n)")
        response = input().strip().lower()
        
        if response == "" or response == "y":
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment", 0, winreg.KEY_WRITE)
            winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, user_path + ";" + _scripts)
            winreg.CloseKey(key)

            # Update all profiles
            _update_profiles()

            # Broadcast change to all windows
            try:
                import ctypes
                HWND_BROADCAST = 0xFFFF
                WM_SETTINGCHANGE = 0x1A
                ctypes.windll.user32.SendMessageW(HWND_BROADCAST, WM_SETTINGCHANGE, 0, "Environment")
            except Exception:
                pass
            
            print("[+] PATH updated!")
        else:
            print("[*] PATH update skipped. Run 'snowline -h' after manually adding to PATH.")
except Exception:
    pass

# 5. Read PATH from registry for current session
try:
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

# Check if already installed during pip install
def _check_reinstall():
    """Suggest update after pip install if already installed."""
    import os
    # Only run during pip install context
    if not any('pip' in arg for arg in sys.argv):
        return
    
    skills_dir = Path.cwd() / ".agents" / "skills"
    if skills_dir.exists() and (skills_dir / "deep_analyzer").exists():
        skill_count = len([f for f in skills_dir.rglob("*.py") if f.suffix == ".py"])
        print("")
        print("[INFO] Snowline already installed (" + str(skill_count) + " tools)")
        print("[INFO] Run 'snowline update --apply' to update tools")
        print("")

_check_reinstall()
