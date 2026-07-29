"""
AGENTIC COMPANION v4.1 SIMPLIFIED
=========================
Fixed vocabulary logic.
Tool selection improved.
"""

import os
import sys
import re
from typing import Dict, List, Optional
from dataclasses import dataclass

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

TOOL_KEYWORDS = {
    "smart_search": [
        "cari", "find", "search", "locate", "ketemu", "where", "grep", "import", "module", "dependencies"
    ],
    "smart_replace": [
        "ganti", "replace", "tukar", "ubah", "change", "modify", "edit", "rename", "refactor", "konversi", "convert", "migration"
    ],
    "selective_reader": [
        "baca", "read", "lihat", "view", "show", "cek", "check", "inspect", "dokumentasi"
    ],
    "smart_tree": [
        "struktur", "tree", "map", "folder", "direktori", "arsitektur", "layout"
    ],
    "scope_guardian": [
        "scope", "area", "batass", "batasan", "limits", "di area", "seluruh"
    ],
    "clean_sweeper": [
        "bersihkan", "bersih", "cleanup", "clean", "hapus", "delete", "buang", "sampah", "residu", "garbage", "unused", "backup", "archive", "temporary", "tmp"
    ],
    "deep_analyzer": [
        "analisa", "analyze", "overview", "ringkasan", "summary", "statistik", "diagnosa", "evaluasi", "inventori"
    ],
    "auto_scaffolder": [
        "generate", "generate", "buat", "create", "new", "tambah", "add", "instance", "scaffolding", "tambah component"
    ],
    "crash_decoder": [
        "error", "bug", "crash", "debug", "log", "trace", "gagal", "failed", "masalah", "issue", "exception", "perbaiki"
    ],
    "impact_analyzer": [
        "impact", "dampak", "effect", "affected", "depend", "dependency", "terkait", "relasi", "pemakaian"
    ],
    "project_guardian": [
        "keamanan", "security", "audit", "vulnerability", "amankan", "proteksi", "credential", "password", "token", "secret", "auth", "encryption"
    ],
}

NEEDS_CLARIFICATION = {
    "export": {
        "keywords": ["export", "eksport", "excel", "xlsx", "csv", "spreadsheet"],
        "message": "Tool untuk export Excel/CSV belum ada. Gunakan library manual atau dokumentasikan."
    },
    "pdf": {
        "keywords": ["pdf", "laporan", "report", "cetakan"],
        "message": "Tool untuk generate PDF belum ada. Gunakan library manual atau dokumentasikan."
    }
}


# ============================================================
# ANALYZER
# ============================================================

def analyze_intent(user_input: str) -> IntentResult:
    """Analyze user intent and extract keywords."""
    text = user_input.lower()
    keywords = []

    # Extract keywords
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

    # Priority order
    tool_priority = [
        "project_guardian", "smart_search", "smart_replace",
        "selective_reader", "smart_tree", "scope_guardian",
        "clean_sweeper", "deep_analyzer", "auto_scaffolder",
        "crash_decoder", "impact_analyzer"
    ]

    for tool in tool_priority:
        if tool in used_tools:
            continue
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

    # Check for clarification needed
    for key, info in NEEDS_CLARIFICATION.items():
        for kw in info["keywords"]:
            if kw in text:
                steps.append(Step(
                    order=order,
                    tool="NEEDS_CLARIFICATION",
                    params=key,
                    reason=f"'{kw}' detected",
                    needs_clarify=True,
                    clarify_note=info["message"]
                ))
                order += 1
                break

    return steps


def get_params(tool: str) -> str:
    """Get command params for tool."""
    params_map = {
        "smart_search": "<keyword>",
        "smart_replace": "<old> <new> --apply",
        "selective_reader": "<filepath>",
        "smart_tree": ". <depth>",
        "project_guardian": "--summary",
        "clean_sweeper": ".",
        "deep_analyzer": ". --json",
        "auto_scaffolder": "<type> <name> --apply",
        "crash_decoder": "<logfile>",
        "impact_analyzer": "<file> .",
        "scope_guardian": "<filepath>",
    }
    return params_map.get(tool, ".")


def get_command(step: Step) -> str:
    """Get full command string."""
    if step.tool == "NEEDS_CLARIFICATION":
        return f"# MANUAL: {step.params}"

    script_map = {
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
    }
    script = script_map.get(step.tool, f"{step.tool}/main.py")
    return f"python .agents/skills/{script} {step.params}"


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
    print("COMPANION v4.1 - FIXED VOCABULARY TEST")
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
