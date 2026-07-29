# Agentic Companion Layer v2

## Concept

**Agent = Hunter** - Powerful, free to hunt, can execute anything.

**Companion = Chain** - Keeps agent safe, no overflow.

```
Agent is free to hunt...
But companion walks with at every step.
If agent goes too far, chain pulls back.
No restrict, but no overflow.
```

## Full Workflow

Agent works through 5 phases, companion walks with at each:

```
┌─────────────────────────────────────────────────────────┐
│  PHASE 1: REASONING                                     │
│  "What does user want?"                                │
│  companion.analyze_intent() → clarity, keywords        │
│  companion.ask_clarification() → if vague             │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  PHASE 2: THINKING                                      │
│  "What steps needed?"                                 │
│  companion.plan_execution() → steps[]                  │
│  companion.validate_plan() → safe/warning              │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  PHASE 3: PREPARING                                    │
│  "What command to run?"                               │
│  companion.prepare_step() → command                    │
│  companion.get_command() → python script               │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  PHASE 4: EXECUTING                                    │
│  "Is this safe to run?"                               │
│  companion.validate_execution() → safe/warning/blocked │
│  companion.alert() → if overflow detected              │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  PHASE 5: FINISHING                                    │
│  "Did task complete successfully?"                     │
│  companion.validate_output() → quality check           │
│  companion.finish() → session summary                 │
└─────────────────────────────────────────────────────────┘
```

## Usage

### Basic Usage

```python
from companion import AgenticCompanion

companion = AgenticCompanion(project_root=".")

# 1. REASONING - Analyze intent
intent = companion.analyze_intent("cari bug di login")
print(f"Clarity: {intent.clarity}")
print(f"Keywords: {intent.keywords}")

# If vague, ask for clarification
if intent.clarity in ["vague", "ambiguous"]:
    print(companion.ask_clarification(intent))

# 2. THINKING - Plan execution
steps = companion.plan_execution(intent)
for step in steps:
    print(f"Step {step.order}: {step.tool}")

# 3. PREPARING - Get command
for step in steps:
    cmd = companion.get_command(step)
    print(f"Execute: {cmd}")

# 4. EXECUTING - Validate safety
result = companion.validate_execution(steps[0])
if result.status == "blocked":
    print(companion.alert("Cannot proceed!"))

# 5. FINISHING - Complete
summary = companion.finish()
print(summary)
```

### Quick Interface

```python
from companion import analyze_input, plan_steps

# Quick analysis
intent = analyze_input("cek keamanan project")

# Quick planning
steps = plan_steps("analisa project, terus generate report")
```

## Intent Analysis

The companion analyzes user input for:

| Aspect | Values | Meaning |
|--------|--------|---------|
| **Clarity** | clear, ambiguous, vague | Is intent understandable? |
| **Type** | single_action, multi_action, question, unknown | What kind of request? |
| **Keywords** | list | Detected keywords for tool matching |

## Tool Selection

Tools are selected based on keyword matching:

| Keyword | Tool | Command |
|---------|------|---------|
| keamanan, security | project_guardian | `--summary` |
| cari, find | smart_search | `<keyword>` |
| ganti, replace | smart_replace | `<old> <new> --apply` |
| baca, read | selective_reader | `<filepath>` |
| struktur, tree | smart_tree | `. <depth>` |
| scope | scope_guardian | `<filepath>` |
| analisa | deep_analyzer | `. --json` |
| cleanup, bersihkan | clean_sweeper | `.` |
| error, crash | crash_decoder | `<logfile>` |
| generate, buat | auto_scaffolder | `<type> <name>` |

## Validation

### Scope Validation
Checks if file operations are within `scope_lock.json` boundaries.

### Security Validation
- Detects dangerous actions (delete, rm, DROP)
- Flags sensitive files (.env, .key, .pem)
- Warns about exposed credentials

### Plan Validation
- Warns if no tools selected
- Warns if plan has >5 steps

## Example Sessions

### Clear Intent
```
Input: "cari bug di login"

[REASONING] Clarity: clear
[REASONING] Keywords: ['cari', 'bug']
[THINKING] Steps: 1
  Step 1: smart_search
[EXECUTING] Status: [SAFE]
```

### Multi-Action Intent
```
Input: "analisa project, terus generate report"

[REASONING] Type: multi_action
[THINKING] Steps: 3
  Step 1: deep_analyzer
  Step 2: auto_scaffolder
  Step 3: clean_sweeper
[EXECUTING] Status: [SAFE]
```

### Vague Intent
```
Input: "cek"

[REASONING] Clarity: ambiguous
[REASONING] Keywords: []
[THINKING] Steps: 0
Clarification: "Spesifikasikan apa yang mau dicek/dilakukan"
```

## Files

```
companion/
├── companion.py      # Main companion class + validators
├── tool_registry.py # Tool definitions (reference)
└── README.md        # This file
```

## Principles

1. **Thin Layer** - Minimal overhead, fast execution
2. **Watcher** - Observes, doesn't control
3. **Chain** - Keeps agent safe, no overflow
4. **Walks With** - Present at every phase

## Status

Full prototype v2 - All 5 phases implemented and tested.
