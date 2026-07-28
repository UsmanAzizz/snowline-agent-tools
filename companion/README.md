# Agentic Companion Layer

## Concept

**Agent = Hunter** - Powerful, free to hunt, can execute anything.

**Companion = Chain** - Keeps agent safe, no overflow.

```
Agent is free to hunt...
But companion walks with at every step.
If agent goes too far, chain pulls back.
No restrict, but no overflow.
```

## Workflow

Agent works through phases:
1. **Reasoning** - Understanding user intent
2. **Thinking** - Planning steps
3. **Preparing** - Selecting tools
4. **Executing** - Running actions
5. **Finishing** - Delivering results

At every phase, Companion is present.

## Usage

### Python API

```python
from companion import AgenticCompanion

companion = AgenticCompanion(project_root=".")

# Agent starts reasoning
companion.observe("reasoning", {"intent": "fix login bug"})

# Agent wants to execute something
result = companion.check_execute("modify file", target="src/auth.js")
if result.status == "blocked":
    print("⚠️ Cannot proceed!")

# Companion guides based on intent
steps = companion.guide("cek keamanan project")
# Returns: [{"tool": "project_guardian", "reason": "..."}]
```

### Tool Registry

All tools are registered with their purpose:

```python
from companion.tool_registry import suggest_tools, list_all_tools

# What tools fit this intent?
suggestions = suggest_tools("cek keamanan")

# List all available tools
all_tools = list_all_tools()
```

## Files

```
companion/
├── companion.py      # Core companion class
├── tool_registry.py # Tool definitions
└── README.md
```

## Companion Responsibilities

| Responsibility | Tool/Check |
|----------------|------------|
| Security | project_guardian patterns |
| Scope | scope_guardian patterns |
| Tool Selection | tool_registry + guide() |
| Phase Tracking | observe() |

## Principles

1. **Thin Layer** - Minimal overhead
2. **Watcher** - Observes, doesn't control
3. **Alert** - Warns, doesn't block (unless critical)
4. **Walks With** - Present at every phase

## Status

Prototype. Testing in progress.
