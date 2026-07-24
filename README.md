# Snowline Agent Tools: The 4-Pillars Ecosystem

A suite of lightweight, high-performance custom tools and operational protocols engineered to solve critical bottlenecks in AI-assisted coding for mid-tier and enterprise-level projects (e.g., token exhaustion, context loss, and unverified destructive file edits).

## The 4 Pillars Philosophy

This toolset was completely overhauled to adhere to 4 strict design pillars, specifically tailored for mid-level production codebases where security, speed, and reliability are paramount:
1. **Extreme Portability:** 100% Pure Python. No Node.js required. No external binaries (like `ripgrep`). Just clone into your workspace and run instantly.
2. **Aggressive Token Saving:** Suppresses verbose `[OK]` logs. Outputs are strictly limited to `[FAIL]` and `[WARN]` to preserve the AI's context window and reduce LLM inference costs. File sizes are capped at 500KB to prevent memory bottlenecks.
3. **AI Bridge (UX):** Tools do not just dump raw data. At the end of every scan, the tool generates a ready-to-use **Copy-Paste Prompt** that human engineers can directly feed back to their AI agent for immediate, context-aware remediation.
4. **Interactive Accessibility:** A central `run_all.py` dashboard allows engineers to execute any security or refactoring tool interactively without memorizing complex CLI arguments.

## The Arsenal

1. **Smart Replace (`smart_replace/replace_text.py`)**
   - High-speed find-and-replace using pure Python regex. 
   - **Guardrails:** Defaults to a dry-run preview. Forces the AI to use the `--apply` flag to mutate files. Automatically creates backups in `.backup_replace/` before overwriting.
2. **Smart Search (`smart_search/code_finder.py`)**
   - Context-aware code search. Returns a clean block of code (strictly limited to 5 lines of context) so the AI understands the implementation instantly.
3. **Selective File Reader (`selective_reader/reader.py`)**
   - Uses Python regex heuristics to extract the skeleton (Table of Contents) of JS/TS/Py files. Allows the AI to surgically read only the lines it needs.
4. **Clean Sweeper (`clean_sweeper/sweeper.py`)**
   - A project health scanner that finds leftover logs, temporary folders, and `TODO/FIXME` tags.
5. **Project Guardian (`project_guardian/guardian.py`)**
   - A holistic security and health auditor (Satpam). Detects exposed credentials, validates `.gitignore` rules, checks for broken relative imports, and flags unused npm packages. Uses `--summary` for silent execution.
6. **Context Mapper (`context_mapper/context_mapper.py`)**
   - The Knowledge Catalog builder. Automatically generates `PROJECT_STRUCTURE.md` and `COMMON_PATTERNS.md` inside `.agents/knowledge/`. AI agents are instructed to read these files first to instantly understand the project's architecture without blind-searching.
7. **Deep Analyzer (`deep_analyzer/analyzer.py`)**
   - The Project Profiler (X-Ray Scanner). Automatically extracts the tech stack, core dependencies, file statistics, and available testing/linting commands directly from `package.json` or config files. Prevents the AI from wasting tokens reading massive configuration files manually.

## Installation & Prerequisites

These tools are designed to run locally on your machine, callable by your AI agent or by yourself.

- **Python 3.x**: The only requirement.

## Usage (Interactive Dashboard)

For human users, the easiest way to use the ecosystem is via the central interactive dashboard:
```bash
python run_all.py
```
This will launch a CLI menu where you can select and run any of the 6 tools interactively.

## Usage (For AI Agents)

Place these folders inside your project's workspace customizations directory (e.g., `.agents/skills/` at the root of your project). 

Example commands your agent will run:
```bash
# Smart Search
python .agents/skills/smart_search/code_finder.py "/path/to/project/src" "MyComponent" --ext ".jsx,.js"

# Project Guardian (Silent Mode)
python .agents/skills/project_guardian/guardian.py --summary

# Smart Replace (Dry Run)
python .agents/skills/smart_replace/replace_text.py "/path/to/project/src" "TODO" "DONE"
```

## Compatibility
These tools were originally built and battle-tested within the Gemini (Antigravity IDE) ecosystem. However, they are highly portable and should be easily adaptable for Claude Code, Aider, or other CLI-based AI agents that support custom system prompts and bash execution.
