"""smart_search tidak boleh membanjiri keluaran dengan nama berkas biner.

Ditemukan uji lapangan 28-08-2026 di proyek nyata: mencari satu kata di
`src/backend` menghasilkan 1268 baris, 460 di antaranya nama berkas gambar di
folder unggahan. Agen yang menerimanya berhenti membacanya di tengah.

Dua hal yang dijaga:

1. Berkas bukan-kode dilewati SEBELUM dibuka, dan dilaporkan sebagai satu
   angka, bukan satu baris per berkas.
2. Berkas teks yang benar-benar dilewati (terlalu besar) tetap disebut, tetapi
   daftarnya dipotong.

Arah kedua ada supaya perbaikannya tidak berubah jadi "diam saja". Berkas teks
yang tidak terbaca itu informasi; empat ratus nama gambar bukan.
"""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKRIP = (REPO / "src" / "snowline" / "templates" / "skills" / "smart_search"
         / "code_finder.py")

NL = chr(10)

# Folder sementara dibuat di drive yang sama dengan repo. code_finder memakai
# os.path.relpath dan jatuh kalau target dan cwd beda drive:
#   [ERROR] ValueError: path is on mount 'C:', start on mount 'D:'
# Itu cacat tersendiri, di luar lingkup uji ini. Dicatat 28-08-2026.
SCRATCH = REPO / "scratch"


def _proyek_dengan_aset(tmp, jumlah_gambar=120):
    src = Path(tmp) / "src"
    src.mkdir(parents=True, exist_ok=True)
    (src / "app.js").write_text(
        "const token = 1;" + NL + "function pakaiToken() { return token; }" + NL,
        encoding="utf-8")

    unggahan = src / "uploads"
    unggahan.mkdir(exist_ok=True)
    for i in range(jumlah_gambar):
        # bita biner sungguhan, bukan teks berekstensi .png
        (unggahan / ("gambar_" + str(i) + ".png")).write_bytes(
            bytes([0x89, 0x50, 0x4E, 0x47]) + os.urandom(64))
    return src


def _jalankan(target, kata):
    return subprocess.run(
        [sys.executable, str(SKRIP), str(target), kata],
        capture_output=True, text=True, timeout=120,
    ).stdout


def test_biner_tidak_membanjiri_keluaran():
    SCRATCH.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        src = _proyek_dengan_aset(tmp, jumlah_gambar=120)
        keluaran = _jalankan(src, "token")

        # Tidak satu pun nama gambar muncul di keluaran
        nama_gambar = [b for b in keluaran.split(NL) if "gambar_" in b]
        assert not nama_gambar, (
            str(len(nama_gambar)) + " nama berkas gambar muncul di keluaran. "
            "Berkas bukan-kode harus dihitung, bukan didaftar." + NL
            + NL.join(nama_gambar[:5])
        )

        # Tetapi jumlahnya dilaporkan
        assert "120 berkas bukan-kode dilewati" in keluaran, (
            "Jumlah berkas bukan-kode tidak dilaporkan. Melewatkan berkas "
            "diam-diam sama menyesatkannya dengan mendaftar semuanya." + NL
            + keluaran[-400:]
        )

        # Dan pencariannya tetap bekerja
        assert "app.js" in keluaran, "Berkas kode yang sah ikut terlewat"

        baris = len(keluaran.split(NL))
        assert baris < 60, (
            "Keluaran " + str(baris) + " baris untuk satu berkas kode dan 120 "
            "gambar. Seharusnya jauh lebih pendek."
        )
        print("PASS: 120 gambar jadi satu baris, keluaran " + str(baris) + " baris")


def test_berkas_teks_terlalu_besar_tetap_disebut():
    SCRATCH.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        src = _proyek_dengan_aset(tmp, jumlah_gambar=2)
        # Tujuh berkas teks di atas MAX_FILE_SIZE (500 KB)
        for i in range(7):
            (src / ("besar_" + str(i) + ".js")).write_text(
                "// token" + NL + ("x" * 600 * 1024), encoding="utf-8")

        keluaran = _jalankan(src, "token")

        assert "7 berkas teks dilewati" in keluaran, (
            "Berkas teks yang terlalu besar harus tetap disebut jumlahnya." + NL
            + keluaran[-400:]
        )
        contoh = [b for b in keluaran.split(NL) if "besar_" in b]
        assert len(contoh) <= 5, (
            "Daftar berkas dilewati tidak dipotong: " + str(len(contoh)) + " baris."
        )
        assert "dan 2 lainnya" in keluaran, (
            "Sisa yang dipotong harus disebut jumlahnya." + NL + keluaran[-400:]
        )
        print("PASS: 7 berkas teks dilewati -> 5 contoh + 'dan 2 lainnya'")


def test_jalur_cache_tidak_jatuh():
    """Jalan kedua memakai cache. Jalur itu punya penugasan variabel sendiri.

    Bug 28-08-2026: perbaikan kebisingan menambah penghitung `non_code`, tetapi
    cabang cache tidak pernah mengisinya. Jalan pertama lolos, jalan kedua
    jatuh dengan UnboundLocalError. Uji lama memakai folder baru tiap kali,
    jadi selalu cache miss dan tidak pernah menyentuh cabang itu.
    """
    SCRATCH.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        src = _proyek_dengan_aset(tmp, jumlah_gambar=30)

        pertama = _jalankan(src, "token")
        kedua = _jalankan(src, "token")

        for label, keluaran in (("jalan pertama", pertama), ("jalan kedua", kedua)):
            assert "Error" not in keluaran and "error:" not in keluaran.lower(), (
                label + " menghasilkan galat:" + NL + keluaran[-500:]
            )
            assert "30 berkas bukan-kode dilewati" in keluaran, (
                label + " tidak melaporkan jumlah berkas bukan-kode:" + NL
                + keluaran[-400:]
            )
            assert "app.js" in keluaran, label + " kehilangan hasil pencarian"

        print("PASS: jalur cache miss dan cache hit sama-sama utuh")


if __name__ == "__main__":
    test_biner_tidak_membanjiri_keluaran()
    test_berkas_teks_terlalu_besar_tetap_disebut()
    test_jalur_cache_tidak_jatuh()
    print(NL + "SMART SEARCH NOISE OK!")
