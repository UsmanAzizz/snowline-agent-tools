import os
import sys
import unittest
from pathlib import Path

# Add src to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from snowline.core_entry_checker import check_entry
import io


def test_exemption_line_numbers():
    # Shouldn't fail because :529, entri 24, 21-08 are not quantitative claims
    content = """
    Selesai!
    Tadi baca file di baris :529 dan entri 24 pada 21-08. Hash commit 6cae2d2.
    ```
    $ echo "hello"
    hello
    ```
    """
    assert check_entry(content) is True, "Exemptions blocked incorrectly"
    
def test_quantitative_claim_rejected():
    # 90% without output source
    content = """
    Selesai, akurasi 90%.
    ```
    $ echo "hello"
    hello
    ```
    """
    held, sys.stdout = sys.stdout, io.StringIO()
    try:
        assert check_entry(content) is False, "Should be rejected because 90% not in output"
        assert "Angka klaim pengukuran '90%' tidak ditemukan" in sys.stdout.getvalue()
    finally:
        sys.stdout = held
    
def test_quantitative_claim_accepted():
    # 40/40 found in output
    content = """
    Selesai, tes lulus 40/40.
    ```
    $ run_tests
    Passed 40/40
    ```
    """
    assert check_entry(content) is True, "Should be accepted"

def test_real_qa_entries():
    # Test 3 real QA entries from history
    history_dir = Path(".here_we_are/history")
    if not history_dir.exists():
        return
        
    entries_to_test = [
        "caching/01-caching.md",
        "clean_sweeper/01-clean_sweeper.md",
        "blind_test/01-blind_test.md"
    ]
    
    held, sys.stdout = sys.stdout, io.StringIO()
    try:
        for rel_path in entries_to_test:
            path = history_dir / rel_path
            if path.exists():
                text = path.read_text(encoding='utf-8')
                result = check_entry(text)
                assert result is True, f"Real QA entry {rel_path} failed check_entry! Output: {sys.stdout.getvalue()}"
    finally:
        sys.stdout = held

import subprocess
import tempfile
import os

def test_cli_exit_code():
    # Write a passing entry to a temporary file
    pass_content = """
    Selesai!
    ```
    $ echo "hello"
    hello
    ```
    """
    # Write a failing entry to a temporary file (quantitative claim not met)
    fail_content = """
    Selesai, akurasi 90%.
    ```
    $ echo "hello"
    hello
    ```
    """
    
    src_path = Path(__file__).parent.parent / 'src'
    cli_path = src_path / 'snowline' / 'cli.py'
    
    env = os.environ.copy()
    env['PYTHONPATH'] = str(src_path) + os.pathsep + env.get('PYTHONPATH', '')
    
    with tempfile.NamedTemporaryFile('w', encoding='utf-8', delete=False) as f_pass, \
         tempfile.NamedTemporaryFile('w', encoding='utf-8', delete=False) as f_fail:
        f_pass.write(pass_content)
        f_pass_path = f_pass.name
        f_fail.write(fail_content)
        f_fail_path = f_fail.name
        
    try:
        # Test passing entry
        result_pass = subprocess.run(
            [sys.executable, str(cli_path), "check-entry", f_pass_path],
            capture_output=True,
            text=True,
            env=env
        )
        assert result_pass.returncode == 0, f"Expected passing entry to have exit code 0, got {result_pass.returncode}. Stderr: {result_pass.stderr}"
        
        # Test failing entry
        result_fail = subprocess.run(
            [sys.executable, str(cli_path), "check-entry", f_fail_path],
            capture_output=True,
            text=True,
            env=env
        )
        assert result_fail.returncode == 1, f"Expected failing entry to have exit code 1, got {result_fail.returncode}. Stderr: {result_fail.stderr}"
    finally:
        os.remove(f_pass_path)
        os.remove(f_fail_path)

def test_tl_verdict_rejected():
    import sys
    import io
    old_stdout = sys.stdout
    sys.stdout = capsys = io.StringIO()
    content = """# TL -> PM
Berikut laporannya.
Kode ini sudah stabil dan siap rilis.
"""
    assert check_entry(content) is False
    out = capsys.getvalue()
    sys.stdout = old_stdout
    assert "stabil" in out
    assert "baris" in out

def test_tl_verdict_accepted():
    content = """# TL -> PM
Berikut laporannya.
### Apa yang tidak saya periksa
Saya tidak memeriksa apakah ini sudah stabil atau bersih sepenuhnya.
"""
    assert check_entry(content) is True

def test_tl_qa_verdict_rejected():
    import sys
    import io
    old_stdout = sys.stdout
    sys.stdout = capsys = io.StringIO()
    content = """# TL -> QA
Berikut laporannya.
Kode ini sudah bersih dan siap rilis.
"""
    assert check_entry(content) is False
    out = capsys.getvalue()
    sys.stdout = old_stdout
    assert "bersih" in out
    assert "baris" in out

def test_tl_qa_verdict_accepted():
    content = """# TL -> QA
Berikut laporannya.
### Apa yang tidak saya periksa
Saya tidak memeriksa apakah ini sudah stabil atau bersih sepenuhnya.
"""
    assert check_entry(content) is True
