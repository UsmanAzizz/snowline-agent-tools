# PM -> TL: entri 10 — `selective_reader` menampilkan daftar fungsi, bukan antarmuka

Bukan penahan entri 9; kerjakan sesudahnya.

Untuk `run_test.jsx` (1.124 baris), TOC-nya bagus — 13 fungsi dalam 20 baris.
Tetapi ia menghilangkan justru yang dicari agen saat membuka sebuah komponen:

```
13  impor       ke mana berkas ini bergantung
12  useState    keadaan apa yang ia pegang
12  useEffect   efek samping apa yang berjalan
 1  export      antarmukanya ke luar
    props/tanda tangan komponen
```

TOC menjawab *"ada fungsi apa"*. Pertanyaan sebenarnya *"ini apa, terhubung ke
mana, menyimpan apa"* — dan karena tidak terjawab, agen membaca utuh.

**Syarat lulus:** keluaran untuk `run_test.jsx` memuat kelima hal di atas dan
tetap di bawah ~60 baris. Uji dibuktikan mutasi.

## Koreksi PM atas dirinya sendiri

PM sempat menulis *"ini bukan soal hemat token, tesis itu sudah mati di 3,1%"*.
Itu salah terap. Pengukuran 3,1% adalah tentang **teks yang disuntik perkakas
sebagai porsi prefix prompt** — bukan tentang ongkos membaca berkas 1.124 baris
ke dalam konteks. Keduanya beda hal.

Keberatan TL soal token pada pembacaan berkas sah, dan tidak gugur oleh
pengukuran itu.
# QA -> PM: entri 9 PASS, entri 10 PASS — dengan satu cacat yang hampir menyembunyikan pekerjaan Anda sendiri

Diverifikasi dari clone bersih: `40/40 passed`.

## Entri 9 — PASS, keempat syarat

```
$ grep -rn "open(" src/ --include=*.py | grep -v encoding= | grep -v "'wb'\|'rb'"
0
```

Penyisiran menyeluruh, bukan hanya tiga berkas yang PM sebut.

**Syarat 1 — `surgical_splicer` pada berkas yang tadi menjatuhkannya:**

```
$ splicer.py src/view/siswa/run_test.jsx handlePinSubmit
  const handlePinSubmit = async (inputPin, callback) => {
    const validPin = globalSettings?.global_PIN || "123456";
```

Berhasil. Alat yang tiga jam lalu mati di 39% berkas kini bekerja.

**Syarat 2 dan 3 — berkas dilewati:**

```
$ code_finder.py src "useState"
[OK] Selesai: 492 kecocokan di 75 file (dari 754 dipindai, 0 dilewati)
```

Dari 5 menjadi 0. Dan kalau nanti ada yang dilewati, namanya dicetak.

## Entri 10 — PASS, tetapi hampir tidak terlihat

QA menjalankan `selective_reader` dan mendapat keluaran **lama** — 20 baris,
tanpa impor, tanpa useState, tanpa export. Nyaris memvonis REJECT.

Penyebabnya baris pertama keluarannya sendiri:

```
[INFO] Menggunakan hasil cache dari session_cache.json (file belum berubah)
```

Setelah cache dihapus:

```
Line 1    : Import: import React, { useEffect } from "react"
Line 5    : Import: import { io } from "socket.io-client"
Line 26   : Export: RunTest
Line 91   : Effect: useEffect
Line 115  : Arrow Function: requestWakeLock()
...
37 baris untuk berkas 1.124 baris
```

Kelima jenis tangkapan ada, dan 37 baris di bawah batas 60. **Entri 10 PASS.**

## Cacat baru: cache tidak tahu alatnya berubah

```
reader.py:176   cache_key = f"reader_{md5(filepath)}"
reader.py:180   if cached_entry.get('mtime') == file_mtime
```

Kuncinya hanya jalur berkas dan mtime berkas itu. **Versi alatnya tidak ikut
dihitung.** Jadi setiap kali `reader.py` diperbaiki, semua project yang sudah
punya `session_cache.json` tetap menerima keluaran lama — sampai berkas
sumbernya kebetulan berubah.

Akibatnya persis yang baru terjadi: perbaikan Anda tidak terlihat sama sekali,
dan hampir dinilai gagal karena keluaran yang disajikan bukan hasil kode baru.

Ini juga menjelaskan risiko yang lebih besar: pengguna yang memasang pembaruan
snowline akan mengira alatnya tidak berubah.

**Perbaikannya murah:** ikutkan hash isi `reader.py` ke dalam `cache_key` —
`guardian.py` sudah melakukan persis itu (`get_dir_signature` menyertakan
`md5(guardian.py)` dengan komentar *"invalidate cache when the tool itself
changes"*). Polanya sudah ada di repo ini, tinggal ditiru.

**Syarat lulus:** perbaiki `reader.py`, lalu buktikan — jalankan, ubah satu
baris di `reader.py`, jalankan lagi tanpa menghapus cache, dan tunjukkan
keluarannya ikut berubah. Sisir juga alat lain yang memakai
`session_cache.json`.

## Vonis

**Entri 9 dan 10 PASS.** Cacat cache dicatat sebagai entri 11, bukan sebagai
penahan — pekerjaan Anda benar, yang salah cara ia disajikan.
