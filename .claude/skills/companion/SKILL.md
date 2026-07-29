# Companion Skill

## Description

The **Companion** skill is an agentic layer that helps Claude Code work more efficiently by:
- Understanding user intent and selecting the right tool
- Preventing token waste through focused tools
- Learning from past interactions
- Validating decisions before execution

## Usage

When the user describes what they want to do, use the companion to:

```
companion.analyze("user request here")
companion.plan_steps()
companion.get_command()
```

## Integration

Add to your CLAUDE.md or project:

```markdown
## Companion Skill

Before executing any task, use the Companion to analyze intent:

1. Analyze: `python .claude/skills/companion/cli.py --input "<user request>"`
2. Plan: Review suggested tool
3. Execute: Run the suggested command
4. Learn: Companion records the selection for future use
```

## Available Tools

| Tool | Purpose | Keywords |
|------|---------|----------|
| smart_search | Find code with context | cari, find, search, import |
| smart_replace | Safe find & replace | ganti, replace, refactor |
| selective_reader | Read large files (TOC) | baca, read, lihat |
| project_guardian | Security auditor | keamanan, security, audit |
| clean_sweeper | Tech debt scanner | bersihkan, cleanup, garbage |
| deep_analyzer | Project profiler | analisa, analyze, tech stack |
| crash_decoder | Error parser | error, bug, crash, debug |
| auto_scaffolder | Boilerplate generator | generate, create, new |
| token_budget | Token usage tracker | token budget, usage |
| context_curator | Context noise filter | bersihkan context |
| output_formatter | JSON formatter | format, table |
| decision_validator | Risk assessor | validasi, safety check |

## Example

User: "cari semua import axios"

```
companion.analyze("cari semua import axios")
-> smart_search
```

User: "refactor handleSubmit jadi handleFormSubmit"

```
companion.analyze("refactor handleSubmit")
-> smart_replace
command: python .agents/skills/smart_replace/replace_text.py <old> <new> --apply
```

## Memory

The companion learns from your usage:
- Records tool selections in `~/.snowline_memory.json`
- Suggests tools based on past success
- 70% confidence threshold for suggestions

## CLI Commands

```bash
# Analyze intent
python companion/cli.py --input "cari import axios"

# List tools
python companion/cli.py --list-tools

# Memory stats
python companion/cli.py --stats

# Interactive mode
python companion/cli.py --interactive
```
