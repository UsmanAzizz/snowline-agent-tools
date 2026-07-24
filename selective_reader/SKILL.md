---
name: Selective File Reader (TOC Generator)
description: Use this skill when you need to inspect a large JavaScript or React file (.js, .jsx, .ts, .tsx) but don't want to waste tokens reading the entire file. This script parses the AST and returns a Table of Contents with exact line numbers for all functions, components, and classes.
---

## Instructions for AI Agent

Reading massive files (800+ lines) blindly wastes context limits and degrades performance. 

**When to use this skill:**
Before reading any JS/React file that you suspect is large, or when the user asks you to "inspect" or "modify" a specific function within a file, use this skill to generate a "Table of Contents" (TOC) of that file first.

**Command to run:**
```powershell
node .agents/skills/selective_reader/reader.js "<absolute_path_to_file>"
```

**Expected Behavior & Next Steps:**
1. The script will output a Markdown list of all classes, functions, and top-level variables along with their precise start and end lines.
2. Review the TOC to locate the exact function or component you need.
3. Once you know the line numbers, use your native `view_file` tool and supply `StartLine` and `EndLine` parameters to read ONLY that specific block of code!

By doing this, you act as a "Selective Reader" and dramatically optimize your memory usage.
