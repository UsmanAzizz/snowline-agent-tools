"""
EXECUTOR - Run commands automatically
==================================
Takes planned steps and executes them.
"""

import subprocess
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class ExecutionResult:
    success: bool
    tool: str
    output: str
    error: Optional[str] = None
    duration_ms: float = 0


class Executor:
    """
    Executes planned steps and returns structured results.
    """

    def __init__(self, project_root: str = "."):
        self.project_root = project_root

    def execute_step(self, step) -> ExecutionResult:
        """Execute single step and return result."""
        import time
        start = time.time()

        # Build command
        if step.tool == "NEEDS_CLARIFICATION":
            return ExecutionResult(
                success=False,
                tool=step.tool,
                output="",
                error=f"Manual step needed: {step.clarify_note}"
            )

        # Map tool to script path
        script_map = {
            "project_guardian": "project_guardian/guardian.py",
            "smart_search": "smart_search/code_finder.py",
            "smart_replace": "smart_replace/replace_text.py",
            "selective_reader": "selective_reader/reader.py",
            "smart_tree": "smart_tree/scripts/tree_viewer.py",
            "scope_guardian": "scope_guardian/scripts/scope_check.py",
            "clean_sweeper": "clean_sweeper/sweeper.py",
            "deep_analyzer": "deep_analyzer/analyzer.py",
            "impact_analyzer": "impact_analyzer/analyzer.py",
            "crash_decoder": "crash_decoder/decoder.py",
            "auto_scaffolder": "auto_scaffolder/scaffolder.py",
            "context_mapper": "context_mapper/context_mapper.py",
        }

        script = script_map.get(step.tool)
        if not script:
            return ExecutionResult(
                success=False,
                tool=step.tool,
                output="",
                error=f"Unknown tool: {step.tool}"
            )

        # Build command
        cmd = f'python .agents/skills/{script} {step.params}'
        if step.params == ".":
            cmd = f'python .agents/skills/{script} {self.project_root}'
        elif step.params == "--summary":
            cmd = f'python .agents/skills/{script} --summary'
        elif step.params == ". --json":
            cmd = f'python .agents/skills/{script} {self.project_root} --json'
        else:
            cmd = f'python .agents/skills/{script} {step.params}'

        # Execute
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=self.project_root
            )
            duration = (time.time() - start) * 1000

            return ExecutionResult(
                success=result.returncode == 0,
                tool=step.tool,
                output=result.stdout or "",
                error=result.stderr if result.returncode != 0 else None,
                duration_ms=round(duration, 1)
            )

        except subprocess.TimeoutExpired:
            duration = (time.time() - start) * 1000
            return ExecutionResult(
                success=False,
                tool=step.tool,
                output="",
                error="Command timeout (>30s)",
                duration_ms=round(duration, 1)
            )
        except Exception as e:
            duration = (time.time() - start) * 1000
            return ExecutionResult(
                success=False,
                tool=step.tool,
                output="",
                error=str(e),
                duration_ms=round(duration, 1)
            )

    def execute_all(self, steps: List) -> List[ExecutionResult]:
        """Execute all steps and return results."""
        results = []
        for step in steps:
            result = self.execute_step(step)
            results.append(result)
            if not result.success and step.tool != "NEEDS_CLARIFICATION":
                # Stop on failure
                break
        return results


def execute_command(cmd: str, cwd: str = ".") -> Dict[str, Any]:
    """Quick execute shell command."""
    executor = Executor(cwd)
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd, timeout=30)
    return {
        "success": result.returncode == 0,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "exit_code": result.returncode
    }
