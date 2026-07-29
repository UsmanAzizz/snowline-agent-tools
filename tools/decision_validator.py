"""
DECISION VALIDATOR
====================
Validate decisions before execution.
Check safety, scope, risk.
"""

import re

# Risk patterns
HIGH_RISK = [
    r"drop\s+table",
    r"drop\s+database",
    r"rm\s+-rf",
    r"sudo",
    r"chmod\s+777",
    r"eval\s*\(",
    r"exec\s*\(",
]

# Scope keywords
SCOPE_KEYWORDS = [
    "src/", "lib/", "app/", "components/",
    "routes/", "services/", "utils/",
]

# File operations
FILE_OPS = ["write_to_file", "edit", "delete", "remove"]


class DecisionCheck:
    """Result of decision check."""
    def __init__(self, risk: str, scope: str, verdict: str):
        self.risk = risk  # low/medium/high
        self.scope = scope  # in/out/unknown
        self.verdict = verdict  # proceed/caution/stop

    def __str__(self):
        return f"[{self.risk.upper()}] {self.verdict}"


class DecisionValidator:
    """Validate decisions before execution."""

    def validate(self, action: str, target: str = "") -> DecisionCheck:
        """Check decision safety."""
        risk = self._risk_level(action, target)
        scope = self._scope_check(target)
        verdict = self._verdict(risk, scope)
        return DecisionCheck(risk, scope, verdict)

    def _risk_level(self, action: str, target: str) -> str:
        action_lower = action.lower()
        if any(re.search(p, action_lower) for p in HIGH_RISK):
            return "high"
        if any(op.lower() in action_lower for op in ["write", "edit", "delete", "remove", "replace", "modify", "rename", "move", "refactor"]):
            return "medium"
        return "low"

    def _scope_check(self, target: str) -> str:
        if not target:
            return "unknown"
        return "in" if any(s in target for s in SCOPE_KEYWORDS) else "out"

    def _verdict(self, risk: str, scope: str) -> str:
        if risk == "high" or scope == "out":
            return "stop"
        if risk == "medium" or scope == "unknown":
            return "caution"
        return "proceed"


# Quick interface
def validate(action: str, target: str = "") -> str:
    dv = DecisionValidator()
    result = dv.validate(action, target)
    return str(result)


# CLI interface
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        action = sys.argv[1]
        target = sys.argv[3] if len(sys.argv) > 3 and sys.argv[2] == "--target" else ""
        validator = DecisionValidator()
        result = validator.validate(action, target)
        print(f"[{result.risk.upper()}] {result.verdict}")
        print(f"Scope: {result.scope}")
    else:
        print("Usage: decision_validator.py <action> [--target <path>]")
