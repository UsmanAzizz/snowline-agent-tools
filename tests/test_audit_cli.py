import os
import sys
import tempfile
import json
import shutil
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

def run_snowline_audit(args, cwd):
    env = dict(os.environ)
    env['PYTHONPATH'] = str(REPO / 'src') + os.pathsep + env.get('PYTHONPATH', '')
    cmd = [sys.executable, "-m", "snowline.cli", "audit"] + args
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8", env=env)

def test_audit_directions():
    temp_dir = tempfile.mkdtemp(prefix="test_a4_")
    try:
        # Arah a: log kosong / tidak ada -> pesan wajar, bukan galat (exit 0)
        res_empty = run_snowline_audit([], temp_dir)
        assert res_empty.returncode == 0
        assert "Belum ada catatan tulisan" in res_empty.stdout
        print("PASS: Arah A (log tidak ada -> pesan wajar, exit 0)")

        agents = os.path.join(temp_dir, ".agents")
        os.makedirs(agents)
        log_file = os.path.join(agents, "write_log.jsonl")

        # Buat campuran: 14 tulisan (11 dalam lingkup, 3 di luar lingkup, 5 lewat shell)
        entries = [
            {"waktu": "2026-08-25T10:00:00", "alat": "smart_replace", "berkas": "src/App.jsx", "dalam_lingkup": True, "tugas": "perbaiki header"},
            {"waktu": "2026-08-25T10:05:00", "alat": "smart_replace", "berkas": "src/Button.jsx", "dalam_lingkup": True, "tugas": "perbaiki header"},
            {"waktu": "2026-08-25T10:10:00", "alat": "shell", "berkas": "src/config.js", "dalam_lingkup": False, "tugas": "perbaiki header"},
            {"waktu": "2026-08-25T10:15:00", "alat": "shell", "berkas": "src/config.js", "dalam_lingkup": False, "tugas": "perbaiki header"},
            {"waktu": "2026-08-25T10:20:00", "alat": "shell", "berkas": "../lain/x.py", "dalam_lingkup": False, "tugas": "perbaiki header"},
            {"waktu": "2026-08-25T10:25:00", "alat": "shell", "berkas": "src/Header.jsx", "dalam_lingkup": True, "tugas": "perbaiki header"},
            {"waktu": "2026-08-25T10:30:00", "alat": "shell", "berkas": "src/Footer.jsx", "dalam_lingkup": True, "tugas": "perbaiki header"},
        ]
        for i in range(7):
            entries.append({"waktu": "2026-08-25T11:00:00", "alat": "smart_replace", "berkas": f"src/f{i}.jsx", "dalam_lingkup": True, "tugas": "perbaiki header"})

        with open(log_file, "w", encoding="utf-8") as f:
            for e in entries:
                f.write(json.dumps(e) + "\n")

        # Arah b: log berisi campuran -> angkanya cocok dengan isi berkas
        res_mix = run_snowline_audit([], temp_dir)
        assert res_mix.returncode == 0
        assert "14 tulisan, 3 di luar lingkup" in res_mix.stdout
        assert "src/config.js" in res_mix.stdout
        assert "2 kali" in res_mix.stdout
        assert "../lain/x.py" in res_mix.stdout
        assert "1 kali" in res_mix.stdout
        assert "lewat shell (deteksi best-effort): 5" in res_mix.stdout
        print("PASS: Arah B (ringkasan campuran cocok)")

        # Arah c: --hanya-luar-lingkup -> cuma menampilkan yang di luar
        res_only_out = run_snowline_audit(["--hanya-luar-lingkup"], temp_dir)
        assert res_only_out.returncode == 0
        assert "3 tulisan di luar lingkup (dari 14 total)" in res_only_out.stdout
        assert "src/config.js" in res_only_out.stdout
        assert "../lain/x.py" in res_only_out.stdout
        assert "lewat shell" not in res_only_out.stdout
        print("PASS: Arah C (--hanya-luar-lingkup)")

        # Arah d: log rusak sebagian -> baris rusak dilewati, disebutkan berapa
        with open(log_file, "a", encoding="utf-8") as f:
            f.write("INI BARIS RUSAK BUKAN JSON\n")
            f.write("{json tidak tutup\n")

        res_corrupt = run_snowline_audit([], temp_dir)
        assert res_corrupt.returncode == 0
        assert "2 baris log rusak dilewati" in res_corrupt.stdout
        assert "14 tulisan, 3 di luar lingkup" in res_corrupt.stdout
        print("PASS: Arah D (baris rusak dilewati dan disebutkan berapa)")

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    test_audit_directions()
    print("\nALL ENTRI A4 DIRECTIONS PASSED!")
