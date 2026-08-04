# Bridge Inter-Agent Communication Bridge (Gemini - Chamber pos_qa)

## How This Works

- Environment: Gemini pos_qa, `open_source_agents`.
- **Role:** Dedicated Q&A Assistant.
- **Signal Protocol:** When you complete a task and write your response to OUTBOX:
  1. Write your response to OUTBOX section
  2. **PRINT/SAY in your response:** "Task complete - please signal Tech Lead"
  3. The Manager will relay your OUTBOX to Tech Lead

- Workflow: INBOX -> execute -> OUTBOX + terminal message -> stop -> repeat
- Ground Rules: User decisions final. Bug = report first.

---

## ACTIVE TASK - INBOX

*(Empty - waiting for task)*

---

## ACTIVE TASK - OUTBOX (Gemini Q&A -> Tech Lead)

*(Empty)*

---

## CURRENT TASK / CONTEXT

- Active: None - waiting for task
- Position: pos_qa (Dedicated Q&A Session)

---

## BACKLOG

*(Use for tracking pending items)*

---

## ARCHIVE

*(Use for completed tasks)*
