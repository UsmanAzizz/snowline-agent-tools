---
name: Selective File Reader (TOC Generator)
description: Use this skill when you need to inspect a large file but don't want to waste tokens reading the entire file. This script parses the file using regex heuristics and returns a Table of Contents with exact line numbers for all functions, components, and classes.
---

## Instructions for AI Agent

Reading massive files (800+ lines) blindly wastes context limits and degrades performance. 

**When to use this skill:**
Before reading any JS/React/Py file that you suspect is large, or when the user asks you to "inspect" or "modify" a specific function within a file, use this skill to generate a "Table of Contents" (TOC) of that file first.

**Command to run:**
```powershell
python .agents/skills/selective_reader/reader.py "<absolute_path_to_file>"
```

**Expected Behavior & Next Steps:**
1. The script will output a Markdown list of all classes, functions, and top-level variables along with their precise start lines.
2. Review the TOC to locate the exact function or component you need.
3. Once you know the line numbers, use your native `view_file` tool and supply `StartLine` and `EndLine` parameters to read ONLY that specific block of code!

By doing this, you act as a "Selective Reader" and dramatically optimize your memory usage.

## ⚠️ Known Limitations & Future Enhancements
- **Monolithic JSX Components**: The heuristic regex currently only detects function and class declarations. If a file contains a single massive React component returning a huge block of JSX (e.g., hundreds of lines of <table> or <form>), the TOC will only show the top-level function. You may still need to manually paginate through the file to find specific HTML structures. 
- *Future Enhancement Idea:* Add regex rules to detect major JSX landmarks (like <table, <form, or <Modal) to improve precision in UI components.
