"""
TOKEN BUDGET TRACKER
========================
Monitor approximate token usage.
Estimates based on input/output character count.
"""

import time
import json
from dataclasses import dataclass
from typing import Dict, List

try:
    from .memory import memory
    HAS_MEMORY = True
except ImportError:
    HAS_MEMORY = False


@dataclass
class TokenEstimate:
    input_chars: int
    output_chars: int
    estimated_tokens: int
    timestamp: str
    session_id: str


class TokenBudget:
    """Track approximate token usage per session."""

    def __init__(self, session_id: str = "default"):
        self.session_id = session_id
        self.usage_log: List[TokenEstimate] = []
        self.start_time = time.time()
        self.budget_limit = 200_000  # Approximate limit
        self.budget_warning = 150_000

    def estimate(self, text: str) -> int:
        """Estimate tokens from character count."""
        return int(len(text) // 4)

    def record(self, input_text: str, output_text: str = "") -> TokenEstimate:
        """Record usage and return estimate."""
        estimate = TokenEstimate(
            input_chars=len(input_text),
            output_chars=len(output_text),
            estimated_tokens=self.estimate(input_text) + self.estimate(output_text),
            timestamp=time.strftime("%H:%M:%S"),
            session_id=self.session_id
        )
        self.usage_log.append(estimate)
        return estimate

    def status(self) -> Dict:
        """Get current budget status."""
        if not self.usage_log:
            return {"status": "empty", "budget_used_pct": 0}

        total = sum(e.estimated_tokens for e in self.usage_log)
        return {
            "session": self.session_id,
            "requests": len(self.usage_log),
            "budget_used": total,
            "budget_limit": self.budget_limit,
            "budget_used_pct": min(100, int(total / self.budget_limit * 100)),
            "budget_remaining": max(0, self.budget_limit - total),
            "status": "ok" if total < self.budget_warning else "warning" if total < self.budget_limit else "critical"
        }

    def reset(self):
        """Reset session."""
        self.usage_log = []
        self.start_time = time.time()


def track(input_text: str, output_text: str = "") -> TokenEstimate:
    tracker = TokenBudget()
    return tracker.record(input_text, output_text)


# CLI interface
if __name__ == "__main__":
    import sys
    tracker = TokenBudget()

    if len(sys.argv) > 1:
        if sys.argv[1] == "--status":
            print(json.dumps(tracker.status(), indent=2))
        elif sys.argv[1] == "--reset":
            tracker.reset()
            print("Budget reset!")
        elif sys.argv[1] == "--record":
            if len(sys.argv) > 2:
                text = sys.argv[2]
                result = tracker.record(text)
                print(json.dumps({
                    "input_chars": result.input_chars,
                    "estimated_tokens": result.estimated_tokens,
                    "timestamp": result.timestamp
                }, indent=2))
            else:
                print("Usage: token_budget.py --record <text>")
        else:
            print("Usage: token_budget.py [--status|--reset|--record <text>]")
    else:
        print("Usage: token_budget.py [--status|--reset|--record <text>]")
