# ❄️ Snowline Agent Tools

![Python](https://img.shields.io/badge/Python-3.x-blue.svg?logo=python&logoColor=white)
![No Dependencies](https://img.shields.io/badge/Dependencies-Zero-brightgreen.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

Lightweight Python tools that help AI coding assistants work smarter — not harder.

## The Mission

**While others race to burn tokens, we prevent the waste.**

This toolkit exists because AI agents often read too much, search too broadly, and modify files without understanding context. These tools provide targeted capabilities that reduce token usage while improving accuracy.

## Core Principles

1. **Portable** — Pure Python, no external dependencies (except `pymysql` for db_extractor)
2. **Token Efficient** — Concise output, surgical precision
3. **Safe** — Dry-run modes and backup systems for destructive operations
4. **Structured** — Both human-readable and JSON output for agentic processing

## Installation

```bash
pip install git+https://github.com/UsmanAzizz/snowline-agent-tools.git
```

Initialize in your project:
```bash
python -m snowline_toolkit.cli init --apply
```

## Tools Overview (14 Tools)

### Search & Modify
| Tool | Purpose |
|------|---------|
| `smart_search` | Find code with 5-line context |
| `smart_replace` | Safe find-and-replace with backup |
| `import_fixer` | Fix broken relative imports |

### Audit & Analyze
| Tool | Purpose |
|------|---------|
| `project_guardian` | Security & health auditor |
| `clean_sweeper` | Find tech debt & garbage files |
| `deep_analyzer` | Project profiler (tech stack, stats) |
| `selective_reader` | Extract TOC from large files |
| `context_mapper` | Build knowledge catalog |
| `smart_tree` | Compact directory visualizer |
| `db_extractor` | Database schema extractor |
| `scope_guardian` | File scope validator |

### Workflow Helpers
| Tool | Purpose |
|------|---------|
| `crash_decoder` | Parse crash logs |
| `auto_scaffolder` | Generate boilerplate code |
| `impact_analyzer` | Predict impact of changes |

### Shared Module
| Module | Purpose |
|--------|---------|
| `tree_gen` | Reusable tree generation logic |

## Usage Examples

### Smart Search
```bash
# Human-readable output
python .agents/skills/smart_search/code_finder.py . "handleSubmit" --ext ".jsx"

# JSON output (for agents)
python .agents/skills/smart_search/code_finder.py . "handleSubmit" --json
```

### Selective Reader
```bash
# Extract TOC
python .agents/skills/selective_reader/reader.py src/App.jsx

# JSON output
python .agents/skills/selective_reader/reader.py src/App.jsx --json
```

### Project Guardian
```bash
# Human-readable audit
python .agents/skills/project_guardian/guardian.py

# Summary only
python .agents/skills/project_guardian/guardian.py --summary

# JSON (for programmatic processing)
python .agents/skills/project_guardian/guardian.py --json
```

### Smart Tree
```bash
# Visual tree (depth=3)
python .agents/skills/smart_tree/scripts/tree_viewer.py . 3

# Simple output (no icons)
python .agents/skills/smart_tree/scripts/tree_viewer.py . --simple
```

### Scope Guardian
```bash
# Check if file is in scope
python .agents/skills/scope_guardian/scripts/scope_check.py src/components/Button.jsx
# Output: [ALLOWED] or [BLOCKED]
```

## Shared Tree Module

`tree_gen.py` provides reusable tree generation logic used by both `context_mapper` and `smart_tree`:

```python
from tree_gen.tree_gen import generate_tree, get_tree_stats

# Generate tree
tree = generate_tree('/path/to/project', max_depth=3)

# Get stats
stats = get_tree_stats('/path/to/project')
# {'total_files': 100, 'total_dirs': 20, 'max_depth': 5}
```

## Compatibility

Works with any AI agent that supports:
- Python script execution
- Bash/Shell commands
- Custom system prompts

Tested with: Claude Code, Gemini, DeepSeek, Aider

## License

MIT
