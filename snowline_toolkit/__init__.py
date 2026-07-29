"""
Snowline Toolkit
Auto-initializes PowerShell alias on import.
"""
import os
import sys

__version__ = "1.0.1"

def _auto_alias():
    """Auto-create alias if not exists."""
    profile = os.path.join(
        os.environ.get('USERPROFILE', ''),
        'Documents',
        'WindowsPowerShell',
        'Microsoft.PowerShell_profile.ps1'
    )
    if not profile:
        return

    python_exe = sys.executable
    alias_line = f'\nfunction snowline {{ {python_exe} -m snowline_toolkit.cli $args }}\n'

    # Check existing
    if os.path.exists(profile):
        try:
            with open(profile, 'r', encoding='utf-8') as f:
                content = f.read()
            if 'function snowline' in content:
                return  # Already exists
        except:
            pass

    # Create alias
    try:
        os.makedirs(os.path.dirname(profile), exist_ok=True)
        with open(profile, 'a', encoding='utf-8') as f:
            f.write('\n# Snowline Agent Tools\n' + alias_line)
    except:
        pass

# Auto-run on import
_auto_alias()
