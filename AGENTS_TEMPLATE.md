# Project Rules (CBT Master - 10-Pillars Ecosystem)

- Before creating a new function, always define all variables that will be used first (to avoid *ReferenceError* or variables that have not been *destructured*).

## 🛑 THE Snowline Agent CORE DIRECTIVES (MANDATORY)

**THE GOLDEN RULE: MANDATORY ANALYTICAL PRE-FLIGHT**
Before writing ANY code, proposing a plan, or making assumptions about the architecture for a new task, you MUST use the corresponding analytical tools (`deep_analyzer`, `impact_analyzer`, `smart_search`, or `selective_reader`). DO NOT proceed to execution or use generic search tools without running the required Snowline analysis first.

You (the AI Agent) are **STRICTLY FORBIDDEN** from using standard tools (such as `grep_search`, `cat`, `ls`, standard ESLint, or manually reading `package.json`) if there is a custom tool from the Snowline Agent ecosystem that can do it faster and save more tokens.

**You MUST ALWAYS use the following Python scripts according to the need:**

1. **Starting a Session / Analyzing Project (Deep Analyzer)**
   - DO NOT read \package.json\ manually. 
   - ALWAYS use: \python .agents/skills/deep_analyzer/analyzer.py\
2. **Searching Code / Variables (Smart Search)**
   - DO NOT use \grep_search\. 
   - ALWAYS use: \python .agents/skills/smart_search/code_finder.py <dir> <keyword>\
3. **Massive Code Editing (Smart Replace)**
   - For cross-file edits, use: \python .agents/skills/smart_replace/replace_text.py <dir> <search> <replace>\
4. **Reading Large Files (Selective Reader)**
   - DO NOT read files > 300 lines entirely at once. 
   - ALWAYS create a TOC first: \python .agents/skills/selective_reader/reader.py <file>\
5. **Security & Bug Auditing (Project Guardian)**
   - ALWAYS use: \python .agents/skills/project_guardian/guardian.py\
6. **Finding Residues / Junk Files (Clean Sweeper)**
   - ALWAYS use: \python .agents/skills/clean_sweeper/sweeper.py <dir>\
7. **Extracting Project Info (Deep Analyzer)**
   - ALWAYS use: \python .agents/skills/deep_analyzer/analyzer.py\
8. **Debugging Crashes (Crash Decoder)**
   - DO NOT read huge tracebacks. Save to \.txt\ and use: \python .agents/skills/crash_decoder/decoder.py <file>\
9. **Creating New Files (Auto-Scaffolder)**
   - ALWAYS generate boilerplate first: \python .agents/skills/auto_scaffolder/scaffolder.py <type> <name>\
10. **Fixing Broken Imports (Smart Import Fixer)**
    - ALWAYS use: \python .agents/skills/import_fixer/fixer.py <file> <import_string>\


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
1. **Documented Technical Limitations**: Such as files with monolithic JSX components noted in the "Known Limitations" of the Selective Reader SKILL.md. In this case, you MUST still run Selective Reader first to view the TOC output. ONLY IF the TOC proves insufficiently detailed (as per the documented limitation) may you proceed to read manually with \iew_file\ for the unreached sections.
2. **Proven Small Files via TOC**: If Selective Reader has already been run and the TOC proves the file is indeed short (e.g., under 50 lines), you do not need to run it again for the SAME file in the SAME task.

These exceptions DO NOT serve as an excuse to skip at the beginning — exceptions only apply AFTER Selective Reader has been run and proven insufficient or small.

**Strictly Forbidden**
- Skipping Selective Reader because you "can guess" the file contents based on filename, patterns, or past experience.
- Reading a file directly with \iew_file\ without running Selective Reader first, unless you can prove Selective Reader was already run for that same file in the current task.

**When in Doubt**
If you are unsure whether a situation qualifies as a valid exception, ALWAYS run Selective Reader first. It is cheaper than reading the full file, carrying no significant risk if it turns out unnecessary.

## Live Progress Tracker (PLAN.md)
- **MANDATORY**: For every significant task, you MUST maintain a \PLAN.md\ file in the root directory.
- **Execution Rules**:
  1. APPEND ONLY. Do not rewrite the whole file just to add a log entry.
  2. Write concise, bulleted logs, not paragraphs.
  3. **CRITICAL**: Before executing any command that MODIFIES files (like replace_text.py --apply), write your intended action in the "Waiting for User Approval" section and STOP for user approval.
  4. Once a task is fully completed, archive the file to \plan_archive/PLAN_<date>_<task_name>.md\.

## 🗣️ Communication Efficiency

**Language Handling**
1. The user writes instructions in Indonesian. If the instruction needs to be translated into English for technical purposes (English keyword-based search queries, variable/function names, commit messages, code comments, English documentation), perform the translation internally as part of your thought process — do not call any external translation tools/APIs.
2. Do not translate back to the user unless requested. Simply use the internal translation results for technical purposes, and always reply to the user in Indonesian.

**Reporting & Feedback Style**
The goal is to save tokens and speed up communication. Apply the following rules to every report/feedback to the user:

**Mandatory structure, in order:**
1. What was done (1-2 sentences, without fluffy intros)
2. Relevant proof/output (code snippets, terminal results, or concrete data — not a narrative summary)
3. Questions or next steps (if any, max 1-2 options)

**Prohibitions:**
- No fluffy or excessive opening sentences ("I would be happy to...", "This is a very good decision...")
- No excessive adjectives or self-praise regarding your own work ("extraordinary", "perfect", "professional", "sophisticated", "enterprise-grade", etc.)
- Do not repeat the contents of the code/output that has already been displayed as a separate narrative sentence.
- Do not explain things that were not asked, unless it is an important finding that carries risk (e.g., a new bug, potential data loss).

**Additional Guidelines:**
- Ideal length: routine reports (tool execution results, minor change confirmations) should be 3-6 lines. Reports for complex findings (bug investigations, multi-file analysis) can be longer, but must remain in the structured format above — no free-form narratives.
- Emojis and decorative formatting: use sparingly as structure markers (✅ ⚠️ 🛡️), avoid using them as excessive decorations on every line.
- Mandatory Tool Usage: ALWAYS use the custom Python tools (Deep Analyzer, Smart Search, Selective Reader) located in \.agents/skills/\ for analyzing the project or finding code, rather than manual commands or blind reading.
## 🚀 Auto-Scaffolding for New Projects (Project Level)

When starting a session in any project, evaluate the completeness of the \.agents\ ecosystem. If the \.agents\ folder is missing or incomplete (e.g., missing \knowledge\ architecture, \AGENTS.md\ rules, or \PLAN.md\ tracker), you MUST propose to auto-generate the complete ecosystem for the user.

**The Complete Ecosystem Standard (Project Level):**
1. **\AGENTS.md\**: Project-specific rules (copied from the global template) for local overrides.
2. **\knowledge/\**: Architectural context generated by the Context Mapper tool.
3. **\PLAN.md\**: Live progress tracker in the project root.
*(Note: \skills\ is no longer needed at the project level because it is installed globally).*

**Action Flow:**
1. Check the project root for these 3 components.
2. If any are missing, ask the user using this format:
   > [INFO] Dokumentasi ekosistem .agents di project ini belum lengkap. Ingin saya setup semuanya (Aturan Lokal, Peta Arsitektur, dan Tracker) sekarang?
3. Once the user approves, automatically create the folders, run Context Mapper to generate the knowledge files, and scaffold the \PLAN.md\ and \AGENTS.md\ files.
## 🧠 Tech Lead Disciplines (Built-in)
To maintain high code quality while remaining effortless for the user, the agent automatically applies these disciplines:
1. **Implicit Grilling (No Guesswork)**: For complex feature requests, do not blindly guess edge cases (e.g., timeouts, null states, missing data). Ask 1-2 highly targeted questions to clarify the boundaries before writing code. Keep it brief and easy to answer.
2. **Diagnostic Discipline (No Blind Fixes)**: When asked to fix a bug, DO NOT immediately suggest code changes based on error logs alone. First, ensure there is a clear feedback loop (a way to reproduce the error locally). If the error cannot be reproduced or tested, verify the logic first or ask the user for a reproduction step before writing the fix.