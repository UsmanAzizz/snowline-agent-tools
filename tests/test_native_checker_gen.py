import os
import sys
import shutil
import tempfile
import subprocess
from pathlib import Path

AKAR = Path(__file__).parent.parent
SKRIP = AKAR / "src" / "snowline" / "templates" / "skills" / "native_checker_gen" / "generator.py"

def test_native_checker_gen_apply():
    """Menguji bahwa alat tidak menulis tanpa --apply, tapi menulis dengan --apply."""
    temp_dir = tempfile.mkdtemp(prefix="snowline_uji_native_")
    try:
        # 1. Tanpa --apply (dry run)
        subprocess.run(
            [sys.executable, str(SKRIP), "--mode", "validator", "--name", "CekDummy"],
            cwd=temp_dir, check=True
        )
        validator_path = Path(temp_dir) / "scripts" / "validators" / "CekDummy.js"
        assert not validator_path.exists(), "Berkas tertulis padahal tidak ada --apply!"

        # 2. Dengan --apply
        subprocess.run(
            [sys.executable, str(SKRIP), "--mode", "validator", "--name", "CekDummy", "--apply"],
            cwd=temp_dir, check=True
        )
        assert validator_path.exists(), "Berkas TIDAK tertulis padahal ada --apply!"
        assert "CekDummy" in validator_path.read_text(encoding="utf-8"), "Isi berkas salah."
        
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
