---
name: Smart Code Reference Finder
description: Use this skill when the user asks you to find WHERE a specific function, component, class, or variable is used across a project. This skill uses a Python script to extract the code blocks surrounding the keyword, providing you with full context (e.g. what props are passed, what variables surround it) instead of just single raw lines like standard grep.
---

## Instructions for AI Agent

When analyzing a codebase to find references, standard `grep_search` is often insufficient because it only returns the exact line containing the keyword, omitting critical surrounding logic. 

**When to use this skill:**
- The user asks to find where a component/function is used.
- You need to know *how* a specific function is invoked across multiple files (what props/arguments are passed).
- You are refactoring a core module and need to see all its dependent implementations in context.

**How to use:**
**Command to run:**
```powershell
python .agents/skills/smart_search/code_finder.py "<absolute_target_directory>" "<keyword>" --ext "<optional_extensions>"
```

**Parameters:**
- `<absolute_target_directory>`: The absolute path to the directory you want to scan (e.g., `/path/to/your/src`).
- `<keyword>`: The exact code string to search for (e.g., `MyComponent`).
- `--ext`: (Optional) Comma-separated file extensions to limit the search (e.g., `.jsx,.js,.php`).

**Expected Output:**
The script will output beautifully formatted Markdown text directly into standard output. It groups results by file and shows blocks of code (with 5 lines of context above and below the match). The exact line containing the match will be highlighted with a `>` arrow. Read this output carefully to understand the implementation context before deciding on your next coding action.
