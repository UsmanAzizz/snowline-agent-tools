`	ext
PS> git status --short
 M .gitignore
 M tests/test_smoke_cli.py

PS> snowline test-clone
[SUCCESS] ... (Completed)

PS> git log --oneline -1
0ba9826 docs(connector): CI merah - uji asap menguji site-packages, bukan pohon kerja

PS> (Invoke-RestMethod -Uri "https://api.github.com/repos/UsmanAzizz/snowline-agent-tools/actions/runs?per_page=1").workflow_runs | Select-Object id, status, conclusion, head_commit
         id status    conclusion head_commit
         -- ------    ---------- -----------
32942705025 completed failure    @{id=0ba9826...}
`

## Pekerjaan dan Bukti

1. **Uji Asap menggunakan PYTHONPATH**: Uji diubah agar mengirim PYTHONPATH=src ke env dan mengeksekusi -m snowline.cli. Konteks diubah menggunakan cwd=tmpdir untuk menghindari terbacanya repo asli yang melebih 250 baris.
2. **Uji Mutasi Subperintah**: Saat import tempfile, subprocess, json dihapus, uji asap gagal dengan menyebut spesifik smoke_cli update (full) dan smoke_cli reinstall (full) yang terkena NameError: name 'tempfile' is not defined.
3. **Pembersihan Skrip Liar**: github_log.html dan 	ests_ast_mut.txt telah dihapus.
4. **Keputusan Berkas Hash**: .agents_md_baseline_hash dikeluarkan dari Git dan ditambahkan ke .gitignore. Alasannya, berkas ini menyimpan state instalasi template agen per mesin; melacaknya di repositori akan memicu konflik hash antar-pengembang dan tidak punya makna global.

## Yang Tidak Saya Periksa
- Saya tidak memeriksa ulang skrip luar seperti cli.py selain untuk menguji jatuhnya uji asap.


---

# QA -> PM: sebab CI merah ditemukan. `PYTHONPATH='src'` itu jalur relatif, dan uji `context` dijalankan dari tempdir.

Batas yang TL sebut — tidak bisa mengunduh log CI karena `403 Must have admin
rights` — memang nyata. Tetapi sebabnya bisa ditemukan tanpa log itu, dengan
meniru kondisi CI yang sebenarnya: **tidak ada paket terpasang.**

## Reproduksi

```
$ sitecustomize: sys.path[:] = [p for p in sys.path if "site-packages" not in p]
$ PYTHONPATH=nopkg python tests/run_tests.py

Results: 80/81 passed, 1 failed
  [FAIL] smoke_cli context (full)
```

Pesan lengkapnya:

```
Command context failed with output:
python.exe: Error while finding module specification for 'snowline.cli'
(ModuleNotFoundError: No module named 'snowline')
```

## Sebabnya dua baris yang bertabrakan

```python
tests/test_smoke_cli.py:7    env['PYTHONPATH'] = 'src' + os.pathsep + ...
tests/test_smoke_cli.py:20   run_cli(['context'], cwd=tmpdir)
```

`'src'` adalah jalur **relatif**. Saat `cwd` diganti ke tempdir, ia menunjuk
`<tmpdir>/src` — yang tidak ada. `-m snowline.cli` lalu gagal.

Sepuluh uji asap lain tetap memakai cwd repo, jadi `'src'` relatifnya kebetulan
benar di sana. Hanya `context` yang dipindah ke tempdir, dan hanya `context`
yang jatuh.

Dibuktikan dua arah, keduanya dari tempdir dengan site-packages dikeluarkan:

```
PYTHONPATH relatif    exit=1   ModuleNotFoundError: No module named 'snowline'
PYTHONPATH absolut    exit=0
```

**Perbaikan:**

```python
REPO = Path(__file__).resolve().parent.parent
env['PYTHONPATH'] = str(REPO / 'src') + os.pathsep + env.get('PYTHONPATH', '')
```

## Dan ini jebakan yang sama, dua kali dalam satu sprint

Perbaikan sprint lalu dibuat untuk menghentikan uji asap menguji paket
terpasang. Perbaikan itu sendiri **diverifikasi terhadap paket terpasang** —
81/81 di mesin ini, karena `snowline` 1.1.3 ada di site-packages dan menambal
lubang yang baru saja dibuat.

Jadi urutannya begini:

```
cacat        uji asap menguji site-packages, bukan pohon kerja
perbaikan    -m snowline.cli + PYTHONPATH=src
verifikasi   81/81 lokal        <- lulus karena site-packages, lagi
kenyataan    CI merah
```

Lokal hijau tidak bisa membedakan "kode benar" dari "site-packages menambal".
Selama itu belum berubah, setiap perbaikan di area ini akan lulus lokal dan
jatuh di CI.

**Yang menutupnya bukan kehati-hatian, tetapi satu uji.** Jalankan suite dengan
site-packages dikeluarkan, dan jadikan itu bagian dari `test-clone` atau langkah
CI tersendiri. Tiga baris:

```python
sys.path[:] = [p for p in sys.path if "site-packages" not in p]
```

Kalau ada uji yang jatuh karenanya, ia memang sedang menguji paket terpasang.

## Yang lulus

**Mutasi butir 2 kali ini benar.** Menghapus `import tempfile, subprocess,
json` membuat `smoke_cli update (full)` dan `smoke_cli reinstall (full)` merah
dengan `NameError: name 'tempfile' is not defined` — galat aslinya, bukan galat
lain. Itu meniru `b3d8568` persis, dan itu yang diminta.

**Berkas liar hilang** — `github_log.html` dan `tests_ast_mut.txt` tidak ada
lagi, dan `git status --short` bersih.

**`.agents_md_baseline_hash` diputuskan, bukan didiamkan:**

```
$ git check-ignore -v .agents_md_baseline_hash
.gitignore:31:.agents_md_baseline_hash
$ git ls-files .agents_md_baseline_hash
(kosong)
```

Alasannya disebut — berkas keadaan pemasangan lokal, berisiko bentrok
antar-mesin. Itu jawaban yang tepat untuk pertanyaan yang tiga sprint tidak
dijawab siapa pun.

## Vonis

| hal | vonis |
|-----|-------|
| mutasi uji asap | PASS, meniru `b3d8568` dengan benar |
| berkas liar dibersihkan | PASS |
| `.agents_md_baseline_hash` | PASS, diputuskan dengan alasan |
| CI merah di `9079168` | **REJECT** |
| `PYTHONPATH` relatif + `cwd=tmpdir` | **REJECT**, sebab dari yang di atas |
| verifikasi lokal atas perbaikan site-packages | **REJECT**, memakai site-packages |

Penahannya satu baris. Yang di bawahnya lebih penting: selama suite bisa lulus
dengan bantuan paket terpasang, "hijau lokal" bukan kabar apa-apa untuk area
ini.


### Laporan Perbaikan (Sprint 718417b)

Semua perbaikan telah selesai dan divalidasi.

1. **Pemilihan Mode Tanpa Site-Packages**
   Mode tanpa `site-packages` saya tanamkan langsung pada `tests/run_tests.py` melalui *flag* `--no-site-packages`. Saya memilih pendekatan ini dan menjadikannya sebagai **langkah kedua di CI**, karena hal ini membuat mode tersebut dapat dijalankan secara terpisah dari `test-clone` dan mendemonstrasikan secara eksplisit di CI bahwa *source code* lokal benar-benar digunakan. Subprocess pada `test_smoke_cli.py` kini akan menambahkan argumen `-S` apabila flag ini diaktifkan.

2. **Bukti Mode Tanpa Site-Packages (PYTHONPATH Relatif)**
   Ketika `PYTHONPATH` relatif (`'src'`), `smoke_cli context (full)` gagal menangkap modul lokal karena berada di dalam `tempdir`. Mode tanpa `site-packages` secara tepat menangkap galat `ModuleNotFoundError` ini (yang sebelumnya disembunyikan oleh instalasi global di environment lokal).
   ```text
   [FAIL] smoke_cli context (full): Command context failed with output:
   python.exe: Error while finding module specification for 'snowline.cli' (ModuleNotFoundError: No module named 'snowline')
   ```

3. **Bukti Mode Tanpa Site-Packages (PYTHONPATH Absolut)**
   Setelah memperbarui `PYTHONPATH` menjadi jalur absolut ke *root repository*:
   ```python
   REPO = Path(__file__).resolve().parent.parent
   env['PYTHONPATH'] = str(REPO / 'src') + os.pathsep + env.get('PYTHONPATH', '')
   ```
   Uji `smoke_cli context (full)` kembali lulus meskipun `site-packages` dikeluarkan.
   ```text
   [PASS] smoke_cli context (full)
   ```

4. **Status CI Terakhir**
   ```text
   name       : CI
   status     : completed
   conclusion : success
   html_url   : https://github.com/UsmanAzizz/snowline-agent-tools/actions/runs/32969641458
   ```

*Catatan: Saya tidak memverifikasi secara langsung file log asli dari GitHub Actions CI karena kendala limitasi `403 Must have admin rights`. Verifikasi ini bergantung secara penuh pada reproduksi simulasi QA di lingkup lokal serta konklusi keberhasilan `success` dari API CI di atas.*

---

# QA -> PM: PASS. Mode tanpa site-packages menangkap persis apa yang tidak bisa dilihat mode biasa.

## Bukti yang menentukan

QA mengembalikan `PYTHONPATH` ke relatif — cacat sprint lalu — lalu menjalankan
kedua mode:

```
mutasi: env['PYTHONPATH'] = str(REPO / 'src')  ->  'src'

mode normal                 Results: 81/81 passed, 0 failed
mode --no-site-packages     Results: 80/81 passed, 1 failed
                              [FAIL] smoke_cli context (full)
```

Satu mutasi, dua mode, dua jawaban berbeda. Mode biasa buta terhadapnya; mode
baru menangkapnya. Itu tepat alasan mode ini ada, dibuktikan dalam satu jalan.

Dipulihkan, `git status --short tests/` kosong.

## Rancangannya menutup kedua sisi

```python
tests/run_tests.py:8-10
if '--no-site-packages' in sys.argv:
    sys.path[:] = [p for p in sys.path if 'site-packages' not in p]
    os.environ['SNOWLINE_TEST_NO_SITE_PACKAGES'] = '1'

tests/test_smoke_cli.py:12
    cmd.append('-S')
```

Runner-nya membersihkan `sys.path` sendiri, lalu menandai lingkungan supaya
subproses uji asap ikut memakai `-S`. Keduanya perlu — membersihkan salah
satunya saja meninggalkan separuh jalur masih tertambal paket terpasang.

Dan CI menjalankan keduanya:

```yaml
- name: Run test suite (with installed packages)
- name: Run test suite (pure local tree, no site-packages)
```

Menjalankan keduanya lebih baik daripada mengganti yang lama. Yang pertama
menguji pengalaman pengguna terpasang, yang kedua menguji kode yang sebenarnya
di-commit.

## Diperiksa QA sendiri

```
mode normal                 81/81
mode --no-site-packages     81/81
CI  42c0ba5                 conclusion: success
```

## Catatan — BOM, kejadian kelima, dan penjaganya tidak menjangkau `tests/`

```
$ (pindai BOM di tests/)
  BOM: tests/run_tests.py
  BOM: tests/test_intercept_native.py
  BOM: tests/test_name_guard.py
  BOM: tests/test_orphan_guard.py

$ grep -n "Path(" tests/test_bom_guard.py
5:    src_dir = Path("src")
```

Empat berkas uji berawalan BOM, termasuk `run_tests.py` sendiri. Penjaga BOM
hanya menyisir `src/`.

Tidak merusak — Python mengimpornya tanpa masalah, dan CI hijau. Tetapi ini
kelas yang sama yang sudah lima kali muncul, dan penjaganya sudah ada; ia
hanya perlu satu direktori lagi.

Bukan penahan. Layak jadi satu baris di sprint berikutnya, bersama pekerjaan
lain — jangan jadi sprint sendiri.

## Vonis

| hal | vonis |
|-----|-------|
| `PYTHONPATH` absolut | PASS |
| mode `--no-site-packages` | PASS, runner dan subproses keduanya |
| dua langkah di CI | PASS |
| bukti dua arah | PASS, dibuktikan QA dengan mutasi |
| CI hijau di `42c0ba5` | PASS |
| BOM di `tests/` | catatan |

**PASS tanpa penahan.** Rantai yang dimulai dari `snowline update` jatuh di
proyek PM sekarang tertutup, dan yang menutupnya bukan perbaikan satu kali —
melainkan mode uji yang akan menangkap keluarga cacat yang sama besok.
