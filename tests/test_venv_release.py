"""
Uji Venv Rilis (Dua Arah) - Dijalankan terpisah sebelum rilis.
Perintah: python tests/test_venv_release.py
"""
import os
import sys
import subprocess
import tempfile
import time
import socket
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

def check_network():
    try:
        socket.create_connection(("github.com", 443), timeout=3)
        return True
    except OSError:
        return False

def get_git_commit(ref="HEAD"):
    res = subprocess.run(["git", "rev-parse", ref], cwd=str(REPO_ROOT), capture_output=True, text=True, check=True)
    return res.stdout.strip()

def run_venv_release_tests():
    if not check_network():
        print("[SKIP] Jaringan tidak tersedia untuk pengujian venv release. Pengujian dilewati secara aman.")
        return 0

    start_time = time.time()
    print("==================================================")
    print("  Snowline Release Venv Verification (Dua Arah)")
    print("==================================================")

    head_sha = get_git_commit("HEAD")
    old_sha = "ea094ed" # Commit lama dengan kode evaluasi baru
    repo_uri = REPO_ROOT.as_uri()

    # 1. Arah 1: Pasang git+file:///<repo>@<HEAD> (harus mutakhir dan menyebut keterangan pembanding)
    print(f"\n[Arah 1] Menguji instalasi lokal git+file @ HEAD ({head_sha[:8]})...")
    with tempfile.TemporaryDirectory() as tmpvenv1:
        subprocess.run([sys.executable, "-m", "venv", tmpvenv1], check=True)
        py1 = os.path.join(tmpvenv1, "Scripts", "python.exe") if sys.platform == "win32" else os.path.join(tmpvenv1, "bin", "python")
        
        # Install git+file @ HEAD
        pip_target1 = f"git+{repo_uri}@{head_sha}"
        subprocess.run([py1, "-m", "pip", "install", pip_target1], check=True)
        
        with tempfile.TemporaryDirectory() as tmpproj1:
            res_init = subprocess.run([py1, "-m", "snowline.cli", "init", "--apply"], cwd=tmpproj1, capture_output=True, text=True)
            res_up = subprocess.run([py1, "-m", "snowline.cli", "update"], cwd=tmpproj1, capture_output=True, text=True)
            res_st = subprocess.run([py1, "-m", "snowline.cli", "status"], cwd=tmpproj1, capture_output=True, text=True)
            
            print("Keluaran update (Arah 1):")
            print(res_up.stdout.strip())
            print("\nKeluaran status (Arah 1):")
            print(res_st.stdout.strip())
            
            assert "All skills are up to date!" in res_up.stdout, f"Arah 1 gagal: update tidak berkata 'All skills are up to date!':\n{res_up.stdout}"
            assert "tertinggal" not in res_up.stdout.lower(), f"Arah 1 gagal: update melaporkan tertinggal:\n{res_up.stdout}"
            assert "-> terbaru" in res_st.stdout, f"Arah 1 gagal: status tidak melaporkan '-> terbaru':\n{res_st.stdout}"
            assert ("sesuai dengan remote HEAD" in res_st.stdout or "sesuai dengan tag" in res_st.stdout), f"Arah 1 gagal: status harus menyebut keterangan pembanding (HEAD atau tag):\n{res_st.stdout}"
            print("\n[OK] Arah 1: Instalasi dari HEAD dilaporkan mutakhir dan memuat keterangan pembanding.")

    # 2. Arah 2: Pasang git+file:///<repo>@<commit lama ea094ed> (harus tertinggal dan memuat keterangan pembanding)
    print(f"\n[Arah 2] Menguji instalasi lokal git+file @ commit lama ({old_sha})...")
    with tempfile.TemporaryDirectory() as tmpvenv2:
        subprocess.run([sys.executable, "-m", "venv", tmpvenv2], check=True)
        py2 = os.path.join(tmpvenv2, "Scripts", "python.exe") if sys.platform == "win32" else os.path.join(tmpvenv2, "bin", "python")
        
        # Install git+file @ commit lama
        pip_target2 = f"git+{repo_uri}@{old_sha}"
        subprocess.run([py2, "-m", "pip", "install", pip_target2], check=True)
        
        with tempfile.TemporaryDirectory() as tmpproj2:
            res_init2 = subprocess.run([py2, "-m", "snowline.cli", "init", "--apply"], cwd=tmpproj2, capture_output=True, text=True)
            res_up2 = subprocess.run([py2, "-m", "snowline.cli", "update"], cwd=tmpproj2, capture_output=True, text=True)
            res_st2 = subprocess.run([py2, "-m", "snowline.cli", "status"], cwd=tmpproj2, capture_output=True, text=True)
            
            print("Keluaran update (Arah 2):")
            print(res_up2.stdout.strip())
            print("\nKeluaran status (Arah 2):")
            print(res_st2.stdout.strip())
            
            assert "Package version tertinggal!" in res_up2.stdout, f"Arah 2 gagal: update tidak mendeteksi status tertinggal:\n{res_up2.stdout}"
            assert ("tertinggal dari" in res_up2.stdout and ("tag" in res_up2.stdout or "HEAD" in res_up2.stdout)), f"Arah 2 gagal: keterangan pembanding hilang di update:\n{res_up2.stdout}"
            assert "-> tertinggal" in res_st2.stdout, f"Arah 2 gagal: status tidak melaporkan '-> tertinggal':\n{res_st2.stdout}"
            assert "tertinggal dari" in res_st2.stdout, f"Arah 2 gagal: keterangan pembanding hilang di status:\n{res_st2.stdout}"
            print("\n[OK] Arah 2: Instalasi dari commit lama berhasil dideteksi tertinggal beserta pembandingnya.")

    elapsed = time.time() - start_time
    print(f"\n==================================================")
    print(f"Semua pengujian rilis venv selesai dalam kisaran {elapsed:.1f} detik ({elapsed/60:.1f} menit).")
    print("==================================================")
    return 0

if __name__ == "__main__":
    sys.exit(run_venv_release_tests())
