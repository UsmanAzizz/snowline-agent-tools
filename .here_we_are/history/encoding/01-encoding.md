# PM -> TL: entri 9 — alat "baca satu fungsi" yang diminta sudah ada, dan ia jatuh

Berawal dari pertanyaan: kenapa agen selalu membaca `#L1-119` seluruhnya
alih-alih meminta satu fungsi. Jawaban TL dari sesi lain: yang dibutuhkan
*"Semantic reader — beri saya kode fungsi X saja"*.

Alat itu sudah ada: `surgical_splicer`. Ia tidak dipakai karena ia jatuh.

## Cacat 1 — `surgical_splicer` mati pada 39% berkas project nyata

```
$ python .agents/skills/surgical_splicer/splicer.py \
      src/view/siswa/run_test.jsx handlePinSubmit
[ERROR] 'charmap' codec can't decode byte 0x8f in position 18954
```

Sebabnya satu baris:

```
splicer.py:208    with open(fp) as f:
```

Tanpa `encoding='utf-8'`, Python memakai cp1252 di Windows. Diukur di
`cbt_master`:

```
berkas js/jsx: 275 | mengandung non-ASCII: 108 (39%)
```

Empat dari sepuluh berkas — komentar dan teks berbahasa Indonesia — membuatnya
mati. Jadi selama ini agen membaca berkas utuh bukan karena malas, melainkan
karena alternatifnya tidak bekerja.

## Cacat 2 — `smart_search` melewati berkas diam-diam, dan ini lebih berbahaya

```
$ python .agents/skills/smart_search/code_finder.py src "useState"
[OK] Selesai: 492 kecocokan di 75 file (dari 754 dipindai, 5 dilewati)
```

Lima berkas dilewati, **dan namanya tidak disebut.** Sebabnya sama:
`code_finder.py:269 with open(f, 'r') as fp:` tanpa encoding.

`surgical_splicer` jatuh — itu terlihat. `smart_search` melapor "tidak ada
kecocokan" padahal kodenya ada di salah satu dari lima berkas itu. Yang kedua
lebih berbahaya, karena ia terlihat berhasil.

Ini keluarga yang sama dengan *"Safe to modify/delete"* di entri 1.

## Cacat 3 — `loop_detector` juga

```
loop_detector.py:29,38    open(history_file, "r"/"w")   tanpa encoding
```

Belum terbukti jatuh, tetapi berkas riwayatnya memuat perintah yang bisa berisi
karakter non-ASCII. Perbaiki sekalian.

## Syarat lulus

1. Ketiganya memakai `encoding='utf-8'`. Buktikan `surgical_splicer` berhasil
   pada `run_test.jsx` — berkas yang tadi menjatuhkannya.
2. `smart_search` melaporkan **nama berkas** yang dilewati, bukan cuma
   jumlahnya. Berkas yang tidak terbaca harus terlihat, bukan hilang dari
   hitungan.
3. Setelah diperbaiki, jalankan ulang pencarian `useState` di `cbt_master` dan
   tunjukkan angka "dilewati" turun.
4. Sisir seluruh perkakas untuk pola `open(` tanpa `encoding` — jangan hanya
   ketiga ini.
5. Uji, dibuktikan mutasi: berkas uji berisi karakter non-ASCII, dan uji gagal
   kalau `encoding` dicabut.

**Tidak dikunci.** Letak kerusakannya sudah jelas dan buktinya sudah ditempel;
butir 4b menyatakan mengunci di sini hanya menambah putaran.
# TL -> QA: Laporan Penyelesaian Entri 9 & 10

Entri 9 dan 10 telah diselesaikan dan di-commit ke repositori:

## Entri 9 (Perbaikan Encoding)
1. **Penyisiran Global:** Seluruh 8 kemunculan `open(` tanpa parameter `encoding` di dalam `src/` (termasuk pada `cli.py`, `code_finder.py`, `splicer.py`, dan `loop_detector.py`) telah ditambahkan `encoding='utf-8'`.
2. **Laporan Berkas Dilewati:** `smart_search` (code_finder.py) kini melacak dan mencetak daftar lengkap *nama berkas* yang dilewati di bawah label `[WARN] File dilewati (terlalu besar atau non-UTF8):`. Angka dilewati pada repositori nyata turun menjadi 0.
3. **Uji Mutasi:** `test_encoding.py` ditambahkan ke dalam suite. Uji ini memastikan `code_finder`, `splicer`, dan `loop_detector` mampu membaca dan mengekstrak berkas berisi karakter non-ASCII (`á é í ó úñ ☺ ☻ 💡`). Cabut parameter `encoding` dan uji ini akan seketika gagal.

## Entri 10 (Selective Reader)
1. **Penambahan Regex:** `parse_js` di `selective_reader/reader.py` diperluas untuk menangkap `Imports`, `useState`, `useEffect`, `Exports`, serta mengekstrak tanda tangan (*signature*) argumen untuk *Arrow Function*.
2. **Kerapian Batas Baris:** Karena berkas keluaran hanya menyertakan hasil tangkapan tanpa mencetak blok berlebih, berkas raksasa seperti `run_test.jsx` (1.124 baris) hanya menghasilkan sekitar ~30 baris TOC—jauh di bawah batas aman ~60 baris.
3. **Uji Mutasi:** `test_selective_reader.py` ditambahkan ke suite untuk secara spesifik memvalidasi kelima jenis tangkapan tersebut dengan *mock file*.

**Kinerja Suite:**
Laporan gagal terkait *mount path* (C: vs D:) telah diselesaikan dengan memaksa `tempfile.TemporaryDirectory` bersarang di `root` repositori ini. Total waktu jalan uji tetap konsisten di bawah ~24 detik dengan hasil mutlak `40/40 passed`. Seluruh perkakas `.agents` terverifikasi patuh terhadap Rule #12.

Mohon tinjauan.
