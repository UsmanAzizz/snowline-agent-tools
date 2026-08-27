import os
import sys
import tempfile
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

def run_snowline_rotate(args, cwd):
    env = dict(os.environ)
    env['PYTHONPATH'] = str(REPO / 'src') + os.pathsep + env.get('PYTHONPATH', '')
    cmd = [sys.executable, "-m", "snowline.cli", "rotate"] + args
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8", env=env)

def test_c1_rotate_directions():
    with tempfile.TemporaryDirectory() as tmpdir:
        chamber = os.path.join(tmpdir, ".here_we_are")
        os.makedirs(chamber)
        conn = os.path.join(chamber, "connector.md")
        
        conn_text = "# PM -> TL: Entri 1\nBaris 1\nBaris 2\n---\n# TL -> PM: Entri 2\nBaris 4\nBaris 5\n---\n# PM -> TL: Entri 3\nBaris 7\n"
        with open(conn, "w", encoding="utf-8") as f:
            f.write(conn_text)
            
        orig_lines = len(conn_text.splitlines())
        
        # Arah c: dry-run bawaan lewat CLI subprocess -> tanpa --apply tidak ada berkas berubah
        res_dry = run_snowline_rotate(["arsip-test"], cwd=tmpdir)
        assert res_dry.returncode == 0, f"Dry-run gagal:\n{res_dry.stderr}\n{res_dry.stdout}"
        assert "[DRY RUN]" in res_dry.stdout
        assert "Pratinjau Rotasi Connector" in res_dry.stdout
        
        with open(conn, "r", encoding="utf-8") as f:
            content_after_dry = f.read()
        assert content_after_dry == conn_text, "Arah C gagal: dry-run mengubah connector.md"
        assert not os.path.exists(os.path.join(chamber, "history", "arsip-test")), "Arah C gagal: folder history dibuat pada dry-run"
        print("PASS: Arah C (dry-run lewat CLI subprocess tidak mengubah berkas apa pun)")

        # Arah a: rotasi normal lewat CLI subprocess dengan --apply -> jumlah baris connector + arsip = jumlah semula
        res_apply = run_snowline_rotate(["arsip-sukses", "--apply"], cwd=tmpdir)
        assert res_apply.returncode == 0, f"Apply gagal:\n{res_apply.stderr}\n{res_apply.stdout}"
        assert "[SUCCESS]" in res_apply.stdout
        
        with open(conn, "r", encoding="utf-8") as f:
            lines_conn = len(f.read().splitlines())
            
        archive_file = os.path.join(chamber, "history", "arsip-sukses", "01-arsip-sukses.md")
        assert os.path.exists(archive_file), "Arsip file tidak ada"
        with open(archive_file, "r", encoding="utf-8") as f:
            lines_arch = len(f.read().splitlines())
            
        assert lines_conn + lines_arch == orig_lines, f"Arah A gagal: {lines_conn} + {lines_arch} != {orig_lines}"
        print("PASS: Arah A (rotasi normal lewat CLI subprocess: lines_conn + lines_arch == orig_lines)")

def test_c1_rotate_failure_intact():
    # Arah b: arsip gagal ditulis (misal direktori target tidak bisa ditulis / corrupt) -> connector UTUH
    with tempfile.TemporaryDirectory() as tmpdir:
        chamber = os.path.join(tmpdir, ".here_we_are")
        os.makedirs(chamber)
        conn = os.path.join(chamber, "connector.md")
        conn_text = "# PM -> TL: Entri 1\nBaris 1\n---\n# TL -> PM: Entri 2\nBaris 3\n"
        with open(conn, "w", encoding="utf-8") as f:
            f.write(conn_text)

        # Buat file bernama 'history' (bukan direktori) sehingga mkdir gagal
        hist_blocker = os.path.join(chamber, "history")
        with open(hist_blocker, "w", encoding="utf-8") as f:
            f.write("blocker")

        res_fail = run_snowline_rotate(["arsip-fail", "--apply"], cwd=tmpdir)
        assert res_fail.returncode != 0
        assert "[ABORT]" in res_fail.stdout or "[FAIL]" in res_fail.stdout or "[FAIL]" in res_fail.stderr

        with open(conn, "r", encoding="utf-8") as f:
            content_after_fail = f.read()
        assert content_after_fail == conn_text, "Arah B gagal: connector.md rusak setelah rotasi gagal"
        print("PASS: Arah B (arsip gagal ditulis -> connector UTUH)")

if __name__ == "__main__":
    test_c1_rotate_directions()
    test_c1_rotate_failure_intact()
    print("\nALL ENTRI C1 DIRECTIONS PASSED VIA SUBPROCESS CLI!")
