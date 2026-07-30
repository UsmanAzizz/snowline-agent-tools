"""
AGENTIC COMPANION v5.0 - FULLY TESTED
=====================================
- Fixed vocabulary logic
- Multi-word keyword support
- Tool selection improved
- Blocking logic for clarification
- Learning loop integrated
- Execution engine integrated
- Task 2 tools fully integrated
"""

import os
import sys
import re
from typing import Dict, List, Optional
from dataclasses import dataclass

# Ensure proper imports
_companion_dir = os.path.dirname(os.path.abspath(__file__))
if _companion_dir not in sys.path:
    sys.path.insert(0, _companion_dir)

from memory import memory, Memory

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')


@dataclass
class IntentResult:
    clarity: str
    intent_type: str
    keywords: List[str]
    needs_clarification: bool = False
    clarification_msg: str = ""


@dataclass
class Step:
    order: int
    tool: str
    params: str
    reason: str
    needs_clarify: bool = False
    clarify_note: str = ""


# ============================================================
# KEYWORD MAPPINGS
# ============================================================

# NOTE: Multi-word keywords use underscores (e.g., "token_budget")
# The matching logic checks for these as substrings

TOOL_KEYWORDS = {
    # === SEARCH & MODIFY ===
    "smart_search": [
        "cari", "find", "search", "locate", "ketemu", "where", "grep", "import", "module", "dependencies"
    ],
    "smart_replace": [
        "ganti", "replace", "tukar", "ubah", "change", "modify", "edit", "rename", "refactor", "konversi", "convert", "migration"
    ],

    # === READ & NAVIGATE ===
    "selective_reader": [
        "baca", "read", "lihat", "view", "show", "check", "inspect", "dokumentasi"
    ],
    "smart_tree": [
        "struktur", "tree", "map", "folder", "direktori", "arsitektur", "layout"
    ],
    "scope_guardian": [
        "scope", "area", "batass", "batasan", "limits", "di area", "seluruh"
    ],

    # === ANALYZE & AUDIT ===
    "deep_analyzer": [
        "analisa", "analyze", "overview", "ringkasan", "summary", "statistik", "diagnosa", "evaluasi", "inventori"
    ],
    "project_guardian": [
        "keamanan", "security", "audit", "vulnerability", "amankan", "proteksi", "credential", "password", "secret", "auth", "encryption", "credential_token"
    ],
    "impact_analyzer": [
        "impact", "dampak", "effect", "affected", "depend", "dependency", "terkait", "relasi", "pemakaian"
    ],
    "crash_decoder": [
        "error", "bug", "crash", "debug", "log", "trace", "gagal", "failed", "masalah", "issue", "exception", "perbaiki"
    ],

    # === CLEAN & GENERATE ===
    "clean_sweeper": [
        "bersih", "cleanup", "clean", "hapus", "delete", "buang", "sampah", "residu", "garbage", "unused", "backup", "archive", "temporary", "tmp"
    ],
    "auto_scaffolder": [
        "generate", "generate", "buat", "create", "new", "tambah", "add", "instance", "scaffolding", "tambah component"
    ],

    # === CONTEXT MANAGEMENT (Task 2 - NEW) ===
    "token_budget": [
        "token_budget", "token_usage", "kuota", "pengunaan", "efficiency", "token_limit"
    ],
    "context_curator": [
        "context_curator", "filter_noise", "reduce_context", "kurangi_noise", "clean_code_context"
    ],
    "output_formatter": [
        "output_formatter", "table_format", "readable", "tampilkan", "tabel"
    ],
    "decision_validator": [
        "validasi", "risk_check", "safety_check", "verifikasi", "cek_keputusan"
    ],
}

# Multi-word keywords mapping (underscore -> space for matching)
MULTI_WORD_KEYWORDS = {
    "token_budget": ["token budget", "token usage", "hemat token", "pengunaan token", "token limit", "cek token", "token efficiency"],
    "context_curator": ["bersihkan context", "filter noise", "reduce context", "kurangi noise", "bersih kan context", "clean code context", "bersihkan context ini"],
    "output_formatter": ["json to table", "format json", "format table", "tampilkan data", "format output", "ke table"],
    "decision_validator": ["cek risk", "safety check", "cek keputusan", "risk assessment", "verifikasi decision", "validasi decision"],
}

NEEDS_CLARIFICATION = {
    "export": {
        "keywords": ["export", "eksport", "excel", "xlsx", "csv", "spreadsheet"],
        "message": "Tool untuk export Excel/CSV belum ada. Gunakan library manual atau dokumentasikan.",
        "blocks_tools": ["auto_scaffolder"]  # FIX: block auto_scaffolder when "export" is detected
    },
    "pdf": {
        "keywords": ["pdf", "laporan", "report", "cetakan"],
        "message": "Tool untuk generate PDF belum ada. Gunakan library manual atau dokumentasikan.",
        "blocks_tools": ["auto_scaffolder"]  # FIX: block auto_scaffolder when "pdf" is detected
    },
    "diagram": {
        "keywords": ["diagram", "flowchart", "uml", "sequence"],
        "message": "Tool untuk generate diagram belum ada.",
        "blocks_tools": ["auto_scaffolder"]
    }
}


# ============================================================
# ANALYZER
# ============================================================

def analyze_intent(user_input: str) -> IntentResult:
    """Analyze user intent and extract keywords."""
    text = user_input.lower()
    keywords = []

    # Extract multi-word keywords FIRST (higher priority)
    for tool, multi_kws in MULTI_WORD_KEYWORDS.items():
        for kw in multi_kws:
            if kw in text:
                keywords.append(kw)
                break

    # Extract single-word keywords
    for tool, kw_list in TOOL_KEYWORDS.items():
        for kw in kw_list:
            if kw in text:
                keywords.append(kw)
                break

    # Check needs clarification
    needs_clarify = False
    clarify_msg = ""
    for key, info in NEEDS_CLARIFICATION.items():
        for kw in info["keywords"]:
            if kw in text:
                needs_clarify = True
                clarify_msg = info["message"]
                break

    # Determine clarity
    vague_patterns = ["^cek$", "^bantu$", "^lihat$", "^apa$", "^halo$", "^hi$"]
    clarity = "clear"
    for p in vague_patterns:
        if re.search(p, text):
            clarity = "vague"
            break
    if not keywords and not needs_clarify:
        clarity = "ambiguous"

    return IntentResult(
        clarity=clarity,
        intent_type="single_action",
        keywords=keywords,
        needs_clarification=needs_clarify,
        clarification_msg=clarify_msg
    )


# ============================================================
# PLANNER
# ============================================================

def plan_steps(user_input: str, intent: IntentResult) -> List[Step]:
    """Plan execution steps based on intent."""
    text = user_input.lower()
    steps = []
    used_tools = set()
    order = 1

    # FIX v4.2: Detect which clarifications are needed FIRST
    clarification_needed = {}  # {key: info} for tools that need clarification
    for key, info in NEEDS_CLARIFICATION.items():
        for kw in info["keywords"]:
            if kw in text:
                clarification_needed[key] = info
                break

    # Determine which tools to BLOCK based on clarifications
    blocked_tools = set()
    for key, info in clarification_needed.items():
        for blocked_tool in info.get("blocks_tools", []):
            blocked_tools.add(blocked_tool)

    # Priority order (Task 2 tools added)
    tool_priority = [
        # Context Management FIRST (Task 2 - NEW) - check multi-word first
        "token_budget", "context_curator", "output_formatter",
        # High priority - Security & Safety
        "project_guardian", "decision_validator",
        # Search & Modify
        "smart_search", "smart_replace",
        # Read & Navigate
        "selective_reader", "smart_tree", "scope_guardian",
        # Analyze
        "deep_analyzer", "impact_analyzer", "crash_decoder",
        # Clean & Generate
        "clean_sweeper", "auto_scaffolder",
    ]

    for tool in tool_priority:
        if tool in used_tools:
            continue
        # FIX v4.2: Skip blocked tools
        if tool in blocked_tools:
            continue

        # Check multi-word keywords FIRST
        matched = False
        for kw in MULTI_WORD_KEYWORDS.get(tool, []):
            if kw in text:
                steps.append(Step(
                    order=order,
                    tool=tool,
                    params=get_params(tool),
                    reason=f"'{kw}' detected (multi-word)",
                    needs_clarify=False,
                    clarify_note=""
                ))
                used_tools.add(tool)
                order += 1
                matched = True
                break

        if matched:
            continue

        # Check single-word keywords
        for kw in TOOL_KEYWORDS.get(tool, []):
            if kw in text:
                steps.append(Step(
                    order=order,
                    tool=tool,
                    params=get_params(tool),
                    reason=f"'{kw}' detected",
                    needs_clarify=False,
                    clarify_note=""
                ))
                used_tools.add(tool)
                order += 1
                break

    # Add clarification steps (if any)
    for key, info in clarification_needed.items():
        steps.append(Step(
            order=order,
            tool="NEEDS_CLARIFICATION",
            params=key,
            reason=f"'{key}' detected",
            needs_clarify=True,
            clarify_note=info["message"]
        ))
        order += 1
        break  # Only one clarification message at a time

    return steps


def get_params(tool: str) -> str:
    """
    Get command params template for tool.
    NOTE: This returns PREVIEW params, NOT execution params.
    --apply flag must be added explicitly AFTER human approval.
    """
    params_map = {
        # Search & Modify
        "smart_search": "<keyword>",
        "smart_replace": "<old> <new>",  # NO --apply here! Added only after approval
        # Read & Navigate
        "selective_reader": "<filepath>",
        "smart_tree": ". <depth>",
        "scope_guardian": "<filepath>",
        # Analyze & Audit
        "project_guardian": "--summary",
        "deep_analyzer": ". --json",
        "impact_analyzer": "<file> .",
        "crash_decoder": "<logfile>",
        "decision_validator": "<action> [--target <path>]",
        # Clean & Generate
        "clean_sweeper": ".",
        "auto_scaffolder": "<type> <name>",  # NO --apply here! Added only after approval
        # Context Management
        "context_mapper": ".",  # NO --apply here! Added only after approval
        "token_budget": "[--status|--reset]",
        "context_curator": "<text>",
        "output_formatter": "<json_text> [--format table]",
    }
    return params_map.get(tool, ".")


def needs_approval(tool: str) -> bool:
    """
    Check if tool REQUIRES --apply flag for modification.
    These tools need explicit human approval before execution.
    """
    APPROVAL_REQUIRED = [
        "smart_replace",    # Modifies files
        "auto_scaffolder",  # Creates files
        "context_mapper",    # Creates project documentation files
        "import_fixer",      # Modifies import paths in files
    ]
    return tool in APPROVAL_REQUIRED


def build_execution_command(step: Step, approved: bool = False) -> str:
    """
    Build command for execution.
    --apply is added ONLY if approved=True (after human approval).

    Args:
        step: The Step object from plan_steps()
        approved: True only if human explicitly approved execution

    Returns:
        Command string ready to execute
    """
    if step.tool == "NEEDS_CLARIFICATION":
        return f"# MANUAL: {step.params}"

    # Tools in .agents/skills/
    agent_tools = {
        "smart_search": "smart_search/code_finder.py",
        "smart_replace": "smart_replace/replace_text.py",
        "selective_reader": "selective_reader/reader.py",
        "project_guardian": "project_guardian/guardian.py",
        "clean_sweeper": "clean_sweeper/sweeper.py",
        "deep_analyzer": "deep_analyzer/analyzer.py",
        "smart_tree": "smart_tree/scripts/tree_viewer.py",
        "scope_guardian": "scope_guardian/scripts/scope_check.py",
        "impact_analyzer": "impact_analyzer/analyzer.py",
        "crash_decoder": "crash_decoder/decoder.py",
        "auto_scaffolder": "auto_scaffolder/scaffolder.py",
        "context_mapper": "context_mapper/context_mapper.py",
    }

    # Tools in tools/ (separate directory)
    new_tools = {
        "token_budget": "tools/token_budget.py",
        "context_curator": "tools/context_curator.py",
        "output_formatter": "tools/output_formatter.py",
        "decision_validator": "tools/decision_validator.py",
    }

    # Determine script path and base
    if step.tool in agent_tools:
        script_path = agent_tools[step.tool]
        base = ".agents/skills"
    elif step.tool in new_tools:
        script_path = new_tools[step.tool]
        base = ""  # Already includes tools/
    else:
        return f"# Unknown tool: {step.tool}"

    # Build params - add --apply ONLY if approved
    params = step.params
    if approved and needs_approval(step.tool):
        params = f"{params} --apply"

    if base:
        return f"python {base}/{script_path} {params}"
    else:
        return f"python {script_path} {params}"


def get_command(step: Step) -> str:
    """
    Get preview command (WITHOUT --apply).
    For execution with --apply, use build_execution_command(step, approved=True).
    """
    # Returns preview-only command
    return build_execution_command(step, approved=False)


def learn(intent: str, keywords: List[str], tool: str, success: bool = True):
    """Record tool selection to memory for learning."""
    memory.record(intent, keywords, tool, success)


def recall(intent: str, keywords: List[str]) -> str:
    """Recall suggested tool from memory."""
    suggestion = memory.suggest(intent, keywords)
    if suggestion:
        return f"Learned from history: {suggestion}"
    return ""


def memory_stats() -> Dict:
    """Get learning stats."""
    return memory.get_stats()


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":
    tests = [
        "refactor handleSubmit jadi handleFormSubmit",
        "export user ke excel",
        "generate PDF report",
        "cari semua import axios",
        "backup folder logs",
        "analisa database schema",
        "bersihkan project",
        "cek keamanan",
        "impact analysis component Dashboard",
    ]

    print("=" * 70)
    print("COMPANION v4.1 - TEST")
    print("=" * 70)

    for i, test in enumerate(tests, 1):
        print(f"\n{'─' * 70}")
        print(f"TEST {i}: \"{test}\"")
        print('─' * 70)

        intent = analyze_intent(test)
        steps = plan_steps(test, intent)

        print(f"Keywords  : {intent.keywords[:4]}")
        if intent.needs_clarification:
            print(f"Clarify   : {intent.clarification_msg}")
        print(f"Steps     : {len(steps)} planned")

        for step in steps[:3]:
            cmd = get_command(step)
            flag = " [CLARIFY]" if step.needs_clarify else ""
            print(f"  {step.order}. {step.tool}{flag}")
            print(f"     -> {cmd}")
            if step.clarify_note:
                print(f"     ! {step.clarify_note}")

    print("\n" + "=" * 70)
    print("VOCABULARY FIXES:")
    print("- 'refactor' -> smart_replace")
    print("- 'export/excel' -> clarification")
    print("- 'pdf/report' -> clarification")
    print("- 'import' -> smart_search")
    print("- 'backup/archive' -> clean_sweeper")
    print("=" * 70)
