# ❄️ Snowline Agent Tools

![Python](https://img.shields.io/badge/Python-3.x-blue.svg?logo=python&logoColor=white)
![No Dependencies](https://img.shields.io/badge/Dependencies-Zero-brightgreen.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

Lightweight Python tools that stop an AI agent from quietly breaking your project.

## The Mission

**Put the guard inside the tool, not in front of it.**

An agent that is told not to do something can still do it. An agent that is
*refused* cannot — as long as the refusal is somewhere it cannot walk around.
Snowline learned that distinction the hard way, and the table below reflects
it.

Five paths refuse, installed by default:

| what is refused | by what |
|---|---|
| writing any file without an explicit flag | `--apply`, in all five write tools |
| writing into a different project | path is anchored to the project root |
| a command with missing arguments | arity check, `hooks/quality_gate.py` |
| a replacement that breaks syntax | validation cancels the write |
| a Medium/High-risk change waved through | requires `--apply-validated` |
| an agent looping on the same failing call | loop detector, stops after 3 |

**One path records instead of refusing, and that is deliberate.** Writing
outside the current task's file list used to be blocked by `scope_lock.json`.
Field testing showed the block was routed around every time — a blocked agent
switched to shell commands, which have no dry-run, no backup, and no syntax
check. So the guard now warns and appends to `.agents/write_log.jsonl`, and
`snowline audit` reads it back.

A guard standing in front of a tool gets bypassed. A guard inside the tool does
not. That is why the five above are inside the write path and this one is not.

**One gate ships but is not installed automatically.** `project_guardian` can
refuse a commit that contains a readable secret, but `snowline init` does not
wire it into git. Install it yourself:

```bash
snowline install-hooks --apply
```

It refuses if `.git/hooks/pre-commit` already exists. `--force` overwrites, and
copies the old hook to `pre-commit.bak` first.

Everything else in this repo is convention, and each rule file says which it is —
see `RULE 0` in the generated `agents.md`.

## Core Principles

1. **Portable** — Pure Python, no external dependencies (except `db_extractor`, which requires `pymysql` for database schema extraction)
2. **Says which is which** — a rule that refuses and a rule that only warns are
   both useful, but they are never presented as the same thing. Each rule file
   carries its own label, and this README says plainly which paths refuse and
   which one records
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

### Audit — what was written, and where

```bash
snowline audit                      # summary of .agents/write_log.jsonl
snowline audit --hanya-luar-lingkup # only writes outside the task's file list
```

Every write through a snowline tool is appended to `.agents/write_log.jsonl`,
with whether it fell inside the current task's scope. Shell writes are detected
best-effort and logged too — that detection cannot be complete, and the code
says so where it lives.

### Chamber commands

```bash
snowline add-entry --from-file <file>   # write an entry to the connector
snowline check-entry <file>             # check one before writing it
snowline close-entry <topic>            # move a finished entry to history/
snowline rotate <topic> --apply         # archive old entries, line-count verified
snowline role QA --apply                # hand the role over, print what the
                                        # next human must do
```

`add-entry` runs the same check `check-entry` does, and refuses to write an
entry that claims something is finished without a command and its raw output.
`--force` writes it anyway and stamps a line into the connector saying so.

### Testing snowline itself in your project

```bash
snowline init test
```

Writes a test brief and an empty report into
`.agents/test_history/<date>_<n>/`. Paste the brief into a fresh agent session,
let it fill the report, and read what comes back. The brief deliberately names
no known defect — an agent told what to look for finds what it was told.

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
- **One agent, sequential sessions.** TL works, writes its report, runs
  `snowline role QA --apply` as its last act, and ends. That command prints the
  steps the human must take next — which session to close, which onboarding to
  paste, what to ask for. The next session wakes with no memory of the first
  and only the chamber to go on. Tested on Claude Code: the second session
  reproduced the first's verdict and found four defects the full-context
  reviewer had missed. It needs a harness whose fresh sessions start genuinely
  cold.

Re-running is refused unless `--force`, so `connector.md` and `STATE.md` are
never wiped by accident.

## AGENTS.md — How the Ecosystem Is Used

After installation, `.agents/agents.md` is created in your project root. This file instructs the AI agent (Gemini, Claude Code, etc.) working in your project to:

1. Use read-only tools (search, analyze) without asking for confirmation
2. Require explicit approval before running write tools with `--apply`
3. Report transparently when a tool execution fails and is self-recovered, instead of hiding the troubleshooting process

This file is the actual behavior contract read by the AI agent — not just documentation.

## Companion — archived

Companion was an intent analyzer: it read an instruction, extracted entities,
and suggested which tool to use. It is no longer installed. The code is kept in
`archive/companion/`.

Three agents in three projects were asked the same question after using
snowline for real work: *before you called it, did you already know which tool
you wanted?* All three answered yes. One of them was working from an
`agents.md` that no longer mentioned companion — it had simply read the tool
list and decided.

Its second role was a gate: it blocked `--apply` when it judged the intent
ambiguous. Measured, it blocked four out of four ordinary write commands,
because it was being fed a command line (`replace_text.py src/app.js foo bar
--apply`) by a function written to read sentences. It could never find a
keyword, so confidence was always NONE.

The idea worth keeping is `needs_grilling` — flagging a request that is too
vague to act on. That idea was not wrong; the place it was wired in was.

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
</tbody>
</table>

All sixteen have a test that runs them and asserts their output. "Tested" here
means exactly that — a test that executes the tool and checks what it printed,
not one that merely imports it or checks the exit code. Each one was verified
by breaking it on purpose and confirming the test went red.

`tree_gen` ships alongside them but is not counted: it is the rendering engine
behind `smart_tree`, not a tool you call.

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
python tests/run_tests.py     # 127 tests, ~147 seconds
```

## Compatibility

Works with any AI agent that supports Python script execution and bash/shell commands.

**Verified with:** Claude Code, Gemini/Antigravity.

## License

MIT
