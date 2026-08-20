---
name: Smart Directory Mapper (Tree Viewer)
description: Use this skill when you need to understand the project structure, locate files, or map out a directory tree WITHOUT consuming a huge amount of tokens. This script generates a compact, .gitignore-aware visual tree of a directory, making it vastly superior to the default `list_dir` tool which returns verbose JSON output.
---

## Relationship with Context Mapper

**Smart Tree** and **Context Mapper** share the same underlying tree generation logic (`tree_gen/tree_gen.py`) but serve different purposes:

| Aspect | Smart Tree | Context Mapper |
|--------|------------|---------------|
| **Purpose** | On-demand visualization | Build persistent knowledge catalog |
| **Output** | Terminal output | Files in `.agents/knowledge/` |
| **Scope** | Configurable depth | Full project, unlimited depth |
| **When to use** | Need to see folder structure NOW | First time in project, major changes |

## Instructions for AI Agent

When exploring a new project or trying to locate where certain feature files might be stored, DO NOT use the default `list_dir` tool on large folders, as it will flood your context window with raw JSON and token-heavy metadata.

Instead, ALWAYS use this `smart_tree` tool.

## Usage

Run the script using Python. You can provide an optional `max_depth` argument to control how deep the tree goes (default is 3).

```bash
python .agents/skills/smart_tree/scripts/tree_viewer.py <directory_path> [max_depth]
```

### Examples:
Map the entire project root up to 2 levels deep:
```bash
python .agents/skills/smart_tree/scripts/tree_viewer.py . 2
```

Map a specific component folder up to 5 levels deep:
```bash
python .agents/skills/smart_tree/scripts/tree_viewer.py src/view/admin 5
```

Unlimited depth (use with caution):
```bash
python .agents/skills/smart_tree/scripts/tree_viewer.py . 0
```

Simple output (no icons, like standard tree command):
```bash
python .agents/skills/smart_tree/scripts/tree_viewer.py . --simple
```

## Advantages

1. **Token Efficient**: Outputs a clean visual hierarchy (`├──`, `└──`) instead of raw JSON.
2. **Noise Reduction**: Automatically parses `.gitignore` and hard-ignores junk directories (`node_modules`, `vendor`, `.git`, `.agents`, `dist`) so you don't get overwhelmed with irrelevant files.
3. **Controlled Depth**: The `max_depth` parameter prevents you from accidentally reading an infinitely deep directory structure.
4. **Shared Core**: Uses `tree_gen.py` - same tree logic as Context Mapper, ensuring consistency.
