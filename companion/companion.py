"""
AGENTIC COMPANION LAYER v2
==============================
Full prototype that walks with agent through all phases.

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
from typing import Dict, List, Optional, Any, Tuple
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
# INTENT ANALYZER
# ============================================================

class IntentAnalyzer:
    """
    Analyzes user input to determine clarity and intent type.

    Companion Layer 1: Smart Translator foundation
    """

    # Intent patterns
    SINGLE_ACTION = [
        r'cek\s+(keamanan|struktur|scope|file)',
        r'cari\s+\w+',
        r'ganti\s+\w+\s+jadi\s+\w+',
        r'baca\s+\w+',
        r'fix|perbaiki|bug',
        r'delete|hapus|buat\s+file',
    ]

    MULTI_ACTION = [
        r', terus|dan|setelah itu',
        r'setelah\s+',
        r'lalu',
        r'analisa.*generate',
        r'cek.*report',
    ]

    QUESTION = [
        r'^apa\b',
        r'^bagaimana\b',
        r'^kenapa\b',
        r'^berapa\b',
        r'apa itu',
        r'tolong jelaskan',
    ]

    VAGUE = [
        r'^cek\b',
        r'^bantu',
        r'^lihat',
        r'^apa aja',
        r'semua',
    ]

    def analyze(self, user_input: str) -> IntentAnalysis:
        """
        Analyze user input for clarity and intent type.
        """
        input_lower = user_input.lower()

        # Extract keywords
        keywords = []
        keyword_patterns = [
            'keamanan', 'security', 'audit',
            'cari', 'find', 'search',
            'ganti', 'replace', 'ubah',
            'baca', 'read', 'file',
            'struktur', 'tree', 'map',
            'scope', 'area',
            'bug', 'error', 'fix',
            'cleanup', 'bersihkan',
            'generate', 'buat', 'create',
        ]

        for kw in keyword_patterns:
            if kw in input_lower:
                keywords.append(kw)

        # Determine clarity
        clarity = "clear"
        ambiguity_notes = ""
        suggested_clarification = ""

        if any(re.search(p, input_lower) for p in self.VAGUE):
            clarity = "vague"
            ambiguity_notes = "Input terlalu umum"
            suggested_clarification = "Spesifikasikan apa yang mau dicek/dilakukan"

        # Check for multi-action
        intent_type = "single_action"
        if any(re.search(p, user_input) for p in self.MULTI_ACTION):
            intent_type = "multi_action"

        # Check for question
        if any(re.search(p, user_input, re.IGNORECASE) for p in self.QUESTION):
            intent_type = "question"

        # Check for ambiguity
        if len(keywords) == 0:
            clarity = "ambiguous"
            ambiguity_notes = "Tidak ada keyword yang dikenali"
            suggested_clarification = "Gunakan kata kunci: cek keamanan, cari kode, ganti text, dll"

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
    Selects appropriate tools based on intent.

    Companion Layer 1: Smart Translator
    """

    # Tool mapping based on keywords
    TOOL_MAP = {
        # Security
        "keamanan": ("project_guardian", "--summary", "Security audit"),
        "security": ("project_guardian", "--summary", "Security check"),
        "audit": ("project_guardian", "--summary", "Project audit"),
        "vulnerability": ("project_guardian", "", "Vulnerability scan"),

        # Search
        "cari": ("smart_search", "<keyword>", "Code search"),
        "find": ("smart_search", "<keyword>", "Find code"),
        "search": ("smart_search", "<keyword>", "Search operation"),
        "where is": ("smart_search", "<target>", "Locate code"),

        # File reading
        "baca": ("selective_reader", "<filepath>", "File reading"),
        "read": ("selective_reader", "<filepath>", "Read file"),
        "file": ("selective_reader", "<filepath>", "File content"),
        "toc": ("selective_reader", "<filepath>", "Extract TOC"),

        # Structure
        "struktur": ("smart_tree", ". <depth>", "Directory structure"),
        "tree": ("smart_tree", ". <depth>", "Tree view"),
        "map": ("context_mapper", "--apply", "Build knowledge map"),
        "directory": ("smart_tree", ". <depth>", "Folder structure"),

        # Replace
        "ganti": ("smart_replace", "<old> <new> --apply", "Text replacement"),
        "replace": ("smart_replace", "<old> <new> --apply", "Replace operation"),
        "ubah": ("smart_replace", "<old> <new> --apply", "Modify text"),

        # Cleanup
        "bersihkan": ("clean_sweeper", ".", "Project cleanup"),
        "cleanup": ("clean_sweeper", ".", "Tech debt scan"),
        "residu": ("clean_sweeper", ".", "Find residue"),
        "garbage": ("clean_sweeper", ".", "Scan garbage"),

        # Scope
        "scope": ("scope_guardian", "<filepath>", "Check scope"),
        "area": ("scope_guardian", "<filepath>", "Validate area"),

        # Analysis
        "analisa": ("deep_analyzer", ". --json", "Project analysis"),
        "impact": ("impact_analyzer", "<file> .", "Impact analysis"),

        # Generate
        "generate": ("auto_scaffolder", "<type> <name> --apply", "Generate code"),
        "buat": ("auto_scaffolder", "<type> <name> --apply", "Create new"),
        "create": ("auto_scaffolder", "<type> <name> --apply", "Generate boilerplate"),

        # Error
        "error": ("crash_decoder", "<logfile>", "Decode error"),
        "crash": ("crash_decoder", "<logfile>", "Crash analysis"),
        "debug": ("crash_decoder", "<logfile>", "Debug log"),
        "log": ("crash_decoder", "<logfile>", "Parse logs"),

        # Health
        "kesehatan": ("project_guardian", "--summary", "Health check"),
        "health": ("project_guardian", "--summary", "Project health"),
    }

    def select_tools(self, intent: str, keywords: List[str]) -> List[Step]:
        """
        Select appropriate tools based on keywords.

        Returns list of steps with order.
        """
        steps = []
        order = 1

        # Priority order for tool selection
        priority_keywords = [
            "keamanan", "security", "vulnerability",
            "cari", "find", "search",
            "ganti", "replace", "ubah",
            "baca", "read", "file",
            "struktur", "tree", "map",
            "scope", "area",
            "bersihkan", "cleanup", "residu",
            "analisa", "impact",
            "generate", "buat", "create",
            "error", "crash", "debug",
        ]

        # Process keywords in priority order
        for keyword in priority_keywords:
            if keyword in intent.lower():
                tool_info = self.TOOL_MAP.get(keyword)
                if tool_info:
                    tool, params, reason = tool_info

                    # Check if tool already added
                    existing = [s.tool for s in steps]
                    if tool not in existing:
                        steps.append(Step(
                            order=order,
                            action=reason,
                            tool=tool,
                            params=params,
                            reason=f"'{keyword}' detected"
                        ))
                        order += 1

        # Add context tools if multi-action
        if "analisa" in intent.lower() or "report" in intent.lower():
            if "clean_sweeper" not in [s.tool for s in steps]:
                steps.append(Step(
                    order=order,
                    action="Tech debt scan",
                    tool="clean_sweeper",
                    params=".",
                    reason="Part of analysis"
                ))

        return steps


# ============================================================
# SCOPE VALIDATOR
# ============================================================

class ScopeValidator:
    """
    Validates if actions are within scope.
    """

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
        if not self.current_task:  # No scope defined
            return ValidationResult(
                status="warning",
                message="No scope defined. Define with scope_lock.json"
            )

        file_path = file_path.replace('\\', '/')

        # Check exact matches
        for allowed in self.allowed_files:
            allowed = allowed.replace('\\', '/')
            if file_path.endswith(allowed) or allowed.endswith(file_path) or file_path == allowed:
                return ValidationResult(
                    status="safe",
                    message=f"File within scope: {self.current_task}"
                )

        # Check pattern matches
        import fnmatch
        for pattern in self.allowed_patterns:
            if fnmatch.fnmatch(file_path, pattern):
                return ValidationResult(
                    status="safe",
                    message=f"File matches allowed pattern"
                )

        # Out of scope
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
    """
    Quick security checks.
    """

    SENSITIVE_PATTERNS = [
        ("password", "Hardcoded password"),
        ("api_key", "API key detected"),
        ("secret", "Secret token"),
        ("Bearer ", "Bearer token"),
    ]

    DANGEROUS_ACTIONS = [
        "delete",
        "rm ",
        "rmdir",
        "DROP TABLE",
        "DROP DATABASE",
    ]

    def validate_file(self, file_path: str) -> ValidationResult:
        """Check file for security concerns."""
        filename = os.path.basename(file_path).lower()

        # Check for sensitive files
        if filename == '.env' and 'example' not in filename:
            return ValidationResult(
                status="warning",
                message=".env file detected (may contain secrets)"
            )

        suspicious_extensions = ['.env', '.key', '.pem', '.p12', '.password']
        for ext in suspicious_extensions:
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
                    message=f"Dangerous action detected: {danger}",
                    details={"action": action}
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

        # Agent receives user input
        intent_analysis = companion.analyze_intent(user_input)
        if intent_analysis.clarity == "vague":
            companion.ask_clarification(intent_analysis)

        # Agent plans execution
        steps = companion.plan_execution(intent_analysis)

        # Agent executes each step
        for step in steps:
            companion.prepare(step)
            companion.check_safe(step)
            companion.execute(step)

        # Agent finishes
        companion.finish()
    """

    def __init__(self, project_root: str = None):
        self.project_root = project_root or os.getcwd()
        self.scope_validator = ScopeValidator(self.project_root)
        self.security_validator = SecurityValidator()
        self.intent_analyzer = IntentAnalyzer()
        self.tool_selector = ToolSelector()

        # State
        self.current_phase: str = None
        self.current_intent: str = ""
        self.current_steps: List[Step] = []
        self.observations: List[Dict] = []
        self.alerts: List[Dict] = []

    # --------------------------------------------------------
    # PHASE 1: REASONING
    # --------------------------------------------------------

    def analyze_intent(self, user_input: str) -> IntentAnalysis:
        """
        PHASE 1: Analyze user intent.
        Is the request clear? What does user want?
        """
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
        """
        Generate clarification question if intent is vague.
        """
        if intent.clarity in ["vague", "ambiguous"]:
            return f"Konfirmasi: {intent.suggested_clarification}. Contoh: 'cek keamanan project' atau 'cari bug di login'."
        return ""

    # --------------------------------------------------------
    # PHASE 2: THINKING
    # --------------------------------------------------------

    def plan_execution(self, intent: IntentAnalysis) -> List[Step]:
        """
        PHASE 2: Plan execution steps.
        What tools should be used? In what order?
        """
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
        """
        Validate if the plan is reasonable.
        """
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

    # --------------------------------------------------------
    # PHASE 3: PREPARING
    # --------------------------------------------------------

    def prepare_step(self, step: Step) -> Dict:
        """
        PHASE 3: Prepare for step execution.
        What parameters are needed?
        """
        self.current_phase = Phase.PREPARING

        return {
            "ready": True,
            "tool": step.tool,
            "command": f"python .agents/skills/{step.tool}/script.py {step.params}",
            "companion_says": f"Ready to execute: {step.action} with {step.tool}"
        }

    def get_command(self, step: Step) -> str:
        """
        Get the actual command to execute.
        """
        # Map tool to actual script path
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

    # --------------------------------------------------------
    # PHASE 4: EXECUTING
    # --------------------------------------------------------

    def validate_execution(self, step: Step, target: str = None) -> ValidationResult:
        """
        PHASE 4: Validate if execution is safe.
        Check scope and security.
        """
        self.current_phase = Phase.EXECUTING

        results = []

        # Check action safety
        action_result = self.security_validator.validate_action(step.action)
        results.append(action_result)

        # Check scope if target provided
        if target:
            scope_result = self.scope_validator.validate(target)
            results.append(scope_result)

            # Check file security
            file_result = self.security_validator.validate_file(target)
            results.append(file_result)

        # Determine overall status
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
        """
        Raise an alert when overflow is detected.
        """
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

    # --------------------------------------------------------
    # PHASE 5: FINISHING
    # --------------------------------------------------------

    def validate_output(self, output: str, step: Step) -> ValidationResult:
        """
        PHASE 5: Validate output quality.
        """
        self.current_phase = Phase.FINISHING

        # Basic checks
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
        """
        Complete execution and summarize.
        """
        self.current_phase = Phase.FINISHING

        return {
            "status": "complete",
            "total_steps": len(self.current_steps),
            "steps_completed": len([o for o in self.observations if o["phase"] == Phase.EXECUTING]),
            "alerts_raised": len(self.alerts),
            "companion_says": "Execution complete. All steps within safe bounds."
        }

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    def get_session_summary(self) -> Dict:
        """Get summary of entire companion session."""
        return {
            "intent": self.current_intent,
            "clarity": self.intent_analyzer.analyze(self.current_intent).clarity if self.current_intent else "unknown",
            "steps_planned": len(self.current_steps),
            "steps": [s.tool for s in self.current_steps],
            "alerts": len(self.alerts),
            "observations": len(self.observations)
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
    print("AGENTIC COMPANION v2 - Full Test")
    print("=" * 60)

    companion = AgenticCompanion()

    # Test cases
    test_cases = [
        "cek keamanan project",
        "cari bug di login",
        "ganti handleSubmit jadi handleFormSubmit",
        "analisa project, terus generate report",
        "cek",  # vague
        "apa itu React?",  # question
    ]

    for i, test_input in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"TEST {i}: '{test_input}'")
        print("-" * 60)

        # PHASE 1: Reasoning
        intent = companion.analyze_intent(test_input)
        print(f"  [REASONING] Clarity: {intent.clarity}")
        print(f"  [REASONING] Type: {intent.intent_type}")
        print(f"  [REASONING] Keywords: {intent.keywords}")

        if intent.clarity == "vague":
            print(f"  [REASONING] Clarification: {companion.ask_clarification(intent)}")

        # PHASE 2: Thinking
        steps = companion.plan_execution(intent)
        print(f"  [THINKING] Steps planned: {len(steps)}")

        for step in steps:
            cmd = companion.get_command(step)
            print(f"    Step {step.order}: {step.tool} -> {cmd}")

        plan_validation = companion.validate_plan(steps)
        print(f"  [THINKING] Plan validation: {plan_validation}")

        # PHASE 4: Validate execution
        if steps:
            first_step = steps[0]
            execution_check = companion.validate_execution(first_step)
            print(f"  [EXECUTING] First step validation: {execution_check}")

    print(f"\n{'='*60}")
    print("SESSION SUMMARY:")
    print(json.dumps(companion.get_session_summary(), indent=2))
    print("=" * 60)
