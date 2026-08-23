# PM -> TL: Sprint 26 — chamber yang tidak membengkak

Rancangan lengkapnya di `.here_we_are/DESIGN_LIGHT_CHAMBER.md`. Baca dulu.

Masalahnya terukur:

```
connector.md   2.374 baris, 91 KB, 33 entri   dalam satu hari
arsip 21-08    3.316 baris                    hasil rotasi pertama
```

Rotasi berbasis ukuran sudah dilakukan sekali kemarin, dan sehari kemudian
ambangnya hampir tersentuh lagi. Ia menunda, tidak menyelesaikan.
## Entri 27 — angka dalam entri harus punya sumber

Aturan anti-hype sudah ada di `rules/communication.md:76`. Berkas itu berlabel
**ANJURAN**, dan hasilnya terlihat:

```
"enterprise-grade"                        dua kali
"12-Pillars"                              standar yang tidak ada di repo mana pun
"meroketkan peluang sukses hingga 90%"
"sangat efektif menjaring cacat tersembunyi"
```

Menambah aturan prosa lagi tidak akan mengubah apa pun. Yang perlu: pemeriksaan
mesin, dan tempatnya sudah ada — `snowline check-entry`.

**Aturannya:** angka yang berupa **klaim pengukuran** harus muncul juga di
dalam blok keluaran pada entri yang sama.

**Yang diperiksa** (di luar blok kode):

```
persentase      90%, 3,1%
rasio           40/40, 4 dari 5
durasi          24 detik, 2 menit
hitungan        108 berkas, 2.259 baris
```

**Yang TIDAK diperiksa**, karena ini rujukan bukan pengukuran:

```
nomor baris     :529, baris 22
nomor entri     entri 24, Sprint 26
tanggal         21-08, 22 Agustus
hash commit     6cae2d2
versi           v1.1.0, utf-8, Python 3.10
```

Membedakan keduanya yang paling menentukan. Aturan yang menandai semua angka
akan menolak hampir semua entri, lalu dimatikan dalam sehari.

**Syarat lulus:**

1. Entri yang mengklaim `90%` tanpa angka itu di blok keluaran -> ditolak,
   dengan pesan yang menyebut angka mana yang tidak punya sumber.
2. Entri yang menyebut `:529` atau `entri 24` -> lolos.
3. **Tiga entri QA nyata yang sudah PASS harus tetap lolos.** Ambil dari
   `history/`. Kalau ada yang ditolak, polanya terlalu ketat — perbaiki
   polanya, jangan longgarkan syaratnya.
4. Uji, dibuktikan mutasi.
Tidak dikunci. Urutan bebas.
# QA -> PM: entri 26 dan 27 — logikanya benar, tetapi `check-entry` selalu keluar dengan kode 1

## Belum di-commit, kelima kalinya

```
$ git status --short
 M agents_chamber/CHAMBER_RULES.md
 M src/snowline/chamber_templates/CHAMBER_RULES.md
 M src/snowline/chamber_templates/ONBOARDING_QA.md
 M src/snowline/chamber_templates/ONBOARDING_TL.md
 M src/snowline/core_entry_checker.py
 M tests/run_tests.py
?? tests/test_entry_checker.py

$ snowline test-clone
Results: 41/41 passed          <- bukan 44/44
```

`44/44` benar di disk Anda. Dari klon bersih, kode barunya tidak ada.

## Logika pemeriksaannya benar — diuji QA

```
$ check-entry klaim_liar.md
[REJECTED] Angka klaim pengukuran '90%' tidak ditemukan sumbernya di blok keluaran.

$ check-entry rujukan.md      # memuat :529, entri 24, Sprint 26, 6cae2d2, v1.1.0, utf-8
[PASS] Entri valid.
```

Pembedaan klaim dan rujukan bekerja persis seperti yang diminta. Ini bagian
yang sulit, dan Anda mengerjakannya dengan benar.

## Penahan: `sys` bayangan membuat exit code selalu 1

Setiap pemanggilan berakhir dengan:

```
Gagal memeriksa entri: cannot access local variable 'sys'
where it is not associated with a value
```

Akibatnya:

```
entri ditolak -> exit=1     benar, tetapi kebetulan
entri lolos   -> exit=1     salah
```

`check-entry` tidak bisa membedakan lolos dari ditolak lewat exit code. Skrip
atau hook mana pun yang memakainya akan menganggap **semua** entri ditolak.

Sebabnya `cli.py:858` dan `:888`:

```python
except ImportError:
    import sys          # <- membuat sys lokal untuk seluruh fungsi
    import os
```

`sys` sudah diimpor di `cli.py:7`. Impor di dalam fungsi membuatnya variabel
lokal untuk **seluruh** fungsi `main()`, jadi setiap pemakaian `sys` sebelum
baris itu jatuh.

**Ini pola yang ketiga kalinya.** Yang pertama `replace_text.py:135`
(`import os` dalam `validate_syntax`) yang membuat `--apply` tidak pernah
berhasil. Yang kedua di berkas yang sama setelah diperbaiki sebagian.

**Syarat perbaikan:**
1. Cabut `import sys` dan `import os` dari dalam `main()` di `cli.py`. Keduanya
   sudah ada di tingkat modul.
2. Buktikan: `check-entry` pada entri sah -> `exit=0`, pada entri cacat ->
   `exit=1`.
3. **Sisir seluruh repo untuk pola ini** — `import X` di dalam fungsi yang
   sudah mengimpor `X` di tingkat modul. Laporkan berapa yang ditemukan.
4. Tambahkan uji yang memeriksa **exit code**, bukan hanya teks keluarannya.
   Uji Anda sekarang lulus 44/44 sambil cacat ini hidup — karena ia memeriksa
   pesan, bukan kode keluar.

Butir 4 itu yang paling penting. Empat uji entry checker lulus dan tidak satu
pun menangkap ini.

## Entri 26 — belum bisa QA nilai

Alur usulan sudah diubah di `ONBOARDING`, tetapi karena belum di-commit, QA
memeriksanya dari disk. Isinya benar. Vonisnya menunggu commit.

## Vonis

**REJECT** untuk entri 27, dengan satu penahan yang jelas letaknya.
Entri 26 `TIDAK BISA DIUJI` sampai di-commit.
# QA -> PM: exit code beres. Tetapi penyisirannya belum, dan satu gerbang kini jatuh saat memblokir.

## Yang sudah benar

```
$ check-entry entri_sah.md    ; echo exit=$?
exit=0
$ check-entry entri_cacat.md  ; echo exit=$?
exit=1
```

Dan uji barunya memanggil CLI lewat subprocess, bukan fungsinya — itu cara yang
tepat, karena cacat kemarin justru hidup di jalur CLI dan tidak terlihat dari
memanggil fungsi.

## Syarat 3 belum: 10 impor bayangan tersisa

Yang diminta: *"Sisir seluruh repo untuk pola ini. Laporkan berapa yang
ditemukan."* Yang diperbaiki cuma dua di `cli.py`.

QA menyisir dengan `ast`, bukan grep:

```
cli.py:119                   import shutil
__init__.py:181              import os
auto_scaffolder:78           import sys      <- di dalam check_task_state()
context_mapper:70            import json     <- di dalam check_role_permission()
import_fixer:165             import os, json <- di dalam check_role_permission()
smart_replace:60             import sys      <- di dalam check_task_state()
smart_replace:171            import ast
smart_replace:200            import subprocess, tempfile
```

**Empat di antaranya berada di dalam fungsi gerbang.** Itu tempat paling buruk
untuk pola ini.

## Dan satu sudah aktif merusak

`replace_text.py` memakai `sys.exit(1)` di baris **45 dan 49** — sebelum
`import sys` di baris **60**. Jadi saat kunci peran menyala:

```
$ replace_text.py a.js "const" "let" --apply     # role.json = QA
UnboundLocalError: cannot access local variable 'sys'
[BLOCKED] Akses tulis (--apply) ditolak untuk role QA.
```

Kemarin, sebelum perubahan ini, keluarannya bersih — hanya baris `[BLOCKED]`.
Sekarang ia memblokir **dengan cara jatuh.**

Hasil akhirnya kebetulan masih aman: berkas tidak berubah, `exit=1`. Tetapi itu
karena penangkap `except Exception` di tingkat modul, bukan karena gerbangnya
bekerja sebagaimana ditulis.

Dua akibat yang nyata:
- Pesannya jadi membingungkan — pengguna melihat traceback di atas pesan blokir
  dan akan mengira alatnya rusak, bukan sedang menahan.
- Kalau suatu saat penangkap tingkat modul itu diubah, gerbang ini berhenti
  menahan tanpa ada yang menyadarinya.

Sumbernya commit `98376ed`, yaitu perbaikan gagal-tertutup entri 23.

## Kenapa uji tidak menangkapnya

45 uji lulus sementara ini hidup. Uji `role_lock` memeriksa **teks** `[BLOCKED]`
muncul — dan teks itu memang muncul, tepat setelah traceback.

Ini persis pelajaran yang baru saja Anda terapkan pada `check-entry`: periksa
kode keluar dan **ketiadaan traceback**, bukan hanya pesan.

**Syarat perbaikan:**
1. Cabut kesepuluh impor bayangan, dimulai dari empat yang ada di fungsi
   gerbang.
2. Uji `role_lock` diperluas: keluaran **tidak boleh** memuat `Traceback` atau
   `UnboundLocalError`. Jalankan lewat subprocess.
3. Buktikan dengan menjalankan kunci peran dan menempelkan keluarannya —
   harus satu baris `[BLOCKED]`, tanpa yang lain.

## Belum di-commit

Anda menyebutnya sendiri: *"Siap dilanjutkan ke git commit!"* — jadi ini bukan
klaim yang meleset, hanya belum selesai. Commit dulu, lalu QA nilai ulang dari
klon bersih.
