import os
import sys
import sysconfig
import subprocess
import tempfile
from pathlib import Path
from unittest.mock import patch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "src"))

def test_sprint51_a_path_order_and_presence():
    """Syarat Lulus A1 & A2: Urutan PATH tidak direbut, tapi Scripts tetap ada di PATH."""
    marker_path = os.path.abspath(os.path.join("temp", "my_custom_first_bin"))
    
    # Jalankan subprocess python dengan PATH bersih yang TIDAK memuat direktori Scripts
    script = f'''import os, sys, sysconfig
sys.path.insert(0, r"{REPO / 'src'}")
# Set PATH hanya memuat marker_path dan system directory (tanpa Scripts)
os.environ['PATH'] = r"{marker_path}" + os.pathsep + r"C:\\Windows\\System32"

# Impor snowline
import snowline

# 1. Pastikan jalur penanda tetap paling depan
paths = os.environ.get('PATH', '').split(os.pathsep)
assert paths[0] == r"{marker_path}", f"PATH direbut! Urutan pertama sekarang: {{paths[0]}}"

# 2. Pastikan jalur Scripts tetap ada di PATH
scripts_dir = sysconfig.get_path('scripts')
norm = lambda p: os.path.normcase(os.path.abspath(p))
norm_paths = [norm(p) for p in paths if p]
assert norm(scripts_dir) in norm_paths, f"Direktori Scripts ({{scripts_dir}}) tidak ada di PATH sesudah impor!"

print("PASS: A1 & A2 PATH order preserved and Scripts present")
'''
    res = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True)
    assert res.returncode == 0, f"Uji PATH gagal:\nSTDOUT:\n{res.stdout}\nSTDERR:\n{res.stderr}"
    print(res.stdout.strip())

def test_sprint51_a_no_pip_subprocesses():
    """Syarat Lulus A3 & A4: Tidak ada subprocess ke pip di update() dan status(), versi sinkron."""
    from snowline.cli import update, status, get_installed_package_info
    import snowline
    
    # 3. Instalasi yang dilaporkan adalah yang sedang berjalan
    pkg_info = get_installed_package_info()
    if pkg_info.get("version"):
        assert pkg_info["version"] == snowline.__version__, (
            f"Versi mismatch: pkg_info ({{pkg_info['version']}}) != snowline.__version__ ({{snowline.__version__}})"
        )
    
    # 4. Sadap subprocess.run selama update() dan status()
    called_commands = []
    original_run = subprocess.run
    
    def tracked_run(*args, **kwargs):
        cmd = args[0] if args else kwargs.get("args", [])
        called_commands.append(cmd)
        if isinstance(cmd, list) and len(cmd) > 0 and cmd[0] == "git":
            return original_run(*args, **kwargs)
        from unittest.mock import MagicMock
        m = MagicMock()
        m.returncode = 0
        m.stdout = ""
        return m

    from unittest.mock import patch
    with patch("subprocess.run", side_effect=tracked_run):
        with tempfile.TemporaryDirectory() as tmpdir:
            old_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                update(apply=False)
                status()
            finally:
                os.chdir(old_cwd)

    for cmd in called_commands:
        cmd_str = " ".join(cmd) if isinstance(cmd, list) else str(cmd)
        assert "pip" not in cmd_str.lower(), f"Subprocess pip terdeteksi: {cmd_str}"

    print(f"PASS: A3 & A4 No pip subprocesses called ({len(called_commands)} total subprocess calls recorded)")

if __name__ == "__main__":
    test_sprint51_a_path_order_and_presence()
    test_sprint51_a_no_pip_subprocesses()
    print("\nALL SPRINT 51 BAGIAN A TESTS PASSED!")
