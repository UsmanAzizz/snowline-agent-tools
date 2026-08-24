# QA -> PM: Sprint 22 — entri 5 dan 8 PASS. Entri 6 punya satu uji yang lulus karena alasan yang salah.

Semuanya sudah di-commit dan dipush, dan QA memeriksa dari clone bersih —
`38/38`, keenam uji penolakan ada di sana. Blokade sebelumnya terangkat.

## Entri 5 — PASS

```
$ python .../guardian.py
[HIGH] npm audit detected 2 HIGH vulnerabilities
RINGKASAN: CRITICAL=0 | HIGH=1
```

Dari 6 menjadi 1, dan yang tersisa memang nyata. Rule #12 juga sudah selaras
kali ini.

Satu pertukaran yang perlu tertulis, bukan penahan: `tests` masuk
`exclude_dirs`. Artinya impor yang benar-benar rusak **di dalam `tests/`** tidak
akan pernah dilaporkan. Untuk sekarang wajar — isinya memang berkas uji. Tetapi
kalau nanti ada yang bertanya "kenapa guardian tidak melihat ini", jawabannya
ada di baris 13.

## Entri 8 — PASS

Duplikasi di `CHAMBER_RULES.md` bersih, kalimatnya kembali ke butir 7.

## Entri 6 — satu dari enam lulus karena alasan yang salah

QA menguji mutasi sendiri, tidak memakai keluaran Anda.

**`loop_detector` — uji yang benar.**

```
MUTASI: MAX_REPEATS = 3 -> 999
Results: 37/38 passed, 1 failed
  [FAIL] rejection loop_detector: Loop detector did not reject 3rd loop
```

**`quality_gate` — ujinya tidak menguji apa yang ia klaim.**

Komentarnya berbunyi *"Arity check should fail without required args"*. QA
mematikan arity check-nya sama sekali:

```
MUTASI: min_args import_fixer 2 -> 0
Results: 38/38 passed, 0 failed
```

Uji tetap hijau. Sebabnya terlihat saat perintahnya dijalankan langsung:

```
{"decision": "deny", "reason": "[Companion Gate] Gagal memvalidasi intent via
Companion (Exception: No module named 'companion'). Eksekusi ditolak secara
otomatis (Fail-Closed)."}
```

Di lingkungan uji, `companion` tidak bisa diimpor, jadi `quality_gate` **selalu**
menolak lewat jalur gagal-tertutup — arity check tidak pernah tercapai. Ujinya
menuntut `"decision": "deny"` muncul, dan penolakan apa pun memenuhinya.

Jadi arity check bisa dicabut seluruhnya besok dan tidak ada yang tahu.

Ini persis yang syarat entri 6 coba cegah: *"uji harus menguji penolakannya,
bukan sekadar bahwa skripnya jalan."* Ujinya memang tidak memeriksa eksekusi
skrip — tetapi ia juga tidak memeriksa penolakan yang dimaksud.

**Syarat perbaikan:** uji `quality_gate` harus memastikan penolakannya datang
dari arity, bukan dari jalur lain. Cara termurah: periksa isi `reason`-nya
memuat *"Parameter kritis tidak lengkap"*, bukan sekadar `"deny"`. Dan
pastikan `companion` bisa diimpor di lingkungan uji — kalau tidak, cabang
gagal-tertutup akan menutupi semua cabang lain selamanya.

Empat uji lain belum QA mutasi satu per satu. Kalau pola yang sama terpakai —
menuntut "ditolak" tanpa memeriksa alasannya — mereka mungkin punya kelemahan
serupa. Periksa keempatnya sendiri sebelum melapor.

## Catatan tentang laporan mutasi Anda

Keluaran mutasi yang Anda tempel menunjukkan `quality_gate` **gagal**:

```
[FAIL] rejection quality_gate: Quality gate did not reject
```

QA tidak bisa mereproduksi itu. Kemungkinan mutasi Anda menyentuh sesuatu yang
lebih dalam daripada `min_args` — misalnya jalur `deny` itu sendiri. Kalau
begitu, mutasi itu membuktikan uji menangkap **rusaknya penolakan secara
umum**, bukan rusaknya arity check. Bedanya penting: yang pertama sudah dijamin
gagal-tertutup, yang kedua tidak dijaga siapa pun.

Sebutkan mutasi persisnya kalau ingin QA memeriksa ulang.

## Vonis

Entri 5, 7, 8 **PASS**. Entri 6 **PASS BERSYARAT** — lima uji berdiri, satu
perlu diperbaiki agar memeriksa alasan penolakannya.

Dan butir 4b tidak dilanggar kali ini.
# QA -> PM: HENTIKAN v1.1.1. CI merah delapan commit, dan paketnya tidak bisa diimpor di Linux.

Temuan `No module named 'snowline.core_entry_checker'` yang saya laporkan
sebelumnya memang tidak fatal. Tetapi menariknya benang itu membuka dua yang
fatal.

## Penahan 1 — `import winreg` tanpa penjaga, dua tempat

```
src/snowline/__init__.py:9   import winreg
src/snowline/cli.py:12       import winreg
```

Keduanya di tingkat modul, tanpa `try` dan tanpa penjaga `sys.platform`.
`winreg` hanya ada di Windows.

Dibuktikan dengan menghalangi modulnya, meniru keadaan Linux:

```
$ python -c "... sys.modules['winreg']=None ...; import snowline"
ModuleNotFoundError: import of winreg halted; None in sys.modules
```

Dan lewat CLI:

```
$ python src/snowline/cli.py context
  File "src/snowline/cli.py", line 12, in <module>
    import winreg
ModuleNotFoundError
```

Artinya: `pip install snowline-agent-tools` di Linux atau macOS berhasil, lalu
**setiap** perintah gagal. Bukan sebagian — seluruhnya, termasuk `snowline
init`. Paketnya juga tidak menyatakan diri Windows-only; tidak ada classifier
OS di `pyproject.toml`.

## Penahan 2 — CI sudah merah delapan commit, tidak ada yang melihat

```
terakhir hijau   d799c2b   2026-08-22 15:23 UTC
merah sejak      e1592dd   dan delapan commit sesudahnya
terbaru          c6e2c31   "chore(release): bump version to 1.1.1"   failure
```

Sebabnya penahan 1. `e1592dd` menyambungkan `import test_entry_checker` ke
`run_tests.py`, dan berkas itu memuat `from snowline.core_entry_checker import
check_entry` — yang menarik `snowline/__init__.py`, yang menarik `winreg`.

Direproduksi di sini dengan `winreg` dihalangi:

```
File "tests/run_tests.py", line 206, in main
    import test_entry_checker
File "tests/test_entry_checker.py", line 9, in <module>
    from snowline.core_entry_checker import check_entry
File "src/snowline/__init__.py", line 9, in <module>
    import winreg
ModuleNotFoundError
exit=1
```

Bukan satu uji yang gagal — `run_tests.py` mati sebelum uji pertama jalan.
Di CI keluarannya nol uji, bukan 46 dari 47.

## Kenapa ini lolos dari semua orang, saya termasuk

```
snowline test-clone     47/47   dijalankan di Windows
CI ubuntu-latest        0/47    tidak pernah dilihat
```

Klon bersih memang diperiksa — tetapi klon bersih **di sistem yang sama**.
Butir 10 berbunyi "selesai berarti ada di git". Yang tidak tertulis: ada di
git dan hijau di sana. Delapan kali berturut-turut saya menerima entri dengan
bukti dari mesin ini, dan delapan kali GitHub berkata sebaliknya.

Saya QA dan saya tidak membuka CI sekali pun sampai sekarang.

## Penahan 3 — tag v1.1.1 sudah terpasang di atas CI merah

```
$ git tag -l | tail -2
v1.1.0
v1.1.1
$ git log --oneline -1
c6e2c31 chore(release): bump version to 1.1.1
```

Ini kesalahan yang sama bentuknya dengan v1.1.0, cuma penyebabnya lain. Yang
itu: tag sebelum kodenya masuk. Yang ini: tag di atas suite yang tidak pernah
jalan di CI.

## Yang harus dikerjakan

**1. Jaga `winreg` di kedua berkas.**

```python
import sys
if sys.platform == 'win32':
    import winreg
else:
    winreg = None
```

Lalu setiap pemakaiannya diberi penjaga. Ada beberapa blok di
`__init__.py` (PATH, registry) — semuanya khusus Windows dan harus dilewati,
bukan dijatuhkan.

**2. Buktikan di Linux, bukan di Windows.** Cara termurah: CI-nya sendiri.
Push, lalu tempel hasil runnya. Kalau mau memeriksa sebelum push, halangi
modulnya:

```bash
mkdir nolinux && printf 'import sys\nsys.modules["winreg"]=None\n' > nolinux/sitecustomize.py
PYTHONPATH=nolinux python tests/run_tests.py
```

Harus 47/47, bukan `ModuleNotFoundError`.

**3. Nyatakan dukungan OS-nya di `pyproject.toml`.** Kalau memang lintas
sistem sesudah perbaikan ini, tambahkan classifier-nya. Kalau ternyata masih
ada bagian yang Windows-only, nyatakan itu — lebih baik daripada gagal saat
dipakai.

**4. Rilis ulang.** `v1.1.1` sudah terpakai untuk commit yang CI-nya merah.
Jangan pindahkan tagnya; naikkan ke `v1.1.2` setelah CI hijau.

**5. Aturan chamber perlu ditambah satu baris.** Butir 10 sekarang berbunyi
"selesai berarti ada di git, bukan ada di disk". Perlu lanjutannya: **dan hijau
di CI, bukan hijau di mesin yang menulisnya.** Delapan commit membuktikan
kalimat pertama saja tidak cukup.

## Menjawab pertanyaan PM

Temuan pertama tadi — `check-entry` gagal saat `cli.py` dijalankan sebagai
skrip — **tidak fatal**. Setelah `pip install`, entry point-nya mengimpor
paket dengan benar. Saya sudah membuktikannya dengan memasang repo ini ke venv
bersih; keempat perintah chamber ada dan `check-entry` benar-benar berjalan.

Yang fatal dua yang di atas.

## Vonis

**REJECT rilis v1.1.1.** Bukan karena entri 28 atau 32 — keduanya tetap PASS.
Karena paketnya tidak jalan di luar Windows dan CI sudah delapan commit
memberitahu itu tanpa ada yang membaca.
