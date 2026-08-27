import os
import tempfile

def test_init_test_creates_files():
    import sys
    sys.path.insert(0, 'src')
    from snowline.cli import init_test
    
    with tempfile.TemporaryDirectory() as tmpdir:
        cwd = os.getcwd()
        os.chdir(tmpdir)
        try:
            init_test(force=False)
            if not os.path.exists("SNOWLINE_TEST.md"): raise AssertionError()
            if not os.path.exists("TEST_REPORT.md"): raise AssertionError()
            
            with open("SNOWLINE_TEST.md", "rb") as f:
                if f.read().startswith(b"\xef\xbb\xbf"): raise AssertionError()
            with open("TEST_REPORT.md", "rb") as f:
                if f.read().startswith(b"\xef\xbb\xbf"): raise AssertionError()
                
            with open("TEST_REPORT.md", "r", encoding="utf-8") as f:
                text = f.read()
                
                if "council" in text.lower(): raise AssertionError()
                
            with open("SNOWLINE_TEST.md", "r", encoding="utf-8") as f:
                text = f.read()
                if "Dilarang memperbaiki" not in text: raise AssertionError()
                if "Catat tebakan" not in text: raise AssertionError()
                if "Kerjakan berurutan" not in text: raise AssertionError()
                if "winreg" in text: raise AssertionError()
        finally:
            os.chdir(cwd)

def test_init_test_rejects_overwrite():
    import sys
    sys.path.insert(0, 'src')
    from snowline.cli import init_test
    
    with tempfile.TemporaryDirectory() as tmpdir:
        cwd = os.getcwd()
        os.chdir(tmpdir)
        try:
            with open("TEST_REPORT.md", "w", encoding="utf-8") as f:
                f.write("OLD CONTENT")
            
            init_test(force=False)
            
            with open("TEST_REPORT.md", "r", encoding="utf-8") as f:
                if f.read() != "OLD CONTENT": raise AssertionError()
        finally:
            os.chdir(cwd)

def test_init_test_force_overwrite():
    import sys
    sys.path.insert(0, 'src')
    from snowline.cli import init_test
    
    with tempfile.TemporaryDirectory() as tmpdir:
        cwd = os.getcwd()
        os.chdir(tmpdir)
        try:
            with open("TEST_REPORT.md", "w", encoding="utf-8") as f:
                f.write("OLD CONTENT")
            
            init_test(force=True)
            
            with open("TEST_REPORT.md", "r", encoding="utf-8") as f:
                text = f.read()
                if text == "OLD CONTENT": raise AssertionError()
                if "Laporan Pengujian Snowline" not in text: raise AssertionError()
        finally:
            os.chdir(cwd)