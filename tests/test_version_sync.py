import os
import sys
import subprocess
import re
from pathlib import Path
from unittest.mock import patch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "src"))

import snowline
from snowline.cli import get_snowline_version


def _jalankan(args, env_extra=None):
    env = dict(os.environ)
    env["PYTHONPATH"] = str(REPO / "src") + os.pathsep + env.get("PYTHONPATH", "")
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    if env_extra:
        env.update(env_extra)
    return subprocess.run(
        [sys.executable, "-B", "-m", "snowline.cli"] + args,
        capture_output=True, text=True, env=env, timeout=30,
    )


def _jalankan_module_main(args):
    env = dict(os.environ)
    env["PYTHONPATH"] = str(REPO / "src") + os.pathsep + env.get("PYTHONPATH", "")
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(
        [sys.executable, "-B", "-m", "snowline"] + args,
        capture_output=True, text=True, env=env, timeout=30,
    )


def test_version_sync():
    root = REPO

    # 1. Extract from pyproject.toml
    pyproject_path = root / 'pyproject.toml'
    pyproject_content = pyproject_path.read_text(encoding='utf-8')
    pyproject_version_match = re.search(r'version\s*=\s*"([^"]+)"', pyproject_content)
    assert pyproject_version_match, "Could not find version in pyproject.toml"
    pyproject_version = pyproject_version_match.group(1)

    # 2. Extract from src/snowline/__init__.py
    init_path = root / 'src' / 'snowline' / '__init__.py'
    init_content = init_path.read_text(encoding='utf-8')
    init_version_match = re.search(r'__version__\s*=\s*"([^"]+)"', init_content)
    assert init_version_match, "Could not find __version__ in __init__.py"
    init_version = init_version_match.group(1)

    assert pyproject_version == init_version, (
        f"Version mismatch: pyproject.toml ({pyproject_version}) != __init__.py ({init_version})"
    )

    # 3. Verify snowline --version matches snowline.__version__ dynamically
    res_ver = _jalankan(["--version"])
    assert res_ver.returncode == 0, f"--version failed: {res_ver.stderr}"
    assert snowline.__version__ in res_ver.stdout, (
        f"snowline --version output '{res_ver.stdout.strip()}' does not match snowline.__version__ '{snowline.__version__}'"
    )

    # 4. Verify python -m snowline --version (via __main__.py) gives identical output
    res_mod = _jalankan_module_main(["--version"])
    assert res_mod.returncode == 0, f"python -m snowline --version failed: {res_mod.stderr}"
    assert res_mod.stdout.strip() == res_ver.stdout.strip(), (
        f"Mismatch: 'python -m snowline --version' ({res_mod.stdout.strip()}) != 'snowline --version' ({res_ver.stdout.strip()})"
    )

    # 5. Verify header in default snowline call matches snowline.__version__ dynamically (ignoring ANSI)
    res_help = _jalankan([])
    cleaned_help = re.sub(r'\x1b\[[0-9;]*m', '', res_help.stdout)
    assert f"Version: {snowline.__version__}" in cleaned_help, (
        f"Default header does not contain 'Version: {snowline.__version__}'!\nCleaned output:\n{cleaned_help}"
    )

    # 6. Syarat Lulus B2: Mengubah __version__ ke angka lain dan menunjukkan get_snowline_version ikut berubah
    with patch("snowline.__version__", "9.8.7"):
        v_mod = get_snowline_version()
        assert v_mod == "9.8.7", f"get_snowline_version failed to reflect modified __version__: got {v_mod}"

    # 7. Syarat Lulus B3: Saat __version__ tidak terbaca/kosong, get_snowline_version melempar RuntimeError
    with patch("snowline.__version__", None):
        try:
            get_snowline_version()
            assert False, "get_snowline_version should raise RuntimeError when __version__ is None"
        except RuntimeError as e:
            assert "Gagal membaca __version__" in str(e)

    # 8. Syarat Lulus B1: Memastikan tidak ada literal versi bertipe X.Y.Z di cli.py
    cli_code = (root / 'src' / 'snowline' / 'cli.py').read_text(encoding='utf-8')
    ver_literals = re.findall(r'"\d+\.\d+\.\d+"', cli_code)
    assert len(ver_literals) == 0, f"Found unexpected version literals in cli.py: {ver_literals}"

    print(f"[PASS] All versions synced at {init_version}, --version, dynamic changes, and error behavior verified.")


if __name__ == '__main__':
    test_version_sync()
