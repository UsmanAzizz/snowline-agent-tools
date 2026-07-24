# Snowline Agent Tools: The 10-Pillars Ecosystem

A suite of lightweight, high-performance custom tools and operational protocols engineered to solve critical bottlenecks in AI-assisted coding for mid-tier and enterprise-level projects (e.g., token exhaustion, context loss, and unverified destructive file edits).

## The Philosophy

This toolset was completely overhauled to adhere to 4 strict design pillars, specifically tailored for mid-level production codebases where security, speed, and reliability are paramount:
1. **Extreme Portability:** 100% Pure Python. No Node.js required. No external binaries (like `ripgrep`). Just clone into your workspace and run instantly.
2. **Aggressive Token Saving:** Suppresses verbose logs. Outputs are strictly limited to actionable insights (`[FAIL]`, `[WARN]`) to preserve the AI's context window and reduce LLM inference costs. File sizes are capped at 500KB to prevent memory bottlenecks.
3. **AI Bridge (UX):** Tools do not just dump raw data. At the end of every scan, the tool generates a ready-to-use **Copy-Paste Prompt** that human engineers can directly feed back to their AI agent for immediate, context-aware remediation.
4. **Interactive Accessibility:** A central `run_all.py` dashboard allows engineers to execute any security or refactoring tool interactively without memorizing complex CLI arguments.

---

## 🛠️ The Arsenal (10 Core Tools)

The ecosystem is divided into three major categories: **Search & Modify**, **Audit & Analyze**, and **Workflow Helpers**.

### Category 1: Search & Modify
These tools replace standard IDE search and regex-replace functions with AI-optimized alternatives.

**1. Smart Replace (`smart_replace/replace_text.py`)**
- **Function:** High-speed find-and-replace using pure Python regex.
- **Why it's better:** It has built-in guardrails. By default, it runs a dry-run preview. It forces the user/AI to use the `--apply` flag to mutate files. When applying, it automatically creates backups in a `.backup_replace/` folder before overwriting, preventing catastrophic code loss.
- **Usage:** `python replace_text.py <dir> <search_string> <replace_string> [--apply]`

**2. Smart Search (`smart_search/code_finder.py`)**
- **Function:** Context-aware code search.
- **Why it's better:** Instead of just returning a single line like `grep`, it returns a clean block of code (strictly limited to 5 lines of context) so the AI understands the implementation instantly.
- **Usage:** `python code_finder.py <dir> <keyword>`

**3. Smart Import Fixer (`import_fixer/fixer.py`)**
- **Function:** Automatically resolves broken relative imports.
- **Why it's better:** If a file is moved, relative imports (like `../../services/api.js`) break. This tool searches the entire project for the missing file, calculates the correct relative path, and patches the file automatically (with dry-run and backup safety nets).
- **Usage:** `python fixer.py <source_file> <broken_import_string> [--apply]`

### Category 2: Audit & Analyze
These tools replace manual file reading and code reviews, saving massive amounts of AI tokens.

**4. Project Guardian (`project_guardian/guardian.py`)**
- **Function:** A holistic security and health auditor. 
- **Why it's better:** It detects exposed credentials (passwords, API keys), validates `.gitignore` rules against active `.env` files, checks for broken relative imports, flags unused npm packages, and runs NPM audit—all in one command.
- **Usage:** `python guardian.py [--summary]`

**5. Clean Sweeper (`clean_sweeper/sweeper.py`)**
- **Function:** A project health and tech-debt scanner.
- **Why it's better:** It finds leftover quarantine logs, temporary backup folders (like `AA/`, `old/`), massive commented-out code blocks, and `TODO/FIXME` tags.
- **Usage:** `python sweeper.py <target_dir>`

**6. Deep Analyzer (`deep_analyzer/analyzer.py`)**
- **Function:** The Project Profiler / X-Ray Scanner.
- **Why it's better:** Automatically extracts the tech stack (React, Node, Vite, etc.), core dependencies, file statistics, and available testing/linting commands directly from `package.json` or config files. Prevents the AI from wasting tokens reading massive configuration files manually.
- **Usage:** `python analyzer.py <target_dir>`

**7. Selective Reader (`selective_reader/reader.py`)**
- **Function:** Table of Contents (TOC) Extractor for large files.
- **Why it's better:** Uses Python regex heuristics to extract the skeleton (classes, functions, arrow functions) of JS/TS/Py files. Allows the AI to surgically read only the lines it needs rather than dumping a 1000-line file into the context window.
- **Usage:** `python reader.py <absolute_file_path>`

**8. Context Mapper (`context_mapper/context_mapper.py`)**
- **Function:** The Knowledge Catalog builder. 
- **Why it's better:** Automatically generates `PROJECT_STRUCTURE.md` and `COMMON_PATTERNS.md` inside `.agents/knowledge/`. AI agents are instructed to read these files first to instantly understand the project's architecture without blind-searching.
- **Usage:** `python context_mapper.py`

### Category 3: Workflow Helpers
These tools assist the AI when actively writing or debugging code.

**9. Crash Decoder (`crash_decoder/decoder.py`)**
- **Function:** The Error Trace Analyzer.
- **Why it's better:** Parses massive terminal crash logs (like from `npm run dev` or Vitest), filters out irrelevant `node_modules` and internal node noise, and pinpoints the exact file and line in your source code that caused the crash.
- **Usage:** `python decoder.py <path_to_error_log.txt>`

**10. Auto-Scaffolder (`auto_scaffolder/scaffolder.py`)**
- **Function:** The Pattern Generator. 
- **Why it's better:** Instantly generates boilerplate files for React components or API routes following the project's standards, avoiding inconsistent manual coding or missing imports.
- **Usage:** `python scaffolder.py <react|api> <ComponentName> [target_dir]`

---

## Installation & Prerequisites

These tools are designed to run locally on your machine, callable by your AI agent or by yourself.

- **Python 3.x**: The only requirement.

## Usage (Interactive Dashboard)

For human users, the easiest way to use the ecosystem is via the central interactive dashboard:
```bash
python run_all.py
```
This will launch a CLI menu where you can select and run any of the 10 tools interactively.

## Usage (For AI Agents)

Place these folders inside your project's workspace customizations directory (e.g., `.agents/skills/` at the root of your project). 

Example commands your agent will run:
```bash
# Smart Search
python .agents/skills/smart_search/code_finder.py "/path/to/project/src" "MyComponent"

# Project Guardian (Silent Mode)
python .agents/skills/project_guardian/guardian.py --summary

# Auto Scaffold a React Component
python .agents/skills/auto_scaffolder/scaffolder.py react "DataSiswa" "src/view/admin/data_siswa"
```

## Compatibility
These tools were originally built and battle-tested within the Gemini (Antigravity IDE) ecosystem. However, they are highly portable and should be easily adaptable for Claude Code, Aider, or other CLI-based AI agents that support custom system prompts and bash execution.
