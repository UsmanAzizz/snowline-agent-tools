# Connector: Tech Lead (TL)

See `ONBOARDING.md` in this same folder for role definition, mandatory/forbidden rules, and coordination flow.

## Signal Protocol
When done: write to OUTBOX below, then say "Task complete - please signal PM" in your terminal response.

---

## ACTIVE TASK - INBOX

**[New Task]** - **`snowline status` Should Offer (Not Auto-Run) Force-Reinstall + Update When a Newer Version Exists**

**Goal:** `snowline status` stays read-only/safe by default (checks current vs. latest version), but if a newer version IS available, it should interactively OFFER the user a combined refresh: force-reinstall the package + run `snowline update --apply` in one confirmed step - not run automatically, requires explicit user confirmation (consistent with this project's dry-run-by-default, explicit-apply-required philosophy used everywhere else).

**This touches `snowline_toolkit/cli.py` - shipped to ALL end users, not personal dev-tooling** - so this needs the full rigor: your review, QA counterbalance, Executor implementation with live-testing, same as any user-facing tool change.

**Design questions for you and QA to work through:**
1. How does `status` determine "newer version available" - compare local installed version against what's on the GitHub repo (requires a network call)? What happens gracefully if there's no network access (should still show current status, just skip/skip-with-a-note the update-check part)?
2. What should the interactive prompt look like - a simple y/n, or show what's changed (changelog) before asking?
3. Should this be a NEW flag (e.g. `snowline status --check-updates`) or just always check by default now (with a fast/cached check to avoid slowing down every `status` call)?
4. Confirm the actual combined refresh command matches what's already documented in README.md (`pip uninstall ... && pip install ... --force-reinstall --no-cache-dir` then `snowline update --apply`) - don't invent new steps, reuse the exact proven sequence.

**Live-test required once approved:** simulate an outdated-version scenario, confirm `status` detects it and prompts correctly; confirm declining the prompt leaves everything unchanged; confirm accepting runs the full sequence correctly. Also test the up-to-date case (no prompt shown) and no-network case (graceful degradation).

**Status:** [READY]

---

## ACTIVE TASK - OUTBOX (TL -> PM)

**Laporan Eksekusi Proposal Solusi Proaktif (QA v2.1)**
Proposal telah disahkan oleh QA dan langsung saya operasionalkan:

1. **Fragment Fix (`<></>`):** Celah *blind-spot* JSX fragment temuan QA telah ditambahkan ke dalam rancangan kode (`isalpha() or line[j+1] == '>'`). Tugas bedah kode ini (bersama dengan uji terminal) telah saya delegasikan sepenuhnya ke **INBOX Executor_01**.
2. **Utilitas `update_header.py`:** Skrip CLI lokal ini telah selesai saya rakit di `shared/update_header.py`. Birokrasi administratif kini ditangani otomatis oleh skrip, sehingga ruang token AI kita tetap murni untuk logika (*Zero-Bloat* terbukti!).
3. **Pemisahan `DESIGN_PHILOSOPHY.md`:** Saya telah menciptakan file tersebut di dalam `shared/`. Semua landasan akademis (seperti teori *Role Specialization* MetaGPT) akan ditampung di sana, memastikan `project_context.md` tetap menjadi catatan fakta sejarah yang ringkas dan padat.

Semua tugas di meja TL (Task 47) telah tuntas tak bersisa.

Task complete - please signal PM

---

## CURRENT TASK / CONTEXT

- Active: Menunggu instruksi (task) berikutnya dari PM.
- Position: 1. TL (migrated from `gemini/pos_01` -> `pos/TL` -> current)

---

## BACKLOG

- PM's chamber-improvement suggestions (partially addressed, tracked in RULES.md now):
  1. Mandate checking Ledger/project_context.md for contradictions before writing new architectural rules - DONE (added to RULES.md TL mandatory list + Ledger footer note).
  2. Establish a clear test-sandbox convention - DONE (added to RULES.md Shared Rules #6).
  3. Mandate that any new file created must be documented - DONE (added to RULES.md Shared Rules #5).
  4. Keep task numbering strictly sequential/linear - noted inconsistency (39 -> 42/43 -> 41 -> 44 out of order), no formal rule added yet.
  5. QA should periodically review RULES.md/the Ledger itself for internal contradictions, not just review code - not yet formally assigned as a recurring QA duty.

---

## ARCHIVE

- [Tasks 41-44] Built Surgical Code Splicer & Indentation Fallback (VERIFIED by TL AND independently re-verified by PM). Rebuffed autonomous misbehavior via Manual Override.
- [Tasks 42-43] Chamber Optimizations (Decentralized Archiving & The Ledger in RULES.md). Rejected Semaphores.
- [Task 39] On-the-Fly Recursive Traversal + `--depth` Parameter (QA Tested & Verified).
- Design verdict: Graphify soft-integration REJECTED (dual-path maintenance bloat + staleness risk violating "verify from source" philosophy). Documented in project_context.md.
- Mandate accepted: Gemini is Tech Lead, ~3-week engagement, PM (human) oversees.
- Discussion: Hermes comparison - worktree isolation rejected (over-indexing on unvalidated problem), "amnesia as a feature" (mandatory session resets) accepted and added to RULES.md.
- Task 2 (Round 1): impact_analyzer 2 silent-wrong-result bugs found. Promoted to connector Task 38, fixed and verified.
- Task 1: safe_substitute_line() position bug found. Promoted to Task 37, fixed via reverse-iteration approach.
- Design verdict: chamber/orchestrator stay personal/manual-only, not integrated into installer.
- Folder structure renamed 3x: `claude_code/gemini` pos_XX -> `pos/[ROLE]` -> `pos/N.ROLE` -> `pos/N. ROLE` with Executor slots nested under `pos/3. Executor/` (current).
