"""
COMPANION - Python Module Interface
===================================
Simple import interface untuk companion.

Usage:
    from companion import analyze_intent, plan_steps, get_command

    intent = analyze_intent("cari import axios")
    steps = plan_steps("cari import axios", intent)

CLI:
    python companion/cli.py --input "cari import axios"
"""

import sys
import os

# Ensure UTF-8
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Add parent directory to path
_parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

# Import from companion_core
from companion.companion_core import (
    analyze_intent,
    plan_steps,
    get_command,
    TOOL_KEYWORDS,
    NEEDS_CLARIFICATION
)


# Simple companion interface
class Companion:
    """Simple interface untuk companion layer."""

    def __init__(self, project_root=".agents/skills"):
        self.project_root = project_root

    def analyze(self, user_input: str) -> dict:
        """Analyze user input."""
        intent = analyze_intent(user_input)
        return {
            "clarity": intent.clarity,
            "intent_type": intent.intent_type,
            "keywords": intent.keywords,
            "needs_clarification": intent.needs_clarification,
            "clarification_msg": intent.clarification_msg
        }

    def plan(self, user_input: str) -> list:
        """Plan steps based on intent."""
        intent = analyze_intent(user_input)
        steps = plan_steps(user_input, intent)
        return [
            {
                "tool": s.tool,
                "params": s.params,
                "reason": s.reason,
                "needs_clarify": s.needs_clarify,
                "clarify_note": s.clarify_note,
                "command": get_command(s) if not s.needs_clarify else None
            }
            for s in steps
        ]

    def run(self, user_input: str) -> dict:
        """Full workflow: analyze + plan."""
        steps = self.plan(user_input)
        return {
            "intent": self.analyze(user_input),
            "steps": steps,
            "tool": steps[0]["tool"] if steps else None,
            "command": steps[0]["command"] if steps else None
        }


# Singleton instance
companion = Companion()


# Quick functions
def analyze(input_str: str) -> dict:
    """Quick analyze."""
    return companion.analyze(input_str)


def plan(input_str: str) -> list:
    """Quick plan."""
    return companion.plan(input_str)


def run(input_str: str) -> dict:
    """Quick run."""
    return companion.run(input_str)
