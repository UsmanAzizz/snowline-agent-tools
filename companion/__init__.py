"""
COMPANION - Python Module Interface
===================================
Simple import interface untuk companion.

Usage:
    from companion import Companion

    c = Companion()
    r = c.analyze("cari import axios")
    r = c.plan("cari axios")

CLI:
    python companion/cli.py --input "cari axios"
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
    build_execution_command,
    needs_approval,
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
        result = []
        for s in steps:
            result.append({
                "tool": s.tool,
                "params": s.params,
                "reason": s.reason,
                "needs_approval": needs_approval(s.tool),
                "command": build_execution_command(s, approved=False) if s.tool != "NEEDS_CLARIFICATION" else None
            })
        return result

    def run(self, user_input: str, approved: bool = False) -> dict:
        """Full workflow with approval check.

        Args:
            user_input: User's intent
            approved: True when user confirmed (for tools that need approval
        """
        intent = analyze_intent(user_input)
        steps = plan_steps(user_input, intent)

        if not steps:
            return {"intent": intent.__dict__, "steps": [], "tool": None, "command": None}

        step = steps[0]
        tool = step.tool

        if needs_approval(tool) and not approved:
            # Tool needs approval - return preview only
            preview_cmd = build_execution_command(step, approved=False)
            return {
                "intent": intent.__dict__,
                "steps": [{"tool": tool, "command": preview_cmd}],
                "tool": tool,
                "command": preview_cmd,
                "approved": False,
                "needs_approval": True
            }

        # Approved or no approval needed - execute
        exec_cmd = build_execution_command(step, approved=approved)
        return {
            "intent": intent.__dict__,
            "steps": [{"tool": tool, "command": exec_cmd}],
            "tool": tool,
            "command": exec_cmd,
            "approved": approved
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


def run(input_str: str, approved: bool = False) -> dict:
    """Quick run with optional approval."""
    return companion.run(input_str, approved=approved)
