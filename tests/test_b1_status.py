import os
import sys
import tempfile
import json
import shutil
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "src"))

def test_b1_status_directions():
    from snowline.cli import status

    # Arah a: direct_url editable -> menyebut editable dan jalurnya, tanpa saran reinstall
    with patch("snowline.cli.get_installed_package_info") as mock_pkg, \
         patch("snowline.cli.fetch_remote_package_info") as mock_remote, \
         patch("snowline.cli.print_error") as mock_err, \
         patch("snowline.cli.print_info") as mock_info:
        
        mock_pkg.return_value = {
            "commit": None,
            "version": "1.2.0",
            "unknown_kind": "editable",
            "unknown_reason": "dipasang dalam mode editable (menunjuk ke file:///D:/fake/path)",
        }
        mock_remote.return_value = {"head_commit": "12345678", "latest_tag_commit": None, "latest_tag_name": None}
        
        status()
        
        info_calls = [c.args[0] for c in mock_info.call_args_list if c.args]
        info_str = " ".join(info_calls)
        assert "editable" in info_str, f"Arah A gagal: tidak menyebut editable:\n{info_str}"
        assert "file:///D:/fake/path" in info_str, f"Arah A gagal: tidak menyebut jalur:\n{info_str}"
        assert "pip install --force-reinstall" not in info_str, f"Arah C gagal: saran reinstall muncul:\n{info_str}"
        print("PASS: Arah A & C (editable -> menyebut editable dan jalur, saran ditekan)")

    # Arah b: direct_url tanpa vcs_info dan tanpa dir_info -> tetap menyebut wheel, tanpa saran reinstall
    with patch("snowline.cli.get_installed_package_info") as mock_pkg, \
         patch("snowline.cli.fetch_remote_package_info") as mock_remote, \
         patch("snowline.cli.print_error") as mock_err, \
         patch("snowline.cli.print_info") as mock_info:
        
        mock_pkg.return_value = {
            "commit": None,
            "version": "1.2.0",
            "unknown_kind": "wheel",
            "unknown_reason": "direct_url.json ada tetapi tanpa vcs_info (dipasang dari wheel, bukan dari git)",
        }
        mock_remote.return_value = {"head_commit": "12345678", "latest_tag_commit": None, "latest_tag_name": None}
        
        status()
        
        info_calls = [c.args[0] for c in mock_info.call_args_list if c.args]
        info_str = " ".join(info_calls)
        assert "wheel" in info_str, f"Arah B gagal: tidak menyebut wheel:\n{info_str}"
        assert "pip install --force-reinstall" not in info_str, f"Arah C gagal: saran reinstall muncul:\n{info_str}"
        print("PASS: Arah B & C (wheel -> menyebut wheel, saran ditekan)")

def test_b1_fail_closed_when_scope_guardian_missing():
    skills = REPO / "src" / "snowline" / "templates" / "skills"
    with tempfile.TemporaryDirectory() as tmpdir:
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
