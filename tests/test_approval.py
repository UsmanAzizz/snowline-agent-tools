#!/usr/bin/env python3
"""Regression test for companion approval flow.

Run: python tests/test_approval.py
"""
import sys
sys.path.insert(0, '.')

def test_needs_approval_exported():
    """Test (1) needs_approval exists in __init__."""
    from companion import needs_approval
    assert callable(needs_approval), "needs_approval must be callable"
    print("[PASS] needs_approval exported")

def test_no_apply_by_default():
    """Test (2) risky tools don't get --apply in command without approval."""
    from companion import Companion
    c = Companion()
    tests = [
        ("ganti submit jadi button", "smart_replace"),
        ("generate component Button", "auto_scaffolder"),
    ]
    for test_input, expected_tool in tests:
        r = c.run(test_input, approved=False)
        cmd = r.get('command', '')
        tool = r.get('tool', '')
        assert tool == expected_tool, f"Wrong tool: expected {expected_tool}, got {tool}"
        assert '--apply' not in (cmd or ''), f"FAILED: {test_input} got --apply without approval: {cmd}"
        needs_appr = r.get('needs_approval', False)
        assert needs_appr, f"FAILED: {test_input} should need approval"
        print(f"[PASS] {test_input}: tool={tool}, no --apply, needs_approval={needs_appr}")

if __name__ == "__main__":
    test_needs_approval_exported()
    test_no_apply_by_default()
    print("\n[PASS] All approval regression tests passed")
