#!/usr/bin/env python3
"""
Static One-Shot Orchestrator for Claude Code Agent Bridge

Replaces the deprioritized daemon-based watcher.
Run manually: python orchestrator.py - does ONE check-and-relay cycle, then exits.

Design:
- subprocess.Popen for Windows-safe process tree killing
- Real-time streaming output
- Lock file prevents concurrent invocation
- taskkill /F /T ensures no orphaned processes on timeout
"""

import os
import sys
import subprocess
import time
import shutil
import re

CONNECTOR_PATH = "D:\\project\\scarecrow\\for_claude\\agents_connector.md"
LOCK_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "orchestrator.lock")
TIMEOUT_SECONDS = 300
AGENT_PROJECT = "D:\\AAAAAAAAA\\open_source_agents"

def safe_write(path, content):
    """Write with backup-first safety."""
    backup = path + ".bak"
    if os.path.exists(path):
        shutil.copy2(path, backup)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def read_connector():
    with open(CONNECTOR_PATH, 'r', encoding='utf-8') as f:
        return f.read()

def get_inbox_status(content):
    """Parse INBOX status - scoped to first occurrence (INBOX section first in file).

    KNOWN LIMITATION: relies on INBOX being the first '**Status:**' in the file.
    File structure is stable (INBOX -> OUTBOX -> ARCHIVE), so this is acceptable.
    """
    m = re.search(r'## ACTIVE TASK - INBOX.*?\*\*Status:\*\* \[([^\]]+)\]', content, re.DOTALL)
    return m.group(1) if m else None

def set_inbox_status(content, new_status):
    """Update INBOX status field."""
    return re.sub(
        r'(\*\*Status:\*\* \[)[^\]]+(\])',
        r'\g<1>' + new_status + r'\g<2>',
        content,
        count=1
    )

def kill_process_tree(pid):
    """Kill entire process tree on Windows using taskkill."""
    if sys.platform == 'win32':
        subprocess.run(['taskkill', '/F', '/T', '/PID', str(pid)],
                       capture_output=True)

def main():
    print(f"[INFO] Orchestrator starting (one-shot mode)")
    print(f"[INFO] Connector: {CONNECTOR_PATH}")

    # 1. Check lock file
    if os.path.exists(LOCK_FILE):
        print("[WARN] orchestrator.lock exists - another instance may be running. Exiting.")
        return 1

    # 2. Create lock file
    lock_fd = None
    try:
        with open(LOCK_FILE, 'w') as f:
            f.write(str(time.time()))
        print(f"[INFO] Lock file created: {LOCK_FILE}")

        # 3. Read connector
        content = read_connector()
        status = get_inbox_status(content)
        print(f"[INFO] INBOX status: [{status}]")

        # 4. Only process if READY
        if status != 'READY':
            print(f"[INFO] Status is not READY - exiting without action.")
            return 0

        # 5. Set PROCESSING
        content = set_inbox_status(content, 'PROCESSING')
        safe_write(CONNECTOR_PATH, content)
        print("[INFO] Status set to [PROCESSING], invoking Claude...")

        # 6. Invoke Claude Code with Popen (streaming)
        cmd = [
            "claude", "-p",
            "Read D:\\project\\scarecrow\\for_claude\\agents_connector.md and execute the task in INBOX.",
            "--tools", "Read,Glob",
            "--permission-mode", "plan"
        ]

        print(f"[INFO] Running: {' '.join(cmd[:3])}...")
        proc = subprocess.Popen(
            cmd,
            cwd=AGENT_PROJECT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1  # Line buffered
        )
        print(f"[INFO] Process started with PID: {proc.pid}")

        output_lines = []
        start = time.time()
        try:
            for line in proc.stdout:
                print(line, end='')  # Real-time streaming
                output_lines.append(line)

                # Check for timeout
                elapsed = time.time() - start
                if elapsed > TIMEOUT_SECONDS:
                    print(f"\n[WARN] Timeout ({TIMEOUT_SECONDS}s) - killing process tree...")
                    proc.terminate()
                    time.sleep(1)
                    if proc.poll() is None:
                        print("[WARN] Process still running, forcing kill...")
                        kill_process_tree(proc.pid)
                    break
        except KeyboardInterrupt:
            print("\n[INFO] Interrupted by user - killing process tree...")
            kill_process_tree(proc.pid)
            proc.wait()

        proc.wait()
        elapsed = time.time() - start
        print(f"[INFO] Process completed in {elapsed:.1f}s with exit code: {proc.returncode}")

        # 7. Set DONE
        content = read_connector()
        content = set_inbox_status(content, 'DONE')
        safe_write(CONNECTOR_PATH, content)
        print("[INFO] Status set to [DONE]. Orchestrator exiting.")

        return 0

    finally:
        # 8. Cleanup lock file
        if os.path.exists(LOCK_FILE):
            os.remove(LOCK_FILE)
            print(f"[INFO] Lock file removed")

if __name__ == "__main__":
    sys.exit(main())
