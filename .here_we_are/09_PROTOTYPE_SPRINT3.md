# 09_PROTOTYPE_SPRINT3.md — Blueprint Presisi & Anti-Stalemate

Disusun 20 Agustus 2026. Mencatat hasil dari *Dry-Run* prototipe Sprint 3, berfokus pada "Presisi di atas Efisiensi".

Berdasarkan riset mendalam terhadap kegagalan dominan agen otonom (SWE-bench), kita menemukan bahwa LLM rentan mengalami *Reasoning-Driven Hallucination* dan *Cognitive Deadlocks* (berputar-putar memperbaiki tes yang sama). Oleh karena itu, dua lapisan pelindung telah diprototipekan secara aman (tanpa mengubah *core project*) di direktori `v2_prototypes`.

## 1. Syntax Guardian (Lapis Pertama - Presisi)
Meminta LLM menebak logika secara probabilistik sangat rapuh. Guardian ini bertindak sebagai *Deterministic Solver*.
- **Konsep:** Sebelum sebuah file diizinkan untuk disimpan ke sistem operasi, kodenya harus lolos parsing *Abstract Syntax Tree* (AST).
- **Hasil Prototipe (`syntax_guardian.py`):** Berhasil mencegat dan memblokir seketika file Python yang memiliki kurung buka tak tertutup (*exit code 1*).
- **Arah Implementasi:** Fungsi ini (yang sebagian sudah ada di `auto_scaffolder`) harus diekstraksi menjadi gembok universal untuk semua aksi penulisan agen (seperti *Agent Computer Interface* milik SWE-agent).

## 2. Loop Detector / Action Hashing (Lapis Kedua - Anti-Stalemate)
Agen sering kehilangan akal dan melakukan eksekusi perintah yang sama persis berulang kali ketika menghadapi *traceback* galat yang panjang.
- **Konsep:** Menggunakan algoritma *hashing* deterministik (SHA-256) untuk mencatat histori argumen aksi (misalnya, `{"test_file": "App.test.jsx"}`).
- **Hasil Prototipe (`loop_detector.py`):** Berhasil membiarkan 2 percobaan pertama, dan melempar sinyal `TERMINATE` secara paksa (memblokir eksekusi) saat mendeteksi *hash* yang sama untuk ketiga kalinya.
- **Arah Implementasi:** Harus diintegrasikan ke *middleware* `orchestrator` atau `companion`. Jika loop terdeteksi, langkah pamungkas yang direkomendasikan adalah melakukan **Rollback Konteks** (`git reset --hard`) untuk membebaskan LLM dari racun memori *error* yang berulang.

## Kesimpulan Arah Baru
Evolusi Snowline berikutnya tidak lagi membahas pemangkasan token, melainkan tentang memasang **Jaring Pengaman Deterministik**. Prototipe ini membuktikan bahwa kita bisa memutus kebuntuan agen dengan *soft-locks* tanpa memerlukan *sandbox* sekelas Docker.
