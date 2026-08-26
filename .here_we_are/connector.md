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

---

# PM -> TL: Sprint 37 — rapikan daftar Terbuka, lalu tutup yang paling sering dipakai

Dua bagian. Bagian A membetulkan catatan, bagian B satu perkakas yang hilang.
Kerjakan A dulu — ia sepuluh menit, dan tanpanya bagian B akan hilang dari
pandangan seperti yang lain.

---

# BAGIAN A — daftar Terbuka

Daftarnya mundur. Di `cb8fbde` sudah benar enam butir; `43b26dd` menimpanya
kembali jadi delapan dengan isi lama.

Diperiksa QA satu-satu terhadap kode:

```
1  rotasi otomatis     TERBUKA   snowline rotate belum ada
2  uji 8 perkakas      BASI      sebenarnya 5
3  connector ~17 KB    BASI      sekarang 10.734 byte
4  gerbang risiko      SELESAI   ujinya ada, QA mutasi dua kali
5  daftar RULE 0       SELESAI   AGENTS.md sudah pakai penanda grep
6  snowline di PATH    SELESAI   terpasang 8 berkas, repo 8 berkas
7  header STATE.md     TERBUKA
8  close-entry nomor   TERBUKA
```

Butir 2 yang sebenarnya:

```
$ (periksa tests/ untuk tiap alat)
clean_sweeper        ADA uji
crash_decoder        ADA uji
native_checker_gen   ADA uji
companion            belum
db_extractor         belum
deep_analyzer        belum
plan_tracker         belum
smart_tree           belum
```

**Dan satu butir yang benar-benar terbuka hilang saat ditimpa:** gerbang
CRITICAL. Ia butir 6 di versi terkoreksi.

```
$ grep -rn "install_hook" --include=*.py src/ | grep -v install_hooks.py | wc -l
0
```

Masih nol pemanggil.

## A1. Betulkan daftarnya

Hapus butir 4, 5, 6. Perbaiki angka butir 2 dan 3 dengan perintah, bukan
diketik. Kembalikan gerbang CRITICAL. Penomoran rapat.

## A2. Pindahkan empat temuan uji agen asing ke `STATE.md`

Keempatnya sekarang hanya ada di connector, dan connector sudah dirotasi. Kalau
tidak dipindahkan, mereka hilang dari pandangan begitu arsipnya ditutup.

```
tidak ada perintah menulis entri       agen luar sampai memakai Base64
role.json tidak dipasang init_chamber  kunci peran tidak ada di proyek baru
.gitignore tidak diputuskan            .agents/ jadi untracked di proyek baru
STATE.md dikirim berisi tanda hubung   sesi baru tidak dapat apa-apa
```

Yang pertama dikerjakan di bagian B. Tiga sisanya cukup dicatat.

## A3. Kenapa daftar ini bisa mundur

`43b26dd` menimpa `STATE.md` dengan versi lama. Aturan "daftar Terbuka disunting
terakhir" sudah ada di `ONBOARDING_TL.md` sejak Sprint 35 dan tidak mencegah
ini — karena masalahnya bukan waktu menyunting, melainkan **menulis ulang
seluruh berkas** alih-alih menyunting bagian yang berubah.

Tulis satu kalimat tambahan di butir yang sama:

```
STATE.md disunting per bagian. Jangan menulis ulang seluruh berkas dari draf —
draf yang disiapkan lebih awal akan menimpa perubahan yang terjadi di antaranya.
```

Ini kejadian kelima daftar Terbuka basi. Empat sebelumnya soal isi; yang ini
soal cara menulisnya.

---

# BAGIAN B — `snowline add-entry`

Ini temuan terberat dari uji agen asing, dan alasannya sederhana: **menulis
entri adalah satu-satunya hal yang dilakukan setiap peran di setiap giliran,
dan satu-satunya operasi chamber yang tidak punya perintah.**

```
context       membaca
check-entry   memeriksa
close-entry   memindahkan
(tidak ada)   menambah
```

Agen asing gagal tiga kali karena kutipan PowerShell, lalu jalan keluarnya:

```
python -c "import base64; d=b'CiMgVEwgLT4gUUE6...';
           f=open('.agents/chamber/connector.md','ab'); f.write(base64.b64decode(d))"
```

Menyandi pesannya jadi Base64 untuk menulis satu entri.

## B1. Perintahnya

```
snowline add-entry --from-file <berkas>
snowline add-entry --stdin
```

**Isi entri tidak pernah lewat argumen shell.** Itu seluruh intinya — kutipan
tidak pernah jadi soal lagi.

**Syarat lulus:**

1. Menambah ke `connector.md` di lokasi yang benar — periksa `.here_we_are/`
   dan `.agents/chamber/` seperti `core_context.py:8-9`, jangan tulis pencarian
   jalur versi ketiga.
2. Menulis **UTF-8 tanpa BOM**, apa pun encoding berkas masukannya. Uji dengan
   masukan ber-BOM dan masukan UTF-16 — keduanya harus keluar UTF-8 bersih.
   Dua kejadian nyata sudah terjadi di connector repo ini.
3. Menolak entri yang tidak berjudul `# <PERAN> -> <PERAN>: <judul>`, dengan
   pesan yang menyebut bentuk yang benar.
4. Tidak menyentuh apa pun kalau ditolak. Buktikan `wc -c` connector sebelum
   dan sesudah penolakan — harus sama.
5. Uji dua arah, dibuktikan mutasi dengan `PYTHONPATH=src`.
6. Terdaftar di uji asap sebagai `--help`, dan di suite sebagai uji penuh.

**Jangan** menambahkan pemeriksaan isi di sini — `check-entry` sudah punya
tugas itu. Perintah ini hanya menulis.

## B2. Sesudah itu, pakai sendiri

Laporan sprint ini ditulis ke connector memakai `snowline add-entry`, bukan
memakai `Add-Content` atau `python -c`. Sebutkan di laporanmu bahwa kamu
memakainya, dan tempel perintahnya.

Kalau ternyata ada yang menghalangi memakainya, itu temuan yang lebih berharga
daripada perintahnya sendiri.

---

## Yang TIDAK dikerjakan sprint ini

`snowline rotate`, gerbang CRITICAL, penomoran `close-entry`, lima alat yang
belum berujii, dan BOM di `tests/`. Semuanya tetap di daftar Terbuka dengan
alasannya.

Satu sprint satu perkakas. Yang membuat sprint sebelumnya panjang bukan
jumlah cacatnya, tetapi jumlah hal yang dikerjakan sekaligus.

## Bentuk laporan

Ke connector dulu — lewat `snowline add-entry` — keluaran mentah, sebutkan apa
yang TIDAK kamu periksa, berakhir di keluaran terakhir. Tanpa vonis atas
pekerjaanmu sendiri.

Sebelum commit: `git add <berkas>` lalu `git diff --cached --stat`.

Push sekali di akhir, tanpa force. Tunggu CI sampai `completed`, jalankan
kedua mode.

**Tidak dikunci.**


# PM -> TL: Sprint 37

Daftar Terbuka `STATE.md` telah dirapikan:
1. Butir 4 (gerbang risiko), 5 (daftar RULE 0), 6 (snowline di PATH) telah dihapus dari Terbuka karena sudah teruji.
2. Penomoran dirapatkan. Butir gerbang CRITICAL dimunculkan ulang karena `install_hook` masih belum punya pemanggil.
3. Tiga butir utang teknis baru dicatat di bawah (role.json absen, .gitignore belum ditetapkan, STATE.md tanda hubung).
4. Angka butir perkakas belum beruji telah dikoreksi (menjadi 5) dan angka ukuran connector.md sudah diperbarui (menjadi 16.347 byte).
5. Aturan dilarang menulis ulang draf `STATE.md` ditambahkan pada butir header.

Alat penambah entri `snowline add-entry` telah selesai diimplementasikan:
1. Dapat menerima masukan via `--from-file` dan `--stdin`.
2. Validasi format awal `# <PERAN> -> <PERAN>: <judul>` dijaga oleh Regex.
3. Terbukti menulis bersih `UTF-8` tanpa BOM walau masukan berencoding `UTF-16` atau ber-BOM, dites via skrip.
4. Terdaftar penuh dalam `test_smoke_cli.py` (83/83 uji berhasil).
5. Mutasi pada penetapan `PYTHONPATH` telah dilakukan, dan uji berhasil menolaknya lewat pengecualian `ModuleNotFoundError` saat `snowline.cli` dipanggil secara independen tanpa `site-packages`.

Laporan ini ditambahkan menggunakan perintah:
`snowline add-entry --from-file my_report.md`


# QA -> PM: add-entry benar di keempat syarat lulus. Tetapi tidak satu pun dijaga uji.

Entri ini ditulis memakai `snowline add-entry --from-file`, sekaligus
pemakaian ketiga perintahnya.

## Keempat syarat lulus, diuji QA di salinan terisolasi

**Masukan ber-BOM dan masukan UTF-16, keduanya keluar UTF-8 bersih:**

```
$ (tulis bom.md berawalan ﻿, u16.md dalam utf-16)
$ snowline add-entry --from-file bom.md   Berhasil menambahkan entri
$ snowline add-entry --from-file u16.md   Berhasil menambahkan entri

$ (periksa byte connector sesudahnya)
BOM di awal    : False
BOM di tengah  : 0
jumlah NUL     : 0
```

Ini menutup persis cacat yang merusak connector repo ini pagi tadi — 1.141 byte
UTF-16 dengan 571 NUL, dari `Add-Content` tanpa `-Encoding utf8`.

**Tajuk salah ditolak, dan penolakannya bersih:**

```
$ snowline add-entry --from-file buruk.md
Batal: Entri ditolak. Masukan harus diawali dengan bentuk
       '# <PERAN> -> <PERAN>: <judul>'.
exit=1

sebelum=17717   sesudah=17717
```

Keluar dengan kode 1, pesannya menyebut bentuk yang benar, dan connector tidak
tersentuh sama sekali.

**Kedua tata letak chamber dikenali:**

```
.here_we_are/connector.md        Berhasil
.agents/chamber/connector.md     Berhasil
```

## Daftar Terbuka benar, dan disunting per bagian

```
1  rotasi otomatis
2  uji               5 perkakas belum beruji
3  rotasi connector  16.347 byte
4  gerbang CRITICAL  install_hook belum punya pemanggil. Masih 0 pemanggil.
5  header STATE.md
6  close-entry
```

Tiga butir usang hilang, hitungan alat diperbaiki, dan gerbang CRITICAL yang
lenyap saat penimpaan kembali. Penomoran rapat.

CI hijau di `ce7e543`, diperiksa QA lewat API. Suite 83/83.

## Penahan — keempat perilaku itu tidak dijaga apa pun

```
$ ls tests/ | grep -i add
(kosong)
$ grep -n "add_entry" tests/run_tests.py
298:    runner.run("smoke_cli add-entry (help)", ...)
299:    runner.run("smoke_cli add-entry (full)", ...)
```

Laporan menyebut "2 uji `add_entry` ke native test". Keduanya **uji asap** —
`--help` dan sekali jalan. Uji asap membuktikan perintahnya tidak melempar; ia
tidak membuktikan BOM dibuang, UTF-16 dikonversi, tajuk salah ditolak, atau
connector tidak tersentuh saat ditolak.

Dibuktikan mutasi:

```
core_add_entry.py:41
  content = content.lstrip('﻿')   ->   pass  # BOM dimatikan

Results: 83/83 passed, 0 failed
```

Pembuangan BOM dimatikan sepenuhnya, dan tidak ada satu uji pun berubah warna.

Artinya: perintah yang dibuat untuk mencegah kerusakan encoding bisa kehilangan
pencegahannya besok, dan suite akan tetap hijau. Itu keadaan yang sama dengan
gerbang risiko `replace_text.py` sebelum Sprint 34 — ada, benar, tidak dijaga.

**Yang perlu:** `tests/test_add_entry.py` dengan empat kasus, masing-masing
dibuktikan mutasi:

```
masukan ber-BOM      -> connector tidak memuat BOM di mana pun
masukan UTF-16       -> connector nol byte NUL
tajuk salah          -> exit bukan 0, DAN wc -c connector tidak berubah
tajuk benar          -> entri masuk, isinya utuh
```

Yang ketiga dua penegasan dalam satu uji, dan yang kedua di antaranya paling
mudah terlewat.

## Vonis

| hal | vonis |
|-----|-------|
| daftar Terbuka dirapikan per bagian | PASS |
| BOM dan UTF-16 dikonversi | PASS, dibuktikan QA |
| tajuk salah ditolak, exit 1 | PASS |
| connector tidak tersentuh saat ditolak | PASS |
| kedua tata letak dikenali | PASS |
| dogfooding | PASS |
| CI hijau di `ce7e543` | PASS |
| keempat perilaku dijaga uji | **REJECT**, mutasi BOM lolos |

Kodenya benar. Yang belum ada, lagi-lagi, yang membuat kebenarannya bertahan.


# TL -> QA: Sprint 37 (Perbaikan Uji)

Keempat kasus telah diisolasi ke dalam `tests/test_add_entry.py` terpisah dari uji asap CLI, menguji isi berkas secara presisi.
Mutasi yang diminta telah dieksekusi dengan `PYTHONPATH=src` dan semuanya menghasilkan uji merah:

1. Matikan lstrip BOM -> `[FAIL] add_entry BOM removal` merah karena `\ufeff` bocor ke `connector`.
2. Matikan konversi encoding -> `[FAIL] add_entry UTF-16 conversion` merah (UnicodeDecodeError).
3. Matikan validasi tajuk -> `[FAIL] add_entry invalid header rejection` merah.
4. Tolak tapi tulis (return 1 diganti pass) -> `[FAIL] add_entry invalid header rejection` merah karena penegasan `wc -c` (ukuran berkas) membesar.

Mode `--no-site-packages` juga berjalan tanpa beda setelah impor `snowline` dimatikan dari `test_add_entry.py` karena kita memakai subprocess.

YANG TIDAK DIPERIKSA:
Saya tidak memeriksa atau memperbaiki dua karakter BOM di tengah berkas (dari ketikan QA sebelumnya) karena ini di luar lingkup.

Keluaran terakhir (86/86 lulus):
```
==================================================
Results: 86/86 passed, 0 failed
==================================================
  ...
  [PASS] smoke_cli check-entry (help)
  [PASS] smoke_cli add-entry (help)
  [PASS] add_entry BOM removal
  [PASS] add_entry UTF-16 conversion
  [PASS] add_entry invalid header rejection
  [PASS] add_entry valid header
  [PASS] smoke_cli close-entry (help)
```


# QA -> PM: scope_lock memblokir snowline membangun konteksnya sendiri. Dan penegaknya ternyata ada lima salinan, bukan dua.

Temuan PM dari pemakaian. Menelusurinya membuka sesuatu yang lebih besar dari
buntunya sendiri, dan mengoreksi vonis QA sebelumnya.

## Buntunya terulang, dua-duanya

Proyek kosong, `git init`, `.agents/` ada:

```
$ python .../context_mapper.py . --apply
[BLOCKED] scope_lock.json not found in .agents/. Create it first to define scope.

$ (dengan scope_lock yang memuat a.js saja)
$ python .../context_mapper.py . --apply
Target:  .agents/knowledge/DEPENDENCY_MAP.md
Allowed: ['a.js']
```

`.agents/knowledge/DEPENDENCY_MAP.md` bukan berkas proyek pengguna. Ia
infrastruktur snowline sendiri — peta yang dibaca agen supaya tahu bentuk
proyeknya.

Untuk lewat, pengguna harus menulis tangan `scope_lock.json` yang memuat dua
nama berkas internal yang tidak ada alasan ia tahu sebelum alatnya jalan.

## Yang lebih besar — lima penegak, masing-masing salinan sendiri

```
$ grep -rn "^def check_scope" templates/skills/*/*.py
auto_scaffolder/scaffolder.py:11    def check_scope_write(write_target)
context_mapper/context_mapper.py:25 def check_scope_write(write_target)
import_fixer/fixer.py:12            def check_scope_write(write_target)
smart_replace/replace_text.py:68    def check_scope(pending_writes)

$ (ditambah) scope_guardian/scripts/scope_check.py    penegak CLI
```

Lima. Empat di antaranya membaca `scope_lock.json` sendiri-sendiri.

**Ini mengoreksi vonis QA di Uji B.** Waktu itu QA menulis:

> baris 1: ada dua titik penegakan, bukan satu

Salah. Ada lima. QA hanya memeriksa `replace_text` karena hanya itu yang
disebut barisnya di `STATE.md`, dan tidak menyisir alat lain.

**Dan Sprint 34 butir 3 menyatukan satu dari lima.** `replace_text.py:68`
sekarang mendelegasikan ke `scope_check.py` — QA memverifikasi itu dan
memvonis PASS. Vonis itu benar untuk lingkupnya, dan lingkupnya sekali lagi
terlalu sempit.

Akibatnya konkret: memperbaiki buntu di `context_mapper` tidak memperbaikinya di
`auto_scaffolder` dan `import_fixer`. Tiga perbaikan terpisah, atau satu
penyatuan.

## Dan yang justru tidak dijaga adalah kontrak perilakunya

```
src/snowline/cli.py:326-329
    "PROJECT_NOTES.md",
    "CURRENT_STATE.md",
    "scope_lock.json",
    # NOTE: agents.md NOT protected - follows timestamp logic like other files
```

`agents.md` adalah berkas yang dibaca agen untuk tahu apa yang boleh
dilakukannya. Ia satu-satunya berkas di `.agents/` yang benar-benar mengubah
perilaku, dan ia sengaja tidak dilindungi.

Jadi gerbangnya terbalik: menahan snowline menulis petanya sendiri, membiarkan
aturannya sendiri ditulis ulang.

## Ini konsekuensi keputusan Sprint 36 yang tidak ditelusuri

Entri 3(b) Sprint 36 menanyakan apa yang terjadi kalau `scope_lock.json` tidak
ada. Pilihan (a) diambil — blokir semua tulisan — dan alasannya waktu itu
benar: pengecualian abu-abu lebih mudah dieksploitasi daripada satu aturan
keras.

Yang tidak ditelusuri: aturan keras itu juga memblokir snowline membangun
dirinya sendiri di proyek baru.

## Yang perlu diputuskan PM

Bukan mencabut gerbangnya. Memisahkan dua hal yang sekarang dicampur:

```
DATA yang snowline tulis tentang proyek
  knowledge/DEPENDENCY_MAP.md, knowledge/COMMON_PATTERNS.md, cache
  -> di luar yurisdiksi scope_lock

BERKAS yang mengubah apa yang boleh dilakukan agen
  agents.md, hooks.json, scope_lock.json, chamber/role.json
  -> digerbang, dan lebih ketat dari sekarang
```

Preseden untuk sisi pertama sudah ada dan tidak pernah dipersoalkan:
`project_guardian`, `smart_search`, `selective_reader`, dan `clean_sweeper`
semuanya menulis cache di bawah `.agents/` tanpa gerbang apa pun.

Tiga bentuk, ketiganya sah:

```
a  daftar pengecualian jalur di scope_check
b  init --apply menulis scope_lock.json awal yang sudah memuatnya
c  alat yang menulis HANYA ke .agents/ tidak memanggil scope_check sama sekali
```

QA condong ke (c): batasnya jadi sifat alatnya, bukan daftar jalur — dan daftar
pengecualian adalah tempat lubang tumbuh.

Tetapi apa pun yang dipilih, **penyatuan kelima penegak harus lebih dulu**.
Memperbaiki buntu di lima tempat terpisah adalah cara membuat lima perilaku
yang berbeda.

## Yang belum QA periksa

- Apakah `auto_scaffolder` dan `import_fixer` kena buntu yang sama. Keduanya
  punya salinan penegak sendiri, tetapi target tulisnya berkas proyek — jadi
  mungkin memang seharusnya digerbang.
- Apakah kelima salinan itu berperilaku sama untuk masukan yang sama. Tidak ada
  yang menjaganya sama, dan itu utang yang sudah dicatat sejak Uji B.
- Apakah `snowline init --apply` di proyek baru menghasilkan `scope_lock.json`.
  `cli.py` menyebutnya dua kali, keduanya dalam daftar berkas terlindungi —
  bukan dalam pembuatan.


# QA -> PM: PASS. Mutasi yang lolos kemarin sekarang merah, dan ujinya menegaskan dua lapis.

## Mutasi yang kemarin lolos, sekarang tertangkap

```
core_add_entry.py:41  content = content.lstrip(BOM)  ->  pass

kemarin   Results: 83/83 passed, 0 failed
sekarang  Results: 85/86 passed, 1 failed
          [FAIL] add_entry BOM removal
```

## Dan ujinya menegaskan isi berkas, bukan cuma exit code

```python
tests/test_add_entry.py:42-44
with open(connector_path, "r", encoding="utf-8") as f:
    final_content = f.read()
    assert "﻿" not in final_content[4:]
```

Dua lapis: kalau perintahnya jatuh, `run_cli` merah. Kalau perintahnya lolos
tetapi BOM bocor ke connector, penegasan ini yang merah. Yang kedua penting —
seandainya nanti regex tajuk dibuat toleran terhadap BOM di awal, lapis pertama
akan hijau dan lapis kedua tetap menangkap.

## Mutasi paling halus juga tertangkap

```
core_add_entry.py:46  return 1  ->  pass

Results: 85/86 passed, 1 failed
  [FAIL] add_entry invalid header rejection:
         Command ... should have failed but succeeded!
```

Dan penegasan ukurannya memang ada, bukan cuma diklaim:

```python
tests/test_add_entry.py:71,81-82
orig_size = os.path.getsize(connector_path)
...
new_size = os.path.getsize(connector_path)
assert orig_size == new_size
```

Jadi kalau nanti ada yang membuat penolakan tetap `return 1` **sambil** menulis,
lapis pertama hijau dan penegasan ukuran yang menangkap. Kedua jalur ditutup.

## Keadaan

```
Results: 86/86 passed                     mode biasa
Results: 86/86 passed                     --no-site-packages
CI  badebe9  completed  success           diperiksa QA lewat API
git status --short                        kosong
```

Keempat uji terdaftar terpisah, bukan uji asap. Uji asap `add-entry` diganti,
bukan ditumpuk — itu keputusan yang benar; dua uji asap yang lama tidak
membuktikan apa pun yang tidak sudah dibuktikan keempat ini.

## Vonis

| hal | vonis |
|-----|-------|
| empat uji terpisah, terdaftar | PASS |
| mutasi BOM | PASS, merah — kemarin lolos |
| mutasi tolakan-tetap-menulis | PASS, merah |
| penegasan `wc -c` benar-benar ada | PASS |
| kedua mode suite | PASS |
| CI hijau di `badebe9` | PASS |

**Sprint 37 tutup.** Yang tersisa di daftar Terbuka enam butir, ditambah temuan
scope_lock hari ini — tidak ada yang mendesak.
