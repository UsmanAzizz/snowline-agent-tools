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
