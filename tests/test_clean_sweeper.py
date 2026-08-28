import os
import sys
import tempfile
import subprocess
from pathlib import Path

sys.dont_write_bytecode = True
REPO = Path(__file__).resolve().parent.parent

def _get_sweeper():
    sys.dont_write_bytecode = True
    skrip_dir = str(REPO / 'src' / 'snowline' / 'templates' / 'skills' / 'clean_sweeper')
    if skrip_dir not in sys.path:
        sys.path.insert(0, skrip_dir)
    import sweeper
    return sweeper

def test_sweeper_clean_project():
    sweeper = _get_sweeper()
    with tempfile.TemporaryDirectory() as tmpdir:
        os.makedirs(os.path.join(tmpdir, 'src'))
        with open(os.path.join(tmpdir, 'src', 'main.py'), 'w', encoding='utf-8') as f:
            f.write("print('hello')\n")
        
        residue, todo, comments, scanned, skipped = sweeper.sweep(tmpdir)
        assert len(residue) == 0, "Project bersih seharusnya tidak ada file residu"
        assert todo == 0, "Project bersih seharusnya tidak ada TODO"
        assert len(comments) == 0, "Project bersih seharusnya tidak ada komentar besar"

def test_sweeper_needs_cleanup():
    sweeper = _get_sweeper()
    with tempfile.TemporaryDirectory() as tmpdir:
        os.makedirs(os.path.join(tmpdir, 'backup'))
        with open(os.path.join(tmpdir, 'database.db'), 'w', encoding='utf-8') as f:
            f.write("sqlite data")
        with open(os.path.join(tmpdir, 'main.py'), 'w', encoding='utf-8') as f:
            f.write("# TODO: fix this\n")
            f.write("# comment 1\n# comment 2\n# comment 3\n# comment 4\n# comment 5\n# comment 6\n# comment 7\n# comment 8\n")
        
        residue, todo, comments, scanned, skipped = sweeper.sweep(tmpdir)
        assert todo == 1, "Gagal mendeteksi TODO"
        assert len(comments) == 1, "Gagal mendeteksi blok komentar besar"
        assert any(r['type'] == 'local_sqlite' for r in residue), "Gagal mendeteksi database lokal"
        assert any(r['type'] == 'backup_folder' for r in residue), "Gagal mendeteksi backup folder"

def test_sweeper_cache_and_no_cache():
    skrip = str(REPO / 'src' / 'snowline' / 'templates' / 'skills' / 'clean_sweeper' / 'sweeper.py')
    with tempfile.TemporaryDirectory() as tmpdir:
        src_dir = os.path.join(tmpdir, 'src')
        os.makedirs(src_dir, exist_ok=True)
        with open(os.path.join(src_dir, 'app.py'), 'w', encoding='utf-8') as f:
            f.write("print('test sweeper cache')\n")
            
        env = dict(os.environ)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        
        # 1. Panggilan pertama -> memindai dan membuat cache
        res1 = subprocess.run([sys.executable, "-B", skrip, tmpdir], capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
        assert res1.returncode == 0, f"Run 1 failed: {res1.stderr}"
        assert "[INFO] Menggunakan hasil cache" not in res1.stdout, "Run 1 tidak boleh membaca cache!"
        
        # 2. Arah a & c: Panggilan kedua -> menggunakan cache, penanda muncul di awal DAN akhir
        res2 = subprocess.run([sys.executable, "-B", skrip, tmpdir], capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
        assert res2.returncode == 0, f"Run 2 failed: {res2.stderr}"
        assert "[INFO] Menggunakan hasil cache dari session_cache.json" in res2.stdout, "Arah a gagal: Run 2 harus menyebut cache di awal!"
        assert "[INFO] Hasil di atas diambil dari cache (session_cache.json)" in res2.stdout, "Arah c gagal: Run 2 harus menyebut cache di akhir!"
        
        lines2 = [l.strip() for l in res2.stdout.strip().splitlines() if l.strip()]
        assert "Menggunakan hasil cache" in lines2[0], f"Arah c gagal: penanda awal harus di baris pertama: {lines2[0]}"
        assert "Hasil di atas diambil dari cache" in lines2[-1], f"Arah c gagal: penanda akhir harus di baris terakhir: {lines2[-1]}"
        print("PASS: Arah A & C (jalankan dua kali -> penanda cache muncul di awal DAN akhir)")
        
        # 3. Arah b: Panggilan ketiga dengan --no-cache -> memindai ulang, TIDAK menyebut cache sama sekali
        res3 = subprocess.run([sys.executable, "-B", skrip, tmpdir, "--no-cache"], capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
        assert res3.returncode == 0, f"Run 3 failed: {res3.stderr}"
        assert "cache" not in res3.stdout.lower() or "[INFO] Menggunakan hasil cache" not in res3.stdout, "Arah b gagal: Run 3 dengan --no-cache tidak boleh menyebut cache!"
        assert "[INFO] Hasil di atas diambil dari cache" not in res3.stdout, "Arah b gagal: Run 3 dengan --no-cache tidak boleh menyebut cache di akhir!"
        print("PASS: Arah B (jalankan dengan --no-cache -> memindai ulang tanpa membaca cache)")
