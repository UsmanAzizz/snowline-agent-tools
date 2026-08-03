# CHAMBER PROTOCOL

1. **Tech Lead Role**: Only the Tech Lead (Claude, claude.ai session) writes to task_board.md and project_context.md.

2. **Worker Role**: Workers (Claude Code sessions, etc.) NEVER modify task_board.md. You receive tasks in YOUR OWN connector.md INBOX only, reply in YOUR OWN OUTBOX only.

3. **Broadcast**: Check shared/broadcast.md whenever you check your own INBOX - part of the same routine, not separate.

4. **Signal Protocol**: When you complete a task and write to OUTBOX:
   - Write your response to the OUTBOX section
   - PRINT/Say "Task complete - please signal Tech Lead" in your terminal response
   - The Manager will relay to Tech Lead
