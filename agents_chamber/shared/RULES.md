# CHAMBER PROTOCOL

## Folder Structure

```
agents_chamber/
├── shared/                    <- RULES.md (this file), project_context.md, task_board.md, broadcast.md, archive/
└── pos/
    ├── 0. PM/                <- Project Manager (human)
    ├── 1. TL/                <- Tech Lead
    ├── 2. QA/                <- Reviewer
    └── 3. Executor/
        ├── Executor_01/      <- currently Claude Code
        ├── Executor_02/      <- reserved slot, empty until invited
        ├── Executor_03/      <- reserved slot, empty until invited
        ├── Executor_04/      <- reserved slot, empty until invited
        └── Executor_05/      <- reserved slot, empty until invited
```

Each role folder contains `ONBOARDING.md` (role definition - read this first, every fresh session) and `connector.md` (INBOX/OUTBOX, actual work).


## The 4 Roles

**1. Project Manager (PM)** (currently: the human user)
- Holds final authority, provides high-level goals, and relays signals between positions.
- **Delegates all administrative writing** (`RULES.md`, `project_context.md`, `task_board.md`) to the Tech Lead to minimize manual work. PM gives instructions via chat, TL maintains the files.
- Can override any TL decision, demand QA counterbalance on anything, reset any session at any time.

**2. Tech Lead (TL)** (currently: Gemini)
- **Sole Writer:** Only the TL has the authority to write to ANY file in the `shared/` directory (`RULES.md`, `project_context.md`, `task_board.md`).
- Decides task assignments, reviews EVERY proposal before implementation is allowed to start.
- Independently VERIFIES live-test evidence (reads source directly, runs execution checks) rather than trusting claims at face value.
- Checks the Ledger (below) and `project_context.md` for contradictions before writing any new architectural rule.
- Holds final authority on chamber-wide decisions (see `project_context.md`'s "Design Decision" sections for precedent), routing consequential/contested ones through QA first.

**3. QA / Reviewer** (currently: Opus 4.8 / Claude Code, a separate session from the Gemini TL - intentionally a different model to avoid correlated blind spots)
- Adversarial finder role ONLY. Reads real source code, finds bugs/gaps/design issues, verifies claims with real execution evidence where possible.
- **Periodically reviews RULES.md and the Ledger itself for internal contradictions**, ensuring architectural coherence across tasks.
- NEVER writes or commits code directly - findings go to TL for review, then to an Executor to implement.
- Independence from TL is intentional, even if same underlying model - don't assume shared memory/context.

**4. Executor** (currently: Claude Code, position `3. Executor/Executor_01`. Slots `Executor_02` through `Executor_05` reserved for future parallel executors.)
- Implementer role. Proposes approach in OUTBOX BEFORE writing any code - waits for TL approval.
- Once approved, implements + provides RAW live-test evidence (actual command + actual output, not summarized claims).
- Respects explicit architectural mandates (the Ledger) even when a simpler shortcut seems tempting - flag disagreement to TL rather than silently deviating.

## Shared Rules (All Roles)

1. **Broadcast**: Check `shared/broadcast.md` whenever you check your own INBOX - part of the same routine, not separate.

2. **Signal Protocol**: When you complete a task and write to OUTBOX:
   - Write your response to the OUTBOX section
   - PRINT/Say "Task complete - please signal [PM/TL, as appropriate]" in your terminal response
   - The Manager (PM) relays manually between positions menggunakan **SATU** kode tunggal:
     - `''` (empty quotes) = "Giliran Anda. Buka dan periksa *connector* (INBOX/OUTBOX) karena ada sinyal dari agen sebelumnya."
   - **Alur Kerja Deterministik**: Konteks dari `''` ditentukan murni oleh alur kerja saat itu, tanpa perlu embel-embel nama posisi:
     1. TL memberi instruksi kode ke Executor -> PM mengirim `''` ke Executor.
     2. Executor merespons di OUTBOX -> PM mengirim `''` ke TL.
     3. TL menyerahkan hasil eksekusi ke QA -> PM mengirim `''` ke QA.
     4. QA memberikan *verdict* di OUTBOX -> PM mengirim `''` ke TL.
     5. Jika task berakhir (PASS), TL adalah titik terakhir yang menerima informasi dari QA. TL kemudian mengatur status seluruh sektor kembali menjadi *Idle*, dan *flow* diulang dari awal untuk *task* selanjutnya.

3. **Position Persistence**: Your position folder (e.g. `pos/1. TL`) is persistent across resets - the same folder survives, you just resume where you left off.

4. **Amnesia as a Feature**: State lives in FILES (`connector.md`, `project_context.md`, `task_board.md`), not in chat/session history - so a long-running session's history is a liability, not an asset, once this pattern is established (stale context risks hallucination or redoing already-completed work, as happened once - see ARCHIVE incident notes). The Manager should proactively restart an agent's session/CLI after a major task or block of tasks completes, rather than letting one session run indefinitely. A freshly-reset session reads these files and gets 100% clean, relevant context - no accumulated staleness.

5. **New files must be documented**: any new file created as part of a task must be mentioned (at minimum one line) in `project_context.md` before the task is considered done. An undocumented file is an incomplete task.

6. **Test artifacts stay contained**: all test/scratch files go in a clearly-named, gitignored sandbox location - never scattered directly in the project root.

7. **Strict Sequential Task Numbering**: Task numbers (IDs) must be assigned strictly sequentially and linearly (e.g., Task 41, 42, 43...). Do NOT jump backwards or assign numbers out of order. If a new sub-issue is discovered, it must receive the next highest available number in the sequence, rather than being inserted between older numbers. This keeps the history and dependencies traceable.

8. **Single-Writer Delegation (TL sebagai Juru Tulis)**: Untuk mencegah inkonsistensi (*drift*) dan konflik format, penulisan ke `RULES.md`, `project_context.md`, dan `task_board.md` dilakukan melalui satu tangan saja, yaitu TL. Ini **pendelegasian tugas menulis, bukan pemindahan wewenang** - PM tetap pemegang otoritas penuh atas isi dokumen-dokumen tersebut. TL menulis **atas nama PM**: TL menuangkan, PM yang memutuskan.
   - PM menyampaikan keputusan dan arahan lewat *chat*; TL menuliskannya ke dokumen.
   - TL TIDAK berhak menolak atau mengubah substansi arahan PM. Bila TL menilai sebuah arahan bertabrakan dengan aturan atau Ledger yang ada, TL wajib menyampaikan keberatan itu ke PM lebih dulu - bukan mengubahnya sendiri secara diam-diam.
   - Pendelegasian ini demi kerapian format dan pencegahan *drift*, bukan pencabutan hak PM. PM tetap berhak menulis langsung kapan pun diperlukan.

9. **No Pre-filling Verdicts**: OUTBOX hanya boleh ditulis oleh pemilik posisi (misal: QA atau Executor). Siapapun yang memberikan tugas hanya boleh mengisi bagian INBOX dari file `connector.md` agen yang dituju. Hasil/verdict tidak boleh di-prefill. Task board hanya boleh mencatat hasil review/eksekusi SETELAH OUTBOX agen yang bersangkutan terisi dengan laporan riil.

10. **Broadcast All Administrative Updates**: Setiap kali ada perubahan atau penambahan pada aturan administratif (misalnya di `RULES.md`, `AGENTS.md`, atau pembaruan prosedur kerja Chamber), TL WAJIB menyiarkan perubahan tersebut ke dalam `shared/broadcast.md` agar seluruh agen (QA dan Executor) yang baru bangun/reset dapat langsung mengetahui pembaruan tanpa harus membaca seluruh log atau `AGENTS.md` dari awal. **CRITICAL: Aturan yang belum masuk `broadcast.md` = task belum selesai.**

11. **Mandatory QA Validation**: TL DILARANG menutup secara sepihak (*mark as DONE*) task apa pun yang telah selesai dikerjakan oleh Executor. Setiap eksekusi task harus dilempar ke QA (Reviewer) terlebih dahulu untuk diaudit. Hanya QA yang berhak menentukan apakah sebuah task sudah valid dan boleh ditutup. Jika QA menyatakan "PASS", barulah TL boleh memperbarui `task_board.md` menjadi *DONE*. 
    - *Syarat PASS*: QA WAJIB menyertakan *raw output* riil (bukan klaim naratif) sebagai bukti agar TL/PM bisa memverifikasinya.
    - *Micro-Task Exception*: Jika task bersifat sangat minor (seperti ubah satu string, typo, atau kriteria Fast Track Protocol di `plan_first.md`), TL berhak mem-bypass QA dan langsung menutup task tersebut.

12. **Anti-Drift Check**: Selalu verifikasi bahwa setiap perubahan yang dilakukan pada versi *live/installed* (misal di dalam direktori `.agents/`) juga disinkronisasikan secara identik ke *master template* aslinya di `snowline_toolkit/templates/` sebelum menutup sebuah task. Hal ini untuk mencegah lingkungan *live* kita melenceng (*drift*) dari *source code* utama.

## Onboarding a New Position (copy-paste starting point)

When the Manager invites a new position, give it this:

> You are joining `agents_chamber` at `pos/[folder]` (e.g. `pos/1. TL`, `pos/3. Executor/Executor_02`).
> Read `pos/[folder]/ONBOARDING.md` first for your role definition, then `shared/RULES.md` (this file), then `shared/project_context.md`, then check `shared/broadcast.md`, then read `pos/[folder]/connector.md` for your actual task.
> Follow the Signal Protocol once you've completed work. Do not write to `task_board.md` or `project_context.md` unless you are TL.

## Role Transition Note

Gemini has taken over the Tech Lead role for an ongoing ~3-week period, with the human Project Manager overseeing. QA is now filled by Opus 4.8 (Claude Code) in a separate, independent session (`pos/2. QA`) - transitioned from Gemini. Placing a *different* model in QA than in TL strengthens the independent-review safeguard: correlated blind spots between same-model TL/QA are avoided, not just shared session state.

---

## Architectural Decisions (The Ledger)

Long-term memory for architectural precedents agreed upon by the Chamber (TL + QA). Agents MUST abide by these rulings.

**1. Isolation over DRY (Zero-Bloat AI Scripts)**
- **Rule:** Do NOT use shared modules (e.g. a common `utils.py` imported by multiple scripts) when building autonomous AI automation tools (like `impact_analyzer`, `splicer`, etc).
- **The Task 18 Carve-out (Exception):** Core **security/scope boundaries** (such as `is_file_in_scope()` in `scope_guardian`) with a proven history of drift bugs (Tasks 7, 14, 15) MUST be consolidated into a shared module. The risk of disparate implementations bypassing security boundaries is far more dangerous than the risk of Coupled Failure.
- **Why:** In AI ecosystems, shared feature modules are vectors for Coupled Failure - optimizing a shared feature for Tool A can silently break Tool B. For security boundaries specifically, drift causes repeated vulnerabilities instead, which is worse.
- **Action:** Use Pure Copy-Paste (Isolation) for feature logic (code extraction, searching, etc). Use Shared Modules ONLY for unified security/scope boundaries.

**Before adding a new rule here:** check this Ledger and `project_context.md`'s history for anything this might contradict. Note the reconciliation explicitly if there's tension with a past decision, rather than leaving a silent contradiction in the permanent record.
