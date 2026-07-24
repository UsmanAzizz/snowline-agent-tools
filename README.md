# ❄️ Snowline Agent Tools: The 10-Pillars Ecosystem

![Python](https://img.shields.io/badge/Python-3.x-blue.svg?logo=python&logoColor=white)
![No Dependencies](https://img.shields.io/badge/Dependencies-Zero-brightgreen.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

A suite of lightweight, high-performance custom tools and operational protocols engineered to solve critical bottlenecks in AI-assisted coding for mid-tier and enterprise-level projects. 

If you use AI coding assistants (like Gemini, Claude Code, or Aider), you know the pain of **token exhaustion**, **context loss**, and **unverified destructive file edits**. The 10-Pillars Ecosystem solves this by completely replacing standard IDE tools (`grep`, `ls`, `cat`) with AI-optimized, heavily guarded Python alternatives.

## 🏛️ The Philosophy

This toolset was completely overhauled to adhere to 4 strict design pillars, specifically tailored for mid-level production codebases where security, speed, and reliability are paramount:
1. **Extreme Portability:** 100% Pure Python. No Node.js required. No external binaries (like `ripgrep`). Just clone into your workspace and run instantly.
2. **Aggressive Token Saving:** Suppresses verbose logs. Outputs are strictly limited to actionable insights (`[FAIL]`, `[WARN]`) to preserve the AI's context window and reduce LLM inference costs. File sizes are capped at 500KB to prevent memory bottlenecks.
3. **AI Bridge (UX):** Tools do not just dump raw data. At the end of every scan, the tool generates a ready-to-use **Copy-Paste Prompt** that human engineers can directly feed back to their AI agent for immediate, context-aware remediation.
4. **Interactive Accessibility:** A central `run_all.py` dashboard allows engineers to execute any security or refactoring tool interactively without memorizing complex CLI arguments.

---

## 🛠️ The Arsenal (10 Core Tools)

The ecosystem is divided into three major categories: **Search & Modify**, **Audit & Analyze**, and **Workflow Helpers**.

### Category 1: Search & Modify
*These tools replace standard IDE search and regex-replace functions with AI-optimized alternatives.*

#### 1. Smart Replace (`smart_replace/replace_text.py`)
- **Function:** High-speed find-and-replace using pure Python regex.
- **Why it's better:** It has built-in guardrails. By default, it runs a dry-run preview. It forces the user/AI to use the `--apply` flag to mutate files. When applying, it automatically creates backups in a `.backup_replace/` folder before overwriting, preventing catastrophic code loss.
- **Example Output:**
  ```text
  [DRY-RUN MODE]
  File: src/components/Button.jsx
  - old: console.log("debug");
  + new: // console.log("debug");
  
  [OK] Scan selesai (120 file dipindai). Menemukan 1 kecocokan.
  💡 PROMPT UNTUK AI: "Berdasarkan hasil dry-run di atas, tolong jalankan ulang perintah tersebut dengan menambahkan flag --apply..."
  ```

#### 2. Smart Search (`smart_search/code_finder.py`)
- **Function:** Context-aware code search.
- **Why it's better:** Instead of just returning a single line like `grep`, it returns a clean block of code (strictly limited to 5 lines of context) so the AI understands the implementation instantly.
- **Example Output:**
  ```text
  --- File: src/utils/api.js ---
  42: export const fetchUser = async (id) => {
  43:   const response = await axios.get(`/users/${id}`);
  44:   return response.data;
  45: }
  ```

#### 3. Smart Import Fixer (`import_fixer/fixer.py`)
- **Function:** Automatically resolves broken relative imports.
- **Why it's better:** If a file is moved, relative imports (like `../../services/api.js`) break. This tool searches the entire project for the missing file, calculates the correct relative path, and patches the file automatically.

### Category 2: Audit & Analyze
*These tools replace manual file reading and code reviews, saving massive amounts of AI tokens.*

#### 4. Project Guardian (`project_guardian/guardian.py`)
- **Function:** A holistic security and health auditor. 
- **Why it's better:** Detects exposed credentials (passwords, API keys), validates `.gitignore` rules against active `.env` files, checks for broken relative imports, flags unused npm packages, and runs NPM audit—all in one command.
- **Example Output:**
  ```text
  🛡️ PROJECT GUARDIAN AUDITOR 🛡️
  --- MODULE 1: SECRET SCANNER ---
  [FAIL] Potential credential leak in src/config/db.js line 12
  
  --- MODULE 2: ENV & GITIGNORE VERIFIER ---
  [FAIL] File .env.development is missing from .gitignore!
  ```

#### 5. Clean Sweeper (`clean_sweeper/sweeper.py`)
- **Function:** A project health and tech-debt scanner.
- **Why it's better:** Finds leftover quarantine logs, temporary backup folders (like `AA/`, `old/`), massive commented-out code blocks, and `TODO/FIXME` tags.

#### 6. Deep Analyzer (`deep_analyzer/analyzer.py`)
- **Function:** The Project Profiler / X-Ray Scanner.
- **Why it's better:** Automatically extracts the tech stack, core dependencies, file statistics, and available testing/linting commands directly from `package.json` or config files. 
- **Example Output:**
  ```text
  [OK] Tech Stack Detected: Node.js, Vite (React/Vue)
  [INFO] Available npm/yarn Commands:
    - npm run start
    - npm run test
  [INFO] Core Dependencies: 55 runtime, 9 dev
  ```

#### 7. Selective Reader (`selective_reader/reader.py`)
- **Function:** Table of Contents (TOC) Extractor for large files.
- **Why it's better:** Uses Python regex heuristics to extract the skeleton (classes, functions, arrow functions) of JS/TS/Py files. Allows the AI to surgically read only the lines it needs.

#### 8. Context Mapper (`context_mapper/context_mapper.py`)
- **Function:** The Knowledge Catalog builder. 
- **Why it's better:** Automatically generates `PROJECT_STRUCTURE.md` and `COMMON_PATTERNS.md` inside `.agents/knowledge/`. AI agents read these files first to instantly understand the project's architecture.

### Category 3: Workflow Helpers
*These tools assist the AI when actively writing or debugging code.*

#### 9. Crash Decoder (`crash_decoder/decoder.py`)
- **Function:** The Error Trace Analyzer.
- **Why it's better:** Parses massive terminal crash logs, filters out irrelevant `node_modules` and internal node noise, and pinpoints the exact file and line in your source code that caused the crash.

#### 10. Auto-Scaffolder (`auto_scaffolder/scaffolder.py`)
- **Function:** The Pattern Generator. 
- **Why it's better:** Instantly generates boilerplate files for React components or API routes following the project's standards, avoiding inconsistent manual coding.

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
