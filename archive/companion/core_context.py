"""
core_context.py - Project context loading (session-cached).
"""
import os
from typing import Dict

# Session cache: {path: (mtime, content)}
_CONTEXT_CACHE: Dict[str, tuple] = {}


def load_project_context() -> str:
    """Load PROJECT_STRUCTURE.md from context_mapper output.

    Returns empty string if file not found (no error).
    Cached for 5 minutes to avoid repeated disk reads per session.
    """
    # Search for PROJECT_STRUCTURE.md
    search_paths = [
        '.agents/knowledge/PROJECT_STRUCTURE.md',
        '.agents/PROJECT_STRUCTURE.md',
        'PROJECT_STRUCTURE.md',
    ]
    for path in search_paths:
        if os.path.isfile(path):
            try:
                current_mtime = os.path.getmtime(path)
                cached = _CONTEXT_CACHE.get(path)

                # Return cached if mtime unchanged
                if cached:
                    cached_mtime, cached_content = cached
                    if current_mtime == cached_mtime:
                        return cached_content

                # Read and cache
                content = open(path, encoding='utf-8').read()
                _CONTEXT_CACHE[path] = (current_mtime, content)
                return content
            except Exception:
                pass
    return ""


def entity_in_context(entity: str, context: str) -> bool:
    """Check if entity appears in project context."""
    if not context:
        return False
    return entity.lower() in context.lower()
