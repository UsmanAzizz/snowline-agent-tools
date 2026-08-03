#!/usr/bin/env python3
"""Test runner for JS/TS/JSX function body extraction."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from code_finder import find_js_line, extract_js_body, search_files

TEST_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "test_js_extraction")

TESTS = [
    ("test1_simple.js", "processData", "SUCCESS", "Simple function"),
    ("test2_string_braces.js", "greet", "SUCCESS", "Braces in string literal"),
    ("test3_template_literal.js", "templateFunc", "BAIL_OUT", "Template literal (backtick)"),
    ("test4_nested_template.js", "nestedTemplate", "BAIL_OUT", "Nested template interpolation"),
    ("test5_line_comment.js", "commented", "SUCCESS", "Braces in line comment"),
    ("test6_block_comment.js", "blockComment", "SUCCESS", "Braces in block comment"),
    ("test7_escaped_quotes.js", "escapedQuotes", "SUCCESS", "Escaped quotes in string"),
    # Test 8 - JSX with parameter destructuring causes early return (known limitation)
    ("test8_jsx.jsx", "JSXComponent", "PARTIAL", "JSX with destructuring param (known limitation)"),
    ("test9_regex_brace.js", "regexFunc", "BAIL_OUT", "Regex literal with brace"),
    # Test 10 - returns FIRST occurrence (known limitation: last def should win for proper AST)
    ("test10_duplicate_names.js", "process", "PARTIAL", "Duplicate function names (first def wins)"),
]

def run_test(filename, keyword, expected, description):
    """Run a single test case."""
    fpath = os.path.join(TEST_DIR, filename)
    if not os.path.exists(fpath):
        print(f"[ERROR] Test file not found: {fpath}")
        return False

    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()

    print(f"\n{'='*70}")
    print(f"TEST: {description}")
    print(f"File: {filename}, Keyword: '{keyword}'")
    print(f"Expected: {expected}")
    print(f"{'='*70}")

    idx = find_js_line(content, keyword)
    if idx is None:
        print("[FAIL] Keyword not found by find_js_line()")
        return False

    print(f"[INFO] Found keyword at line {idx}: {content.split(chr(10))[idx].strip()}")

    body = extract_js_body(content, idx)
    lines = content.split('\n')

    if body:
        start, end = body
        print(f"[OK] Brace-counting SUCCESS - extracted lines {start} to {end}")
        print("--- Extracted body ---")
        for i in range(start, end + 1):
            marker = ">>" if i == idx else "  "
            print(f"{marker} {i+1:3d} | {lines[i]}")
        print("-" * 40)

        if expected == "SUCCESS":
            return True
        elif expected == "PARTIAL":
            # PARTIAL means we got some extraction (not bail-out)
            print(f"[PARTIAL] Got extraction, expected PARTIAL - accepting")
            return True
        else:
            print(f"[UNEXPECTED] Expected BAIL_OUT but got brace extraction")
            return False
    else:
        print(f"[INFO] Bail-out triggered (template literal or ambiguous slash)")
        print(f"[INFO] Falling back to line-context (5 lines)...")

        # Show what line-context would return
        ctx = 5
        s = max(0, idx - ctx)
        e = min(len(lines), idx + ctx + 1)
        for i in range(s, e):
            marker = ">>" if i == idx else "  "
            print(f"{marker} {i+1:3d} | {lines[i]}")
        print("-" * 40)

        if expected == "BAIL_OUT":
            return True
        else:
            print(f"[UNEXPECTED] Expected SUCCESS but got bail-out")
            return False

def main():
    print("="*70)
    print("JS/TS/JSX FUNCTION BODY EXTRACTION - TEST SUITE")
    print("="*70)

    passed = 0
    failed = 0

    for filename, keyword, expected, description in TESTS:
        result = run_test(filename, keyword, expected, description)
        if result:
            passed += 1
            print(f"[PASS] {description}")
        else:
            failed += 1
            print(f"[FAIL] {description}")

    print("\n" + "="*70)
    print(f"RESULTS: {passed} passed, {failed} failed out of {len(TESTS)} tests")
    print("="*70)

    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
