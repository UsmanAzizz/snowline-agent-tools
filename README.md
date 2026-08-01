# ❄️ Snowline Agent Tools

![Python](https://img.shields.io/badge/Python-3.x-blue.svg?logo=python&logoColor=white)
![No Dependencies](https://img.shields.io/badge/Dependencies-Zero-brightgreen.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

Lightweight Python tools for low-mid tier projects. Work smarter — not harder.

## The Mission

**Prevent token waste in AI agent workflows.**

AI agents often read too much, search too broadly, and act without focus. These tools provide targeted capabilities for faster, more precise results.

## Core Principles

1. **Portable** — Pure Python, no external dependencies (except `db_extractor`, which requires `pymysql` for database schema extraction)
2. **Token Efficient** — Concise output, surgical precision
3. **Safe** — Dry-run modes by default for any operation that writes, modifies, or deletes files. Explicit `--apply` flag required to execute.
4. **Fast** — Low-mid tier focus, no over-engineering

## Installation

```bash
pip install git+https://github.com/UsmanAzizz/snowline-agent-tools.git
```

Initialize in your project:
```bash
python -m snowline_toolkit.cli init --apply
```

To update after a fix has been pushed (regular `pip install` does not always refresh an already-installed package):
```bash
pip uninstall snowline-toolkit -y
pip install git+https://github.com/UsmanAzizz/snowline-agent-tools.git --force-reinstall --no-cache-dir
```

## AGENTS.md — How the Ecosystem Is Used

After installation, `.agents/agents.md` is created in your project root. This file instructs the AI agent (Gemini, Claude Code, etc.) working in your project to:

1. Call `companion_cli.py` first to analyze user intent before picking a tool
2. Use read-only tools (search, analyze) without asking for confirmation
3. Require explicit approval before running write tools with `--apply`
4. Report transparently when a tool execution fails and is self-recovered, instead of hiding the troubleshooting process

This file is the actual behavior contract read by the AI agent — not just documentation.

## Companion

A lightweight intent analyzer that reads user instructions and suggests which tool to use, without making the final decision itself (the calling AI agent decides).

```bash
python .agents/skills/companion_cli.py "cari fungsi handleSubmit"
```

Returns structured data: detected keywords, entities (e.g. function names in camelCase/PascalCase), confidence level, and a suggested tool with its command template.

**Verified working with:** Claude Code (reliably auto-invoked per `.agents/agents.md` instructions) and Gemini/Antigravity (works when instructions are present in `agents.md`, though tool-call approval behavior varies by platform/IDE settings and is outside this project's control).

## Tools (14 Core)

### Search & Modify
| Tool | Purpose | Needs Approval? |
|------|---------|------------------|
| `smart_search` | Find code with surrounding context | No |
| `smart_replace` | Find-and-replace with dry-run, backup, and syntax validation | Yes (`--apply`) |
| `import_fixer` | Fix broken relative imports | Yes (`--apply`) |

### Read & Navigate
| Tool | Purpose | Needs Approval? |
|------|---------|------------------|
| `selective_reader` | Extract table of contents from large files | No |
| `smart_tree` | Compact, `.gitignore`-aware directory visualizer | No |
| `scope_guardian` | Validates whether a file is within the current task's allowed scope | No |

### Analyze & Audit
| Tool | Purpose | Needs Approval? |
|------|---------|------------------|
| `project_guardian` | Scans for exposed credentials, `.gitignore` issues, broken imports | No |
| `deep_analyzer` | Project profiler (tech stack, dependencies, file stats) | No |
| `impact_analyzer` | Traces reverse-dependencies before a file is changed | No |
| `clean_sweeper` | Finds leftover/temp files and tech debt | No |
| `db_extractor` | Extracts database schema (requires `pymysql`) | No (read-only) |

### Workflow Helpers
| Tool | Purpose | Needs Approval? |
|------|---------|------------------|
| `crash_decoder` | Parses crash logs, filters noise | No |
| `auto_scaffolder` | Generates boilerplate files (component/route templates) | Yes (`--apply`) |
| `context_mapper` | Generates architecture documentation into `.agents/knowledge/` | Yes (`--apply`) |

## Usage Examples

### Smart Search
```bash
python .agents/skills/smart_search/code_finder.py . "handleSubmit"
```

### Smart Replace (dry-run, then apply)
```bash
python .agents/skills/smart_replace/replace_text.py . "oldName" "newName"
python .agents/skills/smart_replace/replace_text.py . "oldName" "newName" --apply
```

### Project Guardian
```bash
python .agents/skills/project_guardian/guardian.py --summary
```

### Smart Tree
```bash
python .agents/skills/smart_tree/scripts/tree_viewer.py . 3
```

## Compatibility

Works with any AI agent that supports Python script execution and bash/shell commands.

**Verified with:** Claude Code, Gemini/Antigravity.

## License

MIT
