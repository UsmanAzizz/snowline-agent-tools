# QA -> PM: uji chamber di proyek baru — tiga cacat, dua di antaranya membuat perintahnya tidak bisa dipakai orang lain

Dijalankan di proyek kosong, bukan di repo ini. Yang diuji chamber yang
**dikirim**, bukan yang kita pakai.

## Yang bekerja

```
init_chamber --apply    7 berkas terpasang, nama sudah Inggris semua
check-entry             menolak entri yang mengklaim selesai tanpa keluaran,
                        exit=1; entri sah exit=0
kunci peran             memblokir --apply
rujukan dokumen         tiga berkas yang disebut ONBOARDING semuanya ada
```

## Cacat 1 — `close-entry` tidak jalan di proyek mana pun selain repo ini

```
$ snowline close-entry perbaikan
Error: .here_we_are\connector.md not found.
```

`core_close_entry.py:7-11` memaku jalurnya:

```python
here_we_are = Path(".here_we_are")
connector_file = here_we_are / "connector.md"
state_file = here_we_are / "STATE.md"
history_dir = Path(".here_we_are/history") / topik
```

Proyek yang memasang chamber lewat `init_chamber` menaruhnya di
`.agents/chamber/`. Perintah ini tidak akan pernah menemukannya.

`core_context.py:8-9` sudah benar — ia memeriksa **dua** lokasi. Tiru itu.

## Cacat 2 — `STATE.md` yang dikirim masih berjudul `# KEADAAN`

```
$ snowline context
[STATE.md]
# KEADAAN
```

Nama berkasnya sudah `STATE.md`, judul di dalamnya belum. Rename kemarin
mengubah nama berkas dan rujukan jalur, tetapi tidak menyentuh judul di dalam
templat.

Sekalian periksa isi templat chamber yang lain untuk sisa yang sama.

## Cacat 3 — `test-clone` gagal di proyek tanpa `tests/run_tests.py`

```
$ snowline test-clone
[FAIL] Skrip tes tidak ditemukan di ...\tests\run_tests.py
```

Perintah ini mengandaikan tiap proyek punya `tests/run_tests.py` — itu tata
letak snowline sendiri, bukan tata letak umum.

Untuk proyek lain, ia harus: mendeteksi perintah ujinya (`npm test`,
`pytest`, `python tests/run_tests.py`), atau menerima perintah sebagai argumen:

```
snowline test-clone --cmd "npm test"
```

Kalau tidak ada yang terdeteksi, katakan begitu — jangan `[FAIL]` seolah
ujinya yang gagal. Proyek tanpa uji bukan kegagalan; ia cuma tidak punya uji.

## Cacat 4 — kunci peran masih jatuh saat memblokir

Sudah dilaporkan sebelumnya, dan masih ada di proyek baru:

```
UnboundLocalError: cannot access local variable 'sys'
[BLOCKED] Akses tulis (--apply) ditolak untuk role QA.
```

Pengguna baru yang pertama kali memakai kunci peran akan melihat traceback dan
menyimpulkan alatnya rusak.

## Yang perlu disadari dari uji ini

Tiga dari empat cacat cuma terlihat **di luar repo ini**. Di sini semuanya
lulus, 45/45, karena jalur `.here_we_are` memang ada dan `tests/run_tests.py`
memang ada.

Uji yang berjalan di dalam repo tidak bisa menemukan asumsi tentang tata letak
repo. Untuk perintah yang dikirim ke orang lain, ujinya harus dijalankan di
proyek kosong.

**Usul:** tambahkan satu uji yang membuat proyek sementara, menjalankan
`init_chamber`, lalu memanggil tiap perintah chamber di sana. Itu akan
menangkap ketiganya sekaligus.
