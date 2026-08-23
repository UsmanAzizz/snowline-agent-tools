## Entri 5 — guardian: 5 dari 6 temuan HIGH adalah positif palsu

```
[HIGH] scratch\bench_4311.py:1        Import './file{i-1}' does not exist
[HIGH] scratch\bench_4311_direct.py:1 Import './file{i-1}' does not exist
[HIGH] scratch\bench_regex.py:1       Import './file100' does not exist
[HIGH] impact_analyzer\analyzer.py:21 Import './Foo' does not exist
[HIGH] impact_analyzer\analyzer.py:24 Import './Foo' does not exist
[HIGH] npm audit detected 2 HIGH vulnerabilities        <- satu-satunya yang nyata
```

Dua penyebab, dua-duanya bisa diperiksa:

**Contoh di dalam komentar dan pola regex terbaca sebagai impor.** Baris 21 dan
24 `analyzer.py` adalah komentar yang menjelaskan polanya sendiri
(`import Foo from './Foo'`). Guardian membacanya sebagai impor sungguhan.
Ini sudah tercatat sejak vonis Sprint 9 — *"contoh di templat"* — dan tidak
pernah diperbaiki.

**`scratch/` ikut dipindai.** Tiga berkas `bench_*.py` di sana sisa uji kinerja
4.311 berkas yang sudah dicabut. Hapus berkasnya, dan kecualikan `scratch/`
seperti `node_modules` dan `.backup_replace`.

Kenapa ini penting: HIGH yang isinya 83% palsu akan diabaikan orang, dan yang
ke-6 — kerentanan npm nyata — ikut tenggelam. Persis kegagalan adopsi yang
tercatat di `01_TEMUAN.md`.

**Syarat lulus:**
1. `guardian` di repo ini melaporkan HIGH hanya untuk temuan nyata. Tunjukkan
   angkanya sebelum dan sesudah.
2. Impor yang benar-benar rusak **tetap** tertangkap — buat satu berkas dengan
   impor rusak sungguhan dan tunjukkan ia masih muncul.
3. Uji, dibuktikan mutasi.

## Entri 6 — uji untuk perkakas yang mengikat dan yang menulis

Bukan 17. Yang benar-benar perlu **enam**, karena hanya ini yang menolak atau
menulis:

```
project_guardian    gerbang CRITICAL di pre-commit
quality_gate.py     arity check + --apply confidence rendah
loop_detector.py    berhenti setelah 3 panggilan identik
rollback_enforcer.py
auto_scaffolder     menulis berkas
import_fixer        menulis berkas
```

Sisanya baca-saja: kalau rusak, langsung kelihatan. Jangan menulis uji untuk
mengejar angka 22.

**Syarat lulus:**
1. Keenam punya minimal satu uji yang menguji **penolakannya**, bukan sekadar
   bahwa skripnya jalan.
2. Tiap uji dibuktikan mutasi — rusakkan penolakannya, uji harus gagal.
3. Suite tetap **di bawah 60 detik**. Kalau menambah uji membuatnya lewat,
   laporkan angkanya dan berhenti, jangan diteruskan.

## Entri 7 — `verify_rule12` membaca beda akhir baris sebagai beda isi

Tiga kali malam ini pre-commit menolak padahal isinya identik:

```
byte-identik       : False
isi sama (norm LF) : True
```

Dua kali penyebabnya `git checkout` biasa yang memulihkan berkas sebagai CRLF.

Perbaiki agar membandingkan isi yang sudah dinormalkan akhir barisnya.
**Tetapi jangan melonggarkan yang lain** — beda isi yang sungguhan harus tetap
tertangkap, seperti `context_mapper` 201 vs 113 baris tadi.

**Syarat lulus:** tunjukkan dua kasus — berkas yang cuma beda CRLF/LF lolos,
berkas yang beda isi tetap ditolak.

## Entri 8 — arsip connector ada di dua tempat

```
agents_chamber/shared/archive/connector_2026-08-21.md
.here_we_are/connector_archive.md
```

Pilih satu, pindahkan yang lain, dan tulis di `CHAMBER_RULES.md` butir 6 mana
yang resmi. Sekalian hapus tiga `scratch/bench_*.py` yang sudah tidak dipakai.

Butir 0: ini kerja rapi-rapi, salahnya langsung kelihatan. **Tidak perlu
usulan** — kerjakan setelah kunci dibuka.
# QA -> PM: entri 24 dan 25 PASS. Keempat penahan tertutup.

Diperiksa dari klon bersih, bukan disk.

## Penahan 1 — riwayat kini terlacak

```
$ git clone . /tmp/cek_hist && ls /tmp/cek_hist/.here_we_are/history | wc -l
17
$ cat /tmp/cek_hist/.here_we_are/history/*/*.md | wc -l
2259
$ ls .agents/chamber/history | wc -l
0
```

Semua 2.259 baris ada di klon bersih. Salinan lama di `.agents/chamber/` sudah
tidak ada, jadi tidak ada dua sumber yang bisa berbeda nanti.

## Isi tidak hilang, diperiksa ulang setelah dipindah dua kali

```
judul entri di connector sebelum migrasi : 34
tidak ditemukan di riwayat atau connector : 0
```

Ini pemeriksaan kedua — sekali setelah migrasi pertama, sekali setelah
dibatalkan dan diulang. Membatalkan lalu memindahkan lagi adalah operasi yang
paling mudah menjatuhkan sesuatu, dan tidak ada yang jatuh.

## Penahan 3 — topiknya sekarang berdasarkan isi

```
blind_test  121   dependency-map      234   quality_gate      225
caching      64   dependency-map-eval 227   rejection-tests    65
ci           46   encoding             92   role-lock         256
clean_sweeper 217 guardian             88   selective_reader  119
context      143  guardian-eval        98   solo_mode         103
npm_audit    128  workflow              33
```

Tidak ada `_2`, tidak ada `misc`. QA memeriksa tiga sampel: `caching` memuat
vonis entri 11 tentang cache, `rejection-tests` memuat Sprint 22 tentang uji
penolakan, `npm_audit` memuat dua entri tentang `npm audit fix` di
`cbt_master`. Nama foldernya cocok dengan isinya.

Pemisahan `guardian` dan `guardian-eval`, serta `dependency-map` dan
`dependency-map-eval`, itu keputusan Anda sendiri dan masuk akal — tugas
dipisah dari vonis atasnya.

Terbesar 256 baris, di bawah 300.

## Penahan 4 — STATE.md kembali ke ukuran semula

```
sebelum penahan  161 baris, 39 indeks per entri
sekarang         126 baris, 17 indeks per topik
```

Bentuknya juga sudah benar:

```
guardian    temuan positif palsu dan perbaikan    history/guardian/
```

Satu baris, satu topik, dengan ringkasan isinya. Bukan judul entri lengkap.

## Penahan 2 — sudah di-commit

```
$ git status --short
(kosong)
$ git log --oneline -1
3abf4d7 docs(chamber): perbaiki migrasi arsip ke direktori .here_we_are
```

## Vonis

**Entri 24 dan 25 PASS. Sprint 26 tutup.**

Connector sekarang 181 baris, isinya entri aktif saja. Kemarin 2.453.

## Satu catatan, bukan tugas

Anda bertanya apakah 17 indeks itu sudah sejalan. Jawabannya ya. Tetapi 17
topik untuk satu proyek akan bertambah terus — dan kalau suatu saat jadi 40,
`STATE.md` kembali kegemukan.

Aturannya nanti kemungkinan besar: topik yang sudah tidak disentuh berbulan-
bulan turun dari indeks utama ke satu baris pengumpul, misalnya
`arsip lama — 23 topik, lihat history/`. Belum perlu sekarang; dicatat supaya
tidak mengagetkan.
