# Architecture Overview

## 4-Domain Model

```
Agent Request
      ↓
┌─────────────────────────┐
│     SYSTEM DOMAIN       │ ← Tool registry, config, state
├─────────────────────────┤
│     CHECKS DOMAIN       │ ← Safety validation, guidance
├─────────────────────────┤
│     ACTIONS DOMAIN      │ ← Tool execution
├─────────────────────────┤
│ CONTEXT DOMAIN (Phase 2)│ ← Memory, awareness
└─────────────────────────┘
      ↓
Structured Response + Guidance
      ↓
Agent Decision
```

## Data Flow

1. **Agent** initiates tool call
2. **System** looks up tool definition
3. **Checks** validates safety
4. **Actions** executes with backup (via dry-run first)
5. **Context** memorizes result
6. **Agent** receives guidance

## State Management

SQLite database (`.snowline/state.db`) tracks:
- **Executions**: Execution history.
- **Artifacts**: File backups, previews, tool results.
- **Agent memory**: Episodic & semantic memory (Phase 2).

## Safety Model

Every action:
- ✅ Has a dry-run preview before modifications
- ✅ Creates automatic backup prior to execution
- ✅ Includes a rollback/reversal plan
- ✅ Gets a risk score from RiskAssessor
- ✅ Generates structured guidance for the agent to follow
