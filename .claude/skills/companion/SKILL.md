# Companion Skill

## Description

The **Companion** is a data processor that analyzes user intent and provides tool recommendations.

## CRITICAL: Always Call Companion FIRST

**Before executing ANY tool, ALWAYS run this first:**

```python
python -c "from companion import analyze_intent; print(analyze_intent('<user instruction>'))"
```

Example workflow:
```
User: "cari fungsi handleSubmit"
1. Run: python -c "from companion import analyze_intent; print(analyze_intent('cari fungsi handleSubmit'))"
2. Read the AnalyzeResult:
   - keywords: ["cari"]
   - confidence_level: HIGH
   - single_tool: smart_search
3. Execute the suggested tool
```

## Agent Decision Matrix

| Confidence | Specificity | Action |
|------------|-------------|--------|
| HIGH | high | EXECUTE (mandatory) |
| HIGH | medium | KONFIRMASI |
| MEDIUM | any | KONFIRMASI |
| LOW | any | CLARIFY |
| NONE | any | CLARIFY |

## Available Tools

| Tool | Purpose | Keywords |
|------|---------|----------|
| smart_search | Find code with context | cari, find, search |
| smart_replace | Safe find & replace | ganti, replace, refactor |
| selective_reader | Read large files (TOC) | baca, read |
| project_guardian | Security auditor | keamanan, security |
| clean_sweeper | Tech debt scanner | bersihkan, cleanup |
| deep_analyzer | Project profiler | analisa, analyze |
| crash_decoder | Error parser | error, bug, crash |
| scope_guardian | Scope validator | scope |

## Usage

```python
from companion import analyze_intent, get_agent_action

result = analyze_intent("cari import axios")
print(result.keywords)
print(result.confidence_level)
print(result.single_tool.name if result.single_tool else None)
print(get_agent_action(result))  # EXECUTE/KONFIRMASI/CLARIFY
```

## Example

User: "cari semua import axios"

```
1. Analyze: analyze_intent("cari semua import axios")
   → confidence_level: HIGH
   → single_tool: smart_search
   
2. Execute: python .agents/skills/smart_search/code_finder.py . "import axios"
```

## Memory

Companion learns from usage:
- Records tool selections in `.agents/memory.json`
- Suggests tools based on past success
