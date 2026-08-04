# Connector: QA / Reviewer

See `ONBOARDING.md` in this same folder for role definition, mandatory/forbidden rules, and coordination flow.

## Signal Protocol
When done: write to OUTBOX below, then say "Task complete - please signal TL" in your terminal response.

---

## ACTIVE TASK - INBOX

*(Empty - waiting for task)*

---

## ACTIVE TASK - OUTBOX (QA -> TL)

BROADCAST_ALPHA_OK

*(Empty - waiting for response)*

---

## CURRENT TASK / CONTEXT

- Active: Waiting for next assignment from TL
- Position: 2. QA (migrated from `gemini/pos_02` -> `pos/QA` -> current)

---

## BACKLOG

*(Use for tracking pending items)*

---

## ARCHIVE

- [Task 50 & 51] Desain `_plan` Convention & Grill-First: APPROVED WITH REVISION (Ganti intercept `startswith` menjadi substring `in` agar bulletproof).

- [Task 48] Verifikasi Final Eksekusi JSX Slash & Governance v2.1: VERIFIED & PASSED. (JSX fragment `<></>` dan self-closing tags kini diekstrak utuh tanpa fallback).
- [Task 44] Verify splicer.py Indentation Fallback: VERIFIED & PASSED -> see `shared/archive/task_44_splicer_fallback.md`
- [Task 43] Verify Chamber Optimization: VERIFIED & PASSED -> see `shared/archive/task_43_verify_chamber.md`
- [Task 42] Evaluate 3 Chamber Optimization Concepts: Approved Decentralized Archiving & Ledger in RULES.md, rejected Semaphores.
- [Task 41] Review Blueprint Surgical Code Splicer: Mandated Pure Copy-Paste over Shared Module (Isolation over DRY) - reconciled with Task 18 precedent via Ledger carve-out.
- [Task 40] Evaluate 3 Architecture Concepts: Verified Option 2 (Splicer) as priority, rejected 1 & 3 due to False Positive risks.
- [Task 39] Independent Testing of `--depth` Implementation: VERIFIED & PASSED. (dummy_test chain successful).
