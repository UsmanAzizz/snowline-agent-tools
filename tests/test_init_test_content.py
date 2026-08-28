"""Menjaga isi prompt `snowline init test`, bukan sekadar keberadaannya.

Sprint 42 pernah menanam prompt ini separuh: kerangkanya ada, seluruh tugas
mikronya hilang. Uji lama tetap hijau karena ia cuma memeriksa berkasnya
terbentuk dan memuat beberapa kata kunci.

Uji ini memeriksa dua hal yang berbeda:

1. Hasil `init test` sama bita per bita dengan templat yang dipaketkan.
   Menangkap init_test yang menyimpang dari templatnya.

2. Templat itu sendiri masih memuat isinya.
   Menangkap templat yang dikosongkan — kasus yang tidak akan ketahuan oleh
   perbandingan (1), karena kalau templatnya dikosongkan, hasilnya ikut kosong
   dan keduanya tetap sama.
"""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TEMPLATES = REPO / "src" / "snowline" / "test_templates"

# Diambil dari rancangan yang disepakati. Angka boleh naik kalau tugasnya
# ditambah; kalau turun, ada yang hilang.
MIN_TUGAS_MIKRO = 10
MIN_BAGIAN_LAPORAN = 12
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

    # Verifikasi 3 pertanyaan baru Sprint 47 Entri 4
    assert "Sumber catatan saat merapikan catatan proyek" in isi_laporan, "TEST_REPORT.md missing question 1 (sumber catatan)"
    assert "Pernah menunggu proses yang tidak selesai atau menggantung" in isi_laporan, "TEST_REPORT.md missing question 2 (menunggu)"
    assert "Baris penting di keluaran alat yang sempat terlewat" in isi_laporan, "TEST_REPORT.md missing question 3 (keluaran terlewat)"

    for kata in KATA_TERLARANG:
        gabungan = (isi_prompt + isi_laporan).lower()
        assert kata.lower() not in gabungan, (
            f"Templat memuat kata '{kata}'. Prompt ini tidak boleh menyebut "
            f"cacat yang sudah kita ketahui — kalau disebut, yang diuji "
            f"berubah jadi kemampuan agen mengiyakan kita."
        )

    print(f"PASS: templat berisi ({n_tugas} tugas mikro, "
          f"{n_bagian} bagian laporan, {n_baris_prompt}/{n_baris_laporan} baris)")

    # --- Bagian 1: hasil init test identik dengan templatnya ---
    with tempfile.TemporaryDirectory() as tmp:
        env = dict(os.environ)
        env["PYTHONPATH"] = str(REPO / "src") + os.pathsep + env.get("PYTHONPATH", "")
        hasil = subprocess.run(
            [sys.executable, "-m", "snowline.cli", "init", "test"],
            cwd=tmp, capture_output=True, text=True, env=env, timeout=60,
        )
        assert hasil.returncode == 0, f"init test gagal: {hasil.stderr}"

        for nama, sumber in (("SNOWLINE_TEST.md", src_prompt),
                             ("TEST_REPORT.md", src_laporan)):
            keluaran = Path(tmp) / nama
            assert keluaran.exists(), f"{nama} tidak terbentuk"
            a = keluaran.read_bytes()
            b = sumber.read_bytes()
            if a != b:
                baris_a = a.decode("utf-8", "replace").split("\n")
                baris_b = b.decode("utf-8", "replace").split("\n")
                beda = "(panjangnya berbeda saja)"
                for i in range(min(len(baris_a), len(baris_b))):
                    if baris_a[i] != baris_b[i]:
                        beda = (f"baris {i+1}:\n"
                                f"  hasil  : {baris_a[i][:70]!r}\n"
                                f"  templat: {baris_b[i][:70]!r}")
                        break
                raise AssertionError(
                    f"{nama} hasil init test tidak sama dengan "
                    f"{sumber} ({len(baris_a)} vs {len(baris_b)} baris). {beda}"
                )

        print("PASS: hasil init test identik bita per bita dengan templatnya")


if __name__ == "__main__":
    test_init_test_content()
    print("\nINIT TEST CONTENT OK!")
