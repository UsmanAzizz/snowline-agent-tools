"""
COMPANION - Python Module Interface
===================================
Simple import interface untuk companion.

Usage:
    from companion import analyze_intent, plan_steps

    # Using functions directly
    intent = analyze_intent("cari import axios")
    steps = plan_steps("cari import axios", intent)

    # Using class interface
    from companion.companion_core import Executor
    executor = Executor()

    # CLI
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

# Import using full module path
from companion.companion_core import (
    analyze_intent,
    plan_steps,
    get_command,
    learn,
    recall,
    memory_stats,
    TOOL_KEYWORDS,
    MULTI_WORD_KEYWORDS,
    NEEDS_CLARIFICATION
)
from companion.executor import Executor
from companion.memory import memory


class Companion:
    """
    Simple interface untuk companion layer.
    """

    def __init__(self, project_root="."):
        self.executor = Executor(project_root)
        self.last_intent = None
        self.last_steps = []

    def analyze(self, user_input: str) -> dict:
        """
        Analyze user input dan return intent.

        Returns:
            dict dengan keys:
            - clarity: str
            - intent_type: str
            - keywords: list
            - needs_clarification: bool
        """
        self.last_intent = analyze_intent(user_input)
        return {
            "clarity": self.last_intent.clarity,
            "intent_type": self.last_intent.intent_type,
            "keywords": self.last_intent.keywords,
            "needs_clarification": self.last_intent.needs_clarification,
            "clarification_msg": self.last_intent.clarification_msg
        }

    def plan(self, user_input: str = None) -> list:
        """
        Plan steps based on intent.

        Args:
            user_input: Optional. If provided, will analyze first.

        Returns:
            List of step dicts dengan keys:
            - tool, params, reason, needs_clarify, command
        """
        if user_input:
            self.analyze(user_input)

        if not self.last_intent:
            return []

        self.last_steps = plan_steps(user_input or "", self.last_intent)
        return [
            {
                "tool": s.tool,
                "params": s.params,
                "reason": s.reason,
                "needs_clarify": s.needs_clarify,
                "clarify_note": s.clarify_note,
                "command": get_command(s) if not s.needs_clarify else None
            }
            for s in self.last_steps
        ]

    def execute(self, step_index: int = 0) -> dict:
        """
        Execute a step.

        Args:
            step_index: Index of step to execute (default: 0)

        Returns:
            dict dengan keys:
            - success, tool, output, error, duration_ms
        """
        if not self.last_steps:
            return {"error": "No steps planned. Call plan() first."}

        if step_index >= len(self.last_steps):
            return {"error": f"Step {step_index} not found."}

        step = self.last_steps[step_index]
        if step.needs_clarify:
            return {
                "success": False,
                "tool": step.tool,
                "error": f"Needs clarification: {step.clarify_note}"
            }

        result = self.executor.execute_step(step)

        # Learn from result
        if self.last_intent:
            learn(
                getattr(self.last_intent, 'intent', ''),
                self.last_intent.keywords,
                step.tool,
                result.success
            )

        return {
            "success": result.success,
            "tool": result.tool,
            "output": result.output,
            "error": result.error,
            "duration_ms": result.duration_ms
        }

    def run(self, user_input: str, execute: bool = True) -> dict:
        """
        Full workflow: analyze + plan + (optional) execute.

        Args:
            user_input: User's request
            execute: If True, executes the first step

        Returns:
            dict dengan:
            - intent, steps, command, result
        """
        steps = self.plan(user_input)

        result = {"error": None, "output": None}
        if execute and steps and not steps[0].get("needs_clarify"):
            result = self.execute(0)

        return {
            "intent": self.analyze(user_input),
            "steps": steps,
            "tool": steps[0]["tool"] if steps else None,
            "command": steps[0]["command"] if steps else None,
            "result": result
        }

    def suggest(self) -> str:
        """
        Get suggestion based on memory.

        Returns:
            str: Tool suggestion or empty string
        """
        if not self.last_intent:
            return ""
        return recall("", self.last_intent.keywords)

    def stats(self) -> dict:
        """Get memory statistics."""
        return memory_stats()


# Singleton instance
companion = Companion()


# Quick functions
def analyze(input_str: str) -> dict:
    """Quick analyze."""
    return companion.analyze(input_str)


def plan(input_str: str) -> list:
    """Quick plan."""
    return companion.plan(input_str)


def run(input_str: str, execute: bool = False) -> dict:
    """Quick run."""
    return companion.run(input_str, execute)
