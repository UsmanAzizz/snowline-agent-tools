# Connector: Executor

See `ONBOARDING.md` in this same folder for role definition, mandatory/forbidden rules, and coordination flow.

## Signal Protocol
When done: write to OUTBOX below, then say "Task complete - please signal TL" in your terminal response.

---

## ACTIVE TASK - INBOX

*(Kosong - Menunggu instruksi TL)*

---

## ACTIVE TASK - OUTBOX (Executor -> TL)

*(Kosong)*

---

## BACKLOG

*(Kosong)*

---

## ARCHIVE

- [Task 79] Kontradiksi snowline status vs update - SELESAI. Root cause: update() hanya cek st_mtime, tidak cek git commit. Fix: tambah pengecekan package commit di update(). Konsisten sekarang. MD5: 31c415c041d34a4118347fbe3d59332c.
- [Task 76] Backlog B1 & B2 Companion - SELESAI. B1 ("perlu konfirmasi"), B2 (empty set guard before issubset). SYNCED. MD5 identical.
- [Task 77] Bug Companion F4/F5/F6 - SELESAI. F4 (path resolution companion_cli.py), F5 (_plan contradiction), F6 (entities=None guard core_grilling.py). SYNCED. 3/3 test passed, MD5 identical.
- [Task 78] Perbaikan UX --help + Scope - SELESAI. crash_decoder --help exit 0, db_extractor --help exit 0, scope_guardian sudah CWD-based (tool membaca scope_lock.json dinamis dari os.getcwd()). SYNCED 2 file ke template.
- [Task 75] Companion Multi-Match - SELESAI. get_agent_action multi-match -> KONFIRMASI, main() tampilkan tool teratas + alternatif. SYNCED. 2 test passed, MD5 identical.
- [Task 76]
- [Task 75] Perbaikan Companion Multi-Match - SELESAI. cli.py: get_agent_action() multi-match -> KONFIRMASI, main() tampilkan tool teratas + alternatif. SYNCED ke template. 2 test passed, MD5 identical.
- [Task 74] Enforcement check_scope - SELESAI (REVISI). context_mapper: check per-file (structure_file, patterns_file), auto_scaffolder: check filepath (bukan target_dir), import_fixer LULUS (source_file spesifik). SYNCED ke template. MD5 identical.
- [Task 73] Perbaiki Path Resolution is_file_in_scope - SELESAI (REVISI). Tambah sys.path resolution sebelum import scope_guardian (shadow copy tetap dihapus). SYNCED ke template. 3 test passed (no ModuleNotFoundError, BLOCKED out-of-scope, MD5 identical).
- [Task 71] Update README.md & Bugfix Konfirmasi Reinstall - SELESAI (REVISI). Fix: tambah confirm_msg ke uninstall(), fix double "Run", README tambahkan --apply, fix terminology. Commit 34fa7fd, pushed to main.
- [Task 70] Penyederhanaan Logika Aksi CLI - SELESAI. Hapus else dari blok agents_tersedia (line 636), hapus duplikasi di summary (line 651). snowline update --apply sekarang di satu lokasi.
- [Task 69] Penambahan Pesan Aksi Status CLI - SELESAI. Tambah "-> snowline update --apply" ke summary "Ada file project tersedia update." (line 651). Verifikasi: 3 lokasi aksi (inline project available, inline package behind, summary).
- [Task 68] Status CLI Lapis Ganda - SELESAI. U1 (status() dual layer: Paket + .agents), U2/U3 (reinstall --latest dari GitHub). Live-test passed.
- [Task 67] Perbaikan Alur Instalasi CLI - SELESAI (REVISI). Fix: tambah `force` ke logika penyalinan file (line 263). Live-test: init --apply (ASLI dipertahankan) + init --apply --force (ASLI tertimpa, Pulih dari template).
- [Task 66] Perbaikan Keyword crash_decoder - SELESAI. Hapus "perbaiki", "perbaikan", "memperbaiki", "masalah" dari keywords. Keyword inti error/bug/exception tetap berfungsi. SYNCED ke template.
- [Task 65] Perbaikan Logika Companion - REVISI DONE. Fix 1 (C2 sorting dipindahkan keluar dari blok needs_clarify), Fix 2 (C1 imbuhan TOOL_REGISTRY: menganalisa, memperbaiki, mengganti, membersihkan, dll). SYNCED ke template. PENDING QA (Rule #11).
- [Task 63] Fix Guardian Cache Invalidation & Template Sync - DONE. Guardian.py source hash ditambahkan ke dir_sig, filter path-based, disinkronkan ke 3 lokasi (md5 verified identical).
- [Task 61] Remediasi Task 7.3 & Perbaikan Guardian - DONE. CRITICAL: 18→5. Perubahan: `.venv` excluded, `guardian.py` self-scan fixed, Google/AWS regex added, Bearer diperketat, Rule #7 sinkron. Live-test via `python project_guardian/guardian.py`.
- [Task 50 & 51] `_plan` Convention & Grill-First: DONE. Added Rule #7 to AGENTS_TEMPLATE.md and fast-path intercept to core_intent.py (substring `in` check per QA revision). Syntax verified.
- [Task 49] Interactive `snowline status` with Detached Handoff: DONE. Modified `snowline_toolkit/cli.py`.
- [Task 45] Full Toolkit Stress Test: DONE. Tested 10 tools - all PASSED.
- [Task 44] Indentation Fallback for splicer.py: DONE.
- [Task 41] Build Surgical Code Splicer: DONE (required Manual Override after initial shortcut attempt).
- [Task 39] On-the-Fly Recursive Traversal + `--depth` Parameter.
- [Task 38] impact_analyzer Python blindness + JS explicit extension fix.
- Trial Task: Clean up Tool Inventory table.
