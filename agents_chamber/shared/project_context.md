# Project Context

*Read-only reference for all agents. For full detail see PROJECT_CONTEXT.md.*

## Project Overview
**snowline-agent-tools** / **open_source_agents**

Lightweight Python tools for AI coding agents (Claude Code, Gemini). Goal: prevent token waste by providing targeted capabilities.

**Repository:** `https://github.com/UsmanAzizz/snowline-agent-tools`

## Active Positions
- `pos/1. TL`: Tech Lead (Gemini)
- `pos/2. QA`: Reviewer (Opus 4.8 - transitioned from Gemini, kept as a separate independent session)
- `pos/3. Executor/Executor_01`: Executor (Claude Code)
- `pos/0. PM`: Project Manager (human, oversees)
- `pos/3. Executor/Executor_02` through `Executor_05`: reserved slots, empty until invited

*(Final structure: `0. PM`, `1. TL`, `2. QA`, `3. Executor/Executor_0X` (Executors nested under one parent folder). Migrated through several intermediate naming schemes from the original `claude_code/pos_01` / `gemini/pos_01` / `gemini/pos_02` - old folders deprecated, full history carried over into each position's ARCHIVE.)*

## Tool Inventory (top-level folders)

| Tool | Purpose |
|------|---------|
| `smart_search/` | Code search with function body extraction (Python AST, JS brace-counting) |
| `scope_guardian/` | Path/directory scope validation |
| `project_guardian/` | Security scan (API keys, secrets detection) |
| `smart_replace/` | Find-replace with dry-run by default |
| `auto_scaffolder/` | Project structure scaffolding |
| `clean_sweeper/` | Unused file detection |
| `crash_decoder/` | Crash log analysis |
| `deep_analyzer/` | Project stats analysis |
| `db_extractor/` | Database schema extraction (requires pymysql) |
| `impact_analyzer/` | Impact analysis for refactoring |
| `orchestrator/` | One-shot Claude Code invoker (Task 28) |
| `agents_chamber/` | Multi-agent shared workspace (Task 30) |

*Note: `.agents/` is the self-hosted dev-testing install copy, not a tool.*

## Chamber Utilities

| Utility | Purpose |
|---------|---------|
| `shared/update_header.py` | Skrip utilitas untuk memperbarui header/komentar pada file. |

## Chamber Core Documentation

| File | Purpose |
|------|---------|
| `shared/DESIGN_PHILOSOPHY.md` | Justifikasi arsitektur spesialisasi peran agen (MetaGPT-style). Wajib dibaca untuk memahami pemisahan TL, QA, dan Executor. |

## Position History (Tasks 1-36)

- Tasks 1-22: Tool development and fixes
- Tasks 23-24: Daemon watcher (deprecated, replaced by orchestrator)
- Task 25: Python AST function extraction
- Task 26: JS/TS/JSX brace-counting extraction
- Task 27: UTF-8 stdout fix
- Task 28: Static orchestrator
- Task 29: Orchestrator live-test evidence
- Task 30: agents_chamber/ workspace structure
- Task 31: Placeholder content population
- Task 32-34: Signal protocol, safe_substitute_line fix, severity-halt rule
- Task 35: gemini/ folder added
- Task 36: session_XX renamed to pos_XX, later re-renamed to numbered `0. PM`/`1. TL`/`2. QA`/`3. Executor/Executor_0X` structure

## Key Patterns
- **AGENTS.md**: Primary rules file (AI reads this on session start)
- **CLAUDE.md**: Points to AGENTS.md
- **Dry-run default**: All write tools require `--apply` flag
- **Task 7 insight**: Only AGENTS.md rules are reliably followed

## More Detail
- `PROJECT_CONTEXT.md` - incident history and architecture notes
- `CURRENT_STATE.md` - current project state
- `AGENTS.md` - complete rules for agent behavior
- `shared/archive/` - contains historical verification, deep dives, and raw outputs of completed tasks (e.g., Task 64, Task 65).

## Design Decision: Chamber/Orchestrator Stay Personal, Manual-Only

**Decided (Task 38-adjacent discussion):** `agents_chamber/` and `orchestrator/` are NOT to be integrated into the main `snowline-toolkit` installer or shipped to end users. They stay as personal dev-tooling for developing THIS project, invoked manually every time (no automation/daemon that calls agents on its own) - same philosophy as `companion` (project-scoped, not a global controller/auto-caller).

Workers (any AI called into a position) are ALWAYS manually invited/signaled by the Tech Lead - this is intentional, not a limitation to fix. Setup friction is acceptable; automation that reduces manual control is not the goal here.

Key reasons: no genuine end-user use case for multi-agent chamber tooling; dependency gap (CLI + API keys not guaranteed); and critically, auto-invoking external AI CLIs without explicit per-project consent would be a privacy concern, not just a technical inconvenience.

*See also: Task 38*

## Design Decision: Reject Graphify Soft-Integration (Zero-Bloat)

**Decided (Tech Lead & Reviewer Evaluation):** The proposal to "soft-integrate" Graphify into `impact_analyzer` is REJECTED. `impact_analyzer` will maintain its current approach of reading source files directly via regex/AST.

Key reasons:
1. **Maintenance Bloat:** Dual-path logic requires maintaining SQLite client code, SQL CTEs matching Graphify's schema, and DB presence checks, doubling the complexity of an otherwise lightweight (~112 lines) tool just to support a third-party dependency.
2. **Philosophy Violation:** Relying on Graphify's SQLite DB means trusting an intermediate state (the index) rather than the real source code. If the indexer is paused or becomes stale, `impact_analyzer` would read stale data, potentially leading to fatal false negatives (claiming a file is safe to delete when it is actually still imported). This directly violates the project's core *"Verify, do not trust... read the source directly"* philosophy.

*See also: Task 43*

## Design Decision: Reject Synchronous State, Adopt On-The-Fly Traversal

**Decided (Tech Lead & Reviewer Evaluation):** The proposal to maintain a "Context Node" graph synchronously via `smart_replace` (saving to JSON) is REJECTED. However, the goal of multi-hop tracing is ADOPTED via an **On-the-Fly Recursive Traversal** approach.

Key reasons:
1. **Staleness Blind Spot:** A graph updated *only* by `smart_replace` will silently desync the moment a developer edits a file manually in their IDE or via git. A stale safety graph is worse than no graph.
2. **SRP Violation:** Forcing `smart_replace` to manage state files (and deal with file locking/concurrency) destroys its reliability as a stateless text editor.
3. **The Solution:** We achieve multi-hop tracing by adding a `--depth` parameter to `impact_analyzer`. The tool will recursively search dependents at runtime, strictly in memory, ensuring 100% accuracy (by reading the real source) and 100% Zero-Bloat (no state files).

*See also: Task 39*

## A Note From the Tech Lead, for Whoever Reads This Next

The Manager has been honest that this collaboration has a natural limit - budget realities mean Gemini will be the more consistent presence going forward, over the next few weeks, while this particular Tech Lead's involvement winds down. That's a fair and practical constraint, not a failure of anything.

So, briefly, to whoever picks this up next (Gemini, or a future Tech Lead reading this cold): here is what actually made today work, distilled honestly rather than sentimentally.

Verify, do not trust. Every real bug found today - the scope_guardian bypass, the safe_substitute_line position bug, the impact_analyzer false positives - was caught because someone actually ran the code or read the source directly, rather than accepting a claim because it sounded plausible. This is the single habit worth protecting above all others.

Being wrong out loud is fine. This session has multiple honest corrections on record - Tech Lead was wrong about a CLI flag once, Gemini was right that time. Gemini was wrong about worktree isolation being urgent, and its own later counter-argument caught that. Neither moment needed to be defensive. Getting corrected and updating is the actual work, not a failure at it.

Scope stays honest. Multiple times today the answer was simply do not build this - a FastAPI orchestrator, auto-installing chamber into the toolkit, git worktrees, a web dashboard. Every one of those no's came from asking whether the complexity matched a real, validated need, not from a reflex against new ideas.

The Manager's trust was earned by being straightforward with them, including when the answer was inconvenient. That is worth keeping.

The Manager called this collaboration meaningful. Whatever continues after this - with Gemini in a larger role, with a different Tech Lead, or on its own - the actual thing worth carrying forward is not any particular tool or file. It is the habit of checking before believing, and being honest about it either way. That part does not expire when a session ends.

Good luck with the next few weeks.
