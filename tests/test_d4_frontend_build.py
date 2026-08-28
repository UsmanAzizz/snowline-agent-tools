import os
import sys
import json
import tempfile
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKRIP = REPO / "src" / "snowline" / "templates" / "skills" / "smart_replace" / "replace_text.py"

class ProyekUji:
    def __init__(self, berkas, pkg_scripts=None):
        self.berkas = berkas
        self.pkg_scripts = pkg_scripts

    def __enter__(self):
        self.dir = tempfile.mkdtemp(prefix="snowline_uji_build_")
        for nama, isi in self.berkas.items():
            jalur = os.path.join(self.dir, nama)
            os.makedirs(os.path.dirname(jalur), exist_ok=True)
            with open(jalur, "w", encoding="utf-8") as f:
                f.write(isi)

        # Setup role.json sebagai TL
        chamber_dir = os.path.join(self.dir, ".agents", "chamber")
        os.makedirs(chamber_dir, exist_ok=True)
        with open(os.path.join(chamber_dir, "role.json"), "w", encoding="utf-8") as f:
            f.write(json.dumps({"role": "TL"}))

        if self.pkg_scripts is not None:
            pkg_json = {
                "name": "mock-frontend",
                "version": "1.0.0",
                "scripts": self.pkg_scripts
            }
            with open(os.path.join(self.dir, "package.json"), "w", encoding="utf-8") as f:
                f.write(json.dumps(pkg_json, indent=2))
                
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        import shutil
        shutil.rmtree(self.dir, ignore_errors=True)

    def jalankan(self, *args, env_extra=None):
        env = dict(os.environ)
        env["PYTHONPATH"] = str(REPO / "src") + os.pathsep + env.get("PYTHONPATH", "")
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        if env_extra:
            env.update(env_extra)
        return subprocess.run(
            [sys.executable, "-B", str(SKRIP), *args],
            cwd=self.dir, capture_output=True, text=True, env=env, encoding="utf-8", errors="replace"
        )

def test_d4_frontend_build_directions():
    # Arah c: Proyek tanpa scripts.build -> dilewati dan dikatakan dilewati
    with ProyekUji({"kode.js": "const namaLama = 1;\n"}, pkg_scripts={"test": "echo test"}) as p:
        res_c = p.jalankan(".", "namaLama", "namaBaru", "--apply")
        assert res_c.returncode == 0, f"Arah c gagal: {res_c.stderr}\n{res_c.stdout}"
        assert "[BUILD SUCCESS]" not in res_c.stdout and "[BUILD FAIL]" not in res_c.stdout, f"Arah c tidak boleh memicu build: {res_c.stdout}"
        assert "dilewati" in res_c.stdout.lower() or "tidak ditemukan" in res_c.stdout.lower(), f"Arah c missing skip message: {res_c.stdout}"
        print("PASS: Arah C (proyek tanpa scripts.build -> pemeriksaan build dilewati dan dilaporkan)")

    # Arah b: Proyek dengan scripts.build, berkas benar -> build lulus dan dilaporkan
    build_ok_cmd = f'{sys.executable} -c "import sys; print(\\"Frontend build passed\\"); sys.exit(0)"'
    with ProyekUji({"kode.js": "const namaLama = 1;\n"}, pkg_scripts={"build": build_ok_cmd}) as p:
        res_b = p.jalankan(".", "namaLama", "namaBaru", "--apply")
        assert res_b.returncode == 0, f"Arah b gagal: {res_b.stderr}\n{res_b.stdout}"
        assert "[BUILD SUCCESS]" in res_b.stdout, f"Arah b missing BUILD SUCCESS: {res_b.stdout}"
        print("PASS: Arah B (proyek dengan scripts.build lulus -> [BUILD SUCCESS] dilaporkan)")

    # Arah a: Proyek dengan scripts.build, berkas rusak / build gagal -> build gagal dilaporkan, penulisan tidak crash
    build_fail_cmd = f'{sys.executable} -c "import sys; sys.stderr.write(\\"Build error: syntax broken\\"); sys.exit(1)"'
    with ProyekUji({"kode.js": "const namaLama = 1;\n"}, pkg_scripts={"build": build_fail_cmd}) as p:
        res_a = p.jalankan(".", "namaLama", "namaBaru", "--apply")
        assert res_a.returncode == 0, f"Arah a gagal: {res_a.stderr}\n{res_a.stdout}"
        assert "[BUILD FAIL]" in res_a.stdout, f"Arah a missing BUILD FAIL: {res_a.stdout}"
        assert "Build error" in res_a.stdout or "Build error" in res_a.stderr, f"Arah a missing error details: {res_a.stdout}"
        print("PASS: Arah A (proyek dengan scripts.build gagal -> [BUILD FAIL] dilaporkan)")

    # Arah d: Build memakan lebih dari batas waktu -> dihentikan (timeout) dan dikatakan
    build_sleep_cmd = f'{sys.executable} -c "import time; time.sleep(3)"'
    with ProyekUji({"kode.js": "const namaLama = 1;\n"}, pkg_scripts={"build": build_sleep_cmd}) as p:
        res_d = p.jalankan(
            ".", "namaLama", "namaBaru", "--apply",
            env_extra={"SNOWLINE_BUILD_TIMEOUT": "1"}
        )
        assert res_d.returncode == 0, f"Arah d gagal: {res_d.stderr}\n{res_d.stdout}"
        assert "[BUILD TIMEOUT]" in res_d.stdout, f"Arah d missing BUILD TIMEOUT: {res_d.stdout}"
        assert "60 detik" in res_d.stdout or "dihentikan" in res_d.stdout.lower(), f"Arah d missing timeout details: {res_d.stdout}"
        print("PASS: Arah D (build melebihi batas waktu -> [BUILD TIMEOUT] dihentikan dan dilaporkan)")

if __name__ == "__main__":
    test_d4_frontend_build_directions()
    print("\nALL D4 FRONTEND BUILD DIRECTIONS PASSED!")
