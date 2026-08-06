# Connector: QA / Reviewer

See `ONBOARDING.md` in this same folder for role definition, mandatory/forbidden rules, and coordination flow.

## Signal Protocol
When done: write to OUTBOX below, then say "Task complete - please signal TL" in your terminal response.

---

## ACTIVE TASK - INBOX

*(Kosong)*

---

## ACTIVE TASK - OUTBOX (QA -> TL)

**Status Check QA Session 2026-08-06**

**Inbox:** Kosong - tidak ada task aktif.
**Task board discrepancy:** task_board.md menunjuk "Verifikasi Task 80" tapi tidak ada instruksi di INBOX QA, tidak ada mention Task 80 di broadcast, dan TL OUTBOX menunjukkan status lama (catatan Task 66).
**Recommendation:** TL perlu update task_board.md untuk mencerminkan status aktual (Task 79 DONE, tidak ada Task 80 pending).

**Status QA:** Idle - Menunggu sinyal `''` dari PM dengan task baru.

---

**Full Ecosystem Test — Project Nyata: D:\project\scarecrow\for_claude**

Full report: `shared/archive/full_ecosystem_test_2026_08_06_scarecrow.md`

**Hasil: 33/33 PASS, 0 FAIL, 0 CRASH**

| Kategori | Tested | PASS |
|----------|--------|------|
| Companion intent | 20 | 20 |
| Companion task lock | 3 | 3 |
| Tools direct | 10 | 10 |
| UX flags | 4 | 4 |

**Companion highlights:**
- 14 tool matching tests: semua tepat ✅
- Multi-tool: import_fixer + smart_search ✅, smart_tree + clean_sweeper ✅
- EXECUTE path: "generate component NavBar" ✅
- _plan trigger: MEDIUM + CLARIFY ✅
- Task lock: start/status/end ✅

**Tools highlights:**
- smart_search: found export default in 3+ files ✅
- scope_guardian: scope lock worked for auto_scaffolder ✅
- project_guardian: CRITICAL=8, HIGH=7 ✅
- auto_scaffolder: dry-run dengan scope ✅
- impact_analyzer: App.jsx → index.jsx dependency ✅

**Temuan minor (bukan bug):**
1. ".agentssssss" typo folder — bukan bug tool
2. "evaluate" (EN) ≠ "evaluasi" (ID) — design intention
3. db_extractor timeout pada project besar tanpa DB config

---

## BACKLOG

- scope_lock.json gitignore question (pending PM konfirmasi — bukan bug)
- Bonus Findings: F-B1 (batass typo, di OUTBOX TL), F-B2 (usage logging design gap)

---

## ARCHIVE

- [Full Test 2026-08-06] Ecosystem on real project (scarecrow/for_claude) — 33 tests, 33 PASS. Report: shared/archive/full_ecosystem_test_2026_08_06_scarecrow.md
- [Task 79] Kontradiksi snowline status vs update - SELESAI. QA PASS.
- [Task 78] Perbaikan UX --help + Scope - SELESAI. QA PASS.
- [Task 77] Perbaikan Bug Companion F4/F5/F6 - SELESAI. QA PASS.
- [Task 76] Backlog B1 & B2 Companion - SELESAI. QA PASS.
- [Stress Test 2026-08-06] Full Ecosystem (synthetic) — 16 tool + companion. Report: shared/archive/stress_test_2026_08_06_full_ecosystem.md
- [Audit 2026-08-06] Full Ecosystem Audit — 7 findings. Report: shared/archive/audit_2026_08_06_chamber_companion.md.
