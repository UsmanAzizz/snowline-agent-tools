import os
from pathlib import Path
import re

def test_version_sync():
    root = Path(__file__).parent.parent
    
    # Extract from pyproject.toml
    pyproject_path = root / 'pyproject.toml'
    pyproject_content = pyproject_path.read_text(encoding='utf-8')
    pyproject_version_match = re.search(r'version\s*=\s*"([^"]+)"', pyproject_content)
    assert pyproject_version_match, "Could not find version in pyproject.toml"
    pyproject_version = pyproject_version_match.group(1)
    
    # Extract from src/snowline/__init__.py
    init_path = root / 'src' / 'snowline' / '__init__.py'
    init_content = init_path.read_text(encoding='utf-8')
    init_version_match = re.search(r'__version__\s*=\s*"([^"]+)"', init_content)
    assert init_version_match, "Could not find __version__ in __init__.py"
    init_version = init_version_match.group(1)
    
    # Extract from src/snowline/cli.py
    cli_path = root / 'src' / 'snowline' / 'cli.py'
    cli_content = cli_path.read_text(encoding='utf-8')
    cli_version_match = re.search(r'Version:\{Colors\.RESET\}\s*([^"]+)"', cli_content)
    assert cli_version_match, "Could not find Version: in cli.py"
    cli_version = cli_version_match.group(1)
    
    assert pyproject_version == init_version, f"Version mismatch: pyproject.toml ({pyproject_version}) != __init__.py ({init_version})"
    assert pyproject_version == cli_version, f"Version mismatch: pyproject.toml ({pyproject_version}) != cli.py ({cli_version})"
    
    print(f"[PASS] All versions synced at {pyproject_version}")

if __name__ == '__main__':
    test_version_sync()
