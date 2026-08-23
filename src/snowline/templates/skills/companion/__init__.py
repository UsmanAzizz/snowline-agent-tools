"""
COMPANION v5.0 - MODULAR
========================
Pure data processor for agent tool routing.
Agent makes decisions, companion provides structured data.

Usage (from project root with .agents/skills/companion/):
    python .agents/skills/companion_cli.py "cari axios"
    python -c "import sys; sys.path.insert(0, '.agents/skills'); from companion import analyze_intent"

Or use companion_cli() for automatic path detection:
    python .agents/skills/companion_cli.py --analyze "cari axios"
"""

import sys
import os

# ============================================================
# AUTO-DISCOVERY - Make 'from companion import' work
# ============================================================

def _auto_import():
    """Auto-detect and import companion module.

    This allows 'from companion import' to work from any directory
    by automatically finding .agents/skills/companion/ or companion.py and loading it.
    """
    # Check if already loaded
    if 'companion' in sys.modules:
        return True

    # Search for companion module
    search_dirs = [
        '.agents/skills',
        '.agents/skills/companion',
        'skills',
        'skills/companion',
    ]

    # Also search parent directories (up to 4 levels)
    cwd = os.getcwd()
    for i in range(4):
        for d in search_dirs:
            candidate = os.path.join(cwd, d)

            # Check for companion.py (single file)
            companion_file = os.path.join(candidate, 'companion.py')
            if os.path.isfile(companion_file):
                if candidate not in sys.path:
                    sys.path.insert(0, candidate)
                return True

            # Check for companion/ directory (module)
            companion_dir = os.path.join(candidate, 'companion')
            init_file = os.path.join(companion_dir, '__init__.py')
            if os.path.isdir(companion_dir) and os.path.isfile(init_file):
                if candidate not in sys.path:
                    sys.path.insert(0, candidate)
                return True

        cwd = os.path.dirname(cwd)
        if not cwd or cwd == '/':
            break

    return False

# Run auto-import
_auto_import()

# If we're being imported as a module, reload from detected path
if __name__ != '__main__':
    try:
        import companion as _mod
        # Re-export everything from the detected module
        for _name in dir(_mod):
            if not _name.startswith('_') and _name not in globals():
                globals()[_name] = getattr(_mod, _name)
    except (ImportError, ModuleNotFoundError):
        pass

# Ensure UTF-8
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass


# ============================================================
# RE-EXPORT all public API from submodules
# ============================================================

# core_intent
from .core_intent import (
    AnalyzeResult,
    ToolMatch,
    TOOL_REGISTRY,
    CLARIFICATION_TRIGGERS,
    APPROVAL_REQUIRED,
    extract_entities,
    analyze_intent,
)

# core_grilling
from .core_grilling import should_grill

# core_context
from .core_context import (
    load_project_context,
    entity_in_context,
)

# core_memory
from .core_memory import (
    load_user_level,
    load_task_lock,
    save_task_lock,
    start_task_lock,
    add_grilling_qa,
    update_task_lock,
    end_task_lock,
    get_task_status,
    load_decision_history,
    save_decision_history,
    DECISION_HISTORY_FILE,
    MAX_HISTORY_ENTRIES,
    TASK_LOCK_FILE,
)

# cli
from .cli import main, task_lock_cli, needs_approval, get_agent_action
from .cli import (
    Colors,
    safe_print,
    print_header,
    print_success,
    print_info,
    print_warning,
)


# Entry point for CLI
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "task":
        from .cli import task_lock_cli
        task_lock_cli(sys.argv[2:])
    else:
        from .cli import main
        main()
