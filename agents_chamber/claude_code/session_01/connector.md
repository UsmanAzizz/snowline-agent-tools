# Bridge Inter-Agent Communication Bridge (Claude Code - Chamber Session 01)

## How This Works

- Environment: Claude Code session_01, `open_source_agents`.
- **Signal Protocol:** When you complete a task and write your response to OUTBOX:
  1. Write your response to OUTBOX section
  2. **PRINT/SAY in your response:** "Task complete - please signal Tech Lead"
  3. The Manager will relay your OUTBOX to Tech Lead

- Workflow: INBOX -> execute -> OUTBOX + terminal message -> stop -> repeat
- Ground Rules: User decisions final. Bug = report first.

---

## ACTIVE TASK - INBOX

*(Empty - waiting for task from Tech Lead)*

---

## ACTIVE TASK - OUTBOX (Claude Code -> Tech Lead)

*(Empty)*

---

## CURRENT TASK / CONTEXT

- Active: None - waiting for task
- Session: session_01

---

## BACKLOG

*(Use for tracking pending items)*

---

## ARCHIVE

*(Use for completed tasks)*
