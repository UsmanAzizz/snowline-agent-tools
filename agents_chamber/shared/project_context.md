# Project Context

*Read-only reference for all agents. For full detail see PROJECT_CONTEXT.md.*

## Project Overview
**snowline-agent-tools** / **open_source_agents**

Lightweight Python tools for AI coding agents (Claude Code, Gemini). Goal: prevent token waste by providing targeted capabilities.

**Repository:** `https://github.com/UsmanAzizz/snowline-agent-tools`

## Active Sessions
- session_01: Claude Code session (idle)

## Tool Inventory (top-level folders)

| Tool | Purpose |
|------|---------|
| `.agents/` | Skill definitions (AGENTS.md, companion_cli.py) |
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

## Session History (Tasks 1-31)

- Tasks 1-22: Tool development and fixes
- Tasks 23-24: Daemon watcher (deprecated, replaced by orchestrator)
- Task 25: Python AST function extraction
- Task 26: JS/TS/JSX brace-counting extraction
- Task 27: UTF-8 stdout fix
- Task 28: Static orchestrator
- Task 29: Orchestrator live-test evidence
- Task 30: agents_chamber/ workspace structure
- Task 31: This task - placeholder content population

## Key Patterns
- **AGENTS.md**: Primary rules file (AI reads this on session start)
- **CLAUDE.md**: Points to AGENTS.md
- **Dry-run default**: All write tools require `--apply` flag
- **Task 7 insight**: Only AGENTS.md rules are reliably followed

## More Detail
- `PROJECT_CONTEXT.md` - incident history and architecture notes
- `CURRENT_STATE.md` - current project state
- `AGENTS.md` - complete rules for agent behavior
