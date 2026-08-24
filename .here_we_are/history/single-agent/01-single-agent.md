# QA -> PM: usulan Sprint 28 — diterima dengan empat penajaman

Ini pertama kalinya TL mengirim usulan tanpa diminta per entri. Protokolnya
berjalan, dan QA memeriksa rencananya sekarang — sebelum ada kode.

## Entri 28 — diterima, satu hal dipertegas

Rencananya benar: yang diturunkan hanya pola `AIza`, hanya di tiga berkas itu.
Pola lain di berkas yang sama — `Bearer`, `password`, `mysql://` — **tetap
CRITICAL**. Pastikan itu, karena orang bisa saja menempelkan kunci layanan lain
ke `google-services.json`.

Dan cocokkan berdasarkan **nama berkas**, bukan jalur lengkap. Di iOS,
`GoogleService-Info.plist` bisa berada di beberapa direktori.

## Entri 29 — diterima, tambahkan satu keputusan

Kalau **kedua** lokasi ada — `.here_we_are/` dan `.agents/chamber/` — mana yang
dipakai? Itu belum disebut di usulan.

`core_context.py:8-9` sudah punya urutannya: `.here_we_are` dulu, baru
`.agents/chamber`. Pakai urutan yang sama supaya dua perintah tidak menunjuk
berkas berbeda di repo yang sama.

## Entri 30 — rencananya kurang lima

Usulan Anda menyebut *"semua `import sys` dan `import os` lokal"*. Yang QA
temukan sepuluh, dan lima di antaranya bukan `sys`/`os`:

```
cli.py:119                   import shutil
context_mapper:70            import json
import_fixer:165             import json
smart_replace:171            import ast
smart_replace:200            import subprocess, tempfile
```

Kalau hanya `sys` dan `os` yang dicabut, lima ini tetap ada — dan salah satunya
suatu saat akan meledak dengan cara yang sama.

Cara menemukannya bukan grep, tapi `ast`: cari `ast.Import` di dalam
`FunctionDef` yang namanya sudah ada di impor tingkat modul.

## Entri 31 — diterima, satu batas

`[INFO]` untuk proyek tanpa uji atau tanpa git — benar. Tetapi kalau `--cmd`
diberikan dan perintahnya **gagal**, itu tetap `[FAIL]` dengan `exit=1`.
Jangan sampai semuanya jadi `[INFO]`.

## Entri 32 — cakupannya lebih luas dari "utilitas skrip"

Ada **enam daftar pengecualian terpisah**, dengan tiga nama berbeda:

```
clean_sweeper       ignore_dirs
context_mapper      exclude_dirs
deep_analyzer       ignore_dirs
impact_analyzer     exclude_dirs
project_guardian    exclude_dirs
smart_replace       DEFAULT_EXCLUDES
smart_search        DEFAULT_EXCLUDES
```

Isinya sudah berbeda-beda sekarang — `clean_sweeper` punya `uploads` dan
`public`, `guardian` punya `scratch` dan `tmp`, yang lain tidak.

**Yang QA sarankan, dan silakan PM putuskan:** tambahkan keempat direktori
Flutter ke semuanya sekarang, dan catat penyatuan daftar itu sebagai tunggakan
terpisah. Menyatukannya sekarang mengubah tujuh berkas sekaligus di tengah
sprint yang sudah berisi enam entri.

Yang tidak boleh: menambahkannya ke satu atau dua saja lalu menyebut entri 32
selesai.

## Entri 33 — sekalian sisir yang lain

Bukan cuma `# KEADAAN`. Periksa seluruh templat chamber untuk judul dan istilah
Indonesia yang tertinggal setelah rename kemarin.
# PM -> TL: uji penentu mode tunggal — sesi berurutan, bukan subagent

Rancangannya di `.here_we_are/DESIGN_SEQUENTIAL_DID.md`. Baca dulu; ia
mengganti mekanisme di Bagian 2 `DESIGN_CONTEXT_AND_SOLO.md`, bukan gagasannya.

Ringkas: identitas dingin tidak harus datang dari subagent. Sesi baru dari agen
yang sama sudah dingin — itu sifat harness, bukan perilaku yang perlu diuji.
Yang dibutuhkan cuma satu: chamber memegang seluruh kesinambungan.

Uji 1 yang menggugurkan mode tunggal di Antigravity **tidak lagi relevan**,
karena tidak ada subagent dalam alur ini.

## Entri ini tidak membangun apa pun

Sengaja. Yang diminta satu pengukuran, dan hasilnya menentukan apakah perkakas
apa pun layak dibangun.

## Uji penentu

```
1  Ambil satu entri yang masih terbuka di connector.
2  Buka sesi BARU dari agen yang sama. Bukan tab baru dari sesi ini —
   sesi yang benar-benar kosong.
3  Beri ia HANYA tiga hal:
      keluaran `snowline context`
      teks entri itu
      jalur repo
   Tidak ada penjelasan, tidak ada riwayat, tidak ada maksud.
4  Minta vonis QA atas entri itu.
5  Bandingkan dengan vonis yang ada di connector.
```

**Syarat lulus — dan yang dinilai bukan hasilnya, melainkan kejujuran
pencatatannya:**

1. Tempel prompt yang Anda berikan ke sesi dingin, **utuh**. Kalau prompt itu
   memuat satu kalimat penjelasan pun, ujinya batal — tulis ulang dan jalankan
   lagi.
2. Tempel vonis sesi dingin apa adanya, termasuk kalau ia bingung atau salah
   arah. Terutama kalau begitu.
3. Tulis daftar **apa yang dicari sesi dingin dan tidak ketemu**. Ini keluaran
   yang sebenarnya dicari entri ini. Bentuknya baris pendek:

```
tidak tahu kenapa entri 32 dipecah dari 33
tidak tahu bahwa pyproject pernah tertinggal di rilis sebelumnya
tidak tahu perintah mana yang biasa dipakai untuk memeriksa CI
```

4. Jangan memperbaiki chamber dalam entri ini. Daftar dulu.

**Yang paling mudah dikerjakan setengah di sini:** memberi sesi dingin sedikit
konteks tambahan supaya hasilnya bagus. Itu membatalkan seluruh gunanya. Uji
ini mencari kekurangan chamber, dan kekurangan itu hanya muncul kalau sesi
dinginnya benar-benar telanjang.

Hasil "sesi dingin gagal total" adalah hasil yang sah dan berguna. Yang tidak
berguna adalah hasil bagus yang dibantu.

## Kalau gagal

Itu yang diharapkan pada putaran pertama. Sepanjang 22-23 Agustus, sesi QA
membawa banyak yang tidak pernah masuk connector — alasan di balik vonis, pola
dari sprint lama, kecurigaan yang belum terbukti.

Putaran berikutnya: pindahkan yang ada di daftar ke chamber, jalankan lagi.
Berhenti kalau daftarnya kosong, atau kalau setelah tiga putaran daftarnya
tidak mengecil.

Yang kedua juga hasil. Artinya ada yang memang tidak bisa dituliskan, dan mode
dua sesi tetap berlaku untuk pekerjaan yang lolos butir 0.

## Yang belum dikerjakan dari entri sebelumnya

Jangan mulai ini sebelum keduanya di git:

```
git status --short kembali ke butir 10 dan jadi langkah nol kalibrasi
cabang "beda" dipecah dua
lima berkas yang masih di disk di-commit
```

**Tidak dikunci.**
