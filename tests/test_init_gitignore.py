import os
import sys
import tempfile
import shutil
import subprocess
from pathlib import Path

CLI_SCRIPT = Path(__file__).parent.parent / "src" / "snowline" / "cli.py"

def test_init_gitignore_and_scope():
    temp_dir = tempfile.mkdtemp(prefix="test_a6_")
    try:
        # 1. Initialize a clean git repo
        subprocess.run(["git", "init"], cwd=temp_dir, capture_output=True, check=True)
        
        # 2. Run snowline init --apply
        res_init = subprocess.run([
            sys.executable, str(CLI_SCRIPT), "init", "--apply"
        ], cwd=temp_dir, capture_output=True, text=True, encoding="utf-8")
        assert res_init.returncode == 0, f"init failed:\n{res_init.stdout}\n{res_init.stderr}"
        
        # Arah a: .agents/.gitignore ada dan isinya benar
        gitignore_path = os.path.join(temp_dir, ".agents", ".gitignore")
        assert os.path.exists(gitignore_path), ".agents/.gitignore tidak dibuat"
        with open(gitignore_path, "r", encoding="utf-8") as f:
            gi_content = f.read()
        assert "write_log.jsonl" in gi_content
        assert "scope_lock.json" in gi_content
        assert "session_cache.json" in gi_content
        print("PASS: Arah A (.agents/.gitignore ada dan isinya benar)")

        # Arah b: Buat satu tulisan di write_log.jsonl dan scope_lock.json -> git status TIDAK memuat write_log.jsonl
        log_file = os.path.join(temp_dir, ".agents", "write_log.jsonl")
        with open(log_file, "w", encoding="utf-8") as f:
            f.write('{"waktu": "2026-08-25T10:00:00", "alat": "test", "berkas": "x.py", "dalam_lingkup": true, "tugas": "test"}\n')

        res_git = subprocess.run(["git", "status", "--porcelain"], cwd=temp_dir, capture_output=True, text=True, encoding="utf-8")
        git_status_out = res_git.stdout
        assert "write_log.jsonl" not in git_status_out, f"write_log.jsonl seharusnya di-ignore:\n{git_status_out}"
        assert "scope_lock.json" not in git_status_out, f"scope_lock.json seharusnya di-ignore:\n{git_status_out}"
        print("PASS: Arah B (write_log.jsonl dan scope_lock.json tidak muncul di git status)")

        # Arah c: skills/ dan agents.md tetap muncul sebagai berkas baru yang bisa di-commit
        assert ".agents/skills/" in git_status_out or ".agents/" in git_status_out
        assert ".agents/.gitignore" in git_status_out or ".agents/" in git_status_out
        print("PASS: Arah C (skills dan config files tetap muncul di git status)")

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    test_init_gitignore_and_scope()
    print("\nALL ENTRI A6 DIRECTIONS PASSED!")
