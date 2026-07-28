"""
AGENTIC COMPANION LAYER
========================
A thin layer that walks with the agent through every phase:
Reasoning → Thinking → Preparing → Executing → Finishing

Concept:
- Agent = Hunter (powerful, free to hunt)
- Companion = Chain (keeps agent safe, no overflow)
- "No restrict, but no overflow"

The companion is NOT:
- A replacement for the agent
- A complex AI system
- A blocker that stops everything

The companion IS:
- A watcher at every phase
- A validator for security and scope
- A thin layer that adds safety without adding friction
"""

import os
import sys
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

# Force UTF-8
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')


# ============================================================
# PHASES - Agent workflow phases
# ============================================================

class Phase:
    """Agent workflow phases that companion walks through."""
    REASONING = "reasoning"    # Understanding user intent
    THINKING = "thinking"       # Planning steps
    PREPARING = "preparing"     # Selecting tools
    EXECUTING = "executing"   # Running actions
    FINISHING = "finishing"    # Delivering results


# ============================================================
# VALIDATORS - Companion checks
# ============================================================

@dataclass
class ValidationResult:
    """Result of companion validation."""
    status: str  # "safe", "warning", "blocked"
    message: str
    details: Optional[Dict[str, Any]] = None

    def __str__(self):
        if self.status == "safe":
            return f"[SAFE] {self.message}"
        elif self.status == "warning":
            return f"[WARNING] {self.message}"
        else:
            return f"[BLOCKED] {self.message}"


class ScopeValidator:
    """
    Validates if actions are within scope.
    Based on scope_guardian concept.
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
        """
        Check if a file operation is within scope.

        Returns:
        - safe: File is in allowed scope
        - warning: File is near scope boundary
        - blocked: File is completely out of scope
        """
        # Normalize path
        file_path = file_path.replace('\\', '/')

        # Check exact matches
        for allowed in self.allowed_files:
            allowed = allowed.replace('\\', '/')
            if file_path.endswith(allowed) or allowed.endswith(file_path) or file_path == allowed:
                return ValidationResult(
                    status="safe",
                    message=f"File '{os.path.basename(file_path)}' is within scope for task: {self.current_task}"
                )

        # Check pattern matches
        import fnmatch
        for pattern in self.allowed_patterns:
            if fnmatch.fnmatch(file_path, pattern):
                return ValidationResult(
                    status="safe",
                    message=f"File matches allowed pattern '{pattern}'"
                )

        # No match found - BLOCKED
        return ValidationResult(
            status="blocked",
            message=f"File '{file_path}' is OUT OF SCOPE",
            details={
                "task": self.current_task,
                "allowed_files": self.allowed_files,
                "allowed_patterns": self.allowed_patterns
            }
        )


class SecurityValidator:
    """
    Quick security checks based on project_guardian patterns.
    """

    # Sensitive patterns that need attention
    SENSITIVE_PATTERNS = [
        ("password", "Hardcoded password detected"),
        ("api_key", "API key in code detected"),
        ("secret", "Secret token detected"),
        ("Bearer ", "Exposed bearer token"),
        (".env", ".env file reference"),
    ]

    def validate_file(self, file_path: str, content: str = None) -> ValidationResult:
        """
        Quick check if file contains sensitive data.

        Note: This is a quick check. Full scan uses project_guardian.
        """
        # Check filename first (faster)
        filename = os.path.basename(file_path).lower()

        if filename == '.env' and 'example' not in filename:
            return ValidationResult(
                status="warning",
                message=".env file detected (may contain secrets)"
            )

        # Check for suspicious extensions
        suspicious_extensions = ['.env', '.key', '.pem', '.p12']
        for ext in suspicious_extensions:
            if filename.endswith(ext):
                return ValidationResult(
                    status="warning",
                    message=f"Sensitive file type detected: {ext}"
                )

        # Check content if provided
        if content:
            for pattern, message in self.SENSITIVE_PATTERNS:
                if pattern in content:
                    # Check if it's a real exposure or just code mentioning it
                    if 'password' in content.lower() and ('example' in content.lower() or 'dummy' in content.lower()):
                        continue  # Probably a test/example
                    return ValidationResult(
                        status="warning",
                        message=message,
                        details={"pattern": pattern}
                    )

        return ValidationResult(
            status="safe",
            message="No immediate security concerns detected"
        )


# ============================================================
# COMPANION - Main class
# ============================================================

class AgenticCompanion:
    """
    The Chain that walks with the agent.

    Role:
    - Watches agent at every phase
    - Validates actions
    - Alerts if overflow detected
    - Keeps agent safe without restricting

    Usage:
        companion = AgenticCompanion(project_root)

        # Agent starts reasoning
        companion.observe(Phase.REASONING, {"intent": "fix bug"})

        # Agent wants to execute something
        result = companion.check_execute(file_path="src/bug.js")
        if result.status == "blocked":
            companion.alert("Cannot proceed: out of scope")
    """

    def __init__(self, project_root: str = None):
        self.project_root = project_root or os.getcwd()
        self.scope_validator = ScopeValidator(self.project_root)
        self.security_validator = SecurityValidator()

        # Phase tracking
        self.current_phase: str = None
        self.phase_history: List[Dict] = []

        # Observation logs
        self.observations: List[str] = []

    def observe(self, phase: str, context: Dict[str, Any]):
        """
        Agent reports what it's doing at current phase.
        Companion simply observes and logs.
        """
        self.current_phase = phase
        observation = f"[{phase.upper()}] {context}"
        self.observations.append(observation)

        return {
            "status": "observed",
            "phase": phase,
            "companion_says": "I'm with you."
        }

    def check_execute(self, action: str, target: str = None, context: str = None) -> ValidationResult:
        """
        Agent asks: "Can I do this action?"

        Companion checks:
        1. Is target within scope?
        2. Any security concerns?
        """
        results = []

        # Check scope if target provided
        if target:
            scope_result = self.scope_validator.validate(target)
            results.append(scope_result)

            # Also check security
            if scope_result.status == "safe":
                security_result = self.security_validator.validate_file(target)
                results.append(security_result)

        # Determine overall status
        blocked = [r for r in results if r.status == "blocked"]
        warnings = [r for r in results if r.status == "warning"]

        if blocked:
            return blocked[0]  # Return first block
        elif warnings:
            return warnings[0]  # Return first warning
        else:
            return ValidationResult(
                status="safe",
                message=f"Action '{action}' approved. Proceed."
            )

    def alert(self, message: str, details: Dict = None):
        """
        Companion raises an alert.
        Used when agent is about to overflow.
        """
        return {
            "status": "alert",
            "message": message,
            "companion_says": f"⚠️ {message}",
            "details": details
        }

    def guide(self, intent: str) -> List[Dict]:
        """
        Given a user intent, companion suggests steps/tools.

        This is the "Smart Translator" capability.
        """
        suggestions = []

        # Simple rule-based suggestions
        intent_lower = intent.lower()

        if any(word in intent_lower for word in ['keamanan', 'security', 'audit', 'vulnerability']):
            suggestions.append({
                "step": 1,
                "action": "Security audit",
                "tool": "project_guardian",
                "suggested_params": "--summary",
                "reason": "Security check detected"
            })

        if any(word in intent_lower for word in ['cari', 'find', 'search', 'where is']):
            # Extract keyword if possible
            suggestions.append({
                "step": 2,
                "action": "Search code",
                "tool": "smart_search",
                "suggested_params": "<keyword>",
                "reason": "Search operation detected"
            })

        if any(word in intent_lower for word in ['struktur', 'map', 'tree', 'directory']):
            suggestions.append({
                "step": 3,
                "action": "Map directory structure",
                "tool": "smart_tree",
                "suggested_params": ". <depth>",
                "reason": "Structure visualization detected"
            })

        if any(word in intent_lower for word in ['baca', 'read', 'file', 'content']):
            suggestions.append({
                "step": 4,
                "action": "Extract file TOC",
                "tool": "selective_reader",
                "suggested_params": "<filepath>",
                "reason": "File reading detected"
            })

        if any(word in intent_lower for word in ['ganti', 'replace', 'ubah']):
            suggestions.append({
                "step": 5,
                "action": "Replace text",
                "tool": "smart_replace",
                "suggested_params": "<search> <replace> --apply",
                "reason": "Replace operation detected"
            })

        return suggestions

    def get_status(self) -> Dict:
        """Get companion status."""
        return {
            "current_phase": self.current_phase,
            "observations_count": len(self.observations),
            "scope_loaded": bool(self.scope_validator.current_task),
            "project_root": self.project_root
        }


# ============================================================
# QUICK INTERFACE - Simple functions for agent use
# ============================================================

def quick_guide(intent: str) -> List[Dict]:
    """Quick guide from user intent."""
    companion = AgenticCompanion()
    return companion.guide(intent)


def quick_check(action: str, target: str = None) -> str:
    """Quick check if action is safe."""
    companion = AgenticCompanion()
    result = companion.check_execute(action, target)
    return str(result)


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("AGENTIC COMPANION LAYER - Quick Test")
    print("=" * 60)

    companion = AgenticCompanion()

    print("\n1. STATUS:")
    print(json.dumps(companion.get_status(), indent=2))

    print("\n2. GUIDE - 'cek keamanan project':")
    suggestions = companion.guide("cek keamanan project")
    for s in suggestions:
        print(f"   Step {s['step']}: {s['tool']} - {s['reason']}")

    print("\n3. CHECK - Action 'delete file':")
    result = companion.check_execute("delete file", "src/test.js")
    print(f"   {result}")

    print("\n" + "=" * 60)
    print("Companion ready. Agent can proceed.")
    print("=" * 60)
