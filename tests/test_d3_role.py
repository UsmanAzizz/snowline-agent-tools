import os
import sys
import json
import tempfile
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

def run_snowline_cli(args, cwd=None):
    cmd = [sys.executable, "-B", "-m", "snowline.cli"] + args
    env = dict(os.environ)
    env["PYTHONPATH"] = str(REPO / "src")
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)

def test_d3_role_directions():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        
        # Arah a: role.json belum ada -> tampilkan bahwa belum diatur, exit 0, tanpa galat
        res_a = run_snowline_cli(["role"], cwd=tmpdir)
        assert res_a.returncode == 0, f"Arah a gagal: {res_a.stderr}"
        assert "belum diatur" in res_a.stdout.lower() or "belum ditemukan" in res_a.stdout.lower(), f"Arah a output salah: {res_a.stdout}"
        print("PASS: Arah A (role.json belum ada -> menampilkan peran belum diatur tanpa galat)")

        # Arah c: tanpa --apply -> role.json TIDAK berubah/dibuat
        res_c = run_snowline_cli(["role", "QA"], cwd=tmpdir)
        assert res_c.returncode == 0, f"Arah c gagal: {res_c.stderr}"
        assert "[DRY-RUN]" in res_c.stdout or "dry-run" in res_c.stdout.lower(), f"Arah c missing dry run: {res_c.stdout}"
        role_file = tmp_path / ".agents" / "chamber" / "role.json"
        assert not role_file.exists(), "Arah c gagal: role.json dibuat padahal tanpa --apply!"
        print("PASS: Arah C (tanpa --apply -> dry run dan berkas tidak berubah)")

        # Arah b: dengan --apply -> ganti peran menjadi QA, berkas berubah, dan instruksi tercetak
        res_b = run_snowline_cli(["role", "QA", "--apply"], cwd=tmpdir)
        assert res_b.returncode == 0, f"Arah b gagal: {res_b.stderr}"
        assert role_file.exists(), "Arah b gagal: role.json tidak terbuat!"
        
        role_data = json.loads(role_file.read_text(encoding="utf-8"))
        assert role_data.get("role") == "QA", f"Arah b gagal: isi role salah: {role_data}"
        
        # Periksa instruksi untuk manusia / operator
        assert "INSTRUKSI" in res_b.stdout or "operator" in res_b.stdout.lower(), f"Arah b missing operator header: {res_b.stdout}"
        assert "ONBOARDING_QA.md" in res_b.stdout, f"Arah b missing ONBOARDING_QA.md instruction: {res_b.stdout}"
        assert "BARU" in res_b.stdout or "baru" in res_b.stdout.lower(), f"Arah b missing new session instruction: {res_b.stdout}"
        print("PASS: Arah B (ganti peran ke QA dengan --apply -> berkas berubah dan instruksi tercetak)")

        # Periksa pembacaan peran yang sudah disetel
        res_read = run_snowline_cli(["role"], cwd=tmpdir)
        assert res_read.returncode == 0
        assert "Peran sekarang: QA" in res_read.stdout, f"Gagal membaca peran sekarang: {res_read.stdout}"
        print("PASS: (Membaca peran tersimpan: QA)")

        # Ganti kembali ke TL dengan --apply
        res_tl = run_snowline_cli(["role", "TL", "--apply"], cwd=tmpdir)
        assert res_tl.returncode == 0
        role_data_tl = json.loads(role_file.read_text(encoding="utf-8"))
        assert role_data_tl.get("role") == "TL"
        assert "ONBOARDING_TL.md" in res_tl.stdout
        print("PASS: (Ganti peran ke TL dengan --apply -> instruksi TL tercetak)")

if __name__ == "__main__":
    test_d3_role_directions()
    print("\nALL D3 ROLE DIRECTIONS PASSED!")
