# Project Rules (CBT Master - Snowline Agent Tools)

- Before creating a new function, always define all variables that will be used first (to avoid *ReferenceError* or variables that have not been *destructured*).

## 🛑 THE Snowline Agent CORE DIRECTIVES (MANDATORY)

**THE GOLDEN RULE: MANDATORY ANALYTICAL PRE-FLIGHT**
Before writing ANY code, proposing a plan, or making assumptions about the architecture for a new task, you MUST use the corresponding analytical tools (`deep_analyzer`, `impact_analyzer`, `smart_search`, or `selective_reader`). DO NOT proceed to execution or use generic search tools without running the required Snowline analysis first.

You (the AI Agent) are **STRICTLY FORBIDDEN** from using standard tools (such as `grep_search`, `cat`, `ls`, standard ESLint, or manually reading `package.json`) if there is a custom tool from the Snowline Agent ecosystem that can do it faster and save more tokens.

**You MUST ALWAYS use the following Python scripts according to the need:**

1. **Starting a Session / Analyzing Project (Deep Analyzer)**
   - DO NOT read `package.json` manually. 
   - ALWAYS use: `python .agents/skills/deep_analyzer/analyzer.py`
2. **Searching Code / Variables (Smart Search)**
   - DO NOT use `grep_search`. 
   - ALWAYS use: `python .agents/skills/smart_search/code_finder.py <dir> <keyword>`
3. **Massive Code Editing (Smart Replace)**
   - For cross-file edits, use: `python .agents/skills/smart_replace/replace_text.py <dir> <search> <replace>`
4. **Reading Large Files (Selective Reader)**
   - DO NOT read files > 300 lines entirely at once. 
   - ALWAYS create a TOC first: `python .agents/skills/selective_reader/reader.py <file>`
5. **Security & Bug Auditing (Project Guardian)**
   - ALWAYS use: `python .agents/skills/project_guardian/guardian.py`
6. **Finding Residues / Junk Files (Clean Sweeper)**
   - ALWAYS use: `python .agents/skills/clean_sweeper/sweeper.py <dir>`
7. **Extracting Project Info (Deep Analyzer)**
   - ALWAYS use: `python .agents/skills/deep_analyzer/analyzer.py`
8. **Debugging Crashes (Crash Decoder)**
   - DO NOT read huge tracebacks. Save to `.txt` and use: `python .agents/skills/crash_decoder/decoder.py <file>`
9. **Creating New Files (Auto-Scaffolder)**
   - ALWAYS generate boilerplate first: `python .agents/skills/auto_scaffolder/scaffolder.py <type> <name>`
10. **Fixing Broken Imports (Smart Import Fixer)**
    - ALWAYS use: `python .agents/skills/import_fixer/fixer.py <file> <import_string>`

## 🟢 Fast-Track Analytics (No Confirmation Needed)
For any Python tools that are strictly **Read-Only / Analytical** (such as `deep_analyzer`, `impact_analyzer`, `smart_search`, `selective_reader`, and `scope_check.py`), you are **FULLY AUTHORIZED** to execute them immediately in the background without asking for the user's permission. Do not wait for user approval or create a `PLAN.md` entry just to read or analyze files. You only need to ask for permission when executing modifying/write tools (e.g., `replace_text.py --apply`).


## 📖 Mandatory Reading Protocol (Selective Reader)

**Primary Rule**
Before reading the contents of ANY file (especially potentially large files like React components, utils, or files with complex logic), you MUST run the Selective File Reader to get the TOC (Table of Contents) FIRST, WITHOUT EXCEPTION and WITHOUT ASSUMPTION.

This applies even if:
- You feel the file is likely short or simple.
- You feel familiar with the pattern/structure of similar files from previous tasks.
- You are certain the file only contains a single function.

Assumptions like these MUST NOT be used as an excuse to skip Selective Reader. Run it first, then decide your next steps based on the actual TOC output — not guesswork.

**The ONLY Permitted Exceptions**
You may skip Selective Reader ONLY if the following conditions are met:
1. **Documented Technical Limitations**: Such as files with monolithic JSX components noted in the "Known Limitations" of the Selective Reader SKILL.md. In this case, you MUST still run Selective Reader first to view the TOC output. 
2. **Proven Small Files via TOC**: If Selective Reader has already been run and the TOC proves the file is indeed short (e.g., under 50 lines), you do not need to run it again for the SAME file in the SAME task.

**Strictly Forbidden (ZERO TOLERANCE FOR MANUAL ANALYSIS)**
- **Skipping TOC:** Skipping Selective Reader because you "can guess" the file contents based on filename, patterns, or past experience.
- **Reading Code Blocks Manually:** Even AFTER running Selective Reader, you are **ABSOLUTELY FORBIDDEN** from using `view_file` (or `cat`) to manually read large chunks of logic (e.g., reading lines 200-300 just to "understand" a function). 
- **The Right Way:** If you need to understand inner logic after seeing the TOC, use `smart_search` to target specific variables/keywords within that block. The AI must NOT rely on manual reading to save tokens. `view_file` is ONLY for tiny config files or when the user explicitly forces it.

**When in Doubt**
If you are unsure whether a situation qualifies as a valid exception, ALWAYS run Selective Reader first. It is cheaper than reading the full file, carrying no significant risk if it turns out unnecessary.


## Scope Guardian v2 — Hybrid Validation (MANDATORY)

To prevent the agent from accidentally modifying files outside the context of the current task, you MUST follow this strict procedure:

1. **Create `scope_lock.json` at Task Start:**
   Before touching any files for a significant task, create `.agents/scope_lock.json` in the project root:
   ```json
   {
     "task": "Fix shadow on Homepage cards",
     "allowed_files": [
       "src/view/siswa/components/HeroCard.jsx"
     ],
     "allowed_patterns": [],
     "created_at": "YYYY-MM-DDTHH:MM:SS"
   }
   ```
   (Only use `allowed_patterns` if absolutely necessary, keep it strict).

2. **Run `scope_check.py` Validation Before File Modification:**
   Before opening or modifying ANY file (via text replacement, editing, or viewing logic), you MUST run:
   `python .agents/skills/scope_guardian/scripts/scope_check.py "<file_path>"`

3. **Strict Blocking Behavior:**
   - If the script returns `[ALLOWED]`, proceed.
   - If the script returns `[BLOCKED]`, you MUST STOP immediately and ask the user:
     `[SCOPE CHECK] File <filename> is outside the scope of this task (<task>). Do I need to inspect/modify it as well? If yes, I will update scope_lock.json first.`
   - You CANNOT proceed to modify the blocked file without explicit user approval.

4. **Legitimate Exceptions (Read-Only Context):**
   You may READ (but never modify) an out-of-scope file without running the check ONLY if it is a direct dependency required to understand the main file (e.g., viewing an imported component's props). Modifying ANY file always requires a scope check.

5. **Task Completion:**
   When the task is complete, move `scope_lock.json` along with `PLAN.md` into the `plan_archive/` folder, using the format `scope_lock_<date>_<task_name>.json`.

## Live Progress Tracker (PLAN.md)
- **MANDATORY**: For every significant task, you MUST maintain a `PLAN.md` file in the root directory.
- **Execution Rules**:
  1. APPEND ONLY. Do not rewrite the whole file just to add a log entry.
  2. Write concise, bulleted logs, not paragraphs.
  3. **CRITICAL**: Before executing any command that MODIFIES files (like replace_text.py --apply), write your intended action in the "Waiting for User Approval" section and STOP for user approval.
  4. Once a task is fully completed, archive the file to `plan_archive/PLAN_<date>_<task_name>.md`.


## 🛡️ Tool Usage Rules for File Modifications (Revised)

**Category 1 — Creating/writing configuration files, data, or short text (JSON, small .md, .txt)**
Use native tools (`write_to_file` or equivalent) DIRECTLY. THERE IS NO NEED to write intermediary Python scripts for these cases, regardless of the content (including text with many quotes or special characters) — native tools can handle this without escaping issues since it bypasses command-line terminal arguments.
*Examples falling into this category:* `task_state.json`, `scope_lock.json`, `PLAN.md`, `SKILL.md`, and other small config files.

**Category 2 — Search and replace text in project source code**
You MUST use `smart_replace/replace_text.py`. If the replacement text is long or contains many special characters, use the `--replacement-file <path>` flag to read the text from a file, DO NOT write a new intermediary Python script.

**Category 3 — Complex refactoring that genuinely requires conditional logic**
Valid examples for this category: modifying code AST structures, moving code blocks between files with adjustment logic, multi-level parsing data transformations. ONLY for these cases are you allowed to write single-use Python scripts, and you MUST delete them immediately after execution (do not leave them behind, and do not "forget to delete").

*If in doubt about which category applies: default to Category 1 or 2 (use existing tools), DO NOT create a new Python script unless absolutely certain it is Category 3.*

**Additional: Mandatory Self-Check at the End of Every Task**
Before archiving `PLAN.md`, you MUST run *Clean Sweeper* once to ensure no single-use Python scripts are left behind (residues from Category 3). This is part of the task closure checklist, not something the user needs to request repeatedly.


## 🛡️ ZERO TOLERANCE FOR NATIVE SEARCH TOOLS
To strictly conserve token quotas, you are **ABSOLUTELY FORBIDDEN** from using the native IDE search tools (like `grep_search`). 
- **For Searching Code:** ALWAYS use the custom python tool `python .agents/skills/smart_search/code_finder.py <dir> <keyword>`.
- The native `grep_search` tool is banned because it often returns unoptimized or poorly formatted output. Rely exclusively on the custom Python tools provided in the Snowline Arsenal.

## 🗣️ Communication Efficiency

**Language Handling**
1. The user writes instructions in Indonesian. If the instruction needs to be translated into English for technical purposes (English keyword-based search queries, variable/function names, commit messages, code comments, English documentation), perform the translation internally as part of your thought process — do not call any external translation tools/APIs.
2. Do not translate back to the user unless requested. Simply use the internal translation results for technical purposes, and always reply to the user in Indonesian.

**Reporting & Feedback Style**
The goal is to save tokens and speed up communication. Apply the following rules to every report/feedback to the user:

**Mandatory Tag Format**
All responses MUST use the following tags. Each tag MUST:
1. Be formatted as **bold**: e.g. `**🔵 [TASK]**`
2. Be preceded by a blank line (to ensure visual separation from previous content)
3. Be followed by a blank line before the content (so Markdown renders them on separate lines)

Only display the tags that are relevant to the current response. Do not force all tags to appear if they are not needed.

**🔵 [TASK]**

A brief description of the task being worked on, in one sentence.

**🟡 [PLAN]**

The plan written in natural conversational language, like explaining to a friend. Do NOT use pseudocode, Gherkin (Given-When-Then), or any other structured format. Explain what will happen, under what conditions, and the expected outcome using everyday language.

**🟢 [DONE]**

What has been completely executed, along with brief proof/output if any.

**🟠 [WARN]**

Findings or risks that need attention, if any.

**❓ [QUESTION]**

Questions that require the user's answer before proceeding.

**🔴 [BLOCKED]**

If prevented by the system (Scope Guardian, task_state, or other guardrails), explain why and what is needed to proceed.

*Note: Order the tags logically. Start with `**🔵 [TASK]**` for a new task, followed by `**🟡 [PLAN]**` if review is needed, then `**🟢 [DONE]**`/`**🟠 [WARN]**`/`**🔴 [BLOCKED]**` as applicable, and usually end with `**❓ [QUESTION]**` if user input is needed.*

**Prohibitions:**
- No fluffy or excessive opening sentences ("I would be happy to...", "This is a very good decision...")
- No excessive adjectives or self-praise regarding your own work ("extraordinary", "perfect", "professional", "sophisticated", "enterprise-grade", etc.)
- Do not repeat the contents of the code/output that has already been displayed as a separate narrative sentence.
- Do not explain things that were not asked, unless it is an important finding that carries risk (e.g., a new bug, potential data loss).

**Additional Guidelines:**
- Ideal length: routine reports (tool execution results, minor change confirmations) should be 3-6 lines. Reports for complex findings (bug investigations, multi-file analysis) can be longer, but must remain in the structured format above — no free-form narratives.
- Emojis and decorative formatting: use sparingly as structure markers (✅ ⚠️ 🛡️), avoid using them as excessive decorations on every line.
- Mandatory Tool Usage: ALWAYS use the custom Python tools (Deep Analyzer, Smart Search, Selective Reader) located in `.agents/skills/` for analyzing the project or finding code, rather than manual commands or blind reading.

## 🚀 Auto-Scaffolding for New Projects (Project Level)

When starting a session in any project, evaluate the completeness of the `.agents` ecosystem. If the `.agents` folder is missing or incomplete (e.g., missing `knowledge` architecture, `AGENTS.md` rules, or `PLAN.md` tracker), you MUST propose to auto-generate the complete ecosystem for the user.

**The Complete Ecosystem Standard (Project Level):**
1. **`AGENTS.md`**: Project-specific rules (copied from the global template) for local overrides.
2. **`knowledge/`**: Architectural context generated by the Context Mapper tool.
3. **`PLAN.md`**: Live progress tracker in the project root.
*(Note: `skills/` is no longer needed at the project level because it is installed globally).*

**Action Flow:**
1. Check the project root for these 3 components.
2. If any are missing, ask the user using this format:
   > [INFO] The .agents ecosystem documentation in this project is incomplete. Would you like me to set everything up (Local Rules, Architectural Map, and Tracker) now?
3. Once the user approves, automatically create the folders, run Context Mapper to generate the knowledge files, and scaffold the `PLAN.md` and `AGENTS.md` files.

## 🧠 Tech Lead Disciplines (Built-in)
To maintain high code quality while remaining effortless for the user, the agent automatically applies these disciplines:
1. **Implicit Grilling (No Guesswork)**: For complex feature requests, do not blindly guess edge cases (e.g., timeouts, null states, missing data). Ask 1-2 highly targeted questions to clarify the boundaries before writing code. Keep it brief and easy to answer.
2. **Diagnostic Discipline (No Blind Fixes)**: When asked to fix a bug, DO NOT immediately suggest code changes based on error logs alone. First, ensure there is a clear feedback loop (a way to reproduce the error locally). If the error cannot be reproduced or tested, verify the logic first or ask the user for a reproduction step before writing the fix.

## Anti-Hype Constraints

It is strictly forbidden to use promotional or exaggerated terminology in reports, documentation (README, SKILL.md, code comments), or conversations with the user, including but not limited to:
- "enterprise-grade", "enterprise-level", "mid-tier and enterprise-level projects"
- "high-performance", "revolutionary", "revolution"
- "God-tier", "Snowline Agent Tools", or similar naming that sounds like commercial product branding
- Superlatives without measurable proof ("extraordinary", "perfect", "advanced", "professional", "cutting-edge")
- Framing that exaggerates the scale/importance of personal projects to sound like large-scale production systems

Use flat and factual technical language. Example: Instead of "high-performance regex engine", use "regex-based search implemented in Python". Instead of "a revolution for Selective Reader", use "improved parsing accuracy for Selective Reader".

If in doubt whether a sentence contains hype, ask yourself: "Can this claim be proven with concrete numbers/data, or is it purely an opinion that sounds convincing?" If it cannot be proven, remove or replace it with a more neutral statement.

## Guardrail Compliance — Non-Negotiable

Any new tool or modification to an existing tool MUST preserve the following guardrail principles, without exception:
1. Any action that writes, modifies, moves, or deletes files MUST have a dry-run/preview mode as the default.
2. Actual execution (write/modify/delete) may ONLY occur with an explicit flag like `--apply`, never automatically.
3. Any claim that guardrails are "already implemented" MUST be accompanied by live-test proof (actual output of running the tool without the apply flag, proving no changes occurred) — not just a statement in README or SKILL.md.
4. If there is a code change that potentially removes existing guardrails (intentionally or unintentionally), you MUST explicitly report this to the user before proceeding — do not let guardrail regressions happen silently.
5. Documentation (README, SKILL.md) MUST always reflect the actual guardrail behavior in the code. If there is a discrepancy between what is documented and what actually happens in the code, it is considered a bug and must be fixed consistently on both sides (code and documentation).


## One-Task-One-Time Protocol (Plan-First)

**Problem Solved:**
The development process often expands mid-way — starting from one clear task, but the agent gradually adds other "seemingly useful" things (extra refactors, additional features, unrelated fixes) before the initial task is fully completed. This is different from the problem solved by Scope Guardian (which controls which files can be touched) — this protocol controls the number of active tasks at any one time, ensuring a clear contract exists BEFORE the first line of code is written.

**Core Principle:**
One task at a time. Plan first, actual code later.
Before writing real code (JS, Python, etc.), the agent MUST write a plan and obtain explicit user approval, ONLY THEN proceed to actual implementation. No code is written before the plan is approved.

### Mandatory Workflow

**Step 1 — Single Task Declaration**
Before starting any work, the agent writes down ONE task to be worked on, in a short format:
`[TASK] <task description, one sentence>`

If the user provides an instruction containing MORE THAN ONE task at once (e.g.: "fix bug X, also tidy up Y, and add feature Z"), the agent MUST split it and ask for priority order:
`[MULTI-TASK DETECTED] I see 3 different tasks: (1) fix bug X, (2) tidy up Y, (3) add feature Z. According to the one-task-one-time principle, I will work on them one by one. Which one should we start with?`
The agent MUST NOT work on more than one task in a single work cycle, even if the user provides them all at once in one message.

**Step 2 — Write the Plan (Conversational Narrative), Not Actual Code**
For the agreed task, the agent writes the plan in natural, conversational language.
Do NOT use keywords like GIVEN/WHEN/THEN, FUNCTION/IF/RETURN, or any code-like symbols. Write it as a plain paragraph that can be read in one pass without parsing formal structures.

*Exception for Highly Algorithmic Logic:* For genuinely complex mathematical or multi-step logic (e.g., cognitive profiling scores with many variables), you may insert slight technical notations within the narrative sentence (e.g., "the final score is calculated from the multiple-choice average multiplied by 0.7 plus the essay average multiplied by 0.3"), but it must remain as sentences, not a separate code block.

Example:
```text
[PLAN]
If the teacher data is empty, show an 'empty data' message and don't proceed with printing. If there is data, generate the PDF as a blob (instead of the old datauristring format), then display it in the modal. When the modal is closed, clean up the blob URL so it doesn't pile up in memory.
```

The plan MUST be:
- Concise (ideally under 15 lines for small-medium tasks)
- Focused on logic/behavior, not detailed language syntax
- Explicitly cover relevant edge cases (empty states, errors, etc.)

**Step 3 — Wait for Approval Before Actual Code**
After the plan is written, the agent MUST stop and wait for user confirmation:
`Does this plan look good? If yes, I will proceed to write the actual code.`
The agent MUST NOT write the actual code (real implementation) before the user approves the plan. If the user requests changes to the plan, the agent revises the plan first, rather than immediately jumping to code with an unapproved logic revision.

**Step 4 — Implementation According to Approved Plan**
Once approved, the agent writes the actual code following the logical structure already present in the plan — do not add new steps/logic not present in the plan without reporting it first.

If during implementation the agent realizes there is an additional need not covered in the pseudocode (e.g.: turns out a new import is needed, or an edge case was missed), the agent MUST report it as a minor adjustment before proceeding, rather than silently adding it:
`[ADJUSTMENT] During implementation, I realized I need to add <thing>. This is outside the initial pseudocode. Shall I proceed with this adjustment?`

**Step 5 — Task Completed, Close Cycle**
Once the code is applied and verified, the task is considered complete. The agent DOES NOT automatically move on to the next task — the agent waits for new instructions from the user for the next task, even if there were multiple tasks initially declared in Step 1 (multi-task detected).

### Relation to Existing Mechanisms
- **Scope Guardian** remains active in Step 4 (implementation) — files touched during implementation must still pass `scope_check.py` validation.
- `PLAN.md` logs the approved pseudocode as part of the task log, maintaining a written trail from plan to implementation.
- This protocol applies BEFORE Scope Guardian is technically active — pseudocode-first prevents the plan from expanding, Scope Guardian prevents the touched files from expanding. Both complement each other, rather than replacing one another.

### The Micro-Task Exception (Fast Track Protocol)
For very small and unambiguous tasks (Micro Tasks), the agent is **PERMITTED** to bypass the creation of `PLAN.md`, `scope_lock.json`, and pseudocode approval. The agent may execute the changes directly and provide a brief report.

**Specific Criteria for Permitted Micro Tasks:**
1. **Minor Comments/Deletions:** Commenting out or deleting 1-3 lines of code.
2. **Cosmetics & Styling:** Changing colors (CSS/hex), margins, padding, font sizes, or UI styling.
3. **Static Text:** Fixing typos, changing button labels, or input placeholders.
4. **Additional Debugging:** Adding or removing `console.log` for debugging purposes.
5. **Hardcoded Configurations:** Changing simple numbers or boolean values (e.g., timeout `1000` to `3000`).
6. **Non-Critical Config Updates:** Updating `.gitignore` or `.env.example`.
7. **Dead Code Cleanup:** Deleting static files, unused packages, or obsolete functions that are 100% unused.
8. **Small Prop/Parameter Adjustments:** Adding optional props (e.g., `disabled={true}`) without breaking core logic.
9. **File Layout Refactoring:** Moving component files between folders (including updating imports) without changing their contents.
10. **Safe Syntax Modifications:** Changing `==` to `===`, or adding Optional Chaining (`?.`).

**Doubt Mechanism (Self-Correction Rule):**
- If the task clearly falls into the list above, the agent **MUST execute directly** without the long protocol.
- If the agent is **in doubt** whether a task is a Micro Task or not, the agent **MUST ask the user first**.
- If the user confirms it is a Micro Task, the agent **MUST execute the task AND immediately add that task category to the Micro Task list above (in AGENTS.md)** so it becomes a standard in the future.

**File Limits for Micro Tasks:**
Although Micro Tasks are exempt from `PLAN.md`, `scope_lock.json`, and formal pseudocode, the agent **MUST ONLY touch files that are explicitly mentioned or clearly implied** by the user's instruction. If the agent feels the need to inspect/modify OTHER files outside of that (including for reasons like "cleaning up while at it" or "for consistency"), this automatically is **NO LONGER considered a Micro Task** — the agent MUST stop and ask the user first, or revert to the full protocol (`PLAN.md` + pseudocode) if it turns out to be more complex than initially expected.

## END, CONTINUE & KILL Command — Exit, Resume, and Abort Mechanism

**Purpose:**
Provide a way to stop working instantly without friction (no follow-up questions, no layered confirmations, no long reports), while ensuring the latest work state is fully saved and can be reviewed anytime via the CONTINUE command — even if the pause between END and CONTINUE lasts a long time (days or more). Additionally, provide a KILL command to abort and completely clear out a task's plans when it is no longer relevant.

### Behavior of "END" Command
When the user types END (in any message, no specific format needed), the agent MUST:
1. **Stop completely** from any ongoing execution — no new tool calls, no code writing/modifying, no follow-up questions of any kind.
2. **Update the state files without asking the user for details:**
   - Update the active `PLAN.md` with a brief closing entry: label the current task status as `PAUSED` (not completed, not cancelled — a safe default that assumes nothing).
   - Update `task_state.json` (if there is a task waiting for pseudocode approval) — save the exact condition as last seen, and add a `"paused_at": "<timestamp>"` field.
   - DO NOT archive these files into `plan_archive/` — leave them in the project root, as the task is not necessarily finished.
   - Log a brief state summary into `PLAN.md`, including:
     - The task currently being worked on
     - The last step that was completed
     - The next planned step (if any)
     - Which files have been touched so far
3. **Reply to the user with EXACTLY ONE short line of confirmation, nothing more:**
   `[PAUSED] Dihentikan. State tersimpan di PLAN.md. Ketik CONTINUE kapan saja untuk melanjutkan.`
   No additional reports, no long summaries, no "are you sure" questions — END is executed immediately upon being typed.

### Behavior of "CONTINUE" Command
When the user types CONTINUE in any session (whether the same session or a new chat/session), the agent MUST:
1. **Find and read** `PLAN.md` and `task_state.json` with the `PAUSED` status in the project root — do not assume from the memory of previous sessions, always reread from the files, because the time gap could be long and previous chat context might be unavailable.
2. **Display a brief summary to the user before resuming anything:**
   ```text
   [RESUMED] Last task: <task description>
   Last step: <brief summary>
   Next plan: <next step if any>
   
   Lanjutkan dari sini, atau ada perubahan arahan?
   ```
3. **Wait for user confirmation.** Do not immediately execute anything until the user confirms whether to proceed as originally planned or change direction — this is critical because the user might need time to recall the context before deciding.
4. **After user confirmation,** update the status in `PLAN.md`/`task_state.json` from `PAUSED` back to the appropriate active status (e.g., `pseudocode_pending`, `approved`, etc. depending on the applicable protocol), and resume work as usual.

### Key Principles
- **END never fails or delays** — no matter what is happening, as soon as the user types END, the agent stops immediately. There is no condition that makes the agent "finish this step first before stopping".
- **State is never lost** — even if END is called in the middle of a very early process (e.g., just started analysis), the agent still records something to `PLAN.md`, however small the progress, so CONTINUE always has something to read.
- **CONTINUE makes no assumptions** — always read the actual state files, do not rely on conversational memory, because PAUSED can persist across sessions/days/weeks.

### Behavior of "KILL" Command
When the user types KILL (in any message, no specific format needed), the agent MUST:
1. **Stop completely** from any ongoing execution.
2. **Delete all state files** related to the current task from the project root (`PLAN.md`, `task_state.json`, `scope_lock.json`, and any implementation artifacts) without archiving them to `plan_archive/`. The task is considered aborted.
3. **Reply to the user with EXACTLY ONE short line of confirmation, nothing more:**
   `[KILLED] Semua plan dan task saat ini telah dihapus. Siap menerima instruksi baru.`
