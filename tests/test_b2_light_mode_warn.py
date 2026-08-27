import os
import sys
import tempfile
import json
import shutil
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILLS = REPO / "src" / "snowline" / "templates" / "skills"

def test_b2_single_warning_when_mode_ringan_corrupt_or_unrecognized():
    with tempfile.TemporaryDirectory() as tmpdir:
        agents = os.path.join(tmpdir, ".agents")
        os.makedirs(agents)
        marker = os.path.join(agents, "mode_ringan.json")
        with open(marker, "w", encoding="utf-8") as f:
            f.write('{"mode_ringan": "not_a_bool"}')

        src_dir = os.path.join(tmpdir, "src")
        os.makedirs(src_dir)
        test_file = os.path.join(src_dir, "test.py")
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("val = 1\n")

        # Run replace_text.py with --apply
        res = subprocess.run([
            sys.executable, str(SKILLS / "smart_replace" / "replace_text.py"),
            test_file, "val = 1", "val = 2", "--apply"
        ], cwd=tmpdir, capture_output=True, text=True, encoding="utf-8")

        output = res.stdout + "\n" + res.stderr
        warn_count = output.count("Mode ringan dimatikan")
        assert warn_count == 1, f"Peringatan mode ringan diharapkan muncul 1 kali, tapi muncul {warn_count} kali:\n{output}"
        print("PASS: Peringatan mode ringan tercetak tepat 1 kali pada replace_text")

        # Also test with scope_check.py alone
        res_sc = subprocess.run([
            sys.executable, str(SKILLS / "scope_guardian" / "scripts" / "scope_check.py"),
            test_file
        ], cwd=tmpdir, capture_output=True, text=True, encoding="utf-8")
        sc_output = res_sc.stdout + "\n" + res_sc.stderr
        warn_count_sc = sc_output.count("Mode ringan dimatikan")
        assert warn_count_sc == 1, f"Peringatan mode ringan pada scope_check diharapkan 1 kali, muncul {warn_count_sc} kali:\n{sc_output}"
        print("PASS: Peringatan mode ringan tercetak tepat 1 kali pada scope_check")

if __name__ == "__main__":
    test_b2_single_warning_when_mode_ringan_corrupt_or_unrecognized()
    print("\nALL ENTRI B2 DIRECTIONS PASSED!")