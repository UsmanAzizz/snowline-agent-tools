# ❄️ Snowline Agent Tools

![Python](https://img.shields.io/badge/Python-3.x-blue.svg?logo=python&logoColor=white)
![No Dependencies](https://img.shields.io/badge/Dependencies-Zero-brightgreen.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## 🚀 Quick Install (Project-Level)
Make any project "AI-Ready" in seconds. Run one of these commands in your project's root folder to instantly install the Snowline Agent ecosystem. It will safely scaffold `.agents/skills`, `.agents/knowledge`, and your `PLAN.md` without affecting global system configs.

**Option 1: Using NPM (Cross-Platform)**
```bash
npx create-snowline-agents
```

**Option 2: Using PowerShell (Windows)**
```powershell
irm https://raw.githubusercontent.com/UsmanAzizz/snowline-agent-tools/main/install.ps1 | iex
```

**Option 3: Using Bash/cURL (Mac/Linux)**
```bash
curl -sL https://raw.githubusercontent.com/UsmanAzizz/snowline-agent-tools/main/install.sh | bash
```

---

A collection of simple, portable, and lightweight Python scripts specifically designed to guide AI coding assistants (like Gemini, Claude, or Aider) working within a repository.

The main goal of this project is to **save LLM token usage** by preventing the AI from reading files blindly, as well as providing safety guardrails for automated file modifications.

## 🏛️ Core Principles

1. **Simple & Portable:** 100% pure Python (`os`, `re`, `json`). No `node_modules` required, no external executors like `ripgrep` needed. Just copy the scripts to your project and run them.
2. **Token Efficient:** Terminal outputs are extremely concise. No useless long logs, only displaying crucial insights (`[FAIL]`, `[WARN]`) to prevent the AI from exhausting its context memory.
3. **AI Prompt Bridge:** Each Python script doesn't just print data; it also returns a ready-to-use prompt sentence at the very last line, so users can instantly copy it to guide the AI.
4. **Protection & Dry-Run:** Scripts that modify files MUST feature a dry-run preview mode by default and force the use of an `--apply` argument before actually altering files on disk.

---

## 🛠️ The Arsenal (13 Core Tools)

The ecosystem is divided into three major categories: **Search & Modify**, **Audit & Analyze**, and **Workflow Helpers**.

### Category 1: Search & Modify
*These tools replace standard IDE search and regex-replace functions with AI-optimized alternatives.*

#### 1. Smart Replace (`smart_replace/replace_text.py`)
- **Function:** High-speed find-and-replace using pure Python regex.
- **Why it's better:** It has built-in guardrails. By default, it runs a dry-run preview. It forces the user/AI to use the `--apply` flag to mutate files. When applying, it automatically creates backups in a `.backup_replace/` folder before overwriting, preventing catastrophic code loss.

#### 2. Smart Search (`smart_search/code_finder.py`)
- **Function:** Context-aware code search.
- **Why it's better:** Instead of just returning a single line like `grep`, it returns a clean block of code (strictly limited to 5 lines of context) so the AI understands the implementation instantly.

#### 3. Smart Import Fixer (`import_fixer/fixer.py`)
- **Function:** Automatically resolves broken relative imports.
- **Why it's better:** If a file is moved, relative imports break. This tool searches the entire project for the missing file, calculates the correct relative path, and patches the file automatically.

### Category 2: Audit & Analyze
*These tools replace manual file reading and code reviews, saving massive amounts of AI tokens.*

#### 4. Project Guardian (`project_guardian/guardian.py`)
- **Function:** A holistic security and health auditor. 
- **Why it's better:** Detects exposed credentials, validates `.gitignore` rules, checks for broken relative imports, flags unused npm packages, and runs NPM audit.

#### 5. Clean Sweeper (`clean_sweeper/sweeper.py`)
- **Function:** A project health and tech-debt scanner.
- **Why it's better:** Finds leftover quarantine logs, temporary backup folders, massive commented-out code blocks, and `TODO/FIXME` tags.

#### 6. Deep Analyzer (`deep_analyzer/analyzer.py`)
- **Function:** The Project Profiler / X-Ray Scanner.
- **Why it's better:** Automatically extracts the tech stack, core dependencies, file statistics, and available testing/linting commands. 

#### 7. Selective Reader (`selective_reader/reader.py`)
- **Function:** Table of Contents (TOC) Extractor for large files.
- **Why it's better:** Uses Python regex heuristics to extract the skeleton of JS/TS/Py files. Allows the AI to surgically read only the lines it needs.

#### 8. Context Mapper (`context_mapper/context_mapper.py`)
- **Function:** The Knowledge Catalog builder. 
- **Why it's better:** Automatically generates architectural maps inside `.agents/knowledge/` to give agents instant context.

#### 9. Smart Tree Viewer (`smart_tree/scripts/tree_viewer.py`)
- **Function:** The compact directory mapper.
- **Why it's better:** Generates a `.gitignore`-aware visual directory tree, avoiding the verbosity of standard `ls` or JSON-based directory listing tools.

#### 10. Database Extractor (`db_extractor/scripts/extractor.py`)
- **Function:** Database Schema Extractor.
- **Why it's better:** Safely parses `.env` to connect to DBs (MySQL/MariaDB) or statically analyzes code for NoSQL schemas, providing full table/column context without running raw SQL queries manually.

### Category 3: Workflow Helpers
*These tools assist the AI when actively writing or debugging code.*

#### 11. Crash Decoder (`crash_decoder/decoder.py`)
- **Function:** The Error Trace Analyzer.
- **Why it's better:** Parses massive terminal crash logs, filters out irrelevant `node_modules` noise, and pinpoints the exact file and line in your source code that caused the crash.

#### 12. Auto-Scaffolder (`auto_scaffolder/scaffolder.py`)
- **Function:** The Pattern Generator. 
- **Why it's better:** Instantly generates boilerplate files for React components or API routes following the project's standards.

#### 13. Impact Analyzer (`impact_analyzer/analyzer.py`)
- **Function:** Dependency Graph / Impact Predictor.
- **Why it's better:** Before modifying or deleting a core component, this tool traces reverse-imports up to 3 levels deep to tell the AI EXACTLY which files will break if the target file is changed.

---

## 🚀 Installation & Usage

These tools are designed to run locally on your machine, callable by your AI agent or by yourself. **Python 3.x is the only requirement.**

### Interactive Dashboard (For Humans)
For human users, the easiest way to use the ecosystem is via the central dashboard:
```bash
python run_all.py
```
This will launch a CLI menu where you can select and run any of the 10 tools interactively.

### AI Agent Workflow (For AI)
Place these folders inside your project's workspace customizations directory (e.g., `.agents/skills/` at the root of your project). 

Example commands your agent will run:
```bash
# Analyze the project stack
python .agents/skills/deep_analyzer/analyzer.py

# Auto Scaffold a React Component
python .agents/skills/auto_scaffolder/scaffolder.py react "DataSiswa" "src/view/admin/data_siswa"

# Project Guardian (Silent Mode)
python .agents/skills/project_guardian/guardian.py --summary
```

## 🤝 Compatibility
These tools were originally built and battle-tested within the Gemini (Antigravity IDE) ecosystem. However, they are highly portable and easily adaptable for **Claude Code**, **Aider**, or other CLI-based AI agents that support custom system prompts and bash execution.
