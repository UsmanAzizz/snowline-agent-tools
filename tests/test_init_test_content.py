import os
import subprocess
import sys
import tempfile
import re
from pathlib import Path
from datetime import datetime

REPO = Path(__file__).resolve().parent.parent
TEMPLATES = REPO / "src" / "snowline" / "test_templates"

MIN_TUGAS_MIKRO = 11
MIN_BAGIAN_LAPORAN = 16
MIN_BARIS_PROMPT = 150
MIN_BARIS_LAPORAN = 150

KATA_TERLARANG = ["council", "mtime", "tempfile", "winreg",
                  "scope_lock", "add-entry", "role.json"]


def _hitung(teks, awalan):
    return sum(1 for b in teks.split("\n") if b.startswith(awalan))


def _bagian_laporan(teks):
    n = 0
    for b in teks.split("\n"):
        if b.startswith("## ") and b[3:].split(".")[0].strip().isdigit():
            n += 1
    return n


def test_init_test_content():
    src_prompt = TEMPLATES / "SNOWLINE_TEST.md"
    src_laporan = TEMPLATES / "TEST_REPORT.md"

    assert src_prompt.exists(), f"Templat hilang: {src_prompt}"
    assert src_laporan.exists(), f"Templat hilang: {src_laporan}"

    isi_prompt = src_prompt.read_text(encoding="utf-8")
    isi_laporan = src_laporan.read_text(encoding="utf-8")

    # --- Bagian 2: templatnya masih berisi ---
    n_tugas = _hitung(isi_prompt, "## M")
    assert n_tugas >= MIN_TUGAS_MIKRO, (
        f"{src_prompt.name} cuma memuat {n_tugas} tugas mikro, "
        f"seharusnya minimal {MIN_TUGAS_MIKRO}. "
        f"Tugas yang hilang membuat aturan 'kerjakan M1 sampai M9' "
        f"menunjuk ke sesuatu yang tidak ada."
    )

    n_bagian = _bagian_laporan(isi_laporan)
    assert n_bagian >= MIN_BAGIAN_LAPORAN, (
        f"{src_laporan.name} cuma memuat {n_bagian} bagian bernomor, "
        f"seharusnya minimal {MIN_BAGIAN_LAPORAN}."
    )

    n_baris_prompt = len(isi_prompt.split("\n"))
    assert n_baris_prompt >= MIN_BARIS_PROMPT, (
        f"{src_prompt.name} cuma {n_baris_prompt} baris, seharusnya minimal "
        f"{MIN_BARIS_PROMPT}. Isinya kemungkinan terpotong."
    )

    n_baris_laporan = len(isi_laporan.split("\n"))
    assert n_baris_laporan >= MIN_BARIS_LAPORAN, (
        f"{src_laporan.name} cuma {n_baris_laporan} baris, seharusnya minimal "
        f"{MIN_BARIS_LAPORAN}. Isinya kemungkinan terpotong."
    )

    for judul in ("## 10. Rapikan catatan",
                  "## 11. Menunggu",
                  "## 12. Keluaran yang tidak kamu baca sampai habis",
                  "## 13. Yang kamu kira sebelum mulai"):
        assert judul in isi_laporan, f"TEST_REPORT.md kehilangan bagian: {judul}"

    for kata in KATA_TERLARANG:
        gabungan = (isi_prompt + isi_laporan).lower()
        assert kata.lower() not in gabungan, (
            f"Templat memuat kata '{kata}'. Prompt ini tidak boleh menyebut "
            f"cacat yang sudah kita ketahui — kalau disebut, yang diuji "
            f"berubah jadi kemampuan agen mengiyakan kita."
        )

    print(f"PASS: templat berisi ({n_tugas} tugas mikro, "
          f"{n_bagian} bagian laporan, {n_baris_prompt}/{n_baris_laporan} baris)")

    # --- Bagian 1: hasil init test masuk ke .agents/test_history/ dan jalur mutlak disisipkan ---
    with tempfile.TemporaryDirectory() as tmp:
        env = dict(os.environ)
        env["PYTHONPATH"] = str(REPO / "src") + os.pathsep + env.get("PYTHONPATH", "")
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        hasil = subprocess.run(
            [sys.executable, "-B", "-m", "snowline.cli", "init", "test"],
            cwd=tmp, capture_output=True, text=True, env=env, timeout=60,
        )
        assert hasil.returncode == 0, f"init test gagal: {hasil.stderr}"

        # 1. Pastikan TIDAK ADA berkas uji ditulis ke akar proyek
        root_test = Path(tmp) / "SNOWLINE_TEST.md"
        root_report = Path(tmp) / "TEST_REPORT.md"
        assert not root_test.exists(), "SNOWLINE_TEST.md ditulis di akar proyek! Seharusnya di .agents/test_history/"
        assert not root_report.exists(), "TEST_REPORT.md ditulis di akar proyek! Seharusnya di .agents/test_history/"

        # 2. Cari folder di .agents/test_history/
        today_str = datetime.now().strftime("%Y-%m-%d")
        history_dir = Path(tmp) / ".agents" / "test_history" / f"{today_str}_1"
        assert history_dir.exists(), f"Folder riwayat uji tidak ditemukan: {history_dir}"

        # 3. TEST_REPORT.md harus identik bita per bita dengan templatnya
        copied_report = history_dir / "TEST_REPORT.md"
        assert copied_report.exists()
        assert copied_report.read_bytes() == src_laporan.read_bytes(), "TEST_REPORT.md tidak identik bita per bita dengan templat"

        # 4. SNOWLINE_TEST.md harus menyisipkan jalur mutlak nyata dan menghapus {{JALUR_LAPORAN}}
        copied_test = history_dir / "SNOWLINE_TEST.md"
        assert copied_test.exists()
        test_bytes = copied_test.read_bytes()
        assert b"{{JALUR_LAPORAN}}" not in test_bytes, "Penanda {{JALUR_LAPORAN}} masih tersisa di SNOWLINE_TEST.md!"
        
        expected_abs_path = str(copied_report.resolve())
        expected_test_bytes = src_prompt.read_bytes().replace(b"{{JALUR_LAPORAN}}", expected_abs_path.encode("utf-8"))
        assert test_bytes == expected_test_bytes, "SNOWLINE_TEST.md tidak cocok dengan substitusi jalur mutlak yang diharapkan"

        # 5. Verifikasi jalur mutlak yang tercetak benar-benar ada di disk
        test_text = copied_test.read_text(encoding="utf-8")
        match = re.search(r"Tuangkan semuanya ke `([^`]+)`", test_text)
        assert match, "Pola 'Tuangkan semuanya ke `...`' tidak ditemukan di SNOWLINE_TEST.md"
        embedded_path = Path(match.group(1))
        assert embedded_path.exists(), f"Jalur yang disisipkan ({embedded_path}) tidak benar-benar ada di disk!"
        assert embedded_path.resolve() == copied_report.resolve(), f"Jalur yang disisipkan ({embedded_path}) tidak menunjuk ke {copied_report}"

        print("PASS: hasil init test menyisipkan jalur mutlak yang nyata di disk dan identik bita dengan templat (setelah substitusi penanda)")


if __name__ == "__main__":
    test_init_test_content()
    print("\nINIT TEST CONTENT OK!")
