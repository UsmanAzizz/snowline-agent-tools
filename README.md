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

Six paths, gated and installed by default:

| what is refused | by what |
|---|---|
| writing any file without an explicit flag | `--apply`, in all five write tools |
| writing outside the current task's file list | `scope_lock.json`, fail-closed |
| a command with missing arguments | arity check, `hooks/quality_gate.py` |
| a replacement that breaks syntax | validation cancels the write |
| a Medium/High-risk change waved through | requires `--apply-validated` |
| an agent looping on the same failing call | loop detector, stops after 3 |

**One gate ships but is not installed automatically.** `project_guardian` can
refuse a commit that contains a readable secret, but `snowline init` does not
wire it into git. Install it yourself:

```bash
python -m snowline.install_hooks <project_dir> <path_to_guardian.py>
```

Note that this **overwrites** `.git/hooks/pre-commit`. If you already have one,
merge it by hand.

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

### Global Setup (Optional)
By default, Snowline is completely portable and importing it modifies nothing. To make the `snowline` command available globally in any terminal without prefixing `python -m`, run:
```bash
python -m snowline.cli setup-path
```

This is the **only** command that modifies your system environment. If you answer `y`, it will:
- **Registry**: Append Python Scripts to `HKCU\Environment\Path`
- **Folder**: Copy `snowline.bat` wrapper to your Python `Scripts` folder
- **PowerShell Profiles**: Add Path configuration to `Documents/PowerShell/Microsoft.PowerShell_profile.ps1` and `Documents/WindowsPowerShell/Microsoft.PowerShell_profile.ps1`
- **Bash Profiles**: Add Path configuration to `~/.bashrc`, `~/.bash_profile`, and `~/.zshrc`

To explicitly opt-out and suppress any prompts (useful in CI/CD), set:
`SNOWLINE_NO_PATH_SETUP=1`

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
QA must not be the same live session — a single session holding both is
reviewing its own work.

Two ways to satisfy that:

- **Two sessions**, relayed by a human PM. Works on any harness.
- **One agent, sequential sessions.** TL works, writes its report, sets
  `role.json` to `QA` as its last act, and ends. The next session wakes with no
  memory of the first and only the chamber to go on. Tested on Claude Code:
  the second session reproduced the first's verdict and found four defects the
  full-context reviewer had missed. It needs a harness whose fresh sessions
  start genuinely cold.

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

A lightweight intent analyzer that reads user instructions, extracts entities, and evaluates ambiguity (`needs_grilling`).

```bash
python .agents/skills/companion_cli.py "cari fungsi handleSubmit"
```

**Status pembuktian:**
- **Yang terbukti**: Ekstraksi entitas (nama fungsi/berkas), deteksi kata kunci, dan penegakan arity check pada pre-hook `quality_gate.py` bekerja akurat.
- **Yang belum terbukti / belum diukur**: Efektivitas saran pemilihan alat terhadap keputusan agen di lapangan (agen sering kali sudah mengetahui alat yang ingin digunakan), serta kegunaan praktis penanda `needs_grilling` saat agen berhadapan dengan instruksi ambigu di sesi nyata.

## Tools (16)

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
<tr><td><code>native_checker_gen</code></td><td>Scaffolds a unit test or a standalone validator script</td><td>Yes (<code>--apply</code>)</td></tr>
<tr><td><code>plan_tracker</code></td><td>Tracks multi-step plan progress</td><td>No</td></tr>
<tr><td><code>tree_gen</code></td><td>Tree-rendering engine behind <code>smart_tree</code></td><td>No</td></tr>
</tbody>
</table>

*Catatan: Modul `companion` telah diarsipkan ke `archive/companion/`. Pengukuran di tiga proyek menunjukkan parsing entitasnya berfungsi baik, namun perannya sebagai gerbang pra-eksekusi menambah latensi tanpa peningkatan akurasi pemilihan alat yang signifikan. Kodenya diarsipkan di `archive/` untuk riset mandiri.*

Coverage is uneven and tracked openly: five of the nineteen have no test that
runs them and asserts their output — `companion`, `db_extractor`,
`deep_analyzer`, `plan_tracker`, `smart_tree`. They are listed as open items in
the project's own state file rather than left unsaid.

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
python tests/run_tests.py     # 56 tests, ~55 seconds
```

## Compatibility

Works with any AI agent that supports Python script execution and bash/shell commands.

**Verified with:** Claude Code, Gemini/Antigravity.

## License

MIT
