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
