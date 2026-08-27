"""
Uji jalur --apply pada smart_replace.

Jalur ini yang paling mahal kalau rusak, dan yang paling lama tidak ketahuan:
`validate_syntax` hanya dipanggil ketika --apply diberikan, sehingga cacat di
dalamnya tidak pernah muncul di mode dry-run. Dua cacat nyata pernah lolos ke
sini — `import os` di dalam fungsi yang membuat UnboundLocalError, dan berkas
sementara yang dilinting di %TEMP% sehingga ESLint tidak pernah menemukan
konfigurasi project.

Uji di berkas ini menjalankan skripnya sungguhan lewat subprocess, bukan
mengimpor fungsinya. Kedua cacat itu hanya terlihat dari ujung ke ujung.
"""
import os
import sys
import json
import glob
import shutil
import tempfile
import subprocess
from pathlib import Path

AKAR = Path(__file__).parent.parent
SKRIP = AKAR / "src" / "snowline" / "templates" / "skills" / "smart_replace" / "replace_text.py"


class ProyekUji:
    """Direktori project sementara berisi .agents/scope_lock.json."""

    def __init__(self, berkas, allowed_files=None, created_at=None, dengan_lock=True):
        self.berkas = berkas
        self.allowed_files = allowed_files
        self.created_at = created_at
        self.dengan_lock = dengan_lock

    def __enter__(self):
        self.dir = tempfile.mkdtemp(prefix="snowline_uji_")
        for nama, isi in self.berkas.items():
            jalur = os.path.join(self.dir, nama)
            os.makedirs(os.path.dirname(jalur), exist_ok=True)
            with open(jalur, "w", encoding="utf-8") as f:
                f.write(isi)

        # Buat dummy linter untuk mempercepat pengujian (melewati npx yang lambat)
        dummy_linter_dir = os.path.join(self.dir, "node_modules", ".bin")
        os.makedirs(dummy_linter_dir, exist_ok=True)
        dummy_linter_path = os.path.join(dummy_linter_dir, "eslint.cmd" if sys.platform == "win32" else "eslint")
        
        dummy_script = """@echo off
if "%~1"=="-v" (
    echo v8.0.0
    exit /b 0
)
if exist "eslint.config.mjs" (
    exit /b 0
) else (
    echo failed to load config
    exit /b 1
)
""" if sys.platform == "win32" else """#!/bin/sh
if [ "$1" = "-v" ]; then
    echo "v8.0.0"
    exit 0
fi
if [ -f "eslint.config.mjs" ]; then
    exit 0
else
    echo "failed to load config"
    exit 1
fi
"""
        with open(dummy_linter_path, "w", encoding="utf-8") as f:
            f.write(dummy_script)
        if sys.platform != "win32":
            os.chmod(dummy_linter_path, 0o755)

        if self.dengan_lock:
            os.makedirs(os.path.join(self.dir, ".agents"), exist_ok=True)
            lock = {
                "task": "uji smart_replace",
                "allowed_files": (self.allowed_files
                                  if self.allowed_files is not None
                                  else list(self.berkas)),
                "allowed_patterns": [],
            }
            if self.created_at:
                lock["created_at"] = self.created_at
            with open(os.path.join(self.dir, ".agents", "scope_lock.json"), "w",
                      encoding="utf-8") as f:
                json.dump(lock, f)
        return self

    def __exit__(self, *_):
        shutil.rmtree(self.dir, ignore_errors=True)

    def jalankan(self, *args):
        hasil = subprocess.run(
            [sys.executable, str(SKRIP), *args],
            cwd=self.dir, capture_output=True, text=True,
        )
        return hasil

    def baca(self, nama):
        with open(os.path.join(self.dir, nama), encoding="utf-8") as f:
            return f.read()


JS_SATU_BARIS = "const namaLama = 1;\n"
PY_SATU_FUNGSI = "def fungsi_lama():\n    return 1\n"


def test_apply_js_benar_benar_menulis():
    """Cacat UnboundLocalError dan abort-karena-linter keduanya berhenti di sini."""
    with ProyekUji({"kode.js": JS_SATU_BARIS}) as p:
        h = p.jalankan(".", "namaLama", "namaBaru", "--apply")
        assert "Traceback" not in h.stdout + h.stderr, \
            f"skrip jatuh:\n{h.stdout}\n{h.stderr}"
        assert "[SUCCESS]" in h.stdout, f"tidak ada [SUCCESS]:\n{h.stdout}"
        assert "namaBaru" in p.baca("kode.js"), "berkas tidak berubah"


def test_apply_py_lewat_ast():
    """Berkas .py memakai cabang ast, bukan cabang linter."""
    with ProyekUji({"alat.py": PY_SATU_FUNGSI}) as p:
        h = p.jalankan(".", "fungsi_lama", "fungsi_baru", "--apply")
        assert "[SUCCESS]" in h.stdout, f"tidak ada [SUCCESS]:\n{h.stdout}"
        assert "fungsi_baru" in p.baca("alat.py")


def test_dry_run_tidak_menulis():
    with ProyekUji({"kode.js": JS_SATU_BARIS}) as p:
        h = p.jalankan(".", "namaLama", "namaBaru")
        assert "[DRY RUN]" in h.stdout, f"bukan dry-run:\n{h.stdout}"
        assert p.baca("kode.js") == JS_SATU_BARIS, "dry-run mengubah berkas"


def test_di_luar_scope_diperingatkan_dan_ditulis():
    """(A1.a) Berkas di luar allowed_files ditulis, dengan peringatan."""
    with ProyekUji({"kode.js": JS_SATU_BARIS}, allowed_files=["lain.js"]) as p:
        h = p.jalankan(".", "namaLama", "namaBaru", "--apply")
        assert "[WARN]" in h.stdout and "OUT OF SCOPE" in h.stdout, f"tidak ada peringatan:\n{h.stdout}"
        assert "[SUCCESS]" in h.stdout, f"seharusnya ditulis:\n{h.stdout}"
        assert p.baca("kode.js") == "const namaBaru = 1;\n", "berkas seharusnya tertulis"


def test_tanpa_scope_lock_diperingatkan_dan_ditulis():
    """(A1.f) Tanpa scope_lock.json sama sekali ditulis, dengan peringatan."""
    with ProyekUji({"kode.js": JS_SATU_BARIS}, dengan_lock=False) as p:
        h = p.jalankan(".", "namaLama", "namaBaru", "--apply")
        assert "[WARN]" in h.stdout and "scope_lock.json tidak ditemukan" in h.stdout, \
            f"tidak ada peringatan:\n{h.stdout}"
        assert "[SUCCESS]" in h.stdout, f"seharusnya ditulis:\n{h.stdout}"
        assert p.baca("kode.js") == "const namaBaru = 1;\n", "berkas seharusnya tertulis"


def test_scope_lock_basi_memperingatkan_tetapi_tidak_memblokir():
    with ProyekUji({"kode.js": JS_SATU_BARIS},
                   created_at="2020-01-01T00:00:00") as p:
        h = p.jalankan(".", "namaLama", "namaBaru", "--apply")
        assert "berumur" in h.stdout, f"tidak ada peringatan umur:\n{h.stdout}"
        assert "[SUCCESS]" in h.stdout, "umur basi seharusnya tidak memblokir"


def test_scope_lock_segar_tidak_memperingatkan():
    from datetime import datetime
    with ProyekUji({"kode.js": JS_SATU_BARIS},
                   created_at=datetime.now().isoformat(timespec="seconds")) as p:
        h = p.jalankan(".", "namaLama", "namaBaru", "--apply")
        assert "berumur" not in h.stdout, f"peringatan umur muncul padahal segar:\n{h.stdout}"


def test_berkas_sementara_tidak_tertinggal():
    """Berkas .snowline_periksa_* ditulis di direktori asli; harus dibersihkan."""
    with ProyekUji({"kode.js": JS_SATU_BARIS}) as p:
        p.jalankan(".", "namaLama", "namaBaru", "--apply")
        sisa = glob.glob(os.path.join(p.dir, "**", ".snowline_periksa_*"),
                         recursive=True)
        assert not sisa, f"berkas sementara tertinggal: {sisa}"


def _npm_tersedia():
    try:
        biner = "npm.cmd" if sys.platform == "win32" else "npm"
        h = subprocess.run([biner, "-v"], capture_output=True, shell=(sys.platform == "win32"))
        return h.returncode == 0
    except Exception:
        return False

def _linter_tersedia():
    try:
        return subprocess.run(["npx", "--yes", "eslint", "-v"],
                              capture_output=True, shell=True).returncode == 0
    except Exception:
        return False


def test_linter_menemukan_konfigurasi_project():
    """Berkas sementara harus ditulis di direktori asli, bukan di %TEMP%.

    ESLint mencari konfigurasi relatif terhadap berkas yang diperiksa. Kalau
    berkas sementara ditaruh di %TEMP%, ia tidak akan pernah menemukan
    konfigurasi project — dan validasi diam-diam turun ke bracket-balancing
    meskipun project ini punya linter yang terkonfigurasi.

    Cacat itu tidak terlihat di project tanpa konfigurasi: kedua lokasi
    sama-sama gagal. Karena itu uji ini memasang konfigurasi lebih dulu.
    """
    if not _linter_tersedia():
        return  # Tanpa ESLint, tidak ada yang bisa dibedakan di sini.

    with ProyekUji({
        "kode.js": JS_SATU_BARIS,
        "eslint.config.mjs": "export default [];\n",
    }) as p:
        h = p.jalankan(".", "namaLama", "namaBaru", "--apply")
        assert "Linter tidak terkonfigurasi" not in h.stdout, (
            "linter tidak menemukan konfigurasi project — berkas sementara "
            f"kemungkinan ditulis di luar direktori aslinya:\n{h.stdout}")
        assert "[SUCCESS]" in h.stdout, f"tidak ada [SUCCESS]:\n{h.stdout}"


def test_nama_berkas_tercetak_benar_pada_target_tunggal():
    """Saat target berupa berkas (bukan direktori), namanya harus tercetak.

    `os.path.relpath(berkas, berkas)` menghasilkan "." — jadi laporan validasi
    dulu menyebut berkasnya sebagai titik, bukan namanya.
    """
    with ProyekUji({"satu.js": JS_SATU_BARIS}) as p:
        h = p.jalankan("satu.js", "namaLama", "namaBaru", "--apply")
        assert "  - .:" not in h.stdout, f"nama berkas tercetak sebagai titik:\n{h.stdout}"
        assert "[SUCCESS]" in h.stdout, f"tidak ada [SUCCESS]:\n{h.stdout}"


def test_sintaks_rusak_membatalkan_penulisan():
    """Penggantian yang merusak kurung harus ditolak, berkas tetap utuh."""
    asli = "function a() {\n  return 1;\n}\n"
    with ProyekUji({"kode.js": asli}) as p:
        h = p.jalankan(".", "}", "", "--apply")
        assert p.baca("kode.js") == asli, \
            f"berkas berubah padahal sintaksnya rusak:\n{h.stdout}"


def test_probe_linter_dipanggil_sekali():
    """Probe (npx eslint -v) memakan waktu lama, harus dipanggil sekali saja walau mengubah banyak berkas."""
    # Kita buat 5 berkas, dan semuanya diedit
    berkas = {f"kode{i}.js": JS_SATU_BARIS for i in range(5)}
    with ProyekUji(berkas) as p:
        h = p.jalankan(".", "namaLama", "namaBaru", "--apply-validated")
        assert "[SUCCESS]" in h.stdout, f"Gagal mengubah:\n{h.stdout}"
        
        # Harus ada tepat satu "[DEBUG] Melakukan probe linter lokal/npx..."
        jumlah_probe = h.stdout.count("[DEBUG] Melakukan probe linter")
        assert jumlah_probe == 1, f"Probe dipanggil {jumlah_probe} kali (diharapkan 1 kali) pada 5 berkas."


def test_gerbang_risiko_medium_high():
    """Menguji bahwa risiko Medium/High dengan --apply diblokir, dan lolos dengan --apply-validated."""
    berkas = {f"kode{i}.js": "const lama = 1;\n" for i in range(4)}
    with ProyekUji(berkas) as p:
        # Uji tolak (menggunakan 'return' memicu is_logic, >3 file memicu is_widespread -> High Risk)
        h1 = p.jalankan(".", "lama", "return baru", "--apply")
        # Penegasan baris keluaran spesifik, bukan sekadar "[BLOCKED]" yang bisa datang dari gerbang scope
        assert "Eksekusi dengan --apply DITOLAK secara sistem untuk mencegah kerusakan." in h1.stdout, \
            f"Gerbang risiko tidak memblokir dengan pesan yang benar:\n{h1.stdout}"
        assert h1.returncode != 0, "Exit code harus bukan 0 jika diblokir gerbang risiko"
        assert p.baca("kode0.js") == "const lama = 1;\n", "Berkas tidak boleh berubah saat ditolak"

        # Uji lolos
        h2 = p.jalankan(".", "lama", "return baru", "--apply-validated")
        assert "[SUCCESS]" in h2.stdout, f"Harus lolos dengan --apply-validated:\n{h2.stdout}"
        assert "return baru" in p.baca("kode0.js"), "Berkas harus berubah saat diloloskan"



def test_scripts_lint_package_json():
    """Urutan probe prioritas package.json scripts.lint (misal oxlint)."""
    if not _npm_tersedia():
        return
    fake_linter = """import sys
if len(sys.argv) > 1:
    with open(sys.argv[1], "r", encoding="utf-8") as f:
        c = f.read()
    if "className{" in c:
        print("[PARSE_ERROR] Expected ... but found Identifier in " + sys.argv[1])
        sys.exit(1)
sys.exit(0)
"""
    with ProyekUji({
        "Component.jsx": "function App() { return <div className='container'>Hello</div>; }\n",
        "fake_oxlint.py": fake_linter,
        "package.json": json.dumps({"scripts": {"lint": f"{sys.executable} fake_oxlint.py"}}),
    }) as p:
        # A: Broken JSX ditolak
        h_a = p.jalankan(".", "className='container'", "className{getElClass('container')}", "--allow-partial-match", "--apply-validated")
        assert h_a.returncode != 0, f"Harus ditolak linter scripts.lint:\n{h_a.stdout}"
        assert "[PARSE_ERROR]" in h_a.stdout or "Syntax validation failed" in h_a.stdout
        assert "className='container'" in p.baca("Component.jsx"), "Berkas tidak boleh berubah saat sintaks rusak"

        # B: Valid JSX lolos
        h_b = p.jalankan(".", "Hello", "World", "--allow-partial-match", "--apply-validated")
        assert h_b.returncode == 0, f"Harus lolos linter scripts.lint:\n{h_b.stdout}"
        assert "World" in p.baca("Component.jsx"), "Berkas harus berubah saat sintaks valid"



def test_sunting_massal_validasi_per_berkas():
    """Validasi seluruh berkas dilakukan sebelum menulis ke disk.
    (a) 8 berkas, ke-5 rusak -> tidak ada yang ditulis, seluruh 8 berkas utuh di disk.
    (b) 8 berkas sah -> seluruh 8 berkas tertulis."""
    # Arah a: 8 berkas, ke-5 rusak
    berkas = {}
    for i in range(8):
        if i == 4:
            berkas[f"File{i}.js"] = "const broken = { TARGET;\n"
        else:
            berkas[f"File{i}.js"] = f"const val{i} = TARGET;\n"

    with ProyekUji(berkas) as p:
        h = p.jalankan(".", "TARGET", "100", "--apply-validated")
        assert h.returncode != 0, f"Harus gagal saat berkas ke-5 rusak:\n{h.stdout}"
        assert "[STOP] Validasi gagal di berkas ke-5 dari 8: File4.js" in h.stdout
        assert "Tidak ada berkas yang ditulis." in h.stdout

        # Pembuktian lewat isi berkas: SELURUH 8 berkas harus tetap utuh di disk
        for i in range(8):
            if i == 4:
                assert p.baca(f"File{i}.js") == "const broken = { TARGET;\n", f"File{i}.js harusnya utuh"
            else:
                assert p.baca(f"File{i}.js") == f"const val{i} = TARGET;\n", f"File{i}.js harusnya utuh"

    # Arah b: 8 berkas sah
    berkas_valid = {f"File{i}.js": f"const val{i} = TARGET;\n" for i in range(8)}
    with ProyekUji(berkas_valid) as p_v:
        h_v = p_v.jalankan(".", "TARGET", "100", "--apply-validated")
        assert h_v.returncode == 0, f"Harus sukses saat semua berkas sah:\n{h_v.stdout}"
        assert "[SUCCESS] Berhasil memodifikasi 8 file." in h_v.stdout
        for i in range(8):
            assert p_v.baca(f"File{i}.js") == f"const val{i} = 100;\n", f"File{i}.js harusnya tertulis"

def test_nol_kecocokan_dan_campuran():
    """(a) 0 kecocokan tidak melaporkan SUCCESS dan tidak membuat backup.
    (c) Campuran 3 berkas (2 ada kecocokan, 1 nol) -> hanya 2 yang dimodifikasi, [SUCCESS] menyebut 2."""
    # Arah a
    with ProyekUji({"coba.py": "val = 1  # AAA\n"}) as p_a:
        h_a = p_a.jalankan(".", "AAA", "BBB", "--apply-validated", "--allow-partial-match")
        assert "[SUCCESS]" not in h_a.stdout, f"0 kecocokan tidak boleh [SUCCESS]:\n{h_a.stdout}"
        assert not os.path.exists(os.path.join(p_a.dir, ".backup_replace")), "0 kecocokan tidak boleh membuat backup"
        assert p_a.baca("coba.py") == "val = 1  # AAA\n"

    # Arah c
    berkas_c = {
        "f1.py": "x = AAA\n",
        "f2.py": "x = 100 # AAA\n",
        "f3.py": "y = AAA\n"
    }
    with ProyekUji(berkas_c) as p_c:
        h_c = p_c.jalankan(".", "AAA", "BBB", "--apply-validated", "--allow-partial-match")
        assert "[SUCCESS]" in h_c.stdout, f"Harus sukses:\n{h_c.stdout}"
        assert "Berhasil memodifikasi 2 file" in h_c.stdout, f"Harus menyebut 2 file bukan 3:\n{h_c.stdout}"
        assert p_c.baca("f1.py") == "x = BBB\n"
        assert p_c.baca("f2.py") == "x = 100 # AAA\n"
        assert p_c.baca("f3.py") == "y = BBB\n"

DAFTAR = [
    ("--apply pada .js benar-benar menulis", test_apply_js_benar_benar_menulis),
    ("--apply pada .py lewat ast", test_apply_py_lewat_ast),
    ("dry-run tidak menulis", test_dry_run_tidak_menulis),
    ("berkas di luar scope diperingatkan dan ditulis", test_di_luar_scope_diperingatkan_dan_ditulis),
    ("tanpa scope_lock diperingatkan dan ditulis", test_tanpa_scope_lock_diperingatkan_dan_ditulis),
    ("scope_lock basi memperingatkan, tidak memblokir",
     test_scope_lock_basi_memperingatkan_tetapi_tidak_memblokir),
    ("scope_lock segar tidak memperingatkan", test_scope_lock_segar_tidak_memperingatkan),
    ("berkas sementara tidak tertinggal", test_berkas_sementara_tidak_tertinggal),
    ("linter menemukan konfigurasi project", test_linter_menemukan_konfigurasi_project),
    ("nama berkas benar pada target tunggal", test_nama_berkas_tercetak_benar_pada_target_tunggal),
    ("sintaks rusak membatalkan penulisan", test_sintaks_rusak_membatalkan_penulisan),
    ("probe linter hanya dipanggil sekali", test_probe_linter_dipanggil_sekali),
    ("gerbang risiko Medium/High memblokir --apply", test_gerbang_risiko_medium_high),
    ("linter scripts.lint package.json diprioritaskan", test_scripts_lint_package_json),
    ("sunting massal divalidasi per berkas", test_sunting_massal_validasi_per_berkas),
    ("nol kecocokan dan campuran berkas", test_nol_kecocokan_dan_campuran),
]

