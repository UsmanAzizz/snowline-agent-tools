"""
COMPANION v5.0 - PURE DATA PROCESSOR
Phase 3: Companion sebagai data processor
"""

import re
from typing import List, Optional
from dataclasses import dataclass, field

@dataclass
class ToolMatch:
    name: str
    confidence: str
    reason: str
    command_template: str
    safety: str

@dataclass
class AnalyzeResult:
    input: str
    keywords: List[str]
    entities: List[str]
    specificity: str
    confidence_level: str
    single_tool: Optional[ToolMatch] = None
    sequential_steps: List = field(default_factory=list)
    needs_clarification: bool = False
    clarification_note: Optional[str] = None

TOOL_REGISTRY = {
    "smart_search": {"keywords": ["cari", "find", "search", "locate", "ketemu", "where", "grep", "import", "module", "dependencies"], "safety": "safe", "command_template": "python .agents/skills/smart_search/code_finder.py <dir> <keyword>"},
    "smart_replace": {"keywords": ["ganti", "replace", "tukar", "ubah", "change", "modify", "edit", "rename", "refactor", "konversi", "convert", "migration"], "safety": "moderate", "command_template": "python .agents/skills/smart_replace/replace_text.py <old> <new> [--apply]"},
    "selective_reader": {"keywords": ["baca", "read", "lihat", "view", "show", "check", "inspect", "dokumentasi"], "safety": "safe", "command_template": "python .agents/skills/selective_reader/reader.py <filepath>"},
    "smart_tree": {"keywords": ["struktur", "tree", "map", "folder", "direktori", "arsitektur", "layout"], "safety": "safe", "command_template": "python .agents/skills/smart_tree/scripts/tree_viewer.py . [depth]"},
    "scope_guardian": {"keywords": ["scope", "area", "batass", "batasan", "limits", "di area", "seluruh"], "safety": "safe", "command_template": "python .agents/skills/scope_guardian/scripts/scope_check.py <filepath>"},
    "deep_analyzer": {"keywords": ["analisa", "analyze", "overview", "ringkasan", "summary", "statistik", "diagnosa", "evaluasi", "inventori"], "safety": "safe", "command_template": "python .agents/skills/deep_analyzer/analyzer.py . --json"},
    "project_guardian": {"keywords": ["keamanan", "security", "audit", "vulnerability", "amankan", "proteksi", "credential", "password", "secret", "auth", "encryption", "credential_token"], "safety": "safe", "command_template": "python .agents/skills/project_guardian/guardian.py --summary"},
    "impact_analyzer": {"keywords": ["impact", "dampak", "effect", "affected", "depend", "dependency", "terkait", "relasi", "pemakaian"], "safety": "safe", "command_template": "python .agents/skills/impact_analyzer/analyzer.py <file> ."},
    "crash_decoder": {"keywords": ["error", "bug", "crash", "debug", "log", "trace", "gagal", "failed", "masalah", "issue", "exception", "perbaiki"], "safety": "safe", "command_template": "python .agents/skills/crash_decoder/decoder.py <logfile>"},
    "clean_sweeper": {"keywords": ["bersih", "bersihkan", "cleanup", "clean", "hapus", "delete", "buang", "sampah", "residu", "garbage", "unused", "backup", "archive", "temporary", "tmp", "beresin"], "safety": "safe", "command_template": "python .agents/skills/clean_sweeper/sweeper.py ."},
    "auto_scaffolder": {"keywords": ["generate", "generate", "buat", "create", "new", "tambah", "add", "instance", "scaffolding", "tambah component", "component baru"], "safety": "moderate", "command_template": "python .agents/skills/auto_scaffolder/scaffolder.py <type> <name> [--apply]"},
    "token_budget": {"keywords": ["token_budget", "token_usage", "kuota", "pengunaan", "efficiency", "token_limit", "token budget", "hemat token"], "safety": "safe", "command_template": "python tools/token_budget.py [--status|--reset]"},
    "context_curator": {"keywords": ["context_curator", "filter_noise", "reduce_context", "kurangi_noise", "clean_code_context", "bersihkan context", "filter noise"], "safety": "safe", "command_template": "python tools/context_curator.py <text>"},
    "output_formatter": {"keywords": ["output_formatter", "table_format", "readable", "tampilkan", "tabel", "json to table", "format json", "format table"], "safety": "safe", "command_template": "python tools/output_formatter.py <json_text> [--format table]"},
    "decision_validator": {"keywords": ["validasi", "risk_check", "safety_check", "verifikasi", "cek_keputusan", "cek risk", "safety check"], "safety": "safe", "command_template": "python tools/decision_validator.py <action> [--target <path>]"},
}

MULTI_WORD_KEYWORDS = {
    "token_budget": ["token budget", "token usage", "hemat token", "pengunaan token", "token limit", "cek token", "token efficiency"],
    "context_curator": ["bersihkan context", "filter noise", "reduce context", "kurangi noise", "bersih kan context", "clean code context", "bersihkan context ini"],
    "output_formatter": ["json to table", "format json", "format table", "tampilkan data", "format output", "ke table"],
    "decision_validator": ["cek risk", "safety check", "cek keputusan", "risk assessment", "verifikasi decision", "validasi decision"],
}

CLARIFICATION_TRIGGERS = {
    "export": {"keywords": ["export", "eksport", "excel", "xlsx", "csv", "spreadsheet"], "message": "Tool untuk export Excel/CSV belum ada."},
    "pdf": {"keywords": ["pdf", "laporan", "report", "cetakan"], "message": "Tool untuk generate PDF belum ada."},
    "diagram": {"keywords": ["diagram", "flowchart", "uml", "sequence"], "message": "Tool untuk generate diagram belum ada."},
}

def extract_entities(text):
    entities = []
    # PascalCase: HandleSubmit
    entities.extend(re.findall(r'[A-Z][a-z]+', text))
    # Remove duplicates and short words
    entities = list(set([e for e in entities if len(e) > 2]))
    return entities


def analyze_intent(user_input):
    text = user_input.lower()
    keywords = _extract_keywords(text)
    entities = extract_entities(user_input)
    clarification_note = _check_clarification(text)
    needs_clarification = clarification_note is not None
    tool_matches = _match_tools(text, keywords)
    specificity = _determine_specificity(tool_matches, keywords, entities)
    confidence_level = _determine_confidence(tool_matches, keywords, needs_clarification, entities)
    single_tool, sequential_steps = _build_tool_signals(tool_matches)
    return AnalyzeResult(input=user_input, keywords=keywords, entities=entities, specificity=specificity, confidence_level=confidence_level, single_tool=single_tool, sequential_steps=sequential_steps, needs_clarification=needs_clarification, clarification_note=clarification_note)

def _extract_keywords(text):
    keywords = []
    for tool, multi_kws in MULTI_WORD_KEYWORDS.items():
        for kw in multi_kws:
            if kw in text:
                keywords.append(kw)
                break
    for tool, tool_info in TOOL_REGISTRY.items():
        for kw in tool_info["keywords"]:
            if kw in text:
                keywords.append(kw)
                break
    return keywords

def _check_clarification(text):
    for key, info in CLARIFICATION_TRIGGERS.items():
        for kw in info["keywords"]:
            if kw in text:
                return info["message"]
    return None

def _match_tools(text, keywords):
    matches = []
    for tool_name, tool_info in TOOL_REGISTRY.items():
        match_count = 0
        matched_kws = []
        for kw in tool_info["keywords"]:
            if kw in text:
                match_count += 1
                matched_kws.append(kw)
        if match_count > 0:
            matches.append({"tool": tool_name, "match_count": match_count, "matched_keywords": matched_kws, "safety": tool_info["safety"], "command_template": tool_info["command_template"]})
    return matches

def _determine_specificity(matches, keywords, entities):
    if matches and entities:
        return "high"
    if len(matches) >= 2:
        return "medium"
    if entities and not matches:
        return "medium"
    return "low"

def _determine_confidence(matches, keywords, needs_clarification, entities):
    if needs_clarification:
        return "NONE"
    if not matches:
        return "LOW"
    
    num_tools = len(matches)
    
    if num_tools >= 2:
        return "LOW"
    
    best = matches[0]
    match_count = best["match_count"]
    
    if match_count >= 2 and entities:
        return "HIGH"
    elif match_count >= 2:
        return "HIGH"
    elif match_count == 1 and entities:
        return "HIGH"
    else:
        return "MEDIUM"

def _build_tool_signals(matches):
    if not matches:
        return None, []
    sorted_matches = sorted(matches, key=lambda x: x["match_count"], reverse=True)
    best = sorted_matches[0]
    
    if len(matches) >= 2:
        confidence = "low"
    elif best["match_count"] >= 2:
        confidence = "high"
    else:
        confidence = "medium"
    
    single_tool = ToolMatch(name=best["tool"], confidence=confidence, reason="Matched: " + ", ".join(best["matched_keywords"]), command_template=best["command_template"], safety=best["safety"])
    
    sequential = []
    if len(sorted_matches) > 1 and sorted_matches[0]["match_count"] == sorted_matches[1]["match_count"]:
        for m in sorted_matches[:3]:
            conf = "medium"
            sequential.append(ToolMatch(name=m["tool"], confidence=conf, reason="Matched: " + ", ".join(m["matched_keywords"]), command_template=m["command_template"], safety=m["safety"]))
    
    return single_tool, sequential

def needs_approval(tool_name):
    return tool_name in ["smart_replace", "auto_scaffolder", "context_mapper", "import_fixer"]
