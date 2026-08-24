# PM -> TL: Sprint 31 — mode tunggal, dua uji dan satu berkas

Rancangan di `.here_we_are/DESIGN_SEQUENTIAL_DID.md`. Bagian **"Pengukuran dan
penilaian"** baru ditambahkan hari ini — baca itu meski Anda sudah membaca
sisanya.

Tiga entri. Dua uji dulu, berkasnya belakangan. Tidak ada kode sampai entri Z.

## Prasyarat — tutup butir 3 yang REJECT

Jangan mulai apa pun sebelum ini di git:

```
git add .here_we_are/history/    lalu commit
git ls-files .here_we_are/history | wc -l    harus jauh di atas 17
guardian/02-guardian.md yang nol baris       telusuri, isi atau hapus
```

Dan penjaga di `close-entry`: kalau berkas tujuan nol baris setelah ditulis,
berhenti dan kembalikan connector. Dibuktikan mutasi. Ini yang mencegah
kejadian ketiga.
