import os
import sys
import tempfile
import shutil
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

def test_b5_install_hooks_directions():
    with tempfile.TemporaryDirectory() as tmpdir:
        env = dict(os.environ)
        env['PYTHONPATH'] = str(REPO / 'src') + os.pathsep + env.get('PYTHONPATH', '')
        
        # 1. Initialize git
        subprocess.run(["git", "init"], cwd=tmpdir, capture_output=True, check=True)
        
        # Test init output has the suggestion
        res_init = subprocess.run([
            sys.executable, "-m", "snowline.cli", "init", "--apply"
        ], cwd=tmpdir, capture_output=True, text=True, encoding="utf-8", env=env)
        assert res_init.returncode == 0
        assert "snowline install-hooks --apply" in res_init.stdout
        print("PASS: init --apply menampilkan anjuran snowline install-hooks --apply")

        pre_commit_path = os.path.join(tmpdir, ".git", "hooks", "pre-commit")

        # Arah a: belum ada pre-commit -> terpasang
        res_ih1 = subprocess.run([
            sys.executable, "-m", "snowline.cli", "install-hooks", "--apply"
        ], cwd=tmpdir, capture_output=True, text=True, encoding="utf-8", env=env)
        assert res_ih1.returncode == 0, f"install-hooks gagal: {res_ih1.stderr}"
        assert os.path.exists(pre_commit_path), "pre-commit file tidak dibuat"
        with open(pre_commit_path, "r", encoding="utf-8") as f:
            content_installed = f.read()
        assert "Project Guardian Pre-Commit Hook" in content_installed
        print("PASS: Arah A (belum ada pre-commit -> terpasang)")

        # Ubah isi pre-commit menjadi hook kustom pengguna
        custom_hook = "#!/bin/sh\necho 'custom user hook'\n"
        with open(pre_commit_path, "w", encoding="utf-8") as f:
            f.write(custom_hook)

        # Arah b: sudah ada pre-commit -> DITOLAK, berkas lama utuh, isinya dibandingkan
        res_ih2 = subprocess.run([
            sys.executable, "-m", "snowline.cli", "install-hooks", "--apply"
        ], cwd=tmpdir, capture_output=True, text=True, encoding="utf-8", env=env)
        assert res_ih2.returncode != 0, "install-hooks seharusnya ditolak"
        assert "[BLOCKED]" in res_ih2.stdout or "[BLOCKED]" in res_ih2.stderr
        with open(pre_commit_path, "r", encoding="utf-8") as f:
            content_after_reject = f.read()
        assert content_after_reject == custom_hook, "Berkas lama berubah padahal seharusnya utuh"
        print("PASS: Arah B (sudah ada pre-commit -> DITOLAK, berkas lama utuh)")

        # Arah c: --force -> ditimpa, dan yang lama disalin ke pre-commit.bak
        res_ih3 = subprocess.run([
            sys.executable, "-m", "snowline.cli", "install-hooks", "--apply", "--force"
        ], cwd=tmpdir, capture_output=True, text=True, encoding="utf-8", env=env)
        assert res_ih3.returncode == 0, f"install-hooks --force gagal: {res_ih3.stderr}"
        with open(pre_commit_path, "r", encoding="utf-8") as f:
            content_after_force = f.read()
        assert "Project Guardian Pre-Commit Hook" in content_after_force
        bak_path = pre_commit_path + ".bak"
        assert os.path.exists(bak_path), "pre-commit.bak tidak dibuat"
        with open(bak_path, "r", encoding="utf-8") as f:
            bak_content = f.read()
        assert bak_content == custom_hook, "Isi pre-commit.bak tidak sama dengan hook kustom lama"
        print("PASS: Arah C (--force -> ditimpa, yang lama disalin ke pre-commit.bak)")

if __name__ == "__main__":
    test_b5_install_hooks_directions()
    print("\nALL ENTRI B5 DIRECTIONS PASSED!")