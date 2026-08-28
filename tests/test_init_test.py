import os
import tempfile
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, os.path.abspath('src'))
from snowline.cli import init_test

def test_init_test_creates_files():
    with tempfile.TemporaryDirectory() as tmpdir:
        cwd = os.getcwd()
        os.chdir(tmpdir)
        try:
            init_test()
            today_str = datetime.now().strftime("%Y-%m-%d")
            history_dir = Path(".agents") / "test_history" / f"{today_str}_1"
            
            if not history_dir.exists(): raise AssertionError("History dir not created")
            if not (history_dir / "SNOWLINE_TEST.md").exists(): raise AssertionError("SNOWLINE_TEST.md not in history dir")
            if not (history_dir / "TEST_REPORT.md").exists(): raise AssertionError("TEST_REPORT.md not in history dir")
            if os.path.exists("SNOWLINE_TEST.md"): raise AssertionError("SNOWLINE_TEST.md in root")
            if os.path.exists("TEST_REPORT.md"): raise AssertionError("TEST_REPORT.md in root")
            
            with open(history_dir / "SNOWLINE_TEST.md", "rb") as f:
                if f.read().startswith(b"\xef\xbb\xbf"): raise AssertionError("BOM in SNOWLINE_TEST.md")
            with open(history_dir / "TEST_REPORT.md", "rb") as f:
                if f.read().startswith(b"\xef\xbb\xbf"): raise AssertionError("BOM in TEST_REPORT.md")
        finally:
            os.chdir(cwd)

def test_init_test_reuses_empty_folder():
    with tempfile.TemporaryDirectory() as tmpdir:
        cwd = os.getcwd()
        os.chdir(tmpdir)
        try:
            today_str = datetime.now().strftime("%Y-%m-%d")
            dir_1 = Path(".agents") / "test_history" / f"{today_str}_1"
            dir_2 = Path(".agents") / "test_history" / f"{today_str}_2"
            
            init_test()
            if not dir_1.exists(): raise AssertionError()
            
            # Jalankan kedua kali saat masih kosong
            init_test()
            if dir_2.exists(): raise AssertionError("dir_2 should not exist when dir_1 is empty")
        finally:
            os.chdir(cwd)

def test_init_test_creates_new_folder_when_filled():
    with tempfile.TemporaryDirectory() as tmpdir:
        cwd = os.getcwd()
        os.chdir(tmpdir)
        try:
            today_str = datetime.now().strftime("%Y-%m-%d")
            dir_1 = Path(".agents") / "test_history" / f"{today_str}_1"
            dir_2 = Path(".agents") / "test_history" / f"{today_str}_2"
            
            init_test()
            
            # Isi TEST_REPORT.md
            with open(dir_1 / "TEST_REPORT.md", "w", encoding="utf-8") as f:
                f.write("# FILLED REPORT\n")
            content_before = (dir_1 / "TEST_REPORT.md").read_bytes()
            
            # Jalankan lagi
            init_test()
            if not dir_2.exists(): raise AssertionError("dir_2 should be created")
            
            content_after = (dir_1 / "TEST_REPORT.md").read_bytes()
            if content_before != content_after: raise AssertionError("dir_1 content modified")
        finally:
            os.chdir(cwd)
