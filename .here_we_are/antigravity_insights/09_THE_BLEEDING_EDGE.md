# Snowline V2: The Bleeding Edge (Sprint 4)

Dokumen ini merangkum batas terluar (*the horizon*) dari rekayasa agen AI otonom. Hasil dari Sprint ini didedikasikan untuk mencegah "Kegagalan Sistemik" yang bahkan masih menjangkiti orkestrator raksasa bernilai triliunan rupiah seperti Devin dan SWE-agent.

## 1. Kegagalan Kognitif (SWE-bench Post-Mortem)
Devin dan SWE-agent gagal >70% pada kasus Github nyata. Analisis membuktikan bahwa kegagalan terbesar **bukan** karena keterbatasan fungsional (*tooling*), melainkan karena **Kelemahan Reasoning Logika**.
- **Cognitive Deadlocks:** Agen membuat satu kesalahan awal, lalu membawanya sebagai konteks yang salah ke langkah berikutnya (Efek Bola Salju), hingga terjebak mencoba solusi yang sama berulang kali.
- **Solusi Arsitektural:** Agen tidak boleh dibiarkan berlari tanpa henti. Harus ada *checkpoint* di mana agen dipaksa untuk merangkum apa yang telah ia coba dan mengapa itu gagal (Refleksi Kognitif), sebelum ia diizinkan melangkah lebih jauh.

## 2. Resolusi Sengketa (Melerai Perang Agen)
Dalam arsitektur *Multi-Agent*, Agen A dan Agen B bisa terjebak dalam *infinite loop* saling membatalkan kode satu sama lain (*Edit Wars*).
- **Solusi Arsitektural (The Judge Agent):** Orkestrator harus menghitung putaran interaksi (*Iteration Counter*). Jika batas terlewati tanpa konklusi, orkestrator membekukan kedua agen dan memanggil agen ketiga (**Agen Hakim**) yang memiliki memori terisolasi. Agen Hakim akan memutuskan resolusi akhir secara otoriter.
- **Solusi Arsitektural (Kill Switch):** Jika Agen Hakim gagal, putus koneksi API dan eskalasi langsung ke manusia (*User Intervention*).

## 3. Eksekusi Konkuren (Mencegah Kehancuran Paralel)
Membiarkan 5 agen mengedit *file* yang sama secara bersamaan adalah bencana *Race Condition*.
- **Solusi Arsitektural (Git Worktrees):** Jangan pernah menggunakan *File Locks/Mutex* tingkat OS, karena membuat agen lain menjadi "buta" (*Context Blindness*). Pendekatan absolut adalah membuatkan setiap agen **Git Worktree (Branch)** terisolasi secara fisik. Biarkan mereka bekerja di cabang masing-masing, dan biarkan Git (bukan LLM) yang menangani *merge conflict* di akhir sesi.
- **Solusi Arsitektural (Optimistic Concurrency Control):** Sebelum agen diizinkan menulis (*write*), orkestrator memvalidasi apakah *hash* file tersebut telah berubah sejak terakhir kali agen membacanya. Jika ya, tolak penulisan dan paksa agen membaca ulang *file* tersebut.
