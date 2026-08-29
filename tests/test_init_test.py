import os
import shutil
import tempfile
import re
from pathlib import Path
from datetime import datetime
from snowline.cli import init_test

def test_init_test_creates_files():
    with tempfile.TemporaryDirectory() as tmpdir:
        cwd = os.getcwd()
        os.chdir(tmpdir)
        try:
            init_test()
            today_str = datetime.now().strftime("%Y-%m-%d")
            history_dir = Path(".agents") / "test_history" / f"{today_str}_1"
            
            test_file = history_dir / "SNOWLINE_TEST.md"
            report_file = history_dir / "TEST_REPORT.md"
            
            if not test_file.exists(): raise AssertionError("SNOWLINE_TEST.md not in history dir")
            if not report_file.exists(): raise AssertionError("TEST_REPORT.md not in history dir")
            if os.path.exists("SNOWLINE_TEST.md"): raise AssertionError("SNOWLINE_TEST.md in root")
            if os.path.exists("TEST_REPORT.md"): raise AssertionError("TEST_REPORT.md in root")
            
            with open(test_file, "rb") as f:
                if f.read().startswith(b"\xef\xbb\xbf"): raise AssertionError("BOM in SNOWLINE_TEST.md")
            with open(report_file, "rb") as f:
                if f.read().startswith(b"\xef\xbb\xbf"): raise AssertionError("BOM in TEST_REPORT.md")
                
            # Verifikasi penanda sudah diganti dengan jalur mutlak nyata
            content = test_file.read_text(encoding="utf-8")
            assert "{{JALUR_LAPORAN}}" not in content, "{{JALUR_LAPORAN}} masih ada di SNOWLINE_TEST.md"
            assert str(report_file.resolve()) in content, "Jalur mutlak TEST_REPORT.md tidak ada di SNOWLINE_TEST.md"
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
            
            # Isi TEST_REPORT.md di dir_1
            with open(dir_1 / "TEST_REPORT.md", "w", encoding="utf-8") as f:
                f.write("# FILLED REPORT\n")
            content_before = (dir_1 / "TEST_REPORT.md").read_bytes()
            
            # Jalankan lagi -> membuat dir_2
            init_test()
            if not dir_2.exists(): raise AssertionError("dir_2 should be created")
            
            content_after = (dir_1 / "TEST_REPORT.md").read_bytes()
            if content_before != content_after: raise AssertionError("dir_1 content modified")
            
            # Verifikasi SNOWLINE_TEST.md di dir_2 menunjuk ke dir_2, BUKAN dir_1
            test_2_text = (dir_2 / "SNOWLINE_TEST.md").read_text(encoding="utf-8")
            report_2_abs = str((dir_2 / "TEST_REPORT.md").resolve())
            report_1_abs = str((dir_1 / "TEST_REPORT.md").resolve())
            
            assert report_2_abs in test_2_text, f"SNOWLINE_TEST.md di dir_2 harus memuat {report_2_abs}"
            assert report_1_abs not in test_2_text, f"SNOWLINE_TEST.md di dir_2 tidak boleh memuat jalur dir_1 ({report_1_abs})"
        finally:
            os.chdir(cwd)
