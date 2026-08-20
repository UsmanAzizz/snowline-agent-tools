# 13_PROTOTYPE_COMPANION_V2.md — Blueprint Companion sebagai Dispatcher

Disusun 20 Agustus 2026. Mencatat hasil mutasi agen Companion menjadi *Traffic Controller* untuk Automated Chamber.

## 1. Pergeseran Paradigma Intensi
Pada versi Snowline sebelumnya, Companion memetakan kata kerja ke nama fungsi statis (misal: "cari" ➔ `smart_search`).
Dalam arsitektur *Automated Chamber 2.0*, pemetaan fungsi satu-per-satu diurus di level *Tool Access* per Sub-Agen. Peran Companion bergeser menjadi tingkat arsitektural yang lebih tinggi: **menentukan Rute Agen**.

## 2. Mekanisme Routing (Intention Matrix)
Berdasarkan *dry-run* pada skrip `companion_v2_poc.py`, matriks baru membagi lalu lintas menjadi tiga jalur utama:
1. **SOLO_AGENT:** Untuk kueri ringan (tanya jawab, pencarian fungsi) yang tidak berisiko merusak *codebase*. Dieksekusi seketika.
2. **CHAMBER_PIPELINE:** Dipicu oleh kata kunci manipulatif ("perbaiki", "refactor"). Companion melempar beban ini ke Orkestrator (State Machine), yang akan memutar roda Investigator ➔ Handoff ➔ Executor.
3. **SUBAGENT_AUDITOR:** Dipicu oleh kata kunci spesialis ("audit", "keamanan"). Companion melempar tugas ke sub-agen terpisah tanpa membuang waktu Investigator.

## Kesimpulan
Companion adalah gerbang terluar (Front-Door) Snowline V2. Dengan perannya yang telah di-refactor menjadi Dispatcher Sub-Agen, pengguna (manusia) tidak lagi perlu memikirkan apakah mereka harus memanggil skrip *Chamber* secara manual. Cukup masukkan perintah seperti biasa, dan Companion akan menyortirnya ke rel eksekusi yang tepat.
