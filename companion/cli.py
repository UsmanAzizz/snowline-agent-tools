#!/usr/bin/env python3
"""
COMPANION CLI v5.0 - Command Line Interface
============================================
Phase 3: Companion as data processor, agent makes decisions.
"""

import sys
import os
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from companion import (
    analyze_intent,
    ToolMatch,
    AnalyzeResult,
    plan_steps,
    get_command,
    build_execution_command,
    needs_approval,
    get_agent_action,
    learn,
    recall,
    memory_stats,
    memory,
)
from executor import Executor

# ANSI colors
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
RESET = "\033[0m"
BOLD = "\033[1m"


def print_header(text):
    print(f"\n{BOLD}{BLUE}{'"'"'='"'"' * 60}{RESET}")
    print(f"{BOLD}{BLUE}{text}{RESET}")
    print(f"{BOLD}{BLUE}{'"'"'='"'"' * 60}{RESET}\n")


def print_result(result: AnalyzeResult):
    """Print v5.0 AnalyzeResult."""
    print(f"{BOLD}Input:{RESET} \"{result.input}\"")
    print(f"{BOLD}Keywords:{RESET} {result.keywords}")
    print(f"{BOLD}Entities:{RESET} {result.entities}")
    print(f"{BOLD}Specificity:{RESET} {result.specificity}")
    print(f"{BOLD}Confidence:{RESET} {result.confidence_level}")
    
    if result.single_tool:
        tool = result.single_tool
        print(f"\n{BOLD}Tool Signal:{RESET}")
        print(f"  Name: {tool.name}")
        print(f"  Confidence: {tool.confidence}")
        print(f"  Safety: {tool.safety}")
        print(f"  Reason: {tool.reason}")
        print(f"  Template: {tool.command_template}")
    
    if result.sequential_steps:
        print(f"\n{BOLD}Sequential Steps:{RESET}")
        for i, step in enumerate(result.sequential_steps, 1):
            print(f"  {i}. {step.name} ({step.confidence})")
    
    if result.needs_clarification:
        print(f"\n{RED}! Clarification Needed:{RESET}")
        print(f"  {result.clarification_note}")
    
    # Agent decision
    action = get_agent_action(result)
    action_colors = {
        "EXECUTE": GREEN,
        "KONFIRMASI": YELLOW,
        "CLARIFY": YELLOW,
        "ABORT": RED,
    }
    color = action_colors.get(action, RESET)
    print(f"\n{BOLD}[Agent Decision]:{RESET} {color}{action}{RESET}")


def handle_input(user_input, execute=False, explicit_approval=False):
    """Handle single user input."""
    print(f"{BOLD}Input:{RESET} \"{user_input}\"")

    # v5.0: Use analyze_intent directly
    result = analyze_intent(user_input)
    print_result(result)

    # Legacy: also get plan_steps for execution
    steps = plan_steps(user_input, result)
    print(f"\n{BOLD}Planned Steps:{RESET} {len(steps)}")

    executor = Executor(".")

    for i, step in enumerate(steps, 1):
        cmd = get_command(step)
        needs_approval_flag = step.tool in ["smart_replace", "auto_scaffolder"]

        if step.needs_clarify:
            status = f"{RED}[NEEDS CLARIFICATION]{RESET}"
            print(f"  {i}. {BOLD}{step.tool}{RESET} {status}")
            print(f"     Reason: {step.reason}")
            print(f"     {YELLOW}! {step.clarify_note}{RESET}")
        else:
            if needs_approval_flag:
                status = f"{YELLOW}[PREVIEW - NEEDS APPROVAL]{RESET}"
            else:
                status = f"{GREEN}[READY]{RESET}"
            print(f"  {i}. {BOLD}{step.tool}{RESET} {status}")
            print(f"     Reason: {step.reason}")
            print(f"     Preview: {cmd}")
            if needs_approval_flag:
                print(f"     {YELLOW}! This modifies files - requires explicit approval{RESET}")

        if execute and not step.needs_clarify:
            if needs_approval(step.tool):
                if explicit_approval:
                    exec_cmd = build_execution_command(step, approved=True)
                    print(f"\n  {YELLOW}Executing with approval...{RESET}")
                    print(f"  Command: {exec_cmd}")
                else:
                    preview_cmd = build_execution_command(step, approved=False)
                    approved_cmd = build_execution_command(step, approved=True)
                    print(f"\n  {YELLOW}! Tool requires explicit approval{RESET}")
                    print(f"  Preview: {preview_cmd}")
                    print(f"  After approval: {approved_cmd}")
            else:
                print(f"\n  {YELLOW}Executing...{RESET}")
                result_exec = executor.execute_step(step)
                if result_exec.success:
                    print(f"  {GREEN}Success ({result_exec.duration_ms}ms){RESET}")
                    learn(user_input, result.keywords, step.tool, True)
                else:
                    print(f"  {RED}Failed: {result_exec.error}{RESET}")
                    learn(user_input, result.keywords, step.tool, False)

    # Memory suggestion
    suggestion = recall(user_input, result.keywords)
    if suggestion:
        print(f"\n{BOLD}Suggestion: {suggestion}{RESET}")

    return steps


def interactive_mode():
    """Start interactive mode."""
    print_header("COMPANION v5.0 INTERACTIVE MODE")
    print("Type your request and press Enter.")
    print("Agent will show decision matrix based on confidence.")
    print("Commands:")
    print("  :stats  - Show memory statistics")
    print("  :reset  - Reset memory")
    print("  :tools  - List available tools")
    print("  :matrix - Show decision matrix")
    print("  :quit   - Exit")
    print()

    while True:
        try:
            user_input = input(f"{GREEN}companion>{RESET} ").strip()

            if not user_input:
                continue

            if user_input == ":quit":
                print("Goodbye!")
                break
            elif user_input == ":stats":
                stats = memory_stats()
                print(f"Total entries: {stats['"'"'total_entries'"'"']}")
                print(f"Tool usage: {stats['"'"'tool_usage'"'"']}")
                continue
            elif user_input == ":reset":
                memory.reset()
                print("Memory reset!")
                continue
            elif user_input == ":tools":
                print("Available tools:")
                for tool in TOOL_REGISTRY.keys():
                    print(f"  - {tool}")
                continue
            elif user_input == ":matrix":
                print("\nAgent Decision Matrix:")
                print("| Confidence | Specificity | Action |")
                print("|------------|-------------|--------|")
                print("| HIGH       | high        | EXECUTE|")
                print("| MEDIUM     | any         | KONFIRMASI |")
                print("| LOW        | any         | CLARIFY|")
                print("| NONE       | any         | ABORT |")
                continue

            print()
            handle_input(user_input, execute=False)
            print()

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"{RED}Error: {e}{RESET}")


def main():
    parser = argparse.ArgumentParser(description="Companion CLI v5.0")
    parser.add_argument("--input", "-i", type=str, help="User input to analyze")
    parser.add_argument("--execute", "-e", action="store_true", help="Execute planned steps")
    parser.add_argument("--interactive", action="store_true", help="Start interactive mode")
    parser.add_argument("--list-tools", action="store_true", help="List available tools")
    parser.add_argument("--stats", action="store_true", help="Show memory statistics")
    parser.add_argument("--reset", action="store_true", help="Reset memory")
    parser.add_argument("--matrix", action="store_true", help="Show decision matrix")

    args = parser.parse_args()

    if args.reset:
        memory.reset()
        print("Memory reset!")
        return

    if args.stats:
        print_header("MEMORY STATISTICS")
        stats = memory_stats()
        print(f"Total entries: {stats['"'"'total_entries'"'"']}")
        print(f"Last used: {stats['"'"'last_used'"'"']}")
        print("\nTool usage:")
        for tool, count in stats['"'"'tool_usage'"'"'].items():
            print(f"  - {tool}: {count}x")
        return

    if args.list_tools:
        print_header("AVAILABLE TOOLS")
        for tool, info in TOOL_REGISTRY.items():
            safety_color = GREEN if info['"'"'safety'"'"'] == "safe" else YELLOW
            print(f"  {GREEN}{tool:<20}{RESET} - {safety_color}{info['"'"'safety'"'"']}{RESET}")
        return

    if args.matrix:
        print_header("AGENT DECISION MATRIX")
        print("| Confidence | Specificity | Agent Action |")
        print("|------------|-------------|--------------|")
        print("| HIGH       | high        | EXECUTE      |")
        print("| MEDIUM     | any         | KONFIRMASI   |")
        print("| LOW        | any         | CLARIFY      |")
        print("| NONE       | any         | ABORT        |")
        return

    if args.interactive:
        interactive_mode()
        return

    if args.input:
        handle_input(args.input, execute=args.execute)
        return

    parser.print_help()
    print("\nExamples:")
    print('"'"'  python companion/cli.py --input "cari semua import axios"'"'"')
    print('"'"'  python companion/cli.py --input "refactor handleSubmit" --execute'"'"')
    print('"'"'  python companion/cli.py --interactive'"'"')
    print('"'"'  python companion/cli.py --matrix'"'"')


if __name__ == "__main__":
    main()
