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

def run_venv_release_tests():
    if not check_network():
        print("[SKIP] Jaringan tidak tersedia untuk pengujian venv release. Pengujian dilewati secara aman.")
        return 0

    start_time = time.time()
    print("==================================================")
    print("  Snowline Release Venv Verification (Dua Arah)")
    print("==================================================")

    # 1. Arah 1: Pasang dari repo lokal / HEAD (harus mutakhir)
    print("\n[Arah 1] Menguji instalasi lokal/HEAD...")
    with tempfile.TemporaryDirectory() as tmpvenv1:
        subprocess.run([sys.executable, "-m", "venv", tmpvenv1], check=True)
        py1 = os.path.join(tmpvenv1, "Scripts", "python.exe") if sys.platform == "win32" else os.path.join(tmpvenv1, "bin", "python")
        
        # Install repo lokal
        subprocess.run([py1, "-m", "pip", "install", str(REPO_ROOT)], check=True)
        
        with tempfile.TemporaryDirectory() as tmpproj1:
            res_init = subprocess.run([py1, "-m", "snowline.cli", "init", "--apply"], cwd=tmpproj1, capture_output=True, text=True)
            res_up = subprocess.run([py1, "-m", "snowline.cli", "update"], cwd=tmpproj1, capture_output=True, text=True)
            
            print("Keluaran update (Arah 1):")
            print(res_up.stdout.strip())
            assert "tertinggal" not in res_up.stdout.lower(), f"Arah 1 gagal: update melaporkan tertinggal:\n{res_up.stdout}"
            assert ("all skills are up to date" in res_up.stdout.lower() or "current skills" in res_up.stdout.lower()), f"Arah 1 gagal: output tidak sesuai:\n{res_up.stdout}"
            print("[OK] Arah 1: Instalasi dari HEAD/lokal dilaporkan mutakhir.")

    # 2. Arah 2: Pasang dari tag rilis lama v1.1.0 (harus tertinggal)
    print("\n[Arah 2] Menguji instalasi dari commit/tag lama (v1.1.0)...")
    with tempfile.TemporaryDirectory() as tmpvenv2:
        subprocess.run([sys.executable, "-m", "venv", tmpvenv2], check=True)
        py2 = os.path.join(tmpvenv2, "Scripts", "python.exe") if sys.platform == "win32" else os.path.join(tmpvenv2, "bin", "python")
        
        # Install tag lama
        subprocess.run([py2, "-m", "pip", "install", "git+https://github.com/UsmanAzizz/snowline-agent-tools.git@v1.1.0"], check=True)
        
        with tempfile.TemporaryDirectory() as tmpproj2:
            res_init2 = subprocess.run([py2, "-m", "snowline.cli", "init", "--apply"], cwd=tmpproj2, capture_output=True, text=True)
            res_up2 = subprocess.run([py2, "-m", "snowline.cli", "update"], cwd=tmpproj2, capture_output=True, text=True)
            
            print("Keluaran update (Arah 2):")
            print(res_up2.stdout.strip())
            assert "tertinggal" in res_up2.stdout.lower(), f"Arah 2 gagal: update tidak mendeteksi status tertinggal:\n{res_up2.stdout}"
            print("[OK] Arah 2: Instalasi dari commit lama berhasil dideteksi tertinggal.")

    elapsed = time.time() - start_time
    print(f"\n==================================================")
    print(f"Semua pengujian rilis venv selesai dalam {elapsed:.2f} detik.")
    print("==================================================")
    return 0

if __name__ == "__main__":
    sys.exit(run_venv_release_tests())
