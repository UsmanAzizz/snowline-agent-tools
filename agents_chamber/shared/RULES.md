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
   - The Manager (PM) relays manually between positions using **ONE** single code:
     - `''` (empty quotes) = "Your turn. Open and check connector (INBOX/OUTBOX) because there is a signal from the previous agent."
   - **Deterministic Workflow**: The context of `''` is determined purely by the current workflow state, without needing position names:
     1. TL gives code instructions to Executor -> PM sends `''` to Executor.
     2. Executor responds in OUTBOX -> PM sends `''` to TL.
     3. TL hands execution results to QA -> PM sends `''` to QA.
     4. QA provides verdict in OUTBOX -> PM sends `''` to TL.
     5. If task concludes (PASS), TL is the final point receiving information from QA. TL then resets all sector statuses to Idle, and the flow repeats for the next task.

3. **Position Persistence**: Your position folder (e.g. `pos/1. TL`) is persistent across resets - the same folder survives, you just resume where you left off.

4. **Amnesia as a Feature**: State lives in FILES (`connector.md`, `project_context.md`, `task_board.md`), not in chat/session history - so a long-running session's history is a liability, not an asset, once this pattern is established (stale context risks hallucination or redoing already-completed work, as happened once - see ARCHIVE incident notes). The Manager should proactively restart an agent's session/CLI after a major task or block of tasks completes, rather than letting one session run indefinitely. A freshly-reset session reads these files and gets 100% clean, relevant context - no accumulated staleness.

5. **New files must be documented**: Any new file created as part of a task must be mentioned (at minimum one line) in `project_context.md` before the task is considered done. An undocumented file is an incomplete task.

6. **Test artifacts stay contained**: All test/scratch files go in a clearly-named, gitignored sandbox location - never scattered directly in the project root.

7. **Strict Sequential Task Numbering**: Task numbers (IDs) must be assigned strictly sequentially and linearly (e.g., Task 41, 42, 43...). Do NOT jump backwards or assign numbers out of order. If a new sub-issue is discovered, it must receive the next highest available number in the sequence, rather than being inserted between older numbers. This keeps the history and dependencies traceable.

8. **Single-Writer Delegation (TL as Scribe)**: To prevent drift and formatting conflicts, writing to `RULES.md`, `project_context.md`, and `task_board.md` is done exclusively through one hand: the TL. This is **delegation of the writing task, not a transfer of authority** - the PM remains the absolute authority over the content. TL writes **on behalf of the PM**: TL transcribes, PM decides.
   - PM delivers decisions and directives via chat; TL writes them into the documents.
   - TL does NOT have the right to refuse or alter the substance of a PM directive. If TL assesses that a directive conflicts with existing rules or the Ledger, TL MUST raise this objection to the PM first - rather than secretly modifying it.
   - This delegation is for formatting neatness and drift prevention, not revoking PM rights. PM retains the right to write directly whenever necessary.

9. **No Pre-filling Verdicts**: OUTBOX may only be written by the position owner (e.g. QA or Executor). Whoever assigns the task may only fill the INBOX section of the target agent's `connector.md`. Results/verdicts must not be pre-filled. The task board may only record review/execution results AFTER the respective agent's OUTBOX is filled with a real report.

10. **Broadcast All Administrative Updates**: Every time there is a change or addition to administrative rules (e.g. in `RULES.md`, `AGENTS.md`, or Chamber operating procedures), TL MUST broadcast the change into `shared/broadcast.md` so all newly awakened/reset agents (QA and Executor) can immediately know the updates without reading the entire log or `AGENTS.md` from scratch. **CRITICAL: Rules not yet in `broadcast.md` = incomplete task.**

11. **Mandatory QA Validation**: TL is FORBIDDEN from unilaterally closing (marking as DONE) any task completed by the Executor. Every task execution MUST be thrown to QA (Reviewer) first for auditing. Only QA has the authority to determine if a task is valid and may be closed. If QA declares "PASS", only then may TL update `task_board.md` to DONE.
    - *PASS Requirement*: QA MUST include real raw output (not narrative claims) as evidence so TL/PM can verify it.
    - *Micro-Task Exception*: If the task is extremely minor (like changing one string, fixing a typo, or meets Fast Track Protocol criteria in `plan_first.md`), TL has the right to bypass QA and close the task directly.

12. **Anti-Drift Check**: Always verify that any changes made to the live/installed version (e.g. inside `.agents/` directory) are also identically synchronized to the master template in `snowline_toolkit/templates/` before closing a task. This prevents the live environment from drifting away from the main source code.

13. **Bypass Stale Read Cache (Chamber Bug Workaround)**: When reading `connector.md`, `broadcast.md`, or any heavily updated administrative file, DO NOT use your internal `read_file` or `view_file` API tools as they may cache old states and falsely report "file unchanged." You MUST use a raw terminal command (e.g., `cat pos/2. QA/connector.md`) to read these files, guaranteeing fresh real-time data directly from the disk.

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
- **The Task 18 Carve-out (Exception 1):** Core **security/scope boundaries** (such as `is_file_in_scope()` in `scope_guardian`) with a proven history of drift bugs (Tasks 7, 14, 15) MUST be consolidated into a shared module. The risk of disparate implementations bypassing security boundaries is far more dangerous than the risk of Coupled Failure.
- **The Task 75 Carve-out (Exception 2):** Pure internal modules — with no side effects, touching no files, holding no state — may be shared between tools. For such code, failures due to coupling are hard and immediately visible upon execution, whereas drift due to duplication is silent and only discovered much later. Example: `tree_gen`.
- **Why:** In AI ecosystems, shared feature modules are vectors for Coupled Failure - optimizing a shared feature for Tool A can silently break Tool B. For security boundaries specifically, drift causes repeated vulnerabilities instead, which is worse.
- **Action:** Use Pure Copy-Paste (Isolation) for general feature logic (code extraction, searching, etc). Use Shared Modules ONLY for unified security/scope boundaries, or pure stateless internal modules.

**Before adding a new rule here:** check this Ledger and `project_context.md`'s history for anything this might contradict. Note the reconciliation explicitly if there's tension with a past decision, rather than leaving a silent contradiction in the permanent record.
