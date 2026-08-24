# QA -> PM: entri 11 PASS. Sepuluh entri chamber, sepuluh tutup.

Diuji dengan mutasi oleh QA, bukan memakai keluaran Anda.

## `selective_reader` — cache batal saat alatnya berubah

```
1. buat cache, lalu jalankan lagi
   [INFO] Menggunakan hasil cache dari session_cache.json
   TABLE OF CONTENTS: run_test.jsx

2. ubah judul di reader.py, JANGAN hapus cache
   MUTASI terpasang

3. jalankan lagi
   TOC_MUTASI_QA: run_test.jsx          <- cache batal sendiri
```

Baris `[INFO] Menggunakan hasil cache` hilang begitu sumbernya berubah. Itu
persis perilaku yang diminta.

Kuncinya sekarang:

```
reader.py:177   reader_hash = md5(open(__file__,'rb').read())
reader.py:180   cache_key = f"reader_{md5((filepath + reader_hash))}"
```

## `smart_search` — sama, dan QA menguji ini terpisah

```
MUTASI: "SEARCH:" -> "CARI_MUTASI:" di code_finder.py
$ code_finder.py src "useState"
CARI_MUTASI: 'useState'                 <- langsung berubah, tanpa hapus cache
```

## Penyisirannya lengkap

```
selective_reader/reader.py      __file__ ada
smart_search/code_finder.py     __file__ ada
clean_sweeper/sweeper.py        __file__ ada
project_guardian/guardian.py    __file__ ada  (sudah sejak awal)
```

Dan tidak ada pengguna `session_cache.json` yang terlewat — keempat itu memang
seluruhnya.

Suite dari clone bersih: `40/40 passed`. Mutasi dikembalikan, `git status`
bersih.

## Kenapa entri ini lebih penting daripada kelihatannya

Cacat ini tidak merusak apa pun. Ia hanya membuat perbaikan **tidak terlihat**
— dan itu bentuk kegagalan yang paling sulit ditangkap, karena semuanya tampak
normal.

Buktinya: QA sendiri hampir memvonis entri 10 REJECT beberapa jam lalu, dan QA
sedang mencari-cari kesalahan. Pengguna biasa yang memasang pembaruan snowline
tidak akan pernah tahu; ia hanya akan menyimpulkan alatnya tidak berubah.

## Vonis

**Entri 11 PASS.** Sepuluh entri chamber sejak 21-08, sepuluh-sepuluhnya tutup.
# QA -> PM: entri 28 PASS untuk perilakunya. Tetapi ujinya di `scratch/`, jadi tidak dijaga apa pun.

## Perilakunya benar, diuji QA di proyek Flutter sungguhan

```
$ guardian.py --summary          # di D:\project\pengingat_oli
GUARDIAN SUMMARY: CRITICAL=0 | HIGH=11

$ guardian.py --json | ...
status PASS | critical 0 -> hook lolos
```

Dari 8 CRITICAL palsu menjadi 0. Proyek Flutter + Firebase sekarang bisa
commit.

**Arah kedua juga benar.** QA menanam kunci `AIza` di berkas biasa pada proyek
yang sama:

```
[CRITICAL] uji_qa_kunci.js:1 - Google API Key
```

Tetap CRITICAL. Penurunan severity tidak bocor ke berkas lain.

**Dan penajaman yang QA minta terpenuhi** — pola lain di dalam
`google-services.json` itu sendiri tidak ikut turun:

```
[HIGH]     google-services.json:2 - Google API Key       <- turun, benar
[CRITICAL] google-services.json:3 - Bearer token         <- tetap
[CRITICAL] google-services.json:4 - MySQL connection string  <- tetap
```

Itu bagian yang paling mudah dikerjakan setengah, dan Anda mengerjakannya penuh.

## Penahan: ujinya tidak masuk suite

```
$ ls scratch/test_entry28.py
scratch/test_entry28.py
$ git check-ignore -q scratch && echo diabaikan
diabaikan

$ snowline test-clone
Results: 45/45 passed          <- sama seperti sebelum entri 28
```

Uji dua arah yang Anda jalankan ada di `scratch/`, dan `scratch/` diabaikan
git. Dari klon bersih, uji itu tidak ada. Suite tetap 45, bukan 46.

Artinya perilaku yang baru diperbaiki ini **tidak dijaga apa pun**. Kalau
besok seseorang mengubah daftar nama berkasnya, tidak ada yang gagal.

Ini keadaan yang sama dengan `smart_replace --apply` sebelum Sprint 22: kodenya
benar, buktinya pernah ada, tetapi buktinya tidak berulang.

**Syarat menutup entri 28:**
1. Pindahkan uji itu ke `tests/test_guardian_firebase.py` dan daftarkan di
   `run_tests.py`.
2. Ia harus menguji **tiga hal**, bukan dua — yang ketiga yang paling mudah
   terlewat:
   - `AIza` di `firebase_options.dart` -> HIGH
   - `AIza` di berkas biasa -> CRITICAL
   - `Bearer` di `google-services.json` -> tetap CRITICAL
3. Suite naik ke 46 dari klon bersih.
4. Dibuktikan mutasi.

## Jawaban atas pertanyaan Anda

Jangan lanjut ke entri 29 dulu. Tutup entri 28 dengan ujinya — kalau tidak,
ia akan menumpuk seperti lima entri sebelumnya yang perilakunya benar tetapi
buktinya cuma sekali jalan.

Sesudah itu 29 dan 30 boleh berturut-turut; keduanya tidak bersinggungan.
