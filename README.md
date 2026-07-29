# ❄️ Snowline Agent Tools

![Python](https://img.shields.io/badge/Python-3.x-blue.svg?logo=python&logoColor=white)
![No Dependencies](https://img.shields.io/badge/Dependencies-Zero-brightgreen.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

Lightweight Python tools for low-mid tier projects. Work smarter — not harder.

## The Mission

**Prevent token waste in AI agent workflows.**

AI agents often read too much, search too broadly, and act without focus. These tools provide targeted capabilities for faster, more precise results.

## Core Principles

1. **Portable** — Pure Python, no dependencies
2. **Token Efficient** — Concise output, surgical precision
3. **Safe** — Dry-run modes for destructive operations
4. **Fast** — Low-mid tier focus, no over-engineering

## Installation

```bash
pip install git+https://github.com/UsmanAzizz/snowline-agent-tools.git
```

Initialize in your project:
```bash
python -m snowline_toolkit.cli init --apply
```

## Tools (10 Core)

### Search & Modify
| Tool | Purpose |
|------|---------|
| `smart_search` | Find code with context |
| `smart_replace` | Safe find-and-replace with backup |
| `import_fixer` | Fix broken imports |

### Read & Navigate
| Tool | Purpose |
|------|---------|
| `selective_reader` | Extract TOC from large files |
| `smart_tree` | Compact directory visualizer |
| `scope_guardian` | File scope validator |

### Analyze & Audit
| Tool | Purpose |
|------|---------|
| `project_guardian` | Security & health auditor |
| `deep_analyzer` | Project profiler |
| `impact_analyzer` | Predict change impact |
| `clean_sweeper` | Find tech debt |

### Workflow Helpers
| Tool | Purpose |
|------|---------|
| `crash_decoder` | Parse crash logs |
| `auto_scaffolder` | Generate boilerplate |

### Shared
| Module | Purpose |
|--------|---------|
| `tree_gen` | Reusable tree logic |

## Usage Examples

### Smart Search
```bash
python .agents/skills/smart_search/code_finder.py . "handleSubmit"
```

### Project Guardian
```bash
python .agents/skills/project_guardian/guardian.py --summary
```

### Smart Tree
```bash
python .agents/skills/smart_tree/scripts/tree_viewer.py . 3
```

## Companion

Built-in intent analyzer for quick tool routing:
```bash
python .agents/skills/companion/companion.py
```

## Compatibility

Works with any AI agent that supports:
- Python script execution
- Bash/Shell commands

**Tested with: Gemini**

## License

MIT
