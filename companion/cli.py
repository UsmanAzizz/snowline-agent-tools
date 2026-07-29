#!/usr/bin/env python3
"""
COMPANION CLI - Command Line Interface
=====================================
Simple CLI untuk companion layer.
Bisa dipakai untuk test atau script automation.

Usage:
    python companion/cli.py --input "cari semua import axios"
    python companion/cli.py --input "refactor handleSubmit" --execute
    python companion/cli.py --interactive

Options:
    --input TEXT       User input to analyze
    --execute          Execute planned steps automatically
    --interactive     Start interactive mode
    --list-tools       List available tools
    --stats            Show memory statistics
    --reset            Reset memory
"""

import sys
import os
import argparse

# Add companion to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from companion_core import (
    analyze_intent,
    plan_steps,
    get_command,
    build_execution_command,
    needs_approval,
    learn,
    recall,
    memory_stats
)
from executor import Executor
from memory import memory

# ANSI colors
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
RESET = "\033[0m"
BOLD = "\033[1m"


def print_header(text):
    print(f"\n{BOLD}{BLUE}{'=' * 60}{RESET}")
    print(f"{BOLD}{BLUE}{text}{RESET}")
    print(f"{BOLD}{BLUE}{'=' * 60}{RESET}\n")


def print_step(step, index):
    """Print a planned step."""
    cmd = get_command(step)  # Preview command (NO --apply)
    needs_approval_flag = step.tool in ["smart_replace", "auto_scaffolder"]

    if step.needs_clarify:
        status = f"{RED}[NEEDS CLARIFICATION]{RESET}"
        print(f"  {index}. {BOLD}{step.tool}{RESET} {status}")
        print(f"     Reason: {step.reason}")
        print(f"     {YELLOW}! {step.clarify_note}{RESET}")
    else:
        if needs_approval_flag:
            status = f"{YELLOW}[PREVIEW - NEEDS APPROVAL]{RESET}"
        else:
            status = f"{GREEN}[READY]{RESET}"
        print(f"  {index}. {BOLD}{step.tool}{RESET} {status}")
        print(f"     Reason: {step.reason}")
        print(f"     Preview: {cmd}")
        if needs_approval_flag:
            print(f"     {YELLOW}! This modifies files - requires explicit approval{RESET}")


def handle_input(user_input, execute=False, explicit_approval=False):
    """
    Handle single user input.

    Args:
        user_input: User's request
        execute: If True, prepare to execute
        explicit_approval: If True, user has explicitly approved modification
                          (--apply will be added for dangerous tools)
    """
    print(f"{BOLD}Input:{RESET} \"{user_input}\"")

    # Analyze
    intent = analyze_intent(user_input)
    print(f"{BOLD}Intent:{RESET} {intent.clarity}")
    print(f"{BOLD}Keywords:{RESET} {intent.keywords}")

    if intent.needs_clarification:
        print(f"{YELLOW}! {intent.clarification_msg}{RESET}")

    # Plan
    steps = plan_steps(user_input, intent)
    print(f"\n{BOLD}Planned Steps:{RESET} {len(steps)}")

    executor = Executor(".")

    for i, step in enumerate(steps, 1):
        print_step(step, i)

        if execute and not step.needs_clarify:
            # Check if this tool needs approval
            if needs_approval(step.tool):
                if explicit_approval:
                    # User explicitly approved - add --apply
                    exec_cmd = build_execution_command(step, approved=True)
                    print(f"\n  {YELLOW}Executing with approval...{RESET}")
                    print(f"  Command: {exec_cmd}")
                    # For now, just show - actual execution would need proper handling
                else:
                    # Not explicitly approved - show what would happen
                    preview_cmd = build_execution_command(step, approved=False)
                    approved_cmd = build_execution_command(step, approved=True)
                    print(f"\n  {YELLOW}! Tool requires explicit approval to modify files{RESET}")
                    print(f"  Preview: {preview_cmd}")
                    print(f"  After approval: {approved_cmd}")
                    print(f"  {YELLOW}  -> Run with --approved flag to execute{RESET}")
            else:
                # Safe tool - execute normally
                print(f"\n  {YELLOW}Executing...{RESET}")
                result = executor.execute_step(step)
                if result.success:
                    print(f"  {GREEN}Success ({result.duration_ms}ms){RESET}")
                    learn(user_input, intent.keywords, step.tool, True)
                else:
                    print(f"  {RED}Failed: {result.error}{RESET}")
                    learn(user_input, intent.keywords, step.tool, False)

    # Check memory for suggestions
    suggestion = recall(user_input, intent.keywords)
    if suggestion:
        print(f"\n{BOLD}Suggestion: {suggestion}{RESET}")

    return steps


def interactive_mode():
    """Start interactive mode."""
    print_header("COMPANION INTERACTIVE MODE")
    print("Type your request and press Enter.")
    print("Commands:")
    print("  :stats  - Show memory statistics")
    print("  :reset  - Reset memory")
    print("  :tools  - List available tools")
    print("  :quit   - Exit")
    print()

    while True:
        try:
            user_input = input(f"{GREEN}companion>{RESET} ").strip()

            if not user_input:
                continue

            # Commands
            if user_input == ":quit":
                print("Goodbye!")
                break
            elif user_input == ":stats":
                stats = memory_stats()
                print(f"Total entries: {stats['total_entries']}")
                print(f"Tool usage: {stats['tool_usage']}")
                continue
            elif user_input == ":reset":
                memory.reset()
                print("Memory reset!")
                continue
            elif user_input == ":tools":
                print("Available tools:")
                for tool in ["smart_search", "smart_replace", "selective_reader",
                             "project_guardian", "clean_sweeper", "deep_analyzer",
                             "crash_decoder", "auto_scaffolder", "token_budget",
                             "context_curator", "output_formatter", "decision_validator"]:
                    print(f"  - {tool}")
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
    parser = argparse.ArgumentParser(description="Companion CLI")
    parser.add_argument("--input", "-i", type=str, help="User input to analyze")
    parser.add_argument("--execute", "-e", action="store_true", help="Execute planned steps")
    parser.add_argument("--interactive", action="store_true", help="Start interactive mode")
    parser.add_argument("--list-tools", action="store_true", help="List available tools")
    parser.add_argument("--stats", action="store_true", help="Show memory statistics")
    parser.add_argument("--reset", action="store_true", help="Reset memory")

    args = parser.parse_args()

    # Handle commands
    if args.reset:
        memory.reset()
        print("Memory reset!")
        return

    if args.stats:
        stats = memory_stats()
        print_header("MEMORY STATISTICS")
        print(f"Total entries: {stats['total_entries']}")
        print(f"Last used: {stats['last_used']}")
        print("\nTool usage:")
        for tool, count in stats['tool_usage'].items():
            print(f"  - {tool}: {count}x")
        return

    if args.list_tools:
        print_header("AVAILABLE TOOLS")
        tools = [
            ("smart_search", "Find code with context"),
            ("smart_replace", "Safe find and replace"),
            ("selective_reader", "Read large files (TOC)"),
            ("project_guardian", "Security auditor"),
            ("clean_sweeper", "Tech debt scanner"),
            ("deep_analyzer", "Project profiler"),
            ("crash_decoder", "Error parser"),
            ("auto_scaffolder", "Boilerplate generator"),
            ("impact_analyzer", "Dependency tracer"),
            ("scope_guardian", "Scope validator"),
            ("token_budget", "Token usage tracker"),
            ("context_curator", "Context noise filter"),
            ("output_formatter", "JSON formatter"),
            ("decision_validator", "Risk assessor"),
        ]
        for tool, desc in tools:
            print(f"  {GREEN}{tool:<20}{RESET} - {desc}")
        return

    if args.interactive:
        interactive_mode()
        return

    if args.input:
        handle_input(args.input, execute=args.execute)
        return

    # No args - show help
    parser.print_help()
    print("\nExamples:")
    print('  python companion/cli.py --input "cari semua import axios"')
    print('  python companion/cli.py --input "refactor handleSubmit" --execute')
    print('  python companion/cli.py --interactive')
    print('  python companion/cli.py --list-tools')


if __name__ == "__main__":
    main()
