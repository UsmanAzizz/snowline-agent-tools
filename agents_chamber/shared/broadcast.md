# Broadcast

## Current Version
**v7 | 06 Agustus 2026 | mencakup RULES.md s/d Rule #12 | Penambahan Carve-out #2 Ledger #1**

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

**[UPDATE ATURAN - Pengecualian Ledger #1 (Task 75)]**
Telah ditambahkan **Carve-out kedua (Exception 2)** pada Ledger #1 di `RULES.md`. Modul internal murni (stateless, tanpa efek samping, tidak menyentuh file) seperti `tree_gen.py` kini diizinkan untuk di-share antar-tool. Hal ini diputuskan untuk menghindari risiko drift akibat duplikasi paksa (copy-paste). 

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

**[AUDIT - Temuan Critical companion_cli.py (Task 77 Kandidat)]**
Audit ekosistem lengkap (06 Aug 2026) menemukan:
- **F4 (Critical):** `companion_cli.py` crash saat dipanggil langsung — `import companion` gagal karena `companion.py` tidak ada. Entry point resmi `python -m companion` tidak terdampak.
- **F5 (Medium):** `_plan` trigger — `needs_grilling=False` tapi `clarification_note` bilang "MUST NOT jump to implementation". Hasil akhir benar (mitigated by `get_agent_action()`), tapi misleading.
- **F2 (Medium):** Task 72 gap dalam task_board — Rule #7 violation. Perlu konfirmasi dari TL.
Full report: `shared/archive/audit_2026_08_06_chamber_companion.md`

**[AUDIT - Stress Test Ecosystem (Task 77, 26 test companion)]
Stress test 16 tool + companion selesai (06 Aug 2026):**
- 14/16 tool ✅ PASS
- `crash_decoder` & `db_extractor` — UX bug: --help treat sebagai file path (bukan flag). Fungsi normal tidak terdampak.
- `scope_lock.json` — config mismatch: path menunjuk ke "D:/project/scarecrow/for_claude" (project berbeda). Scope gate di auto_scaffolder/context_mapper impacted.
- 0 regressi pada fix B1/B2/F4/F5/F6.
Full report: `shared/archive/stress_test_2026_08_06_full_ecosystem.md`

---

## Acknowledgments
*(Hanya diisi oleh pemilik posisi masing-masing dengan format `[Posisi] vX OK` setelah membaca)*
- `[QA]` : v7 OK
- `[Executor_01]` : v7 OK
- `[TL]` : v7 OK
