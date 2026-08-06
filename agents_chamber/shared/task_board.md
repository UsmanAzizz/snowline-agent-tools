# Task Board

*Tech Lead use only - workers never write here*

## Active Tasks
*(None currently assigned through chamber system)*

## Position Status & Active Tasks
*(Single Source of Truth untuk status agen - dilarang menggunakan seksi CURRENT TASK di connector.md)*

| Position | Role | Current Active Task / Status | Notes |
|---------|--------|-----------------------------|-------|
| `pos/0. PM` | **Project Manager** | Mendelegasikan seluruh pembaruan Ledger/Admin ke TL | (Human) |
| `pos/1. TL` | **Tech Lead** | *Idle - Menunggu instruksi PM* | Gemini (Antigravity) |
| `pos/2. QA` | **QA / Reviewer** | *Idle - Menunggu instruksi TL* | Opus 4.8 (Claude Code) |
| `pos/3. Executor/Executor_01` | **Executor** | *Idle - Menunggu instruksi TL* | Claude Code |
| `pos/3. Executor/Executor_02` | **Executor** | *Kosong* | (Reserved) |
| `pos/3. Executor/Executor_03` | **Executor** | *Kosong* | (Reserved) |
| `pos/3. Executor/Executor_04` | **Executor** | *Kosong* | (Reserved) |
| `pos/3. Executor/Executor_05` | **Executor** | *Kosong* | (Reserved) |

## Completed (Recent)
- **Task 75:** Perbaikan Companion (Isu Multi-Match) & Ledger Carve-out #2 - **SELESAI** (QA PASS). Logika multi-match kini mengeluarkan KONFIRMASI dengan tool teratas beserta alternatifnya. Fallback rate membaik drastis (10 -> 4). Ledger diperbarui untuk mengizinkan stateless internal modules.
- **Task 74:** Enforcement `check_scope` pada Tool Berdampak (C1) - **SELESAI** (QA PASS). `import_fixer`, `context_mapper`, dan `auto_scaffolder` kini mengecek `is_file_in_scope` pada target individual file (bukan *folder*), memblokir penulisan ke luar area.
- **Task 73:** Hapus Salinan Bayangan `is_file_in_scope` di `replace_text.py` (C2) - **SELESAI** (QA PASS). *Path resolution* telah diperbaiki sehingga impor keamanan berjalan normal tanpa *crash*.
- **Task 71:** Update README.md & Bugfix Reinstall - **SELESAI** (QA PASS). Dokumentasi baru untuk *status* dan *reinstall*, bug *dry-run* konfirmasi `reinstall` diselesaikan.
- **Task 70:** Penyederhanaan Logika Aksi CLI - **SELESAI** (QA PASS). Logika `--apply` 100% dipastikan bebas bug/kombinasi-hilang.
- **Task 69:** Penambahan Pesan Aksi Status CLI - **SELESAI** (QA PASS). Pesan *actionable* berhasil ditambahkan ke CLI.
- **Task 68:** Konsep "Latest" Menyeluruh - **SELESAI** (QA PASS). Status lapor paket & project, `reinstall --latest` mendownload Git secara aman.
- **Task 67:** Perbaikan Alur Instalasi CLI - **SELESAI** (Revisi disetujui QA). Menambahkan `--force`, fungsi `reinstall`, & pencegahan sukses-palsu auto-update. Tidak memerlukan sinkronisasi template (Rule #12 n/a).
- **Task 66:** Perbaikan Keyword `crash_decoder` - **DONE** (Hapus kata luas, 0 false positive, synced).
- **Task 65:** Perbaikan Logika Companion - **DONE** (QA PASS) - (C1 word boundary + imbuhan, C2 sort confidence dipisah, C3 len>=2->CLARIFY, C4 hapus Memory, D TOOL_REGISTRY sinkron).
- **Task 7.3:** Uji Coba Threshold (Mandatory Halt) - **DONE** (Lulus audit final QA di Task 64)
- **Task 64:** Audit Final Task 63 - **DONE**
- **Task 63:** Fix Guardian Cache Invalidation & Template Sync - **DONE** (QA PASS)
- **Task 61-62:** Remediasi Task 7.3 & Audit Ulang Guardian - **DONE**
- **Task 59-60:** Audit Mandatory Halt Rule (#6) & Aturan Single-Writer (#8) - **DONE**
- **Task 58:** Fix API Key & AGENTS_TEMPLATE Bug - **DONE**
- **Task 55-57:** Evaluasi Skema Splicer & QA Verification - **DONE**
- **Task 54:** *Dibatalkan / Tidak dipakai*
- **Task 53:** Eksekusi Governance Package (Item 1-5) - **DONE**
- Task 42-43: Chamber Optimizations (Arsip & Ledger)
- Task 40: Evaluate Architecture Concepts
- Task 39: On-the-Fly Recursive Traversal + `--depth` Parameter

## Notes
- Both Claude Code and Gemini now have chamber positions
- "Position" (pos_XX) = persistent folder survives agent resets
- agents_chamber/ enables parallel agent trial run
- When Tech Lead assigns a new position: Tech Lead creates appropriate folder first, then notifies the agent
- Existing positions do NOT create their own folders - wait for Tech Lead assignment
