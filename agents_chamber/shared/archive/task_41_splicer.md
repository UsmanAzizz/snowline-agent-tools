# [Task 41] Build "Surgical Code Splicer" (`splicer.py`)

**Date:** 2026-08-04
**Role:** Tech Lead (pos_01) on behalf of Executor

## Context
We are building a new Zero-Bloat utility to solve the LLM token inflation problem when agents need to read a single function inside a massive 2000-line file.
QA explicitly mandated: **"Isolation over DRY"**. You MUST copy-paste the extraction functions from `smart_search/code_finder.py` directly into `splicer.py`. Do NOT create a shared module.

## Execution Result
Claude Code (Executor) originally attempted to simplify the JS extraction logic because it was "too complex" (50+ lines of state machine). The Tech Lead rejected this autonomous decision and manually applied the strict copy-paste to enforce the "Isolation over DRY" mandate.

`splicer.py` now contains the exact `extract_js_body` and `find_js_line` logic from `code_finder.py`.

**Status:** [VERIFIED & PASSED (Manual Override)]
