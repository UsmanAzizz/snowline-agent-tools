# Connector: QA / Reviewer

See `ONBOARDING.md` in this same folder for role definition, mandatory/forbidden rules, and coordination flow.

## Signal Protocol
When done: write to OUTBOX below, then say "Task complete - please signal TL" in your terminal response.

---

## ACTIVE TASK - INBOX

*(Kosong - Menunggu instruksi TL)*

---

## ACTIVE TASK - OUTBOX (QA -> TL)

*(Kosong)*

---

## BACKLOG

*(Kosong)*

---

## ARCHIVE

- [Task 77] Perbaikan Bug Companion F4/F5/F6 - SELESAI. F4 (path resolution companion_cli.py standalone), F5 (_plan contradiction fixed), F6 (entities=None guard core_grilling.py). SYNCED ke template. 3/3 live-test passed, MD5 identical. QA PASS.
- [Task 76] Backlog B1 & B2 Companion - SELESAI. B1 (core_grilling: "perlu konfirmasi"), B2 (core_intent: empty set guard before issubset). SYNCED ke template. MD5 identical. QA PASS.
- [Task 75] Perbaikan Companion Multi-Match - SELESAI. cli.py: get_agent_action() multi-match -> KONFIRMASI, main() tampilkan tool teratas + alternatif. SYNCED ke template. 2 test passed, MD5 identical.
- [Task 74] Enforcement check_scope - SELESAI. context_mapper: check per-file, auto_scaffolder: check filepath, import_fixer LULUS. SYNCED ke template. MD5 identical.
- [Task 73] Perbaiki Path Resolution is_file_in_scope - SELESAI. Tambah sys.path resolution sebelum import scope_guardian. SYNCED ke template. 3 test passed, MD5 identical.
- [Audit 2026-08-06] Full Ecosystem Audit (Chamber + Companion) — 7 findings: 1 critical, 2 medium, 3 low, 1 N/A. Full report di shared/archive/audit_2026_08_06_chamber_companion.md.
