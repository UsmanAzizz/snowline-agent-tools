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
