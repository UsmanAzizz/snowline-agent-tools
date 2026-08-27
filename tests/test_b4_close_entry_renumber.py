import os
import sys
import tempfile
import shutil
from pathlib import Path

from snowline.core_close_entry import renumber_terbuka, close_entry_command

def test_b4_renumber_terbuka_directions():
    # Arah a: daftar dengan nomor ganda -> nomornya berurutan
    state_double = [
        "# KEADAAN",
        "",
        "## Terbuka",
        "",
        "```",
        "1  item pertama      keterangan baris 1",
        "                     lanjutan keterangan",
        "1  item kedua ganda  keterangan baris 2",
        "3  item ketiga       keterangan baris 3",
        "```",
        "",
        "TUTUP lewat chamber, arsip per topik:",
        "```",
        "```"
    ]
    renumbered_a = renumber_terbuka(state_double)
    assert "1  item pertama" in renumbered_a[5]
    assert "2  item kedua ganda" in renumbered_a[7]
    assert "3  item ketiga" in renumbered_a[8]
    print("PASS: Arah A (daftar dengan nomor ganda -> dinomori ulang berurutan)")

    # Arah b: daftar yang sudah benar -> tidak berubah
    state_correct = [
        "# KEADAAN",
        "",
        "## Terbuka",
        "",
        "```",
        "1  item pertama      keterangan baris 1",
        "2  item kedua        keterangan baris 2",
        "3  item ketiga       keterangan baris 3",
        "```",
        "",
        "TUTUP lewat chamber, arsip per topik:",
        "```",
        "```"
    ]
    renumbered_b = renumber_terbuka(state_correct)
    assert renumbered_b == state_correct
    print("PASS: Arah B (daftar yang sudah benar tidak berubah)")

    # Arah c: daftar kosong -> tidak galat
    state_empty = [
        "# KEADAAN",
        "",
        "## Terbuka",
        "",
        "```",
        "```",
        "",
        "TUTUP lewat chamber, arsip per topik:",
        "```",
        "```"
    ]
    renumbered_c = renumber_terbuka(state_empty)
    assert renumbered_c == state_empty
    print("PASS: Arah C (daftar kosong tidak galat)")

    # Test integrated close_entry_command execution
    with tempfile.TemporaryDirectory() as tmpdir:
        chamber = os.path.join(tmpdir, ".here_we_are")
        os.makedirs(chamber)
        conn = os.path.join(chamber, "connector.md")
        with open(conn, "w", encoding="utf-8") as f:
            f.write("# PM -> TL: Entri Baru\n\nIsi entri baru.\n---\n")
            
        st = os.path.join(chamber, "STATE.md")
        with open(st, "w", encoding="utf-8") as f:
            f.write("\n".join(state_double) + "\n")

        # Run close_entry_command in tmpdir
        cwd_orig = os.getcwd()
        try:
            os.chdir(tmpdir)
            close_entry_command("topik-uji")
        finally:
            os.chdir(cwd_orig)

        with open(st, "r", encoding="utf-8") as f:
            st_result = f.read()

        assert "1  item pertama" in st_result
        assert "2  item kedua ganda" in st_result
        assert "3  item ketiga" in st_result
        assert "topik-uji" in st_result
        print("PASS: close_entry_command secara end-to-end menomori ulang Terbuka")

if __name__ == "__main__":
    test_b4_renumber_terbuka_directions()
    print("\nALL ENTRI B4 DIRECTIONS PASSED!")