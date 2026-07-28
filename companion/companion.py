"""
AGENTIC COMPANION LAYER v3
==============================
Full prototype with enriched Indonesian vocabulary.

Concept:
- Agent = Hunter (powerful, free to hunt)
- Companion = Chain (keeps agent safe, no overflow)

Phases:
1. REASONING - Understanding user intent
2. THINKING - Planning steps
3. PREPARING - Selecting tools
4. EXECUTING - Running actions
5. FINISHING - Delivering results
"""

import os
import sys
import json
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

# Force UTF-8
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')


# ============================================================
# DATA CLASSES
# ============================================================

class Phase:
    """Agent workflow phases."""
    REASONING = "reasoning"
    THINKING = "thinking"
    PREPARING = "preparing"
    EXECUTING = "executing"
    FINISHING = "finishing"


@dataclass
class ValidationResult:
    """Result of companion validation."""
    status: str  # "safe", "warning", "blocked"
    message: str
    details: Optional[Dict[str, Any]] = None

    def __str__(self):
        prefix = {"safe": "[SAFE]", "warning": "[WARNING]", "blocked": "[BLOCKED]"}[self.status]
        return f"{prefix} {self.message}"


@dataclass
class IntentAnalysis:
    """Result of intent analysis."""
    clarity: str  # "clear", "ambiguous", "vague"
    intent_type: str  # "single_action", "multi_action", "question", "unknown"
    keywords: List[str]
    ambiguity_notes: str = ""
    suggested_clarification: str = ""


@dataclass
class Step:
    """A planned step in execution."""
    order: int
    action: str
    tool: str
    params: str
    reason: str
    is_safe: bool = True
    overflow_risk: str = "low"


# ============================================================
# ENRICHED VOCABULARY - Indonesian & English
# ============================================================

# Intent Analyzer patterns
INTENT_PATTERNS = {
    # Security / Keamanan
    "security_keywords": [
        "keamanan", "security", "audit", "vulnerability", "vulnerabilities",
        "amankan", "selamatan", "proteksi", "protect",
        "credential", "password", "token", "secret", "api_key", "apikey",
        "enkripsi", "encryption", "auth", "authentication",
    ],

    # Search / Pencarian
    "search_keywords": [
        "cari", "find", "search", "find", "locate", "ketemu", "temukan",
        "dimana", "where", "posisi", "lokasi", "located",
        "grep", "pilih", "select",
    ],

    # Read / Baca
    "read_keywords": [
        "baca", "read", "read", "lihat", "view", "show", "tampilkan",
        "cek", "check", "inspect", "periksa",
    ],

    # Replace / Ganti
    "replace_keywords": [
        "ganti", "replace", "tukar", "exchange", "substitusi", "substitute",
        "ubah", "change", "modify", "edit", "merubah", "mengubah",
        "rename", "namai", "named",
    ],

    # Structure / Struktur
    "structure_keywords": [
        "struktur", "structure", "tree", "map", "directory", "folder",
        "arsitektur", "architecture", "layout", "organisasi", "organization",
    ],

    # Scope / Area
    "scope_keywords": [
        "scope", "area", "batass", "batasan", "limits", "limitasi",
        "di area", "terserah", "dimana saja",
    ],

    # Cleanup / Kebersihan
    "cleanup_keywords": [
        "bersihkan", "cleanup", "bersih", "clean", "kebersihan",
        "hapus sampah", "buang", "sampah", "residu", "garbage",
        "unused", "unused", "tidak terpakai", "gak terpakai",
        "hapus file", "delete", "hapus",
    ],

    # Analysis / Analisa
    "analysis_keywords": [
        "analisa", "analyze", "analysis", "cek", "overview",
        "ringkasan", "summary", "statistik", "statistics",
        "diagnosa", "diagnosis", "evaluate", "evaluasi",
    ],

    # Generate / Buat
    "generate_keywords": [
        "generate", "generate", "buat", "create", "new",
        "tambah", "add", "add", "new", "baru", "insert", "scaffolding",
        "instansi", "instance",
    ],

    # Error / Error
    "error_keywords": [
        "error", "bug", "crash", "debug", "log", "trace",
        "gagal", "failed", "failure", "masalah", "issue",
        "troubleshoot", "resolve", "perbaiki", "fix",
    ],

    # Impact / Dampak
    "impact_keywords": [
        "impact", "dampak", "effect", "effected", "affected",
        "depend", "dependency", "ketergantungan", "related",
        "terkait", "connect", "hubungkan", "usage", "pemakaian",
    ],

    # Question / Pertanyaan
    "question_keywords": [
        "apa", "what", "bagaimana", "how", "kenapa", "why",
        "siapa", "who", "dimana", "where", "kapan", "when",
        "apa itu", "what is", "jelaskan", "explain", "tolong",
    ],
}


# ============================================================
# INTENT ANALYZER
# ============================================================

class IntentAnalyzer:
    """
    Analyzes user input for clarity and intent type.
    Rich Indonesian + English vocabulary.
    """

    # Vague patterns
    VAGUE_PATTERNS = [
        r'^cek$', r'^bantu$', r'^lihat$', r'^apa$', r'^halo$',
        r'^hi$', r'^hay', r'^test', r'^coba', r'^denger',
    ]

    # Multi-action patterns
    MULTI_ACTION_PATTERNS = [
        r', terus', r', lalu', r', setelah', r' dan ',
        r'setelah itu', r'lalu ', r'kemudian',
        r'analisa.*generate', r'cek.*report', r'cleanup.*generate',
    ]

    def analyze(self, user_input: str) -> IntentAnalysis:
        """
        Analyze user input for clarity and intent type.
        """
        input_lower = user_input.lower()

        # Extract keywords
        keywords = []
        for category, kw_list in INTENT_PATTERNS.items():
            for kw in kw_list:
                if kw in input_lower:
                    if kw not in keywords:
                        keywords.append(kw)

        # Determine clarity
        clarity = "clear"
        ambiguity_notes = ""
        suggested_clarification = ""

        # Check vague patterns
        if any(re.search(p, input_lower) for p in self.VAGUE_PATTERNS):
            clarity = "vague"
            ambiguity_notes = "Input terlalu umum"
            suggested_clarification = "Spesifikasikan: 'cek keamanan', 'cari bug', 'bersihkan project', dll"

        # Check for question
        intent_type = "single_action"
        question_count = sum(1 for kw in INTENT_PATTERNS["question_keywords"] if kw in input_lower)
        if question_count > 0:
            intent_type = "question"

        # Check for multi-action
        elif any(re.search(p, input_lower) for p in self.MULTI_ACTION_PATTERNS):
            intent_type = "multi_action"

        # Check for ambiguity
        elif len(keywords) == 0:
            clarity = "ambiguous"
            ambiguity_notes = "Tidak ada keyword yang dikenali"
            suggested_clarification = "Gunakan kata kunci: cek keamanan, cari kode, ganti text, bersihkan project"

        return IntentAnalysis(
            clarity=clarity,
            intent_type=intent_type,
            keywords=keywords,
            ambiguity_notes=ambiguity_notes,
            suggested_clarification=suggested_clarification
        )


# ============================================================
# TOOL SELECTOR
# ============================================================

class ToolSelector:
    """
    Selects appropriate tools based on rich keyword mapping.
    """

    # Comprehensive keyword to tool mapping
    TOOL_MAP = {
        # Security / project_guardian
        **{kw: ("project_guardian", "--summary", "Security audit")
           for kw in INTENT_PATTERNS["security_keywords"]},

        # Search / smart_search
        **{kw: ("smart_search", "<keyword>", "Code search")
           for kw in INTENT_PATTERNS["search_keywords"]},

        # Read / selective_reader
        **{kw: ("selective_reader", "<filepath>", "File reading")
           for kw in INTENT_PATTERNS["read_keywords"]},

        # Replace / smart_replace
        **{kw: ("smart_replace", "<old> <new> --apply", "Text replacement")
           for kw in INTENT_PATTERNS["replace_keywords"]},

        # Structure / smart_tree + context_mapper
        **{kw: ("smart_tree", ". <depth>", "Directory structure")
           for kw in INTENT_PATTERNS["structure_keywords"]},

        # Scope / scope_guardian
        **{kw: ("scope_guardian", "<filepath>", "Check scope")
           for kw in INTENT_PATTERNS["scope_keywords"]},

        # Cleanup / clean_sweeper
        **{kw: ("clean_sweeper", ".", "Project cleanup")
           for kw in INTENT_PATTERNS["cleanup_keywords"]},

        # Analysis / deep_analyzer
        **{kw: ("deep_analyzer", ". --json", "Project analysis")
           for kw in INTENT_PATTERNS["analysis_keywords"]},

        # Generate / auto_scaffolder
        **{kw: ("auto_scaffolder", "<type> <name> --apply", "Generate code")
           for kw in INTENT_PATTERNS["generate_keywords"]},

        # Error / crash_decoder
        **{kw: ("crash_decoder", "<logfile>", "Decode error")
           for kw in INTENT_PATTERNS["error_keywords"]},

        # Impact / impact_analyzer
        **{kw: ("impact_analyzer", "<file> .", "Impact analysis")
           for kw in INTENT_PATTERNS["impact_keywords"]},
    }

    def select_tools(self, intent: str, keywords: List[str]) -> List[Step]:
        """
        Select appropriate tools based on keywords.
        """
        steps = []
        order = 1
        intent_lower = intent.lower()

        # Priority order for tool selection
        priority_tools = [
            ("project_guardian", INTENT_PATTERNS["security_keywords"]),
            ("smart_search", INTENT_PATTERNS["search_keywords"]),
            ("smart_replace", INTENT_PATTERNS["replace_keywords"]),
            ("selective_reader", INTENT_PATTERNS["read_keywords"]),
            ("smart_tree", INTENT_PATTERNS["structure_keywords"]),
            ("scope_guardian", INTENT_PATTERNS["scope_keywords"]),
            ("clean_sweeper", INTENT_PATTERNS["cleanup_keywords"]),
            ("deep_analyzer", INTENT_PATTERNS["analysis_keywords"]),
            ("auto_scaffolder", INTENT_PATTERNS["generate_keywords"]),
            ("crash_decoder", INTENT_PATTERNS["error_keywords"]),
            ("impact_analyzer", INTENT_PATTERNS["impact_keywords"]),
        ]

        existing_tools = set()

        for tool, kw_list in priority_tools:
            for kw in kw_list:
                if kw in intent_lower and tool not in existing_tools:
                    # Get params for this tool
                    params_map = {
                        "smart_search": "<keyword>",
                        "smart_replace": "<old> <new> --apply",
                        "selective_reader": "<filepath>",
                        "smart_tree": ". <depth>",
                        "context_mapper": "--apply",
                        "project_guardian": "--summary",
                        "clean_sweeper": ".",
                        "deep_analyzer": ". --json",
                        "auto_scaffolder": "<type> <name> --apply",
                        "crash_decoder": "<logfile>",
                        "impact_analyzer": "<file> .",
                        "scope_guardian": "<filepath>",
                    }

                    steps.append(Step(
                        order=order,
                        action=f"Execute {tool}",
                        tool=tool,
                        params=params_map.get(tool, "."),
                        reason=f"'{kw}' keyword detected"
                    ))
                    existing_tools.add(tool)
                    order += 1
                    break

        # Add context tools for multi-action
        if "analisa" in intent_lower or "report" in intent_lower or "ringkasan" in intent_lower:
            if "clean_sweeper" not in existing_tools:
                steps.append(Step(
                    order=order,
                    action="Tech debt scan",
                    tool="clean_sweeper",
                    params=".",
                    reason="Part of analysis"
                ))
                order += 1

        return steps


# ============================================================
# SCOPE VALIDATOR
# ============================================================

class ScopeValidator:
    """Validates if actions are within scope."""

    def __init__(self, project_root: str):
        self.project_root = project_root
        self.scope_file = os.path.join(project_root, '.agents', 'scope_lock.json')
        self.allowed_files: List[str] = []
        self.allowed_patterns: List[str] = []
        self.current_task: str = ""
        self._load_scope()

    def _load_scope(self):
        """Load current scope from scope_lock.json."""
        if os.path.exists(self.scope_file):
            try:
                with open(self.scope_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.current_task = data.get('task', 'Unknown')
                    self.allowed_files = data.get('allowed_files', [])
                    self.allowed_patterns = data.get('allowed_patterns', [])
            except Exception:
                pass

    def validate(self, file_path: str) -> ValidationResult:
        """Check if file operation is within scope."""
        if not self.current_task:
            return ValidationResult(
                status="warning",
                message="No scope defined. Define with scope_lock.json"
            )

        file_path = file_path.replace('\\', '/')

        for allowed in self.allowed_files:
            allowed = allowed.replace('\\', '/')
            if file_path.endswith(allowed) or allowed.endswith(file_path) or file_path == allowed:
                return ValidationResult(
                    status="safe",
                    message=f"File within scope: {self.current_task}"
                )

        import fnmatch
        for pattern in self.allowed_patterns:
            if fnmatch.fnmatch(file_path, pattern):
                return ValidationResult(
                    status="safe",
                    message="File matches allowed pattern"
                )

        return ValidationResult(
            status="blocked",
            message=f"OUT OF SCOPE for: {self.current_task}",
            details={
                "allowed_files": self.allowed_files,
                "allowed_patterns": self.allowed_patterns
            }
        )

    def set_scope(self, task: str, allowed_files: List[str], patterns: List[str] = None):
        """Manually set scope."""
        self.current_task = task
        self.allowed_files = allowed_files
        self.allowed_patterns = patterns or []


# ============================================================
# SECURITY VALIDATOR
# ============================================================

class SecurityValidator:
    """Quick security checks."""

    DANGEROUS_ACTIONS = [
        "delete", "rm ", "rmdir", "DROP TABLE", "DROP DATABASE",
        "format", "truncate", "shred",
    ]

    SENSITIVE_FILES = [
        ".env", ".key", ".pem", ".p12", ".password", ".secret",
        "credentials", ".htpasswd",
    ]

    def validate_file(self, file_path: str) -> ValidationResult:
        """Check file for security concerns."""
        filename = os.path.basename(file_path).lower()

        if filename == '.env' and 'example' not in filename:
            return ValidationResult(
                status="warning",
                message=".env file detected (may contain secrets)"
            )

        for ext in self.SENSITIVE_FILES:
            if filename.endswith(ext):
                return ValidationResult(
                    status="warning",
                    message=f"Sensitive file type: {ext}"
                )

        return ValidationResult(
            status="safe",
            message="No immediate security concerns"
        )

    def validate_action(self, action: str) -> ValidationResult:
        """Check if action is dangerous."""
        action_lower = action.lower()

        for danger in self.DANGEROUS_ACTIONS:
            if danger in action_lower:
                return ValidationResult(
                    status="blocked",
                    message=f"Dangerous action: {danger}"
                )

        return ValidationResult(
            status="safe",
            message="Action appears safe"
        )


# ============================================================
# COMPANION - Main class
# ============================================================

class AgenticCompanion:
    """
    The Chain that walks with the agent.

    Usage:
        companion = AgenticCompanion(project_root)
        intent = companion.analyze_intent(user_input)
        steps = companion.plan_execution(intent)
        companion.validate_execution(steps[0])
    """

    def __init__(self, project_root: str = None):
        self.project_root = project_root or os.getcwd()
        self.scope_validator = ScopeValidator(self.project_root)
        self.security_validator = SecurityValidator()
        self.intent_analyzer = IntentAnalyzer()
        self.tool_selector = ToolSelector()

        self.current_phase: str = None
        self.current_intent: str = ""
        self.current_steps: List[Step] = []
        self.observations: List[Dict] = []
        self.alerts: List[Dict] = []

    def analyze_intent(self, user_input: str) -> IntentAnalysis:
        """PHASE 1: Analyze user intent."""
        self.current_phase = Phase.REASONING
        self.current_intent = user_input

        result = self.intent_analyzer.analyze(user_input)

        self.observations.append({
            "phase": Phase.REASONING,
            "input": user_input,
            "result": {
                "clarity": result.clarity,
                "intent_type": result.intent_type,
                "keywords": result.keywords
            }
        })

        return result

    def ask_clarification(self, intent: IntentAnalysis) -> str:
        """Generate clarification question if vague."""
        if intent.clarity in ["vague", "ambiguous"]:
            return f"Konfirmasi: {intent.suggested_clarification}"
        return ""

    def plan_execution(self, intent: IntentAnalysis) -> List[Step]:
        """PHASE 2: Plan execution steps."""
        self.current_phase = Phase.THINKING

        steps = self.tool_selector.select_tools(
            self.current_intent,
            intent.keywords
        )

        self.current_steps = steps

        self.observations.append({
            "phase": Phase.THINKING,
            "steps_planned": len(steps),
            "tools": [s.tool for s in steps]
        })

        return steps

    def validate_plan(self, steps: List[Step]) -> ValidationResult:
        """Validate if plan is reasonable."""
        if not steps:
            return ValidationResult(
                status="warning",
                message="No tools selected. Intent may need clarification."
            )

        if len(steps) > 5:
            return ValidationResult(
                status="warning",
                message=f"Plan has {len(steps)} steps. Consider breaking into smaller tasks."
            )

        return ValidationResult(
            status="safe",
            message=f"Plan looks reasonable: {len(steps)} steps"
        )

    def prepare_step(self, step: Step) -> Dict:
        """PHASE 3: Prepare for step execution."""
        self.current_phase = Phase.PREPARING

        return {
            "ready": True,
            "tool": step.tool,
            "command": self.get_command(step),
            "companion_says": f"Ready: {step.action}"
        }

    def get_command(self, step: Step) -> str:
        """Get actual command to execute."""
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
            "context_mapper": "context_mapper/context_mapper.py",
        }

        script = script_map.get(step.tool, f"{step.tool}/main.py")
        return f"python .agents/skills/{script} {step.params}"

    def validate_execution(self, step: Step, target: str = None) -> ValidationResult:
        """PHASE 4: Validate if execution is safe."""
        self.current_phase = Phase.EXECUTING

        results = []

        action_result = self.security_validator.validate_action(step.action)
        results.append(action_result)

        if target:
            scope_result = self.scope_validator.validate(target)
            results.append(scope_result)

            file_result = self.security_validator.validate_file(target)
            results.append(file_result)

        blocked = [r for r in results if r.status == "blocked"]
        warnings = [r for r in results if r.status == "warning"]

        if blocked:
            return blocked[0]
        elif warnings:
            return warnings[0]
        else:
            return ValidationResult(
                status="safe",
                message=f"Execution approved: {step.action}"
            )

    def alert(self, message: str, details: Dict = None) -> Dict:
        """Raise an alert when overflow is detected."""
        alert = {
            "status": "alert",
            "type": "overflow_warning",
            "message": message,
            "phase": self.current_phase,
            "companion_says": f"⚠️ {message}"
        }
        if details:
            alert["details"] = details
        self.alerts.append(alert)
        return alert

    def validate_output(self, output: str, step: Step) -> ValidationResult:
        """PHASE 5: Validate output quality."""
        self.current_phase = Phase.FINISHING

        if not output or len(output.strip()) == 0:
            return ValidationResult(
                status="warning",
                message="Output is empty. Task may not have completed."
            )

        if "error" in output.lower() and "no matches" not in output.lower():
            return ValidationResult(
                status="warning",
                message="Output contains errors. Review may be needed."
            )

        return ValidationResult(
            status="safe",
            message=f"Step {step.order} completed successfully"
        )

    def finish(self) -> Dict:
        """Complete execution and summarize."""
        self.current_phase = Phase.FINISHING

        return {
            "status": "complete",
            "total_steps": len(self.current_steps),
            "alerts_raised": len(self.alerts),
            "companion_says": "Execution complete. All steps within safe bounds."
        }

    def get_session_summary(self) -> Dict:
        """Get summary of entire companion session."""
        return {
            "intent": self.current_intent,
            "steps_planned": len(self.current_steps),
            "steps": [s.tool for s in self.current_steps],
            "alerts": len(self.alerts),
        }


# ============================================================
# QUICK INTERFACE
# ============================================================

def analyze_input(user_input: str) -> IntentAnalysis:
    """Quick intent analysis."""
    companion = AgenticCompanion()
    return companion.analyze_intent(user_input)


def plan_steps(user_input: str) -> List[Step]:
    """Quick step planning."""
    companion = AgenticCompanion()
    intent = companion.analyze_intent(user_input)
    return companion.plan_execution(intent)


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("AGENTIC COMPANION v3 - Enriched Vocabulary Test")
    print("=" * 60)

    companion = AgenticCompanion()

    # Rich test cases
    test_cases = [
        # Cleanup tests
        "cek kebersihan project",
        "bersihkan project",
        "bersihin folder",
        "hapus sampah",
        "cleanup kode",

        # Security tests
        "cek keamanan",
        "security audit",
        "amankan project",

        # Search tests
        "cari bug di login",
        "where is handleSubmit",
        "find password",
        "ketemu useState",

        # Analysis tests
        "analisa project",
        "overview aplikasi",
        "statistik kode",

        # Structure tests
        "struktur folder src",
        "map direktori",
        "tampilkan tree",

        # Multi-action tests
        "analisa project, terus generate report",
        "cek keamanan lalu cleanup",

        # Question tests
        "apa itu React",
        "kenapa error",

        # Vague tests
        "cek",
        "bantu",
        "halo",
    ]

    for i, test_input in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"TEST {i}: '{test_input}'")
        print("-" * 60)

        intent = companion.analyze_intent(test_input)
        print(f"  Clarity: {intent.clarity} | Type: {intent.intent_type}")
        print(f"  Keywords: {intent.keywords[:5]}{'...' if len(intent.keywords) > 5 else ''}")

        if intent.clarity in ["vague", "ambiguous"]:
            print(f"  Clarification: {companion.ask_clarification(intent)}")

        steps = companion.plan_execution(intent)
        print(f"  Steps planned: {len(steps)}")

        for step in steps[:3]:  # Show max 3 steps
            print(f"    {step.order}. {step.tool} ({step.reason})")

    print(f"\n{'='*60}")
    print("VOCABULARY COVERAGE:")
    for category, kws in INTENT_PATTERNS.items():
        print(f"  {category}: {len(kws)} keywords")
    print(f"  TOTAL: {sum(len(v) for v in INTENT_PATTERNS.values())} keywords")
    print("=" * 60)
