---
name: Project Health & Residue Sweeper
description: Use this skill when the user asks you to scan for project health, technical debt, or leftover residue files across a repository. It runs a Python script that deeply scans the project for unused DBs, temporary folders, TODO/FIXME tags, and large commented code blocks.
---

## Instructions for AI Agent

When the user asks you to "bersihkan project", "cari residu", or check the health/tech debt of a project, use this skill to run a sweeping analysis.

**Command to run:**
```powershell
python .agents/skills/clean_sweeper/sweeper.py "<absolute_target_directory>"
```
*(Make sure your current working directory `Cwd` is set to the root of the user's project when running this).*

**Expected Output:**
The script will output a Markdown-formatted report directly to stdout detailing suspect folders, stray leftover files, count of `TODO`/`FIXME` tags (with proper word boundaries), and large commented out code blocks.

### 🛑 CRITICAL BEHAVIORAL RULE (VETO PROTOCOL)
1. **Never quarantine, move, or delete files automatically.** You MUST NOT assume a file is trash just because the script flagged it.
2. Read the script output and present a clean summary to the user.
3. Explicitly ask the user: *"Mana saja dari daftar ini yang boleh saya pindahkan ke karantina/hapus?"*
4. Wait for the user's explicit confirmation (VETO) per item BEFORE executing any file modification or terminal `mv`/`rm` commands.
