"""
core_intent.py - Intent analysis and entity extraction.
"""
import re
from dataclasses import dataclass
from typing import List, Optional, Dict


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
    sequential_steps: List = None
    needs_clarification: bool = False
    clarification_note: Optional[str] = None
    clarification_context: Optional[Dict] = None  # Structured data for multi-tool-match ambiguity


# ============================================================
# TOOL REGISTRY
# ============================================================

TOOL_REGISTRY = {
    "smart_search": {
        "keywords": ["cari", "find", "search", "locate", "ketemu", "where", "grep", "import", "module", "dependencies", "pencarian", "mencari"],
        "confidence": "medium",
        "safety": "safe",
        "command": "python .agents/skills/smart_search/code_finder.py <dir> <keyword>"
    },
    "smart_replace": {
        "keywords": ["ganti", "replace", "tukar", "ubah", "change", "modify", "edit", "rename", "refactor", "konversi", "convert", "migration", "penggantian", "mengganti", "mengubah"],
        "confidence": "high",
        "safety": "moderate",
        "command": "python .agents/skills/smart_replace/replace_text.py <old> <new> [--apply]",
        "needs_approval": True
    },
    "selective_reader": {
        "keywords": ["baca", "read", "lihat", "view", "show", "check", "inspect", "dokumentasi", "dibaca", "membaca"],
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
        "keywords": ["analisa", "analyze", "overview", "ringkasan", "summary", "statistik", "diagnosa", "evaluasi", "inventori", "menganalisa", "menganalisis", "analisis"],
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
        "keywords": ["error", "bug", "crash", "debug", "log", "trace", "gagal", "failed", "issue", "exception"],
        "confidence": "high",
        "safety": "safe",
        "command": "python .agents/skills/crash_decoder/decoder.py <logfile>"
    },
    "clean_sweeper": {
        "keywords": ["bersih", "bersihkan", "cleanup", "clean", "hapus", "delete", "buang", "sampah", "residu", "garbage", "unused", "backup", "archive", "temporary", "tmp", "beresin", "rapikan", "membersihkan", "menghapus", "pembersihan"],
        "confidence": "medium",
        "safety": "safe",
        "command": "python .agents/skills/clean_sweeper/sweeper.py ."
    },
    "auto_scaffolder": {
        "keywords": ["generate boilerplate", "generate component", "generate instance", "scaffolding", "generate", "create instance"],
        "confidence": "high",
        "safety": "moderate",
        "command": "python .agents/skills/auto_scaffolder/scaffolder.py <type> <name> [--apply]",
        "needs_approval": True
    },
    "db_extractor": {
        "keywords": ["schema", "skema", "database", "erd", "struktur tabel", "kolom tabel", "relasi tabel"],
        "confidence": "high",
        "safety": "safe",
        "command": "python .agents/skills/db_extractor/scripts/extractor.py ."
    },
    "context_mapper": {
        "keywords": ["context mapper", "petakan project", "knowledge base", "project structure", "onboarding project", "dokumentasi arsitektur"],
        "confidence": "high",
        "safety": "moderate",
        "command": "python .agents/skills/context_mapper/context_mapper.py [--apply]",
        "needs_approval": True
    },
    "import_fixer": {
        "keywords": ["import rusak", "broken import", "fix import", "perbaiki import", "module not found", "cannot find module"],
        "confidence": "high",
        "safety": "moderate",
        "command": "python .agents/skills/import_fixer/fixer.py <source_file> <broken_import_string> [--apply]",
        "needs_approval": True
    },
}

APPROVAL_REQUIRED = {"smart_replace", "auto_scaffolder", "context_mapper", "import_fixer"}

CLARIFICATION_TRIGGERS = {
    "export": ["export", "eksport", "excel", "xlsx", "csv", "spreadsheet"],
    "pdf": ["pdf", "cetakan"],
    "diagram": ["diagram", "flowchart", "uml", "sequence"],
}

# Creation verbs: when these appear in input, they signal the user wants to CREATE something new
# (not just read/analyze/edit existing code). Used to override analysis-only tool matches.
CREATION_VERBS = [
    "tambah", "tambahkan",   # Indonesian: add/create
    "buat", "bikin", "buatin",  # Indonesian: make/create
    "create",                   # English: create
    "baru",                     # Indonesian: new (as in "something NEW" / "create new")
]


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
# ANALYZE INTENT
# ============================================================

def analyze_intent(user_input: str) -> AnalyzeResult:
    """Analyze user intent and return structured data."""
    # Import here to avoid circular import
    from .core_context import load_project_context, entity_in_context

    text = user_input.lower()

    # ---------------------------------------------------------
    # Fast-Path: _plan convention trigger
    # ---------------------------------------------------------
    if '_plan' in text:
        return AnalyzeResult(
            input=user_input,
            keywords=["_plan"],
            entities=[],
            specificity="high",
            confidence_level="HIGH",
            needs_clarification=True,
            clarification_note="PLAN_MODE_TRIGGERED: User explicitly requested a formal planning phase. Agent MUST NOT jump to implementation. 1) Grill for gaps, 2) Write PLAN_TEMPLATE.md, 3) Wait for approval."
        )

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
            if re.search(r'\b' + re.escape(kw) + r'\b', text):
                keywords_found.append(kw)
                tool_matches.append({
                    "tool": tool_name,
                    "keyword": kw,
                    "confidence": tool_info["confidence"]
                })
                break

    # Sort tool_matches by confidence: high > medium > low (before any clarify logic)
    conf_order = {"high": 0, "medium": 1, "low": 2}
    tool_matches.sort(key=lambda m: conf_order.get(m["confidence"], 2))

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
        needs_clarify = True
        clarify_note = "Multiple tools matched. Confirm intended tool."
        confidence_level = "MEDIUM"
    elif len(tool_matches) == 1:
        confidence_level = "MEDIUM"
    else:
        confidence_level = "LOW"

    # ---- Creation-verb override: defer when user wants to CREATE but only analysis tools matched ----
    # Define analysis-only tools (tools that READ/ANALYZE code, not CREATE new code)
    analysis_tools = {
        "smart_search", "deep_analyzer", "project_guardian",
        "scope_guardian", "impact_analyzer", "selective_reader",
        "smart_tree", "crash_decoder", "clean_sweeper",
        "smart_replace"
    }

    has_creation_verb = any(cv in text for cv in CREATION_VERBS)
    matched_tool_names = {m["tool"] for m in tool_matches}
    # Override: if creation verb present AND only analysis tools matched (not auto_scaffolder)
    # Note: clean_sweeper is excluded from override because "tambah bersihkan" = "do more cleanup" (not create)
    has_analysis_only = (
        matched_tool_names and
        matched_tool_names.issubset(analysis_tools) and
        "auto_scaffolder" not in matched_tool_names and
        "clean_sweeper" not in matched_tool_names
    )

    # ---- False-positive guard for "baru" (new) ----
    # "baru" in Indonesian means both "new" (creation) AND "recently" (past tense)
    # "cari file yang baru diubah" = "find recently modified files" — NOT creation intent
    # Only suppress "baru" trigger when adjacent to action verbs indicating past/recent actions
    if " baru" in text:
        action_adjacent = any(avi in text for avi in [" cari ", " ubah", " ganti", " edit", " modif", " rubah", " di", " yang ", " udah "])
        if action_adjacent:
            # "baru" likely means "recently", not "new/create" — remove from check
            creation_verbs_filtered = [cv for cv in CREATION_VERBS if cv != "baru"]
            has_creation_verb = any(cv in text for cv in creation_verbs_filtered)

    if has_creation_verb and has_analysis_only and not needs_clarify:
        needs_clarify = True
        clarify_note = (
            "Creation verb detected but only analysis tools matched. "
            "User likely wants to BUILD something new. "
            "Matched: " + ", ".join(sorted(matched_tool_names)) + ". "
            "Confirm: add new feature/component, or different intent?"
        )

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

    # Build clarification_context for multi_tool_match ambiguity (enriched data for agents)
    # Populate when clarification is needed AND at least one tool matched.
    # This exposes ALL matched tools (not just single_tool.first) so agents have complete context.
    clarification_context = None
    if needs_clarify and len(tool_matches) >= 1:
        # Intent signals from creation-verb check
        creation_verbs_in_input = [cv for cv in CREATION_VERBS if cv in text]
        clarification_context = {
            "ambiguity_type": "multi_tool_match" if len(tool_matches) >= 2 else "single_tool_conflict",
            "reason": clarify_note or "Ambiguous intent",
            "matched_tools": [
                {
                    "name": m["tool"],
                    "keyword_matched": m["keyword"],
                    "confidence": m["confidence"]
                }
                for m in tool_matches
            ],
            "intent_signals": {
                "has_creation_verb": bool(creation_verbs_in_input),
                "creation_verbs_detected": creation_verbs_in_input,
            },
            "context": {
                "entity_count": len(entities),
                "keyword_count": len(keywords_found),
                "input_word_count": len(user_input.split()),
            }
        }

    return AnalyzeResult(
        input=user_input,
        keywords=keywords_found,
        entities=entities,
        specificity=specificity,
        confidence_level=confidence_level,
        single_tool=single_tool,
        sequential_steps=[],
        needs_clarification=needs_clarify,
        clarification_note=clarify_note,
        clarification_context=clarification_context
    )
