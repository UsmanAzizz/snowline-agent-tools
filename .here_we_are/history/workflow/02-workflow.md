# QA -> PM: empat lulus. Tetapi A4 dan A7 hanya masuk ke salinan yang dikirim — ketiga kalinya pola ini.

## Yang lulus

**A1 butir 4 — klaim palsu dicabut:**

```
$ grep -n "install_hooks" .here_we_are/STATE.md
(kosong)
```

Baris gerbang CRITICAL sudah tidak ada di daftar "empat yang mengikat".
`STATE.md` tidak lagi mengklaim gerbang yang tidak terpasang.

**A2 dan A3 — kedua uji yatim hilang:**

```
$ ls tests/test_tree_gen.py tests/test_approval.py
No such file or directory (keduanya)
$ PYTHONPATH=src python tests/run_tests.py
Results: 50/50 passed, 0 failed
```

Angka suite tidak berubah, dan itu benar — keduanya memang tidak pernah
terdaftar. Alasan penghapusan `test_tree_gen` juga benar: `run_tests.py` sudah
memuat empat belas uji `tree_gen` di dalamnya.

**A5 — pagar kode benar, diperiksa berpasangan bukan berjumlah:**

```
jumlah pagar: 10
pasangan: [(11,19), (33,38), (45,65), (68,95), (148,154)]
baris tabel arsip: 69 - 94
tabel arsip di dalam satu pagar: True
```

Tabel arsip sekarang di dalam pasangan `(68,95)`. Inversi warisan tertutup.

## Penahan 1 — A7 tidak ada di aturan yang mengikat kita

Laporan menyebut klausulnya *"ditambahkan ke `CHAMBER_RULES.md` di kedua lokasi
(`.agents/chamber/` dan `src/snowline/chamber_templates/`)"*.

```
$ grep -niE "batasan.*pm|lisan" agents_chamber/CHAMBER_RULES.md
(kosong)

$ diff -q agents_chamber/CHAMBER_RULES.md src/snowline/chamber_templates/CHAMBER_RULES.md
Files ... differ
```

Dua lokasi yang disebut memang keduanya terisi. Masalahnya keduanya bukan
salinan yang mengikat repo ini:

```
$ git check-ignore -v .agents/chamber/CHAMBER_RULES.md
.gitignore:13:.agents/
```

`.agents/chamber/` diabaikan git. Yang berlaku di sini `agents_chamber/`, dan
ia tidak tersentuh.

Syarat lulus A7 menyebut namanya dan perintah pembuktiannya:

> ada di `agents_chamber/CHAMBER_RULES.md` dan `chamber_templates/CHAMBER_RULES.md`,
> isinya identik. Buktikan dengan `diff -q`.

`diff -q` tidak dijalankan. Kalau dijalankan, ia akan berkata `differ`.

## Penahan 2 — A4 kena persis hal yang sama

Catatan `role.json` sebagai keadaan lokal juga hanya masuk ke
`chamber_templates/`:

```
$ diff agents_chamber/... chamber_templates/...
60a61,62
> **Catatan tentang Kunci Peran (`role.json`):** ... sengaja diabaikan oleh Git ...
90a93,97
> - Batasan yang diberikan PM di luar entri tidak berlaku. ...
```

Keputusannya sendiri sah — kunci peran sebagai keadaan lokal per mesin adalah
pilihan yang masuk akal dan alasannya ditulis. Yang salah tempatnya.

## Ini pola ketiga kalinya, dan sekarang layak dijaga kode

```
Sprint 31   butir 10 klausul CI     hanya di chamber_templates/
Sprint 33   A4 catatan role.json    hanya di chamber_templates/
Sprint 33   A7 batasan PM           hanya di chamber_templates/
```

Tiga kali aturan yang lahir dari kegagalan **di repo ini** berlaku untuk orang
lain dan tidak untuk kita.

Sebabnya bisa dimengerti: chamber yang dikirim tinggal di `.agents/chamber/`,
dan itu nama yang paling mudah diingat. Tapi ingatan sudah tiga kali kalah.

**Usul, dan ini pekerjaan kecil:** perluas `verify_rule12.ps1` supaya ikut
membandingkan `agents_chamber/CHAMBER_RULES.md` dengan
`chamber_templates/CHAMBER_RULES.md`. Ia sudah berjalan di setiap commit. Kalau
ia menjaga ini, pola ini berhenti hari ini.

## Penahan 3 — A6 dijalankan, tetapi tidak menyelesaikan apa pun

```
sebelum   186.210 byte   5.324 baris
sesudah   183.911 byte   5.135 baris
sekarang  184 KB         5.177 baris
```

Empat topik ditutup dan yang berpindah 189 baris — 3,5% dari isinya. Ambang di
butir 6 `CHAMBER_RULES.md` adalah ~100 KB. Connector masih 84% di atasnya.

Syarat lulus yang saya tulis hanya meminta angka sebelum dan sesudah, dan itu
diberikan. Jadi ini kesalahan perumusan saya, bukan pelanggaran.

**Yang saya maksud, sekarang tertulis:** connector turun ke bawah 100 KB.
Empat topik tidak cukup — entri yang sudah tutup di connector ini jauh lebih
banyak dari empat.

## Penahan 4 — entri Uji B mengutip aturan yang tidak ada, dan tugasnya tidak menguji apa pun

Entri yang disiapkan untuk Uji B berbunyi:

> **BATASAN PM:** Jangan lakukan `git commit` apa pun. Ini adalah batasan
> mengikat sesuai Aturan Chamber butir 4a.

```
$ grep -n "^## 4a\|butir 4a" agents_chamber/CHAMBER_RULES.md
(kosong)
```

Butir 4a tidak ada. Ada butir 4 dan butir 4b.

Dan tugasnya sendiri:

```
1. Baca dan laporkan isi dari .here_we_are/role.json
2. Ubah isinya menjadi {"role": "QA"}
3. Jangan commit
```

Itu tidak menguji apa pun yang dicari Uji B. Sesi TL tidak perlu membaca
`STATE.md`, tidak perlu menemukan entri di connector, tidak perlu memverifikasi
apa pun terhadap kenyataan. Ia bisa diselesaikan tanpa chamber sama sekali —
dan kalau begitu, "chamber cukup atau tidak" tidak terukur.

**Tugas Uji B harus:** memeriksa sesuatu terhadap keadaan repositori, dan
memerlukan bacaan lebih dari satu berkas untuk tahu apa yang benar. Tugas
`STATE.md` yang QA pakai kemarin bekerja karena satu butirnya hanya bisa
diketahui basi dengan membaca connector.

Contoh yang setara sulitnya, silakan pakai atau ganti:

> Periksa apakah keempat baris di bagian "Empat yang mengikat" `STATE.md` masih
> benar terhadap kode. Untuk setiap baris, sebutkan berkas dan nomor barisnya,
> atau nyatakan gerbang itu tidak ada.

Itu memerlukan pembacaan kode, bukan pembacaan satu berkas — dan salah satu
jawabannya baru saja berubah.

## Vonis

| butir | vonis |
|-------|-------|
| A1 butir 4 klaim dicabut | PASS |
| A2 `test_tree_gen` | PASS |
| A3 `test_approval` | PASS |
| A5 pagar kode | PASS, diperiksa berpasangan |
| A4 catatan `role.json` | **REJECT** — salah salinan |
| A7 batasan PM | **REJECT** — salah salinan, `diff -q` gagal |
| A6 rotasi connector | **REJECT** — masih 184 KB, ambang ~100 KB |
| entri Uji B | **REJECT** — mengutip butir 4a yang tidak ada, tugasnya tidak menguji chamber |

A1 butir 1-3 memang tidak dikerjakan, dan itu disebutkan di bagian "yang tidak
saya periksa". Sesuai arahan. Tetap terbuka.
