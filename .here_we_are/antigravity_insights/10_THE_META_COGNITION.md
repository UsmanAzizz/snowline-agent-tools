# Snowline V2: The Meta-Cognition (Sprint 5)

Dokumen ke-10 (dan yang pamungkas) ini merangkum arsitektur di mana agen AI tidak lagi statis, melainkan berevolusi dan dikendalikan secara manusiawi. Ini adalah ujung batas riset kecerdasan buatan (*Meta-Learning & Neuro-Symbolic*).

## 1. Meta-Learning (Agen yang Mengajar Dirinya Sendiri)
Jika agen gagal menjalankan tugas, ia tidak boleh mati begitu saja. Ia harus berefleksi.
- **Solusi Arsitektural (Reflexion & Active Compression):** Saat menemui jalan buntu, agen dipaksa menulis "Alasan Kegagalan". Orkestrator kemudian memampatkan log kegagalan tersebut menjadi satu aturan absolut, lalu menyimpannya ke `.agents/learned_rules.md`. Besoknya, agen tidak akan pernah mengulangi kesalahan logis yang sama.
- **Pencegahan Token Bloat (Importance Decay):** Aturan yang sudah usang atau jarang terpicu akan otomatis dihapus (*Decay*) perlahan dari memori agar *system prompt* tidak meledak.

## 2. Neuro-Symbolic AI (Mengobati Halusinasi Absolut)
LLM (probabilistik) payah dalam matematika dan jaminan keamanan absolut.
- **Solusi Arsitektural (The Solver Guardrail):** Saat melakukan *refactoring* krusial, agen tidak langsung menulis kode. Ia merumuskan niatnya, lalu orkestrator melemparkannya ke *Deterministic Solver* (seperti Z3 Theorem Prover atau Type Checker). Jika ada celah 1% saja, *Solver* menolak kode tersebut dan memaksa LLM merevisinya hingga 100% *Provable Correct*.

## 3. Agentic UI & HITL (Dasbor Penguasa)
Membaca log dari 10 agen yang bergerak paralel akan menghancurkan pikiran manusia.
- **Solusi Arsitektural (Semantic Zooming):** UI orkestrator tidak boleh menampilkan teks mentah. Ia hanya menampilkan pohon status (Goal -> Trace). Tampilkan label "Running", "Blocked", atau "Completed".
- **Sistem Approval Bertahap:** Manusia hanya dipanggil melalui indikator visual saat agen membutuhkan otoritas. UI wajib menampilkan *Diff Preview* (Apa yang berubah) dan *Granular Buttons* (Izinkan Semua, Izinkan 1 Langkah, Edit Draf, atau Tolak).
