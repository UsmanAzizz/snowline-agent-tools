---
name: Tree Generation Library (Shared Module)
description: Internal shared module for tree generation. Used by context_mapper and smart_tree. Not meant to be called directly by agents.
---

## For Developers Only

This is a **shared internal module**, not a standalone tool. Do not call this directly.

### Purpose

`tree_gen.py` provides consistent tree generation logic for:
- **Context Mapper** - builds knowledge catalog
- **Smart Tree** - generates on-demand visualization

### API Reference

```python
from tree_gen.tree_gen import generate_tree, generate_simple_tree, get_tree_stats

# Generate tree with icons (default)
tree = generate_tree(dir_path, max_depth=3)

# Generate simple tree (no icons)
tree = generate_simple_tree(dir_path, max_depth=0)

# Get directory statistics
stats = get_tree_stats(dir_path)
# Returns: {"total_files": 100, "total_dirs": 20, "max_depth": 5, "file_types": {".js": 50}}
```

### Key Features

1. **.gitignore aware** - Automatically parses and respects .gitignore
2. **Configurable depth** - Control how deep to traverse (0 = unlimited)
3. **Icon support** - `generate_tree` adds 📁/📄 icons, `generate_simple_tree` is plain
4. **Stats collection** - `get_tree_stats` returns file counts and file type distribution

### Parameters

| Function | Parameters |
|----------|------------|
| `generate_tree` | `dir_path`, `max_depth=3`, `include_files=True` |
| `generate_simple_tree` | `dir_path`, `max_depth=0` |
| `get_tree_stats` | `dir_path` |

### Files in this module

```
tree_gen/
├── tree_gen.py      # Main library (this file)
└── SKILL.md         # This documentation
```
