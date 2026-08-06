"""
cli.py - CLI interface, argparse, and print helpers.
"""
import sys
import json
import os
from datetime import datetime, timezone


def _log_usage(user_input: str, result, action: str, matched_tool: str | None):
    """Append usage log to companion_usage.jsonl in .agents/ root."""
    log_path = os.path.join(os.path.dirname(__file__), "..", "..", "companion_usage.jsonl")

    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "input": user_input,
        "action": action,
        "confidence": result.confidence_level,
        "specificity": result.specificity,
        "matched_tool": matched_tool
    }

    try:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError:
        pass  # Silently fail if log can't be written


# ANSI colors for terminal
class Colors:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    RESET = '\033[0m'
    CHECK = '+'
    INFO = 'i'
    WARN = '!'
    ERROR = 'x'


def safe_print(text, end="\n"):
    """Print with UTF-8 encoding, fallback to ASCII on Windows."""
    try:
        print(text, end=end)
    except UnicodeEncodeError:
        replacements = {
            '✓': '[+]', '✗': '[x]', 'ℹ': '[i]', '⚠': '[!]',
            '•': '-', '→': '->',
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        print(text, end=end)


def print_header(text):
    safe_print(f"\n{Colors.CYAN}{Colors.BOLD}{'=' * 60}{Colors.RESET}")
    safe_print(f"{Colors.CYAN}{Colors.BOLD}  {text}{Colors.RESET}")
    safe_print(f"{Colors.CYAN}{Colors.BOLD}{'=' * 60}{Colors.RESET}\n")


def print_success(text):
    safe_print(f"{Colors.GREEN}{Colors.CHECK} {text}{Colors.RESET}")


def print_info(text):
    safe_print(f"{Colors.CYAN}{Colors.INFO} {text}{Colors.RESET}")


def print_warning(text):
    safe_print(f"{Colors.YELLOW}{Colors.WARN} {text}{Colors.RESET}")


def needs_approval(tool: str) -> bool:
    from .core_intent import APPROVAL_REQUIRED
    return tool in APPROVAL_REQUIRED


def get_agent_action(result) -> str:
    if result.needs_clarification:
        # Multi-match: suggest top tool instead of empty CLARIFY
        if result.clarification_context and result.clarification_context.get('matched_tools'):
            return "KONFIRMASI"
        return "CLARIFY"
    if result.confidence_level == "HIGH" and result.specificity == "high":
        return "EXECUTE"
    elif result.confidence_level in ("HIGH", "MEDIUM"):
        return "KONFIRMASI"
    else:
        return "CLARIFY"


def main():
    """CLI entry point."""
    import argparse
    from .core_intent import analyze_intent
    from .core_grilling import should_grill

    parser = argparse.ArgumentParser(description='Companion v5.0 - Intent Analyzer')
    parser.add_argument('input', nargs='*', help='Input text to analyze')
    parser.add_argument('--analyze', '-a', help='Analyze input text')
    args = parser.parse_args()

    user_input = args.analyze or ' '.join(args.input)

    if not user_input:
        safe_print("Usage: python companion.py 'your instruction'")
        safe_print("   or: python companion.py --analyze 'your instruction'")
        return

    result = analyze_intent(user_input)
    grill = should_grill(result)

    # Log usage
    action = get_agent_action(result)
    matched_tool = result.single_tool.name if result.single_tool else None
    _log_usage(user_input, result, action, matched_tool)

    print(f"\n{'=' * 60}")
    print(f"COMPANION v5.0 - ANALYSIS RESULT")
    print(f"{'=' * 60}")
    print(f"Input: {result.input}")
    print(f"Keywords: {result.keywords}")
    print(f"Entities: {result.entities}")
    print(f"Specificity: {result.specificity}")
    print(f"Confidence: {result.confidence_level}")
    print(f"Action: {get_agent_action(result)}")
    print(f"")
    print(f"Grilling Check:")
    print(f"  needs_grilling: {grill['needs_grilling']}")
    print(f"  reason: {grill['reason']}")

    if result.single_tool:
        print(f"\nTool: {result.single_tool.name}")
        print(f"  Confidence: {result.single_tool.confidence}")
        print(f"  Reason: {result.single_tool.reason}")
        print(f"  Safety: {result.single_tool.safety}")
        print(f"  Command: {result.single_tool.command_template}")
        print(f"  Needs Approval: {needs_approval(result.single_tool.name)}")
    elif result.needs_clarification:
        print(f"\n! {result.clarification_note}")
        # Show top-ranked tool as main suggestion + alternatives from clarification_context
        if result.clarification_context and result.clarification_context.get('matched_tools'):
            tools = result.clarification_context['matched_tools']
            if tools:
                top = tools[0]
                print(f"\n  Tool (suggested): {top['name']} ({top['confidence']})")
                if len(tools) > 1:
                    alt_names = [f"{t['name']} ({t['confidence']})" for t in tools[1:]]
                    print(f"  Alternatives: {', '.join(alt_names)}")

    print(f"{'=' * 60}\n")


def task_lock_cli(args):
    """CLI interface for task_lock commands."""
    import argparse
    from .core_memory import (
        load_task_lock, start_task_lock, add_grilling_qa,
        update_task_lock, get_task_status, end_task_lock
    )

    parser = argparse.ArgumentParser(description='Task Lock Manager')
    sub = parser.add_subparsers(dest='cmd')

    p = sub.add_parser('start', help='Start new task lock')
    p.add_argument('task_id')
    p.add_argument('user_intent', nargs='+')

    p = sub.add_parser('add', help='Add Q&A to grilling log')
    p.add_argument('question')
    p.add_argument('answer')

    p = sub.add_parser('update', help='Update field')
    p.add_argument('field')
    p.add_argument('value')

    sub.add_parser('status', help='Show current task status')
    sub.add_parser('end', help='End current task')

    args = parser.parse_args(args)

    if args.cmd == 'start':
        intent = ' '.join(args.user_intent)
        result = start_task_lock(args.task_id, intent)
        print(f"Task started: {args.task_id}")
        print(json.dumps(result, indent=2))

    elif args.cmd == 'add':
        result = add_grilling_qa(args.question, args.answer)
        print(f"Q&A added")
        print(json.dumps(result, indent=2))

    elif args.cmd == 'update':
        result = update_task_lock(**{args.field: args.value})
        print(f"Updated {args.field}")
        print(json.dumps(result, indent=2))

    elif args.cmd == 'status':
        result = get_task_status()
        print(json.dumps(result, indent=2))

    elif args.cmd == 'end':
        end_task_lock()
        print("Task ended, lock removed")

    else:
        parser.print_help()
