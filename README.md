# ❄️ Snowline Agent Tools

![Python](https://img.shields.io/badge/Python-3.x-blue.svg?logo=python&logoColor=white)
![No Dependencies](https://img.shields.io/badge/Dependencies-Zero-brightgreen.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

Lightweight Python tools that stop an AI agent from quietly breaking your project.

## The Mission

**Make the destructive paths refuse, instead of asking politely.**

An agent that is told not to do something can still do it. An agent that is
*refused* cannot. Snowline puts a gate on every path that can damage a project,
so a mistake gets stopped rather than logged after the fact.

Seven paths, all gated:

| what is refused | by what |
|---|---|
| writing any file without an explicit flag | `--apply`, in all four write tools |
| writing outside the current task's file list | `scope_lock.json`, fail-closed |
| a command with missing arguments | arity check, `hooks/quality_gate.py` |
| a replacement that breaks syntax | validation cancels the write |
| a Medium/High-risk change waved through | requires `--apply-validated` |
| committing a file with a readable secret | CRITICAL gate in the pre-commit hook |
| an agent looping on the same failing call | loop detector, stops after 3 |

Everything else in this repo is convention, and each rule file says which it is —
see `RULE 0` in the generated `agents.md`.

## Core Principles

1. **Portable** — Pure Python, no external dependencies (except `db_extractor`, which requires `pymysql` for database schema extraction)
2. **Refuses rather than warns** — a rule that only prints a warning is documented as advice, not enforcement
3. **Safe** — Dry-run modes by default for any operation that writes, modifies, or deletes files. Explicit `--apply` flag required to execute.
4. **Proven by running** — every fix ships with a test that was shown to fail before the fix (see [Development](docs/DEVELOPMENT.md))

## Installation

```bash
pip install git+https://github.com/UsmanAzizz/snowline-agent-tools.git
```

Initialize in your project:
```bash
python -m snowline.cli init --apply
```

To update after a fix has been pushed (regular `pip install` does not always refresh an already-installed package):
```bash
pip uninstall snowline-agent-tools -y
pip install git+https://github.com/UsmanAzizz/snowline-agent-tools.git --force-reinstall --no-cache-dir
```

## CLI Commands

### Status Check (Dual-Layer)
```bash
python -m snowline.cli status
```
Checks both **package version** (Python package from GitHub) and **project layer** (`.agents/` skills from local templates) simultaneously. Shows actionable commands when updates are available.

### Reinstall
```bash
# Restore from local package (dry-run)
python -m snowline.cli reinstall

# Execute reinstall from local package
python -m snowline.cli reinstall --apply

# Download and apply latest version from GitHub (dry-run)
python -m snowline.cli reinstall --latest

# Download latest from GitHub and execute reinstall
python -m snowline.cli reinstall --apply --latest
```
If the GitHub download fails, the local installation is left untouched.

### Init (with Force)
```bash
python -m snowline.cli init --apply
python -m snowline.cli init --apply --force  # overwrite existing skills
```
Use `--force` to restore all skills from templates, overwriting any local modifications.

## Chamber (optional)

A working protocol for running two agents against each other, installed
separately from the tools:

```bash
python -m snowline.cli init_chamber --apply
```

Creates `.agents/chamber/` with the rules, a shared `connector.md`, a
`STATE.md` state file, and one onboarding document per role (PM, TL, QA,
Executor). Paste a role's onboarding into a fresh session once; after that a
one-word signal is enough.

The load-bearing rule: an entry is rejected before it is read if it claims
something is done without including the command **and** its raw output. TL and
QA must be separate sessions — a single session holding both is reviewing its
own work.

Re-running is refused unless `--force`, so `connector.md` and `STATE.md` are
never wiped by accident.

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

## Tools (22 Core)

<table>
<thead>
<tr>
<th>Tool</th>
<th>Purpose</th>
<th>Needs Approval?</th>
</tr>
</thead>
<tbody>
<tr><td colspan="3"><strong>🔍 Search & Modify</strong></td></tr>
<tr><td><code>smart_search</code></td><td>Find code with surrounding context</td><td>No</td></tr>
<tr><td><code>smart_replace</code></td><td>Find-and-replace with dry-run, backup, and syntax validation</td><td>Yes (<code>--apply</code>)</td></tr>
<tr><td><code>import_fixer</code></td><td>Fix broken relative imports</td><td>Yes (<code>--apply</code>)</td></tr>
<tr><td><code>surgical_splicer</code></td><td>Extract a single function/class body with zero surrounding context (token-efficient for huge files)</td><td>No</td></tr>
<tr><td colspan="3"><strong>🧭 Read & Navigate</strong></td></tr>
<tr><td><code>selective_reader</code></td><td>Extract table of contents from large files</td><td>No</td></tr>
<tr><td><code>smart_tree</code></td><td>Compact, <code>.gitignore</code>-aware directory visualizer</td><td>No</td></tr>
<tr><td><code>scope_guardian</code></td><td>Validates whether a file is within the current task's allowed scope</td><td>No</td></tr>
<tr><td colspan="3"><strong>🛡️ Analyze & Audit</strong></td></tr>
<tr><td><code>project_guardian</code></td><td>Scans for exposed credentials, <code>.gitignore</code> issues, broken imports</td><td>No</td></tr>
<tr><td><code>deep_analyzer</code></td><td>Project profiler (tech stack, dependencies, file stats)</td><td>No</td></tr>
<tr><td><code>impact_analyzer</code></td><td>Traces reverse-dependencies before a file is changed, with configurable <code>--depth</code> for multi-hop chains</td><td>No</td></tr>
<tr><td><code>clean_sweeper</code></td><td>Finds leftover/temp files and tech debt</td><td>No</td></tr>
<tr><td><code>db_extractor</code></td><td>Extracts database schema (requires <code>pymysql</code>)</td><td>No (read-only)</td></tr>
<tr><td colspan="3"><strong>⚙️ Workflow Helpers</strong></td></tr>
<tr><td><code>crash_decoder</code></td><td>Parses crash logs, filters noise</td><td>No</td></tr>
<tr><td><code>auto_scaffolder</code></td><td>Generates boilerplate files (component/route templates)</td><td>Yes (<code>--apply</code>)</td></tr>
<tr><td><code>context_mapper</code></td><td>Generates dependency map into <code>.agents/knowledge/</code></td><td>Yes (<code>--apply</code>)</td></tr>
</tbody>
</table>

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

## Development

Working on snowline itself — tests, Rule #12, CI, releasing: see
[`docs/DEVELOPMENT.md`](docs/DEVELOPMENT.md).

```bash
python tests/run_tests.py     # 41 tests, ~24 seconds
```

## Compatibility

Works with any AI agent that supports Python script execution and bash/shell commands.

**Verified with:** Claude Code, Gemini/Antigravity.

## License

MIT
