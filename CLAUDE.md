# CLAUDE.md

Aturan kerja lengkap untuk project ini ada di `.agents/AGENTS.md`.
Baca file itu dan seluruh isi `.agents/rules/` sebelum memulai pekerjaan apa pun.

Dokumen ini sengaja singkat — semua aturan operasional sudah
terpusat di .agents/ agar konsisten dipakai baik oleh Gemini/Antigravity
maupun Claude Code, tanpa dua sumber kebenaran yang bisa berbeda.

## KODE SINGKAT (SHORTHAND) & ATURAN WAJIB EXECUTOR
1. **Sinyal Masuk (`""` atau `''` atau Enter kosong):**
   Ini berarti **"Cek INBOX kamu di `agents_chamber/pos/` dan kerjakan tugas yang ada di `connector.md`."** Jangan bingung, jangan bertanya balik, langsung baca *connector* milik posisimu (misal `pos/3. Executor/Executor_01/connector.md`).
2. **Sinyal Keluar (Wajib Tulis ke File!):**
   Setiap kali kamu selesai mengerjakan tugas, kamu **WAJIB MENGEDIT FILE `connector.md`** milikmu dan menuliskan laporan/bukti *raw output* ke bagian `## ACTIVE TASK - OUTBOX`. JANGAN hanya melaporkan hasil di *chat* terminal! TL hanya bisa membaca hasilmu jika kamu menyimpannya ke dalam file *connector* tersebut. Setelah file di-*save*, barulah ucapkan "Task complete" di terminal.
