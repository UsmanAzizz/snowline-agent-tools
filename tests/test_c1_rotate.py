import os
import sys
import tempfile
import shutil
import subprocess
from unittest.mock import patch
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

def test_c1_rotate_directions():
    from snowline.core_rotate import rotate_command

    with tempfile.TemporaryDirectory() as tmpdir:
        chamber = os.path.join(tmpdir, ".here_we_are")
        os.makedirs(chamber)
        conn = os.path.join(chamber, "connector.md")
        
        # Buat connector dengan 3 entri (total 40 baris)
        conn_text = "# PM -> TL: Entri 1\nBaris 1\nBaris 2\n---\n# TL -> PM: Entri 2\nBaris 4\nBaris 5\n---\n# PM -> TL: Entri 3\nBaris 7\n"
        with open(conn, "w", encoding="utf-8") as f:
            f.write(conn_text)
            
        orig_lines = len(conn_text.splitlines())
        
        cwd_orig = os.getcwd()
        try:
            os.chdir(tmpdir)
            
            # Arah c: dry-run bawaan -> tanpa --apply tidak ada berkas berubah
            rotate_command("arsip-test", apply=False)
            with open(conn, "r", encoding="utf-8") as f:
                content_after_dry = f.read()
            assert content_after_dry == conn_text, "Arah C gagal: dry-run mengubah connector.md"
            assert not os.path.exists(os.path.join(chamber, "history", "arsip-test")), "Arah C gagal: folder history dibuat pada dry-run"
            print("PASS: Arah C (dry-run bawaan tidak mengubah berkas apa pun)")

            # Arah b: arsip gagal ditulis -> connector UTUH, tidak ada yang hilang
            # Kita simulasikan kegagalan tulis pada open() arsip
            with patch("builtins.open", side_effect=[
                open(conn, "r", encoding="utf-8"), # read connector
                IOError("Simulasi disk penuh / permission error") # write archive
            ]):
                try:
                    rotate_command("arsip-fail", apply=True)
                except SystemExit as se:
                    assert se.code != 0
                    
            with open(conn, "r", encoding="utf-8") as f:
                content_after_fail = f.read()
            assert content_after_fail == conn_text, "Arah B gagal: connector.md rusak setelah arsip gagal ditulis"
            print("PASS: Arah B (arsip gagal ditulis -> connector UTUH)")

            # Arah a: rotasi normal -> jumlah baris connector + arsip = jumlah semula
            rotate_command("arsip-sukses", apply=True)
            
            with open(conn, "r", encoding="utf-8") as f:
                lines_conn = len(f.read().splitlines())
                
            archive_file = os.path.join(chamber, "history", "arsip-sukses", "01-arsip-sukses.md")
            assert os.path.exists(archive_file), "Arsip file tidak ada"
            with open(archive_file, "r", encoding="utf-8") as f:
                lines_arch = len(f.read().splitlines())
                
            assert lines_conn + lines_arch == orig_lines, f"Arah A gagal: {lines_conn} + {lines_arch} != {orig_lines}"
            print("PASS: Arah A (rotasi normal: lines_conn + lines_arch == orig_lines)")

        finally:
            os.chdir(cwd_orig)

if __name__ == "__main__":
    test_c1_rotate_directions()
    print("\nALL ENTRI C1 DIRECTIONS PASSED!")