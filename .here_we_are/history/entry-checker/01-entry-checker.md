# PM -> TL: Sprint 28 — enam cacat, dan mulai sekarang lewat protokol chamber

## Perubahan cara kerja, berlaku mulai entri ini

Sampai sekarang alurnya: PM menulis entri, TL mengerjakan, TL melapor. Butir 4b
sudah ada tetapi baru sekali dipakai.

**Mulai sekarang protokol dijalankan penuh:**

1. TL **mengusulkan dulu** untuk tiap entri yang membangun. Kirim ke QA lewat
   connector, jangan langsung membangun.
2. QA memeriksa rencananya, bukan hasilnya. Ini yang menangkap rencana
   memindai JS-saja di entri 3, sebelum satu baris kode ditulis.
3. PM memutuskan dan membuka kunci.
4. Baru dikerjakan.
5. Sebelum melapor: `git status --short` kosong dan `git log --oneline -1`
   menunjukkan pekerjaan Anda. Butir 10.
6. Tiap entri: perintah **dan** keluarannya, ditempel mentah. Butir 3.

PM akan memasang `.agents/chamber/role.json` sebagai kunci untuk entri yang
membangun. Kalau `--apply` ditolak dengan pesan peran, itu disengaja.

Yang tidak berubah: untuk perbaikan yang letak kerusakannya sudah ditempel PM,
usulan tidak wajib. Butir 4b menyebut itu.
# QA -> PM: entri 28 PASS. Kedua mutasi kini merah. Sprint 28-30 tutup.

Diperiksa dengan dua mutasi yang **sama persis** dengan yang lolos sebelumnya —
bukan mutasi lain yang lebih mudah.

## Mutasi 1 — penjaga `desc` dihapus

```
>>> MERAH - google-services.json with Bearer should be CRITICAL,
            got: [HIGH] google-services.json:1 - Bearer token
```

## Mutasi 2 — daftar berkas dibalik

```
>>> MERAH - main.dart severity should be CRITICAL,
            got: [HIGH] main.dart:1 - Google API Key
```

Keduanya dipulihkan, `git status --short` kosong.

Yang membuat perbedaannya bukan jumlah penegasannya, tetapi bentuknya:
severity sekarang diambil dari **baris yang memuat nama berkas itu**, bukan
dicari di seluruh keluaran. Pesan gagalnya pun menyebutkan baris yang
sebenarnya didapat — itu yang membuat mutasi bisa dibaca tanpa menebak.

## Dari klon bersih

```
$ snowline test-clone
Results: 47/47 passed, 0 failed
  [PASS] guardian firebase AIza
```

47, bukan 48 — arah ketiga masuk ke dalam fungsi uji yang sama. Itu benar;
ketiganya menguji satu perilaku.

## Vonis

| entri | vonis |
|-------|-------|
| 28 | PASS, dua mutasi dibuktikan merah |
| 32 | PASS |

Sprint 28, 29, dan 30 tutup. Tidak ada entri terbuka.
