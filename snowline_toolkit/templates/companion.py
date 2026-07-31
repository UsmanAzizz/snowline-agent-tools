"""
COMPANION v5.0 - SINGLE FILE
=============================
Pure data processor for agent tool routing.
Agent makes decisions, companion provides structured data.

Usage:
    python companion.py "cari axios"
    from companion import analyze_intent

Auto-discovers module path - works from any directory.
"""

import sys
import os
import re
from dataclasses import dataclass
from typing import List, Optional, Dict

# ============================================================
# AUTO-DISCOVERY PATH
# ============================================================

_companion_file = os.path.abspath(__file__)
_companion_dir = os.path.dirname(_companion_file)

# Add companion directory to path
if _companion_dir not in sys.path:
    sys.path.insert(0, _companion_dir)

# Ensure UTF-8
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')


# ============================================================
# DATA STRUCTURES
# ============================================================

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
    # Search & Modify
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
    # Read & Navigate
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
    # Analyze & Audit
    "deep_analyzer": {
        "keywords": ["analisa", "analyze", "overview", "ringkasan", "summary", "statistik", "diagnosa", "evaluasi", "inventori"],
        "confidence": "high",
        "safety": "safe",
        "command": "python .agents/skills/deep_analyzer/analyzer.py . --json"
    },
    "project_guardian": {
        "keywords": ["keamanan", "security", "audit", "vulnerability", "amankan", "proteksi", "credential", "password", "secret", "auth", "encryption", "credential_token"],
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
    # Clean & Generate
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

# Tools that need approval
APPROVAL_REQUIRED = {"smart_replace", "auto_scaffolder", "context_mapper", "import_fixer"}

# Clarification triggers
CLARIFICATION_TRIGGERS = {
    "export": ["export", "eksport", "excel", "xlsx", "csv", "spreadsheet"],
    "pdf": ["pdf", "laporan", "report", "cetakan"],
    "diagram": ["diagram", "flowchart", "uml", "sequence"],
}


# ============================================================
# ENTITY EXTRACTION
# ============================================================

def extract_entities(text: str) -> List[str]:
    """Extract entities like function names, file paths, etc."""
    entities = []

    # Extract CamelCase (function/class names)
    camel = re.findall(r'\b[A-Z][a-z]+(?:[A-Z][a-z]+)+\b', text)
    entities.extend(camel)

    # Extract quoted strings
    quoted = re.findall(r'["\']([^"\']+)["\']', text)
    entities.extend(quoted)

    # Extract variables with $ or %
    vars_with_sign = re.findall(r'[$%][\w]+', text)
    entities.extend(vars_with_sign)

    return list(set(entities))


# ============================================================
# ANALYZE INTENT
# ============================================================

def analyze_intent(user_input: str) -> AnalyzeResult:
    """Analyze user intent and return structured data.

    Pure data processor - does NOT make decisions.
    Agent decides what to do based on this data.
    """
    text = user_input.lower()
    keywords_found = []
    tool_matches = []

    # Check for clarification triggers
    needs_clarify = False
    clarify_note = None
    for trigger, trigger_keywords in CLARIFICATION_TRIGGERS.items():
        for kw in trigger_keywords:
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

    # Extract entities
    entities = extract_entities(text)

    # Determine specificity (how specific is the input)
    specificity = "low"
    if len(entities) >= 2 or len(keywords_found) >= 2:
        specificity = "high"
    elif len(entities) >= 1 or len(keywords_found) >= 1:
        specificity = "medium"

    # Determine confidence level
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
        best_match = tool_matches[0]
        tool_name = best_match["tool"]
        tool_info = TOOL_REGISTRY[tool_name]
        single_tool = ToolMatch(
            name=tool_name,
            confidence=tool_info["confidence"],
            reason=f"Matched: {best_match['keyword']}",
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
# UTILITY FUNCTIONS
# ============================================================

def needs_approval(tool: str) -> bool:
    """Check if tool requires approval."""
    return tool in APPROVAL_REQUIRED


def get_agent_action(result: AnalyzeResult) -> str:
    """Determine agent action based on AnalyzeResult.

    Decision matrix for agent to follow.
    """
    if result.needs_clarification:
        return "CLARIFY"
    if result.confidence_level == "HIGH" and result.specificity == "high":
        return "EXECUTE"
    elif result.confidence_level in ("HIGH", "MEDIUM"):
        return "KONFIRMASI"
    else:
        return "CLARIFY"


# ============================================================
# CLI INTERFACE
# ============================================================

def main():
    """CLI interface for companion."""
    if len(sys.argv) > 1:
        user_input = " ".join(sys.argv[1:])
    else:
        user_input = input("Enter instruction: ")

    result = analyze_intent(user_input)

    print(f"\n{'='*60}")
    print(f"COMPANION v5.0 - ANALYSIS RESULT")
    print(f"{'='*60}")
    print(f"Input: {result.input}")
    print(f"Keywords: {result.keywords}")
    print(f"Entities: {result.entities}")
    print(f"Specificity: {result.specificity}")
    print(f"Confidence: {result.confidence_level}")
    print(f"Action: {get_agent_action(result)}")

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


if __name__ == "__main__":
    main()
