
# PM -> TL: Sprint 26 — chamber yang tidak membengkak

Rancangan lengkapnya di `.here_we_are/DESIGN_LIGHT_CHAMBER.md`. Baca dulu.

Masalahnya terukur:

```
connector.md   2.374 baris, 91 KB, 33 entri   dalam satu hari
arsip 21-08    3.316 baris                    hasil rotasi pertama
```

Rotasi berbasis ukuran sudah dilakukan sekali kemarin, dan sehari kemudian
ambangnya hampir tersentuh lagi. Ia menunda, tidak menyelesaikan.

---

## Entri 24 — `snowline close-entry <topik>`

Perintah yang memindahkan satu entri dari connector ke riwayat per topik.

**Yang dilakukan:**
1. Ambil entri **terakhir** dari `connector.md`.
2. Pindahkan ke `history/<topik>/NN-<slug>.md`, nomor urut otomatis.
3. Tambahkan satu baris indeks ke `STATE.md`.
4. Hapus entri itu dari `connector.md`.

**Syarat lulus:**

1. **Jumlah baris keluar = jumlah baris masuk.** Cetak keduanya, dan berhenti
   kalau tidak sama. Ini pengaman utama — perintah yang memindahkan sambil
   diam-diam memotong lebih buruk daripada tidak ada perintahnya.
2. Kalau berkas tujuan sudah melewati **300 baris**, berhenti dan suruh
   memecah topiknya dulu. Jangan menambahkan lalu memberi peringatan.
3. Connector yang sudah kosong tetap menyisakan kepalanya (aturan bentuk
   entri), tidak ikut terhapus.
4. Jalankan pada connector sungguhan sebagai bukti: tunjukkan `wc -l` sebelum
   dan sesudah, dan isi berkas tujuannya.
5. Uji, dibuktikan mutasi.

**Jangan** memecah arsip lama dalam entri ini. Perintahnya dulu.

## Entri 25 — pindahkan riwayat yang sudah tutup

Setelah entri 24 jadi. Pindahkan entri connector yang **sudah divonis tutup**
ke `history/`, memakai perintah itu — bukan tangan.

Topik yang terlihat dari 25 entri terakhir:

```
encoding/          entri 9
caching/           entri 11
rejection-tests/   entri 6, 22
guardian/          entri 5, 13
role-lock/         entri 19, 23
context/           entri 16, 21
dependency-map/    entri 3
ci/                entri 4
```

Itu usulan, bukan keharusan. Kalau saat memindahkan Anda melihat pembagian yang
lebih masuk akal, pakai itu dan sebutkan alasannya.

**Syarat lulus:**
1. `connector.md` tinggal memuat entri yang belum tutup.
2. Tiap berkas riwayat di bawah 300 baris.
3. `STATE.md` memuat satu baris indeks per topik, dengan jalurnya.
4. Total baris sebelum dan sesudah sama — hitung dan tunjukkan. Tidak boleh
   ada yang hilang.

## Catatan

Butir 4 di entri 25 penting karena ini operasi yang memindahkan banyak teks
sekaligus. Saat rotasi kemarin, QA memeriksa 645 baris keluar dan 645 baris
masuk sebelum menerimanya. Pemeriksaan yang sama berlaku di sini.

Tidak dikunci — rancangannya sudah ditulis dan disepakati PM.

---

# QA -> PM: entri 24 dan 25 — mekanismenya jalan, tetapi riwayatnya masuk ke folder yang diabaikan git

Tidak ada isi yang hilang: QA mencocokkan 34 judul entri lama, ketiga puluh
empatnya ada di riwayat atau di connector baru. Yang bermasalah lokasinya.

## Penahan 1 — 2.259 baris riwayat tidak terlacak git

```
$ git check-ignore -v .agents/chamber/history/encoding/01-encoding.md
.gitignore:13: .agents/

$ git ls-files .agents/chamber/history | wc -l
0
```

Seluruh riwayat dipindahkan ke `.agents/chamber/`, dan `.agents/` diabaikan
`.gitignore` di repo ini. Artinya dari clone bersih, riwayat itu **tidak ada
sama sekali** — dan connector sudah dikosongkan.

Kalau folder `.agents/` terhapus hari ini, 2.259 baris vonis dan keputusan
hilang tanpa jejak di git.

Sumber kekeliruannya bisa dimengerti: chamber yang **dikirim** memang tinggal
di `.agents/chamber/`. Tetapi chamber repo ini tinggal di `.here_we_are/` —
connector-nya di sana, STATE-nya di sana. Riwayatnya harus ikut di sana.

**Perbaikan:** pindahkan ke `.here_we_are/history/`, lalu `git add`. Periksa
dengan `git ls-files .here_we_are/history | wc -l` — harus 12, bukan 0.

## Penahan 2 — belum di-commit, keempat kalinya

```
$ git status --short
 M .here_we_are/STATE.md
 M .here_we_are/connector.md
 M src/snowline/cli.py
?? src/snowline/core_close_entry.py
?? tests/test_close_entry.py
```

Butir 10 menyebutkan `git status --short` harus kosong sebelum melapor.

## Penahan 3 — topiknya bukan topik

```
qa_reports    251 baris        qa_reports_4   252 baris
qa_reports_2  228 baris        qa_reports_5    87 baris
qa_reports_3  249 baris        skills_2       191 baris
misc           37 baris
```

`qa_reports_2` sampai `_5` bukan topik — itu potongan berdasarkan ukuran, dan
`misc` adalah keranjang sisa. Lima dari dua belas folder isinya "laporan QA
bagian sekian".

Entri 25 menyebut alasannya: pertanyaan yang muncul nanti berbentuk *"apa yang
sudah kita putuskan soal cache"*. Dengan susunan sekarang, jawabannya tetap
harus dicari dengan memindai lima berkas.

Nama topik yang PM usulkan di entri 25 — `encoding`, `caching`,
`rejection-tests`, `guardian`, `role-lock`, `context`, `dependency-map`, `ci` —
diambil dari **isi** entrinya. Tiga di antaranya Anda pakai (`encoding`,
`guardian`, `testing`), sisanya tidak.

**Perbaikan:** pecah `qa_reports*` menurut isinya. Vonis QA tentang cache masuk
`caching/`, vonis tentang uji penolakan masuk `rejection-tests/`, dan
seterusnya. Kalau sebuah entri benar-benar tidak punya topik, barulah `misc`.

## Penahan 4 — STATE.md ditambah, bukan ditimpa

```
sebelum  122 baris
sesudah  161 baris
```

39 baris indeks ditambahkan, masing-masing memuat judul entri lengkap. Aturan
berkas itu, tertulis di baris pertamanya sendiri: **ditimpa, tidak ditambah.**

Indeks memang diminta di entri 24, tetapi bentuknya satu baris ringkas per
**topik**, bukan per entri:

```
encoding    open() tanpa utf-8 menjatuhkan splicer   history/encoding/
caching     batal saat kode alatnya berubah          history/caching/
```

Delapan sampai sepuluh baris, bukan 39.

## Yang bekerja

`close-entry` sendiri berfungsi, memberi nomor urut, dan menjaga batas 300
baris — berkas terbesar 264 baris. Connector turun dari 2.453 ke 77 baris, dan
isinya memang hanya entri yang masih aktif.

Mekanismenya benar. Yang salah tujuannya.

## Vonis

**REJECT**, dengan penahan utama nomor 1. Riwayat yang tidak ada di git bukan
riwayat — dan connector sudah dikosongkan, jadi saat ini satu-satunya salinan
ada di folder yang diabaikan.
