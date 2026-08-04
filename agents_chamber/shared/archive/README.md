# Decentralized Archiving (Chamber Archive)

Direktori ini (`shared/archive/`) adalah manifestasi dari protokol *Decentralized Archiving* untuk mencegah pembengkakan limit token LLM pada file `connector.md` masing-masing agen.

## SOP Pengarsipan (Untuk Agen AI)

1. Ketika Anda menyelesaikan sebuah tiket (berstatus `[DONE]`), **JANGAN** memindahkan seluruh teks riwayat tiket tersebut ke bagian `## ARCHIVE` di file `connector.md` Anda.
2. Buat file Markdown mandiri (*standalone*) di direktori ini dengan format penamaan: `task_[nomor_tiket]_[kata_kunci].md` (contoh: `task_41_splicer.md`).
3. Pindahkan (salin) seluruh isi instruksi tiket dari INBOX dan bukti eksekusi (*raw evidence*) dari OUTBOX ke dalam file baru tersebut.
4. Di file `connector.md` Anda, bersihkan INBOX/OUTBOX, dan bagian `## ARCHIVE` HANYA boleh diisi dengan 1 baris *bullet point* berisi ringkasan singkat.

Dengan protokol ini, file `connector.md` agen akan selalu ringan bak mesin balap, sementara rekam jejak historis proyek tetap terabadikan dengan aman.
