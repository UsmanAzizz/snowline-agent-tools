# Connector: Executor

See `ONBOARDING.md` in this same folder for role definition, mandatory/forbidden rules, and coordination flow.

## Signal Protocol
When done: write to OUTBOX below, then say "Task complete - please signal TL" in your terminal response.

---

## ACTIVE TASK - INBOX

**[Tech Lead Assignment]** - **Task 50 & 51: Implement `_plan` Convention & Grill-First**

QA telah menyetujui rancangan arsitektur untuk konvensi `_plan` dengan satu revisi wajib: pencegatan di `core_intent.py` harus menggunakan pencarian *substring* (`in`) agar *bulletproof* (bisa menangkap `_plan` di tengah kalimat).

**Instruksi Eksekusi:**
1. **Modifikasi `AGENTS_TEMPLATE.md`:** Tambahkan Rule #7 di bagian bawah `Aturan Inti` (sebelum blok Communication) seperti berikut:
   ```markdown
   **7. "Grill First" & Formal Planning (The `_plan` Convention):**
   - Jika prompt user mengandung kata kunci `_plan` (case-insensitive, contoh: `_plan buat fitur login`), Anda DIWAJIBKAN untuk masuk ke mode **Formal Planning** dan dilarang keras langsung memodifikasi kode.
   - **Tahap 1 (Grill First):** Jangan langsung berasumsi. Gunakan `deep_analyzer` atau `context_mapper` untuk membaca struktur proyek, lalu ajukan 1-2 pertanyaan terarah (Grill) kepada user untuk memperjelas batasan atau edge-cases.
   - **Tahap 2 (Blueprint):** Setelah asumsi terjawab, susun rencana eksekusi menggunakan struktur `plan_tracker/PLAN_TEMPLATE.md`. Bagian "Keputusan & Asumsi" dan "Menunggu Konfirmasi" wajib diisi.
   - **Tahap 3 (Explicit Approval):** Berhenti dan tunggu konfirmasi eksplisit dari user ("Proceed", "Silakan lanjut") SEBELUM mengeksekusi tool WRITE apa pun.
   ```

2. **Modifikasi `snowline_toolkit/templates/companion/core_intent.py`:** Di dalam fungsi `analyze_intent(user_input: str) -> AnalyzeResult:`, langsung setelah baris `text = user_input.lower()`, tambahkan *fast-path intercept*:
   ```python
       # ---------------------------------------------------------
       # Fast-Path: _plan convention trigger
       # ---------------------------------------------------------
       if '_plan' in text:
           return AnalyzeResult(
               input=user_input,
               keywords=["_plan"],
               entities=[],
               specificity="high",
               confidence_level="HIGH",
               needs_clarification=True,
               clarification_note="PLAN_MODE_TRIGGERED: User explicitly requested a formal planning phase. Agent MUST NOT jump to implementation. 1) Grill for gaps, 2) Write PLAN_TEMPLATE.md, 3) Wait for approval."
           )
   ```

**Verifikasi:**
- Gunakan alat *replace* untuk melakukan injeksi pada kedua file tersebut.
- Jalankan pengecekan sintaksis (`py_compile`) pada `core_intent.py`.
- Tuliskan laporan dan bukti penyisipan di OUTBOX.

**Status:** [DONE]

---

## ACTIVE TASK - OUTBOX (Executor -> TL)

**Task 50 & 51: Implement `_plan` Convention & Grill-First - COMPLETE**

**BROADCAST_ALPHA_OK**

---

## Implementation Summary

### 1. Modified `AGENTS_TEMPLATE.md` - Added Rule #7

**Location:** After Rule #4 (Communication), before "🔍 Bukti Live-Test" section

```markdown
**7. "Grill First" & Formal Planning (The `_plan` Convention):**
- Jika prompt user mengandung kata kunci `_plan` (case-insensitive, contoh: `_plan buat fitur login`), Anda DIWAJIBKAN untuk masuk ke mode **Formal Planning** dan dilarang keras langsung memodifikasi kode.
- **Tahap 1 (Grill First):** Jangan langsung berasumsi. Gunakan `deep_analyzer` atau `context_mapper` untuk membaca struktur proyek, lalu ajukan 1-2 pertanyaan terarah (Grill) kepada user untuk memperjelas batasan atau edge-cases.
- **Tahap 2 (Blueprint):** Setelah asumsi terjawab, susun rencana eksekusi menggunakan struktur `plan_tracker/PLAN_TEMPLATE.md`. Bagian "Keputusan & Asumsi" dan "Menunggu Konfirmasi" wajib diisi.
- **Tahap 3 (Explicit Approval):** Berhenti dan tunggu konfirmasi eksplisit dari user ("Proceed", "Silakan lanjut") SEBELUM mengeksekusi tool WRITE apa pun.
```

### 2. Modified `core_intent.py` - Fast-Path Intercept

**Location:** After `text = user_input.lower()` in `analyze_intent()` function (line 177)

```python
    # ---------------------------------------------------------
    # Fast-Path: _plan convention trigger
    # ---------------------------------------------------------
    if '_plan' in text:
        return AnalyzeResult(
            input=user_input,
            keywords=["_plan"],
            entities=[],
            specificity="high",
            confidence_level="HIGH",
            needs_clarification=True,
            clarification_note="PLAN_MODE_TRIGGERED: User explicitly requested a formal planning phase. Agent MUST NOT jump to implementation. 1) Grill for gaps, 2) Write PLAN_TEMPLATE.md, 3) Wait for approval."
        )
```

## Verification

```bash
$ python -m py_compile snowline_toolkit/templates/companion/core_intent.py
Syntax OK
```

## Files Modified
1. `snowline_toolkit/templates/AGENTS_TEMPLATE.md` - Added Rule #7
2. `snowline_toolkit/templates/companion/core_intent.py` - Added fast-path intercept (substring `in` check per QA revision)

---

Task 50 & 51: **COMPLETE**

---

## CURRENT TASK / CONTEXT

- Active: None - waiting for next task
- Position: 3. Executor/Executor_01 (migrated from `claude_code/pos_01` -> `pos/Executor_01` -> current)
- Last completed: Task 50 & 51 - `_plan` Convention & Grill-First (Rule #7 + core_intent.py fast-path)

---

## BACKLOG

*(Use for tracking pending items)*

---

## ARCHIVE

- [Task 50 & 51] `_plan` Convention & Grill-First: DONE. Added Rule #7 to AGENTS_TEMPLATE.md and fast-path intercept to core_intent.py (substring `in` check per QA revision). Syntax verified.
- [Task 49] Interactive `snowline status` with Detached Handoff: DONE. Modified `snowline_toolkit/cli.py` - added interactive update prompt with Windows `start cmd.exe /c` detached handoff (2s ping delay) and Unix subprocess fallback. Syntax verified.
- [Task 45] Full Toolkit Stress Test: DONE. Tested 10 tools directly on D:\project\scarecrow - all PASSED. scope_guardian bypass protection verified, project_guardian .env/secret detection working, impact_analyzer --depth parameter working, splicer indentation fallback triggered correctly on template literal code.
- [Task 44] Indentation Fallback for splicer.py: DONE. Added `extract_by_indentation()` as fallback tier, did NOT modify `extract_js_body`/`find_js_line` (per Isolation-over-DRY mandate). Live-tested against 3 real functions with template literals - all passed.
- [Task 41] Build Surgical Code Splicer: DONE (required Manual Override after an initial shortcut attempt) -> see `shared/archive/task_41_splicer.md`
- Task 39: Implement `--depth` Configurable Recursive Traversal in `impact_analyzer`.
- Task 38: impact_analyzer Python blindness + JS explicit extension fix - commit 19fd09b
- Trial Task: Clean up Tool Inventory table (Task 36 trial) - commit 15d20ea
