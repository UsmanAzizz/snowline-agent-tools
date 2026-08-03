# Task Board

*Tech Lead use only - workers never write here*

## Active Tasks
*(None currently assigned through chamber system)*

## Position Status
| Position | Status | Notes |
|---------|--------|-------|
| claude_code/pos_01 | idle | Claude Code agent |
| gemini/pos_01 | idle | Gemini agent |

## Completed (Recent)
- Task 36: Rename session_XX to pos_XX
- Task 35: Add gemini/ folder to agents_chamber
- Task 32-34: Signal protocol, safe_substitute_line fix, severity-halt rule
- Task 31: Placeholder content population
- Task 30: agents_chamber/ structure built

## Notes
- Both Claude Code and Gemini now have chamber positions
- "Position" (pos_XX) = persistent folder survives agent resets
- Regular work flows through `for_claude/agents_connector.md` (manual signal channel)
- agents_chamber/ enables parallel agent trial run
- When Tech Lead assigns a new position: Tech Lead creates appropriate folder first, then notifies the agent
- Existing positions do NOT create their own folders - wait for Tech Lead assignment
