# 14_PROTOTYPE_QA_STANDARD.md — Blueprint Standar QA 3 Lapis

Disusun 20 Agustus 2026. Mencatat standarisasi QA internal untuk Orkestrator (Automated Chamber 2.0).

Mengingat Orkestrator di era V2 bertindak sebagai Pelaksana yang bekerja tanpa campur tangan Manusia (hingga hasil akhir disetorkan), standar QA internal tidak boleh hanya mengandalkan pengecekan sintaks (AST). 

## Arsitektur 3 Lapis QA (QA Triad)
Kode yang ditulis oleh Agen *Executor* **wajib** melewati tiga gerbang berikut secara berurutan:

1. **Gate 1: Syntax Guardian (Deterministik AST)**
   - Mengecek *typo*, kurung yang hilang, atau pelanggaran linting standar.
   - Paling murah dan instan.

2. **Gate 2: QA Guardian (Deterministik Mesin)**
   - Mengeksekusi tes mesin (misal: `npm test`, `pytest`, atau `tsc`).
   - Memastikan bahwa meski sintaksnya benar, kodenya tidak memicu *crash* logis saat dijalankan.
   - Bersifat *binary* (Lulus / Gagal).

3. **Gate 3: Reviewer Subagent (Semantik LLM)**
   - Gerbang termahal dan terakhir. 
   - Walau kode jalan secara logis, Orkestrator memanggil *Reviewer Subagent* (yang hanya memiliki akses *read-only*) untuk membandingkan kode tersebut dengan "Niat/Instruksi Asli Manusia".
   - **Tujuan:** Mencegah masalah pemahaman (Misal: Kode jalan mulus, tombol bisa diklik, tapi warnanya Biru, padahal *User* minta warna Merah).

## Mekanisme Anti-Keras Kepala
Jika pada salah satu dari tiga gerbang tersebut sang *Executor* gagal hingga 3 kali berturut-turut, sistem tidak akan terus membuang token. Gerbang akan menjatuhkan vonis **STALEMATE DETECTED** dan memicu *Git Rollback* (Sprint 4).

Ini memastikan bahwa hasil yang keluar dari Automated Chamber 2.0 dan disetorkan kepada manusia memiliki jaminan keandalan (*Reliability Guarantee*) sebesar 99%.
