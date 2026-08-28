import os
import sys
import json
import time
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

        # Setup dummy linter untuk menghindari probe npx jaringan
        dummy_linter_dir = os.path.join(self.dir, "node_modules", ".bin")
        os.makedirs(dummy_linter_dir, exist_ok=True)
        dummy_linter_path = os.path.join(dummy_linter_dir, "eslint.cmd" if sys.platform == "win32" else "eslint")
        dummy_script = "@echo off\nif \"%~1\"==\"-v\" (echo v8.0.0 & exit /b 0)\nexit /b 0\n" if sys.platform == "win32" else "#!/bin/sh\nexit 0\n"
        with open(dummy_linter_path, "w", encoding="utf-8") as f:
            f.write(dummy_script)
        if sys.platform != "win32":
            os.chmod(dummy_linter_path, 0o755)

        # Setup role.json sebagai TL agar diizinkan tulis
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
    # Arah a: --apply di proyek dengan scripts.build (lambat 10s), TANPA --with-build
    # -> selesai seketika (< 3 detik meskipun build butuh 10 detik), tidak ada build dijalankan, menyebut --with-build
    build_slow_cmd = f'{sys.executable} -c "import time; time.sleep(10)"'
    with ProyekUji({"kode.js": "const namaLama = 1;\n"}, pkg_scripts={"build": build_slow_cmd}) as p:
        t0 = time.time()
        res_a = p.jalankan(".", "namaLama", "namaBaru", "--apply")
        elapsed = time.time() - t0
        assert res_a.returncode == 0, f"Arah a gagal: {res_a.stderr}\n{res_a.stdout}"
        assert elapsed < 4.0, f"Arah a terlalu lambat (menjalankan build padahal tanpa --with-build): {elapsed:.2f}s"
        assert "[BUILD" not in res_a.stdout, f"Arah a tidak boleh memicu build: {res_a.stdout}"
        assert "--with-build" in res_a.stdout, f"Arah a missing mention of --with-build: {res_a.stdout}"
        print(f"PASS: Arah A (--apply tanpa --with-build -> selesai dalam {elapsed:.2f}s, build tidak dijalankan, menyebut --with-build)")

    # Arah b: --apply --with-build, build lulus -> [BUILD SUCCESS]
    build_ok_cmd = f'{sys.executable} -c "import sys; print(\\"Frontend build passed\\"); sys.exit(0)"'
    with ProyekUji({"kode.js": "const namaLama = 1;\n"}, pkg_scripts={"build": build_ok_cmd}) as p:
        res_b = p.jalankan(".", "namaLama", "namaBaru", "--apply", "--with-build")
        assert res_b.returncode == 0, f"Arah b gagal: {res_b.stderr}\n{res_b.stdout}"
        assert "[BUILD SUCCESS]" in res_b.stdout, f"Arah b missing BUILD SUCCESS: {res_b.stdout}"
        print("PASS: Arah B (--apply --with-build lulus -> [BUILD SUCCESS] dilaporkan)")

    # Arah c: --apply --with-build, build gagal -> [BUILD FAIL], berkas tetap ditulis
    build_fail_cmd = f'{sys.executable} -c "import sys; sys.stderr.write(\\"Build error: syntax broken\\"); sys.exit(1)"'
    with ProyekUji({"kode.js": "const namaLama = 1;\n"}, pkg_scripts={"build": build_fail_cmd}) as p:
        res_c = p.jalankan(".", "namaLama", "namaBaru", "--apply", "--with-build")
        assert res_c.returncode == 0, f"Arah c gagal: {res_c.stderr}\n{res_c.stdout}"
        assert "[BUILD FAIL]" in res_c.stdout, f"Arah c missing BUILD FAIL: {res_c.stdout}"
        assert "Build error" in res_c.stdout or "Build error" in res_c.stderr, f"Arah c missing error details: {res_c.stdout}"
        with open(os.path.join(p.dir, "kode.js"), "r", encoding="utf-8") as f:
            content = f.read()
        assert "namaBaru" in content, "Arah c gagal: berkas tidak ditulis saat build gagal!"
        print("PASS: Arah C (--apply --with-build gagal -> [BUILD FAIL] dilaporkan, berkas tetap ditulis)")

    # Arah d: --apply --with-build, tanpa scripts.build -> dilewati dan dikatakan
    with ProyekUji({"kode.js": "const namaLama = 1;\n"}, pkg_scripts={"test": "echo test"}) as p:
        res_d = p.jalankan(".", "namaLama", "namaBaru", "--apply", "--with-build")
        assert res_d.returncode == 0, f"Arah d gagal: {res_d.stderr}\n{res_d.stdout}"
        assert "[BUILD SUCCESS]" not in res_d.stdout and "[BUILD FAIL]" not in res_d.stdout, f"Arah d tidak boleh memicu build: {res_d.stdout}"
        assert "dilewati" in res_d.stdout.lower() or "tidak ditemukan" in res_d.stdout.lower(), f"Arah d missing skip message: {res_d.stdout}"
        print("PASS: Arah D (--apply --with-build tanpa scripts.build -> pemeriksaan build dilewati dan dikatakan)")

if __name__ == "__main__":
    test_d4_frontend_build_directions()
    print("\nALL SPRINT 47 ENTRI 1 DIRECTIONS PASSED!")
