from typing import Dict, Any, List
from dataclasses import dataclass

@dataclass
class SafetyResult:
    safe: bool
    risks: List[str]

@dataclass
class RiskScore:
    score: int
    level: str  # 'low', 'medium', 'high'

@dataclass
class Guidance:
    action: str  # 'abort', 'review', 'modify', 'proceed'
    reason: str
    suggestions: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action,
            "reason": self.reason,
            "suggestions": self.suggestions
        }

class SafetyValidator:
    """Ensures actions are safe before execution."""
    
    def validate(self, action_request: Dict[str, Any]) -> SafetyResult:
        tool_name = action_request.get("tool")
        params = action_request.get("params", {})
        
        # In a real implementation, this would perform actual validation
        # Example safety check: enforce dry_run for destructive actions
        is_dry_run = params.get("dry_run", False)
        
        risks = []
        if tool_name == "smart_replace":
            pattern = params.get("pattern", "")
            if not pattern:
                risks.append("Pattern tidak boleh kosong.")
                return SafetyResult(safe=False, risks=risks)
                
        return SafetyResult(safe=True, risks=[])

class RiskAssessor:
    """Calculates risk score (0-100) for a given action."""
    
    def score(self, action_request: Dict[str, Any]) -> RiskScore:
        tool_name = action_request.get("tool")
        params = action_request.get("params", {})
        
        score_val = 0
        if tool_name == "smart_replace" and not params.get("dry_run", False):
            score_val = 85
        else:
            score_val = 10
            
        level = "low" if score_val < 30 else "medium" if score_val < 70 else "high"
        return RiskScore(score=score_val, level=level)

class GuidanceGenerator:
    """Generates structured guidance for the agent."""
    
    def generate(self, validation: SafetyResult, risk: RiskScore) -> Guidance:
        if not validation.safe or risk.level == "high":
            return Guidance(
                action="abort",
                reason=f"Tingkat risiko tinggi ({risk.score}). {', '.join(validation.risks)}",
                suggestions=["Tambahkan parameter dry_run: true", "Kurangi scope perubahan"]
            )
        elif risk.level == "medium":
            return Guidance(
                action="review",
                reason="Terdapat potensi risiko menengah. Perlu ulasan manual sebelum melanjutkan.",
                suggestions=["Lakukan dry-run terlebih dahulu", "Periksa kembali pola regex"]
            )
        else:
            return Guidance(
                action="proceed",
                reason="Permintaan aman untuk dieksekusi.",
                suggestions=[]
            )
