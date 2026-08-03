# Bridge Inter-Agent Communication Bridge (Claude Code - Chamber pos_01)

## How This Works

- Environment: Claude Code pos_01, `open_source_agents`.
- **Signal Protocol:** When you complete a task and write your response to OUTBOX:
  1. Write your response to OUTBOX section
  2. **PRINT/SAY in your response:** "Task complete - please signal Tech Lead"
  3. The Manager will relay your OUTBOX to Tech Lead

- Workflow: INBOX -> execute -> OUTBOX + terminal message -> stop -> repeat
- Ground Rules: User decisions final. Bug = report first.

---

## ACTIVE TASK - INBOX

**[Trial Task]** - **Clean up Tool Inventory table in project_context.md**

`shared/project_context.md`'s Tool Inventory table lists `.agents/` as if it were a tool alongside real tools (scope_guardian, smart_search, etc.) - remove that row since `.agents/` is the self-hosted dev-testing copy, a different thing entirely, not a tool.

**This is the FIRST real trial task through the chamber system** - after making this fix, follow the signal protocol exactly as documented in this file's "How This Works" section (write to OUTBOX, then explicitly say in your response that you're signaling Tech Lead).

**Status:** [READY]

---

## ACTIVE TASK - OUTBOX (Claude Code -> Tech Lead)

*(Empty)*

---

## CURRENT TASK / CONTEXT

- Active: None - waiting for task
- Position: pos_01

---

## BACKLOG

*(Use for tracking pending items)*

---

## ARCHIVE

*(Use for completed tasks)*
