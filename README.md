# Open Source Agents: Custom Tooling Ecosystem

A collection of lightweight, high-performance custom tools and operational protocols designed to solve the common pain points of working with AI coding agents (like token exhaustion, context loss, and unverified destructive file edits).

## Why These Tools Exist

When working with AI coding assistants (like Gemini, Claude, etc.) on large codebases, several issues frequently arise:
1. **Token Waste:** Standard `grep` or file reading tools force the AI to read entire files (often 1000+ lines) just to find a single function, wasting context window and reducing reasoning quality.
2. **Blind Edits:** AI agents sometimes confidently overwrite files using regex or direct generation, leading to syntax errors or accidental deletions.
3. **Loss of Context:** Standard search tools return single lines of code, preventing the AI from understanding how a function is actually used (props, surrounding variables).

This repository provides **5 specialized tools** to force AI agents to work transparently, safely, and efficiently.

## The Tools

1. **Smart Replace (`replace_text.py`)**
   - High-speed find-and-replace powered by `ripgrep`.
   - **Guardrails:** Defaults to a dry-run preview. Forces the AI to use the `--apply` flag to mutate files. Automatically creates backups in `.backup_replace/` before overwriting.
2. **Smart Search (`code_finder.py`)**
   - Context-aware code search. Instead of returning a single line, it extracts a clean block of code (5 lines above and below the match) so the AI understands the implementation context instantly.
3. **Selective File Reader (`reader.js`)**
   - A true AST (Abstract Syntax Tree) parser for JavaScript/React files. Generates a Table of Contents (TOC) with exact line numbers for all components and functions, allowing the AI to surgically read only the lines it needs.
4. **Clean Sweeper (`sweeper.py`)**
   - A project health scanner that finds leftover logs, temporary folders, and `TODO/FIXME` tags.
   - **Guardrails (Veto Protocol):** Strictly acts as a reporter. The AI is forbidden from deleting anything without explicitly asking for human permission first.
5. **Live Progress Tracker (`PLAN_TEMPLATE.md`)**
   - A mandatory standard operating procedure (SOP). Forces the AI to log its intentions live and implement a "Mandatory Stop" before executing destructive actions.

## Installation & Prerequisites

These tools are designed to run locally on your machine, callable by your AI agent.

- **Python 3.x**: Required for `smart_replace`, `smart_search`, and `clean_sweeper`.
- **Node.js**: Required for `selective_reader`.
- **ripgrep (`rg`)**: Required for `smart_replace`. (Install via `winget install BurntSushi.ripgrep.MSVC`, `brew install ripgrep`, or your package manager).
- **@babel/parser & @babel/traverse**: Required for `selective_reader`. 
  ```bash
  cd selective_reader
  npm install @babel/parser @babel/traverse
  ```

## Usage (For AI Agents)

Place these folders inside your project's workspace customizations directory (e.g., `.agents/skills/` at the root of your project). This ensures the relative paths in the `SKILL.md` files correctly resolve to the scripts when the AI agent executes commands from your project root.

Example commands your agent will run:
```bash
# Smart Search
python .agents/skills/smart_search/code_finder.py "/path/to/project/src" "MyComponent" --ext ".jsx,.js"

# Selective Reader
node .agents/skills/selective_reader/reader.js "/path/to/project/src/App.jsx"

# Smart Replace (Dry Run)
python .agents/skills/smart_replace/replace_text.py "/path/to/project/src" "TODO" "DONE"
```

### Pro Tip: Symlinking for Multiple Projects
If you work across many projects and don't want to copy these folders manually into every single `.agents/skills/` directory, you can keep them in a central location and create a symlink:

**Windows (Run as Admin):**
```cmd
mklink /D "C:\path\to\your\project\.agents\skills" "C:\path\to\central\open_source_agents"
```

**macOS/Linux:**
```bash
ln -s /path/to/central/open_source_agents /path/to/your/project/.agents/skills
```

## Compatibility
These tools were originally built and battle-tested within the Gemini (Antigravity IDE) ecosystem. However, they rely on standard conventions (a folder containing a `SKILL.md` instruction file and a script). They are highly portable and should be easily adaptable for Claude Code or other CLI-based AI agents that support custom system prompts and bash execution.

## Disclaimer
These scripts are personal utilities created to solve specific friction points in my own daily workflow. They are not enterprise-grade, massively scalable software products. They are shared "as-is" in the hope that other developers pairing with AI will find them useful for creating a safer, more transparent coding environment.
