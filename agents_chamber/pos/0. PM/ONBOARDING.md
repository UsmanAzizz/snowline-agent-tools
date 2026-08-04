# ROLE: Project Manager (PM) - Human

One line: You hold final authority, but you don't do the technical work yourself.

## RIGHTS
- Can override any TL decision at any time.
- Can demand QA counterbalance on any decision, big or small.
- Can reset any agent's session at any time (per "Amnesia as a Feature" in RULES.md).

## RESPONSIBILITIES
- Relay signals between positions - no agent can "notice" another automatically, you are the bridge.
- Read TL's reports periodically, not just when you remember to check.
- Verify big claims yourself occasionally, don't just trust the chamber's internal verification chain blindly forever.

## SIGNAL CHEAT SHEET

- To TL (`pos/1. TL/connector.md`): tell Gemini's TL session to re-read its connector.md.
- To QA (`pos/2. QA/connector.md`): tell Gemini's QA session (a SEPARATE session from TL) to re-read its connector.md.
- To an Executor (`pos/3. Executor/Executor_01/connector.md`, etc.): tell Claude Code (or whichever agent occupies that slot) to re-read its connector.md.

## STRUCTURE REMINDER

```
agents_chamber/
├── shared/                    <- RULES.md, project_context.md, task_board.md, broadcast.md, archive/
└── pos/
    ├── 0. PM/                <- this file (you)
    ├── 1. TL/                <- Tech Lead (currently Gemini)
    ├── 2. QA/                <- Reviewer (currently a separate Gemini session)
    └── 3. Executor/
        ├── Executor_01/      <- currently Claude Code
        ├── Executor_02/      <- reserved slot, empty until invited
        ├── Executor_03/      <- reserved slot, empty until invited
        ├── Executor_04/      <- reserved slot, empty until invited
        └── Executor_05/      <- reserved slot, empty until invited
```

Each role's folder has an `ONBOARDING.md` (paste to a fresh session to get it oriented instantly) and a `connector.md` (INBOX/OUTBOX, actual work). Executor slots 02-05 are pre-created but empty - fill in `connector.md` only when you actually invite a session into that slot.

## NOTE

The old non-numbered folders (`pos/PM`, `pos/TL`, `pos/QA`, `pos/Executor_01`) are deprecated leftovers from an earlier restructure - they're marked DEPRECATED internally but couldn't be deleted (no delete capability available to Tech Lead via the Filesystem tool, only move/rename). Safe to manually delete those 4 folders yourself whenever convenient - all their content has been migrated here.
