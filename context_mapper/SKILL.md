---
name: Context Mapper (Knowledge Builder)
description: Use this skill when entering a new project or when the user creates significant new architectural folders. It scans the project and generates a PROJECT_STRUCTURE.md and COMMON_PATTERNS.md in the .agents/knowledge/ folder to give you instant architectural context without wasting tokens on manual search.
---

## Relationship with Smart Tree

**Context Mapper** and **Smart Tree** share the same underlying tree generation logic (`tree_gen/tree_gen.py`) but serve different purposes:

| Aspect | Context Mapper | Smart Tree |
|--------|---------------|------------|
| **Purpose** | Build persistent knowledge catalog | Generate on-demand visualization |
| **Output** | Files in `.agents/knowledge/` | Terminal output |
| **Scope** | Full project, unlimited depth | Configurable depth |
| **When to use** | First time in project, major changes | Need to see folder structure NOW |

## Instructions for AI Agent

**When to use this skill:**
- When you first join a project and need to understand its structure.
- When the user asks you to "map the context" or "build the knowledge catalog".
- When you or the user have added a massive new feature (e.g. adding a whole new `admin/` module) and the `PROJECT_STRUCTURE.md` needs to be updated.

**Command to run:**
```bash
python .agents/skills/context_mapper/context_mapper.py
```

For preview (dry-run):
```bash
python .agents/skills/context_mapper/context_mapper.py
# (runs in preview mode by default)
```

To apply and save to disk:
```bash
python .agents/skills/context_mapper/context_mapper.py --apply
```

**Expected Behavior & Next Steps:**
1. The script will output a success message indicating that the Knowledge Catalog has been built in `.agents/knowledge/`.
2. As a mandatory follow-up, you MUST use the `view_file` tool to read `.agents/knowledge/PROJECT_STRUCTURE.md` and `.agents/knowledge/COMMON_PATTERNS.md` to update your mental model of the project.
3. If the user asks you to document a new coding convention, you should use `replace_file_content` to append it to `COMMON_PATTERNS.md`.

**Quick Reference:**
- Uses shared `tree_gen.py` for consistent tree generation
- Generates stats (file count, directory count, max depth)
- Auto-creates COMMON_PATTERNS.md if not exists
