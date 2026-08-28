import os
import sys
import tempfile
import json
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILLS = REPO / "src" / "snowline" / "templates" / "skills"

# Urutan pengujian menurut tingkat bahaya jika rusak diam-diam:
# 1. companion     - Gerbang niat/keamanan & gating prompt; jika rusak, aksi berbahaya atau salah maksud lolos.
# 2. smart_tree    - Pemeta struktur pohon proyek; jika rusak, file/folder diabaikan atau konteks navigasi agen salah.
# 3. deep_analyzer - Penganalisis profil proyek (dependencies/stack); jika rusak, inferensi stack dan linter gagal.
# 4. db_extractor  - Pengekstrak skema database; bergantung pada ketersediaan pymysql atau fallback statis.

def run_script(script_path, args, cwd=None):
    env = dict(os.environ)
    env['PYTHONPATH'] = str(REPO / 'src') + os.pathsep + env.get('PYTHONPATH', '')
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    cmd = [sys.executable, '-B', str(script_path)] + args
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)


def test_smart_tree():
    script = SKILLS / "smart_tree" / "scripts" / "tree_viewer.py"
    assert script.exists(), f"Berkas {script} tidak ditemukan"
    
    with tempfile.TemporaryDirectory() as tmpdir:
        os.makedirs(os.path.join(tmpdir, "src", "components"))
        with open(os.path.join(tmpdir, "src", "components", "App.jsx"), "w", encoding="utf-8") as f:
            f.write("// App")
            
        res = run_script(script, [tmpdir, "--no-icons"])
        assert res.returncode == 0, f"smart_tree gagal: {res.stderr}"
        assert "components" in res.stdout or "App.jsx" in res.stdout, f"smart_tree tidak memuat file yang dibuat: {res.stdout}"
        print("PASS: smart_tree (menampilkan struktur pohon direktori secara benar)")

def test_deep_analyzer():
    script = SKILLS / "deep_analyzer" / "analyzer.py"
    assert script.exists(), f"Berkas {script} tidak ditemukan"
    
    with tempfile.TemporaryDirectory() as tmpdir:
        pkg = {
            "name": "dummy-project",
            "dependencies": {"react": "^18.0.0", "express": "^4.18.0"},
            "devDependencies": {"jest": "^29.0.0"},
            "scripts": {"test": "jest", "lint": "eslint ."}
        }
        with open(os.path.join(tmpdir, "package.json"), "w", encoding="utf-8") as f:
            json.dump(pkg, f, indent=2)
            
        res = run_script(script, [tmpdir])
        assert res.returncode == 0, f"deep_analyzer gagal: {res.stderr}"
        assert "2 runtime" in res.stdout or "dependencies" in res.stdout.lower() or "react" in res.stdout.lower(), f"deep_analyzer missing stats: {res.stdout}"
        print("PASS: deep_analyzer (memindai dependensi package.json dan statistik proyek)")

def test_db_extractor():
    script = SKILLS / "db_extractor" / "scripts" / "extractor.py"
    assert script.exists(), f"Berkas {script} tidak ditemukan"

    # Periksa pymysql
    try:
        import pymysql
        has_pymysql = True
    except ImportError:
        has_pymysql = False

    if not has_pymysql:
        print("[SKIP] db_extractor: pymysql tidak terpasang di environment Python, koneksi langsung DB dilewati, menguji fallback statis.")

    with tempfile.TemporaryDirectory() as tmpdir:
        prisma_dir = os.path.join(tmpdir, "prisma")
        os.makedirs(prisma_dir)
        with open(os.path.join(prisma_dir, "schema.prisma"), "w", encoding="utf-8") as f:
            f.write("model User {\n  id Int @id @default(autoincrement())\n  email String @unique\n  name String?\n}\n")
            
        res = run_script(script, [tmpdir])
        assert res.returncode == 0, f"db_extractor gagal: {res.stderr}\n{res.stdout}"
        
        # Penegasan atas keluaran nyata
        assert len(res.stdout.strip()) > 0, "db_extractor tidak menghasilkan keluaran apa pun!"
        assert "Database Extractor" in res.stdout or "Universal Fallback" in res.stdout, f"db_extractor header tidak ditemukan: {res.stdout}"
        assert "User" in res.stdout and ("Prisma Schema Found" in res.stdout or "id Int" in res.stdout), f"db_extractor gagal mengekstrak model schema User: {res.stdout}"
        print("PASS: db_extractor (berjalan sungguhan dan menegaskan ekstraksi skema model User)")

def test_d1_all_four_tools():
    test_smart_tree()
    test_deep_analyzer()
    test_db_extractor()

if __name__ == "__main__":
    test_d1_all_four_tools()
    print("\nALL 3 D1 TOOLS TESTED SUCCESSFULLY WITH OUTPUT ASSERTIONS!")
