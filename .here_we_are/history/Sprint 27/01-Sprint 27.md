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
