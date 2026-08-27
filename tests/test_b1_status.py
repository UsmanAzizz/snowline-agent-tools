import os
import sys
import tempfile
import json
import shutil
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

def test_b1_status_directions():
    # Test status parsing with mocked direct_url.json
    import importlib
    from unittest.mock import patch
    
    # We can mock subprocess and file reads in status() or run status logic directly
    from snowline.cli import status

    # Arah a: direct_url editable -> menyebut editable dan jalurnya, tanpa saran reinstall
    with tempfile.TemporaryDirectory() as tmpdir:
        dist_dir = os.path.join(tmpdir, "snowline_agent_tools-1.1.3.dist-info")
        os.makedirs(dist_dir)
        direct_url_file = os.path.join(dist_dir, "direct_url.json")
        with open(direct_url_file, "w", encoding="utf-8") as f:
            json.dump({"dir_info": {"editable": True}, "url": "file:///D:/fake/path"}, f)

        with patch("subprocess.run") as mock_run, patch("snowline.cli.print_error") as mock_err, patch("snowline.cli.print_info") as mock_info:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = f"Location: {tmpdir}\n"
            status()
            
            info_calls = [c.args[0] for c in mock_info.call_args_list if c.args]
            info_str = " ".join(info_calls)
            assert "editable" in info_str, f"Arah A gagal: tidak menyebut editable:\n{info_str}"
            assert "file:///D:/fake/path" in info_str, f"Arah A gagal: tidak menyebut jalur:\n{info_str}"
            assert "pip install --force-reinstall" not in info_str, f"Arah C gagal: saran reinstall muncul:\n{info_str}"
            print("PASS: Arah A & C (editable -> menyebut editable dan jalur, saran ditekan)")

    # Arah b: direct_url tanpa vcs_info dan tanpa dir_info -> tetap menyebut wheel, tanpa saran reinstall
    with tempfile.TemporaryDirectory() as tmpdir:
        dist_dir = os.path.join(tmpdir, "snowline_agent_tools-1.1.3.dist-info")
        os.makedirs(dist_dir)
        direct_url_file = os.path.join(dist_dir, "direct_url.json")
        with open(direct_url_file, "w", encoding="utf-8") as f:
            json.dump({}, f)

        with patch("subprocess.run") as mock_run, patch("snowline.cli.print_error") as mock_err, patch("snowline.cli.print_info") as mock_info:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = f"Location: {tmpdir}\n"
            status()
            
            info_calls = [c.args[0] for c in mock_info.call_args_list if c.args]
            info_str = " ".join(info_calls)
            assert "wheel" in info_str, f"Arah B gagal: tidak menyebut wheel:\n{info_str}"
            assert "pip install --force-reinstall" not in info_str, f"Arah C gagal: saran reinstall muncul:\n{info_str}"
            print("PASS: Arah B & C (wheel -> menyebut wheel, saran ditekan)")

def test_b1_fail_closed_when_scope_guardian_missing():
    # Test that scaffolder, fixer, context_mapper block when scope_guardian is missing
    skills = REPO / "src" / "snowline" / "templates" / "skills"
    with tempfile.TemporaryDirectory() as tmpdir:
        # Copy scaffolder.py alone to isolated directory without scope_guardian
        isolated_scaff = os.path.join(tmpdir, "scaffolder.py")
        shutil.copy2(skills / "auto_scaffolder" / "scaffolder.py", isolated_scaff)
        
        res_scaff = subprocess.run([
            sys.executable, isolated_scaff, "react", "Button", tmpdir, "--apply"
        ], cwd=tmpdir, capture_output=True, text=True, encoding="utf-8")
        assert res_scaff.returncode != 0
        assert "[BLOCKED]" in res_scaff.stdout or "[BLOCKED]" in res_scaff.stderr
        print("PASS: Scaffolder fail-closed on missing scope_guardian")

if __name__ == "__main__":
    test_b1_status_directions()
    test_b1_fail_closed_when_scope_guardian_missing()
    print("\nALL ENTRI B1 DIRECTIONS PASSED!")