"""
COMPANION - Python Module Interface v5.0
=========================================
Phase 3: Pure data processor, agent makes decisions.

Usage:
    from companion import analyze_intent, AnalyzeResult

    result = analyze_intent("cari import axios")
    print(result.confidence_level)  # "HIGH"
    print(result.single_tool.name)  # "smart_search"
"""

import sys
import os

# Ensure UTF-8
if sys.stdout.encoding != '"'"'utf-8'"'"':
    sys.stdout.reconfigure(encoding='"'"'utf-8'"'"')

# Add parent directory to path
_parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

# Import new v5.0 from companion_v2
from companion.companion_v2 import (
    AnalyzeResult,
    ToolMatch,
    analyze_intent,
    extract_entities,
    TOOL_REGISTRY,
    CLARIFICATION_TRIGGERS,
    needs_approval,
)

# Import legacy from companion_core for backward compatibility
from companion.companion_core import (
    IntentResult,
    Step,
    plan_steps,
    build_execution_command,
    get_command,
    get_params,
    learn,
    recall,
    memory_stats,
    memory,
)

# Agent Decision Matrix (for reference)
def get_agent_action(result):
    """Determine agent action based on AnalyzeResult.
    
    | Confidence | Specificity | Agent Action |
    |------------|-------------|--------------|
    | HIGH       | high        | EXECUTE      |
    | HIGH       | medium/low  | KONFIRMASI   |
    | MEDIUM     | any         | KONFIRMASI   |
    | LOW        | any         | CLARIFY      |
    | NONE       | any         | CLARIFY      |
    """
    if result.confidence_level == "HIGH" and result.specificity == "high":
        return "EXECUTE"
    elif result.confidence_level in ("HIGH", "MEDIUM"):
        return "KONFIRMASI"
    else:
        return "CLARIFY"


# Simple companion interface (backward compatible)
class Companion:
    """Simple interface untuk companion layer."""

    def __init__(self, project_root=".agents/skills"):
        self.project_root = project_root

    def analyze(self, user_input):
        """Analyze user input (v5.0 - returns AnalyzeResult)."""
        return analyze_intent(user_input)

    def plan(self, user_input):
        """Plan steps based on intent (legacy compatibility)."""
        result = analyze_intent(user_input)
        steps = plan_steps(user_input, result)
        return [
            {
                "tool": s.tool,
                "params": s.params,
                "reason": s.reason,
                "needs_approval": needs_approval(s.tool),
                "command": get_command(s) if s.tool != "NEEDS_CLARIFICATION" else None
            }
            for s in steps
        ]

    def run(self, user_input, approved=False):
        """Full workflow with approval check (legacy compatibility)."""
        result = analyze_intent(user_input)
        steps = plan_steps(user_input, result)

        if not steps:
            return {
                "input": result.input,
                "confidence": result.confidence_level,
                "specificity": result.specificity,
                "tool": None,
                "command": None
            }

        step = steps[0]
        tool = step.tool

        if needs_approval(tool) and not approved:
            preview_cmd = get_command(step)
            return {
                "input": result.input,
                "confidence": result.confidence_level,
                "specificity": result.specificity,
                "steps": [{"tool": tool, "command": preview_cmd}],
                "tool": tool,
                "command": preview_cmd,
                "approved": False,
                "needs_approval": True
            }

        exec_cmd = build_execution_command(step, approved=approved)
        return {
            "input": result.input,
            "confidence": result.confidence_level,
            "specificity": result.specificity,
            "steps": [{"tool": tool, "command": exec_cmd}],
            "tool": tool,
            "command": exec_cmd,
            "approved": approved
        }


# Singleton instance
companion = Companion()


# Quick functions
def analyze(input_str):
    """Quick analyze."""
    return companion.analyze(input_str)


def plan(input_str):
    """Quick plan."""
    return companion.plan(input_str)


def run(input_str, approved=False):
    """Quick run with optional approval."""
    return companion.run(input_str, approved=approved)


def action(input_str):
    """Get agent action for input."""
    result = analyze_intent(input_str)
    return get_agent_action(result)
