# Broadcast

## Current Version
**v6 | 05 Agustus 2026 | mencakup RULES.md s/d Rule #12 | Klarifikasi Otoritas Rule #8**

## Standing Notices
*(Permanent rules and reminders)*

**[PENTING - KLARIFIKASI OTORITAS (Rule #8)]**
Rule #8 telah direvisi. TL **Bukan** pemegang otoritas aturan Chamber, melainkan **Juru Tulis (Perpanjangan Tangan)** dari PM. Seluruh otoritas tetap ada di PM. PM bebas untuk melakukan edit file secara langsung jika diperlukan.

**[PENTING - ATURAN BARU (Rule #12)]**
Telah ditambahkan **Rule #12 (Anti-Drift Check)** ke `RULES.md`. Setiap Executor wajib mensinkronisasi perubahan dari versi *live* (`.agents/`) ke versi *template* (`snowline_toolkit/templates/`) sebelum menyelesaikan task, agar *source code* tidak tertinggal.

**[PENTING - UPDATE JURISDIKSI]**
Mulai saat ini (Task 61), segala pembaruan yang bersifat administratif (edit `RULES.md`, `AGENTS.md`, `AGENTS_TEMPLATE.md`, `task_board.md`, dan *connector*) adalah **Yurisdiksi Eksklusif TL**.
Executor **DILARANG KERAS** mengedit file administratif tersebut. Jika Executor menerima *task* campuran, Executor wajib menolak bagian administrasinya (biarkan TL yang mengurus) dan Executor hanya fokus mengubah *source code* (Python/JS).

## One-Time Pings
*(Ephemeral messages - clear once acknowledged)* 

**[UPDATE ATURAN - Alur Sinyal Deterministik ('')]**
- **Rule #2 (Signal Protocol)** disederhanakan: PM hanya akan menggunakan satu kode tunggal yaitu `''` (tanpa variasi nama peran).
- Makna sinyal `''` ditentukan oleh alur kerja yang sedang berjalan:
  - TL -> Executor -> TL -> QA -> TL.
  - Setiap kali menerima `''`, agen otomatis tahu bahwa giliran telah berpindah kepadanya.
  - Di akhir task, TL mereset semua sektor menjadi *Idle*. 

**[UPDATE ATURAN - Filosofi Chamber]**
- **Philosophy Update**: Telah ditambahkan `DESIGN_PHILOSOPHY.md` sebagai panduan dasar. QA mengabadikan kutipan PM tentang roh dari "Companion" & "Chamber" agar setiap agen memahami esensi kolaborasi dalam sistem ini.

**[UPDATE ATURAN - Penyiaran Susulan Rule #8 & #9]**
- **Rule #8 (Strict Single-Writer)**: PM tidak lagi mengedit dokumen administratif. Hanya TL yang berhak write ke `RULES.md`, `project_context.md`, dan `task_board.md`.
- **Rule #9 (No Pre-filling Verdicts)**: DILARANG keras mem-prefill OUTBOX milik agen lain.

**[UPDATE ATURAN BARU - Mandatory QA Validation]**
Untuk seluruh agen (khususnya QA dan TL), aturan baru **Rule #11** telah ditambahkan ke `RULES.md`:
Setiap penyelesaian task dari Executor **wajib diserahkan ke QA** untuk audit akhir. TL tidak lagi memiliki wewenang untuk menutup task (DONE) secara sepihak tanpa *verdict* (keputusan) PASS dari QA. QA adalah otoritas terakhir penentu penutupan task.

---

## Acknowledgments
*(Hanya diisi oleh pemilik posisi masing-masing dengan format `[Posisi] vX OK` setelah membaca)*
- `[QA]` : v6 OK
- `[Executor_01]` : v6 OK
