import os
import sys
import tempfile
import json
import shutil
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

def test_b3_role_json_installed_and_ignored():
    with tempfile.TemporaryDirectory() as tmpdir:
        env = dict(os.environ)
        env['PYTHONPATH'] = str(REPO / 'src') + os.pathsep + env.get('PYTHONPATH', '')
        
        # 1. Initialize git
        subprocess.run(["git", "init"], cwd=tmpdir, capture_output=True, check=True)

        # 2. Run snowline init --apply
        res_init = subprocess.run([
            sys.executable, "-m", "snowline.cli", "init", "--apply"
        ], cwd=tmpdir, capture_output=True, text=True, encoding="utf-8", env=env)
        assert res_init.returncode == 0

        # Arah a: init_chamber --apply -> role.json ada, isinya {"peran": null}
        res_ic = subprocess.run([
            sys.executable, "-m", "snowline.cli", "init_chamber", "--apply"
        ], cwd=tmpdir, capture_output=True, text=True, encoding="utf-8", env=env)
        assert res_ic.returncode == 0
        role_file = os.path.join(tmpdir, ".agents", "chamber", "role.json")
        assert os.path.exists(role_file), "role.json tidak terpasang di .agents/chamber/"
        with open(role_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert data.get("peran") is None, f"Isi role.json salah: {data}"
        print("PASS: Arah A (init_chamber --apply -> role.json ada, isinya {'peran': null})")

        # Arah b: Ubah peran jadi TL, jalankan init_chamber lagi tanpa --force -> TIDAK ditimpa
        with open(role_file, "w", encoding="utf-8") as f:
            json.dump({"peran": "TL"}, f)

        res_ic2 = subprocess.run([
            sys.executable, "-m", "snowline.cli", "init_chamber", "--apply"
        ], cwd=tmpdir, capture_output=True, text=True, encoding="utf-8", env=env)
        with open(role_file, "r", encoding="utf-8") as f:
            data2 = json.load(f)
        assert data2.get("peran") == "TL", f"Arah B gagal: role.json ditimpa menjadi {data2}"
        print("PASS: Arah B (init_chamber tanpa --force tidak menimpa role.json)")

        # Arah c: git status -> role.json tidak muncul
        res_git = subprocess.run(["git", "status", "--porcelain"], cwd=tmpdir, capture_output=True, text=True, encoding="utf-8")
        assert "role.json" not in res_git.stdout, f"Arah C gagal: role.json muncul di git status:\n{res_git.stdout}"
        print("PASS: Arah C (git status tidak memunculkan role.json)")

if __name__ == "__main__":
    test_b3_role_json_installed_and_ignored()
    print("\nALL ENTRI B3 DIRECTIONS PASSED!")