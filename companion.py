"""
COMPANION v5.0 - SINGLE FILE
=============================
Pure data processor for agent tool routing.
Agent makes decisions, companion provides structured data.

Usage (from project root with .agents/skills/companion.py):
    python .agents/skills/companion.py "cari axios"
    python -c "import sys; sys.path.insert(0, '.agents/skills'); from companion import analyze_intent"

Or use companion_cli() for automatic path detection:
    python .agents/skills/companion.py --analyze "cari axios"
"""

import sys
import os
import json
import re
from datetime import datetime

# ============================================================
# AUTO-DISCOVERY - Make 'from companion import' work
# ============================================================

def _auto_import():
    """Auto-detect and import companion module.

    This allows 'from companion import' to work from any directory
    by automatically finding .agents/skills/companion.py and loading it.
    """
    # Check if already loaded
    if 'companion' in sys.modules:
        return True

    # Search for companion.py
    search_dirs = [
        '.agents/skills',
        '.agents/skills/companion',
        'skills',
        'skills/companion',
    ]

    # Also search parent directories
    cwd = os.getcwd()
    for i in range(4):  # Up to 4 levels up
        for d in search_dirs:
            candidate = os.path.join(cwd, d)
            companion_file = os.path.join(candidate, 'companion.py')
            if os.path.isfile(companion_file):
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
    sys.stdout.reconfigure(encoding='utf-8')

# ============================================================
# DATA STRUCTURES
# ============================================================

from dataclasses import dataclass
from typing import List, Optional, Dict
import re


@dataclass
class ToolMatch:
    name: str
    confidence: str  # "high" | "medium" | "low"
    reason: str
    command_template: str
    safety: str  # "safe" | "moderate"


@dataclass
class AnalyzeResult:
    input: str
    keywords: List[str]
    entities: List[str]
    specificity: str  # "high" | "medium" | "low"
    confidence_level: str  # "HIGH" | "MEDIUM" | "LOW" | "NONE"
    single_tool: Optional[ToolMatch] = None
    sequential_steps: List[ToolMatch] = None
    needs_clarification: bool = False
    clarification_note: Optional[str] = None


# ============================================================
# TOOL REGISTRY
# ============================================================

TOOL_REGISTRY = {
    "smart_search": {
        "keywords": ["cari", "find", "search", "locate", "ketemu", "where", "grep", "import", "module", "dependencies"],
        "confidence": "medium",
        "safety": "safe",
        "command": "python .agents/skills/smart_search/code_finder.py <dir> <keyword>"
    },
    "smart_replace": {
        "keywords": ["ganti", "replace", "tukar", "ubah", "change", "modify", "edit", "rename", "refactor", "konversi", "convert", "migration"],
        "confidence": "high",
        "safety": "moderate",
        "command": "python .agents/skills/smart_replace/replace_text.py <old> <new> [--apply]",
        "needs_approval": True
    },
    "selective_reader": {
        "keywords": ["baca", "read", "lihat", "view", "show", "check", "inspect", "dokumentasi"],
        "confidence": "medium",
        "safety": "safe",
        "command": "python .agents/skills/selective_reader/reader.py <filepath>"
    },
    "smart_tree": {
        "keywords": ["struktur", "tree", "map", "folder", "direktori", "arsitektur", "layout"],
        "confidence": "medium",
        "safety": "safe",
        "command": "python .agents/skills/smart_tree/scripts/tree_viewer.py . <depth>"
    },
    "scope_guardian": {
        "keywords": ["scope", "area", "batass", "batasan", "limits", "di area", "seluruh"],
        "confidence": "medium",
        "safety": "safe",
        "command": "python .agents/skills/scope_guardian/scripts/scope_check.py <filepath>"
    },
    "deep_analyzer": {
        "keywords": ["analisa", "analyze", "overview", "ringkasan", "summary", "statistik", "diagnosa", "evaluasi", "inventori"],
        "confidence": "high",
        "safety": "safe",
        "command": "python .agents/skills/deep_analyzer/analyzer.py . --json"
    },
    "project_guardian": {
        "keywords": ["keamanan", "security", "audit", "vulnerability", "amankan", "proteksi", "credential", "password", "secret", "auth", "encryption"],
        "confidence": "high",
        "safety": "safe",
        "command": "python .agents/skills/project_guardian/guardian.py --summary"
    },
    "impact_analyzer": {
        "keywords": ["impact", "dampak", "effect", "affected", "depend", "dependency", "terkait", "relasi", "pemakaian"],
        "confidence": "medium",
        "safety": "safe",
        "command": "python .agents/skills/impact_analyzer/analyzer.py <file> ."
    },
    "crash_decoder": {
        "keywords": ["error", "bug", "crash", "debug", "log", "trace", "gagal", "failed", "masalah", "issue", "exception", "perbaiki"],
        "confidence": "high",
        "safety": "safe",
        "command": "python .agents/skills/crash_decoder/decoder.py <logfile>"
    },
    "clean_sweeper": {
        "keywords": ["bersih", "bersihkan", "cleanup", "clean", "hapus", "delete", "buang", "sampah", "residu", "garbage", "unused", "backup", "archive", "temporary", "tmp", "beresin", "rapikan"],
        "confidence": "medium",
        "safety": "safe",
        "command": "python .agents/skills/clean_sweeper/sweeper.py ."
    },
    "auto_scaffolder": {
        "keywords": ["generate", "generate", "buat", "create", "new", "tambah", "add", "instance", "scaffolding", "tambah component"],
        "confidence": "high",
        "safety": "moderate",
        "command": "python .agents/skills/auto_scaffolder/scaffolder.py <type> <name> [--apply]",
        "needs_approval": True
    },
}

APPROVAL_REQUIRED = {"smart_replace", "auto_scaffolder", "context_mapper", "import_fixer"}

CLARIFICATION_TRIGGERS = {
    "export": ["export", "eksport", "excel", "xlsx", "csv", "spreadsheet"],
    "pdf": ["pdf", "laporan", "report", "cetakan"],
    "diagram": ["diagram", "flowchart", "uml", "sequence"],
}

# ============================================================
# PROJECT CONTEXT LOADING (session-cached)
# ============================================================

# Session cache: {path: (mtime, content)}
_CONTEXT_CACHE: Dict[str, tuple] = {}
_CONTEXT_CACHE_TTL_SECONDS = 300  # 5 minutes


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

                # Return cached if within TTL and mtime unchanged
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


# ============================================================
# USER PROFILE (persistent, from memory.json)
# ============================================================

_MEMORY_CACHE: Dict[str, int] = {}  # path -> user_level, cached per session


def load_user_level() -> int:
    """Load user_level from .agents/memory.json.

    Returns default 3 if file or field not found (no error).
    Cached per session to avoid repeated disk reads.
    """
    memory_path = '.agents/memory.json'
    if not os.path.isfile(memory_path):
        return 3

    # Check session cache
    cached = _MEMORY_CACHE.get(memory_path)
    if cached is not None:
        return cached

    try:
        with open(memory_path, encoding='utf-8') as f:
            data = json.load(f)
        level = data.get('user_level', 3)
        if not isinstance(level, int) or level < 1 or level > 10:
            level = 3
        _MEMORY_CACHE[memory_path] = level
        return level
    except (json.JSONDecodeError, IOError, KeyError):
        _MEMORY_CACHE[memory_path] = 3
        return 3


# ============================================================
# ENTITY EXTRACTION
# ============================================================

def extract_entities(text: str) -> List[str]:
    """Extract entities like function names, file paths, etc."""
    entities = []

    # Extract CamelCase (PascalCase)
    camel_upper = re.findall(r'\b[A-Z][a-z]+(?:[A-Z][a-z]+)+\b', text)
    entities.extend(camel_upper)

    # Extract camelCase (starts lowercase)
    camel_lower = re.findall(r'\b[a-z]+(?:[A-Z][a-zA-Z]*)+', text)
    entities.extend(camel_lower)

    # Extract snake_case
    snake = re.findall(r'\b[a-z]+(?:_[a-z]+)+\b', text)
    entities.extend(snake)

    # Extract quoted strings
    quoted = re.findall(r'["\']([^"\']+)["\']', text)
    entities.extend(quoted)

    # Extract variables with $ or %
    vars_with_sign = re.findall(r'[$%][\w]+', text)
    entities.extend(vars_with_sign)

    # Extract React hooks
    hooks = re.findall(r'use[A-Z]\w+', text)
    entities.extend(hooks)

    # Deduplicate
    seen = set()
    result = []
    for e in entities:
        if e not in seen and len(e) > 2:
            seen.add(e)
            result.append(e)

    return result


# ============================================================
# SHOULD GRILL (Phase 4 - Simple Detection)
# ============================================================

def should_grill(result: AnalyzeResult) -> dict:
    """
    Deteksi sederhana apakah instruksi butuh grilling.
    Bahasa disesuaikan berdasarkan user_level dari memory.json.

    Returns:
        dict dengan:
        - needs_grilling: bool
        - reason: str (penjelasan kenapa)
    """
    user_level = load_user_level()

    # Micro Task criteria:
    # HIGH confidence + HIGH specificity = langsung eksekusi
    if result.confidence_level == "HIGH" and result.specificity == "high":
        return {
            "needs_grilling": False,
            "reason": "Micro Task - specific dan confident, langsung eksekusi"
        }

    # Specific entity + high specificity = Micro Task ( MESKIPUN MEDIUM confidence)
    if len(result.entities) >= 1 and result.specificity == "high":
        return {
            "needs_grilling": False,
            "reason": "Micro Task - specific entity detected"
        }

    # MEDIUM/LOW confidence without specific entity = perlu clarify
    if result.confidence_level in ("MEDIUM", "LOW", "NONE"):
        if user_level >= 7:
            # Technical language for experienced users
            reason = (
                f"confidence={result.confidence_level}, specificity={result.specificity} "
                f"({len(result.entities)} entities extracted) — requires clarification before execution"
            )
        else:
            # Simple language for default/low level
            reason = f"Confidence {result.confidence_level} - perlu clarify"
        return {
            "needs_grilling": True,
            "reason": reason
        }

    # Long instruction without entities = ambiguous
    words = result.input.split()
    if len(words) > 15 and len(result.entities) == 0:
        if user_level >= 7:
            reason = f"instruction length={len(words)} words, 0 entities, confidence={result.confidence_level} — ambiguous scope"
        else:
            reason = "Instruction >15 words without specific entity"
        return {
            "needs_grilling": True,
            "reason": reason
        }

    # Default: grilling needed for non-trivial tasks
    return {
        "needs_grilling": True,
        "reason": "Ambiguous intent"
    }


# ============================================================
# ANALYZE INTENT
# ============================================================

def analyze_intent(user_input: str) -> AnalyzeResult:
    """Analyze user intent and return structured data."""
    text = user_input.lower()
    keywords_found = []
    tool_matches = []

    # Load project context for entity validation
    project_context = load_project_context()

    # Check clarification triggers
    needs_clarify = False
    clarify_note = None
    for trigger, trigger_kws in CLARIFICATION_TRIGGERS.items():
        for kw in trigger_kws:
            if kw in text:
                needs_clarify = True
                clarify_note = f"Tool for '{trigger}' not available. Use manual approach."
                break

    # Match keywords to tools
    for tool_name, tool_info in TOOL_REGISTRY.items():
        for kw in tool_info["keywords"]:
            if kw in text:
                keywords_found.append(kw)
                tool_matches.append({
                    "tool": tool_name,
                    "keyword": kw,
                    "confidence": tool_info["confidence"]
                })
                break

    # Extract entities (use ORIGINAL input)
    entities = extract_entities(user_input)

    # Determine specificity — boost when entities are confirmed in project context
    specificity = "low"
    if len(entities) >= 1 and len(tool_matches) >= 1:
        specificity = "high"
    elif len(entities) >= 2:
        specificity = "high"
    elif len(entities) >= 1 or len(tool_matches) >= 1:
        specificity = "medium"

    # Boost specificity when extracted entities appear in project context
    if project_context:
        matched_entities = [e for e in entities if entity_in_context(e, project_context)]
        if matched_entities:
            # Found entity matches in project context — upgrade to high if not already
            if specificity != "high":
                specificity = "high"

    # Determine confidence
    if not tool_matches:
        confidence_level = "NONE"
    elif len(tool_matches) == 1 and tool_matches[0]["confidence"] == "high":
        confidence_level = "HIGH"
    elif len(tool_matches) >= 2:
        confidence_level = "HIGH"
    elif len(tool_matches) == 1:
        confidence_level = "MEDIUM"
    else:
        confidence_level = "LOW"

    # Build single_tool
    single_tool = None
    if tool_matches and not needs_clarify:
        best = tool_matches[0]
        tool_name = best["tool"]
        tool_info = TOOL_REGISTRY[tool_name]
        single_tool = ToolMatch(
            name=tool_name,
            confidence=tool_info["confidence"],
            reason=f"Matched: {best['keyword']}",
            command_template=tool_info["command"],
            safety=tool_info["safety"]
        )

    return AnalyzeResult(
        input=user_input,
        keywords=keywords_found,
        entities=entities,
        specificity=specificity,
        confidence_level=confidence_level,
        single_tool=single_tool,
        sequential_steps=[],
        needs_clarification=needs_clarify,
        clarification_note=clarify_note
    )


# ============================================================
# UTILITY
# ============================================================

def needs_approval(tool: str) -> bool:
    return tool in APPROVAL_REQUIRED


def get_agent_action(result: AnalyzeResult) -> str:
    if result.needs_clarification:
        return "CLARIFY"
    if result.confidence_level == "HIGH" and result.specificity == "high":
        return "EXECUTE"
    elif result.confidence_level in ("HIGH", "MEDIUM"):
        return "KONFIRMASI"
    else:
        return "CLARIFY"


# ============================================================
# CLI
# ============================================================

def main():
    """CLI interface."""
    import argparse
    parser = argparse.ArgumentParser(description='Companion v5.0 - Intent Analyzer')
    parser.add_argument('input', nargs='*', help='Input text to analyze')
    parser.add_argument('--analyze', '-a', help='Analyze input text')
    args = parser.parse_args()

    user_input = args.analyze or ' '.join(args.input)

    if not user_input:
        print("Usage: python companion.py 'your instruction'")
        print("   or: python companion.py --analyze 'your instruction'")
        return

    result = analyze_intent(user_input)
    grill = should_grill(result)

    print(f"\n{'='*60}")
    print(f"COMPANION v5.0 - ANALYSIS RESULT")
    print(f"{'='*60}")
    print(f"Input: {result.input}")
    print(f"Keywords: {result.keywords}")
    print(f"Entities: {result.entities}")
    print(f"Specificity: {result.specificity}")
    print(f"Confidence: {result.confidence_level}")
    print(f"Action: {get_agent_action(result)}")
    print(f"")
    print(f"Grilling Check:")
    print(f"  needs_grilling: {grill['needs_grilling']}")
    print(f"  reason: {grill['reason']}")

    if result.single_tool:
        print(f"\nTool: {result.single_tool.name}")
        print(f"  Confidence: {result.single_tool.confidence}")
        print(f"  Reason: {result.single_tool.reason}")
        print(f"  Safety: {result.single_tool.safety}")
        print(f"  Command: {result.single_tool.command_template}")
        print(f"  Needs Approval: {needs_approval(result.single_tool.name)}")
    elif result.needs_clarification:
        print(f"\n⚠️ {result.clarification_note}")

    print(f"{'='*60}\n")


# ============================================================
# TASK LOCK (Phase 4 - Basic Read/Write Only)
# ============================================================

TASK_LOCK_FILE = '.agents/task_lock.json'

def load_task_lock():
    """Load task_lock.json from current directory."""
    if not os.path.exists(TASK_LOCK_FILE):
        return None
    try:
        with open(TASK_LOCK_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def save_task_lock(data):
    """Save task_lock.json to current directory."""
    # Ensure .agents directory exists
    os.makedirs('.agents', exist_ok=True)
    with open(TASK_LOCK_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return True


def start_task_lock(task_id: str, user_intent: str):
    """Start a new task lock."""
    data = {
        "task_id": task_id,
        "user_intent_raw": user_intent,
        "prompt_classification": None,       # analytical | reasoning | instruction | feature_request
        "classification_reasoning": "",      # agent: alasan kenapa klasifikasi itu dipilih
        "response_mode": None,              # execute | suggest | grill
        "response_mode_reasoning": "",      # agent: alasan kenapa mode itu dipilih
        "clarified_understanding": "",
        "level_target": load_user_level(),  # dari memory.json, default 3
        "grilling_log": [],
        "plan_summary": "",
        "status": "clarifying",
        "created_at": str(datetime.now())
    }
    save_task_lock(data)
    return data


def add_grilling_qa(question: str, answer: str):
    """Add a Q&A pair to the grilling log."""
    data = load_task_lock()
    if not data:
        return None
    data['grilling_log'].append({
        "question": question,
        "answer": answer,
        "timestamp": str(datetime.now())
    })
    save_task_lock(data)
    return data


def update_task_lock(**kwargs):
    """Update task_lock fields."""
    data = load_task_lock()
    if not data:
        return None
    for key, value in kwargs.items():
        if key in data:
            data[key] = value
    save_task_lock(data)
    return data


def end_task_lock():
    """Delete task_lock.json (task complete)."""
    if os.path.exists(TASK_LOCK_FILE):
        os.remove(TASK_LOCK_FILE)
    return True


def get_task_status():
    """Get current task status."""
    data = load_task_lock()
    if not data:
        return {"status": "no_active_task"}
    return data


# ============================================================
# CLI Commands for task_lock
# ============================================================

def task_lock_cli(args):
    """CLI interface for task_lock commands."""
    import argparse
    parser = argparse.ArgumentParser(description='Task Lock Manager')
    sub = parser.add_subparsers(dest='cmd')

    # start <task_id> <user_intent>
    p = sub.add_parser('start', help='Start new task lock')
    p.add_argument('task_id')
    p.add_argument('user_intent', nargs='+')

    # add <q> <a>
    p = sub.add_parser('add', help='Add Q&A to grilling log')
    p.add_argument('question')
    p.add_argument('answer')

    # update <key>=<value>
    p = sub.add_parser('update', help='Update field')
    p.add_argument('field')
    p.add_argument('value')

    # status
    sub.add_parser('status', help='Show current task status')

    # end
    sub.add_parser('end', help='End current task')

    args = parser.parse_args(args)

    if args.cmd == 'start':
        intent = ' '.join(args.user_intent)
        result = start_task_lock(args.task_id, intent)
        print(f"✅ Task started: {args.task_id}")
        print(json.dumps(result, indent=2))

    elif args.cmd == 'add':
        result = add_grilling_qa(args.question, args.answer)
        print(f"✅ Q&A added")
        print(json.dumps(result, indent=2))

    elif args.cmd == 'update':
        result = update_task_lock(**{args.field: args.value})
        print(f"✅ Updated {args.field}")
        print(json.dumps(result, indent=2))

    elif args.cmd == 'status':
        result = get_task_status()
        print(json.dumps(result, indent=2))

    elif args.cmd == 'end':
        end_task_lock()
        print("✅ Task ended, lock removed")

    else:
        parser.print_help()


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "task":
        task_lock_cli(sys.argv[2:])
    else:
        main()

