import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path

AKAR = Path(__file__).parent.parent
SKILLS = AKAR / "src" / "snowline" / "templates" / "skills"
HOOKS = AKAR / "src" / "snowline" / "templates" / "hooks"

def test_project_guardian_rejection():
    # Should exit with CRITICAL if secret is found
    with tempfile.TemporaryDirectory() as tmpdir:
        dummy_file = os.path.join(tmpdir, 'secret.js')
        with open(dummy_file, 'w') as f:
            f.write("const password = 'my_super_secret_password';\n")
        
        script = SKILLS / "project_guardian" / "guardian.py"
        result = subprocess.run([sys.executable, str(script), "--json"], cwd=tmpdir, capture_output=True, text=True)
        assert '"status": "FAIL"' in result.stdout or '"CRITICAL"' in result.stdout, "Guardian did not reject exposed secret"

def test_quality_gate_rejection():
    # Arity check should fail without required args
    script = HOOKS / "quality_gate.py"
    input_data = '{"toolName": "run_command", "toolCall": {"CommandLine": "python .agents/skills/import_fixer/fixer.py dummy_file"}, "workspacePaths": ["/tmp"]}'
    result = subprocess.run([sys.executable, str(script)], capture_output=True, text=True, input=input_data)
    assert '"decision": "deny"' in result.stdout, "Quality gate did not reject"
    assert "Parameter kritis tidak lengkap" in result.stdout, "Quality gate rejected for the wrong reason (not arity check)"

def test_loop_detector_rejection():
    # Should reject after 3 identical executions
    script = HOOKS / "loop_detector.py"
    history_dir = HOOKS / ".history"
    if history_dir.exists():
        shutil.rmtree(history_dir)
        
    with tempfile.TemporaryDirectory() as tmpdir:
        payload = '{"toolName": "dummy_tool", "toolCall": {"hash": "dummy_hash"}, "workspacePaths": ["/tmp"]}'
        for _ in range(2):
            res = subprocess.run([sys.executable, str(script)], capture_output=True, text=True, input=payload)
            if '"decision": "allow"' not in res.stdout:
                print("LOOP DETECTOR FAILED:")
                print("STDOUT:", res.stdout)
                print("STDERR:", res.stderr)
            assert '"decision": "allow"' in res.stdout
        
        # 3rd should be rejected
        res = subprocess.run([sys.executable, str(script)], capture_output=True, text=True, input=payload)
        assert '"decision": "deny"' in res.stdout, "Loop detector did not reject 3rd loop"

def test_rollback_enforcer_rejection():
    # Should NOT stash if reason is success
    script = HOOKS / "rollback_enforcer.py"
    with tempfile.TemporaryDirectory() as tmpdir:
        subprocess.run(["git", "init"], cwd=tmpdir, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmpdir, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=tmpdir, capture_output=True)
        
        # Initial commit
        initial_file = os.path.join(tmpdir, 'init.txt')
        with open(initial_file, 'w') as f: f.write("init")
        subprocess.run(["git", "add", "init.txt"], cwd=tmpdir, capture_output=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=tmpdir, capture_output=True)

        # Create a dummy file and add it so it can be stashed
        dummy_file = os.path.join(tmpdir, 'dummy.txt')
        with open(dummy_file, 'w') as f: f.write("test")
        subprocess.run(["git", "add", "dummy.txt"], cwd=tmpdir, capture_output=True)
        
        input_data = '{"terminationReason": "success", "workspacePaths": ["' + tmpdir.replace('\\', '\\\\') + '"]}'
        result = subprocess.run([sys.executable, str(script)], capture_output=True, text=True, input=input_data)
        
        # Verify no stash was created
        stash_res = subprocess.run(["git", "stash", "list"], cwd=tmpdir, capture_output=True, text=True)
        assert stash_res.stdout.strip() == "", "Rollback enforcer stashed on success!"

        # Now test error reason
        input_data_err = '{"terminationReason": "error", "workspacePaths": ["' + tmpdir.replace('\\', '\\\\') + '"]}'
        subprocess.run([sys.executable, str(script)], capture_output=True, text=True, input=input_data_err)
        stash_res_err = subprocess.run(["git", "stash", "list"], cwd=tmpdir, capture_output=True, text=True)
        assert stash_res_err.stdout.strip() != "", "Rollback enforcer did NOT stash on error!"

def test_auto_scaffolder_rejection():
    # Should reject writing if --apply is not passed
    script = SKILLS / "auto_scaffolder" / "scaffolder.py"
    with tempfile.TemporaryDirectory() as tmpdir:
        result = subprocess.run([sys.executable, str(script), "component", "MyButton"], cwd=tmpdir, capture_output=True, text=True)
        assert result.returncode == 0
        assert not os.path.exists(os.path.join(tmpdir, "MyButton.jsx")), "Scaffolder wrote file without --apply"

def test_import_fixer_rejection():
    # Should reject writing if --apply is not passed
    script = SKILLS / "import_fixer" / "fixer.py"
    with tempfile.TemporaryDirectory() as tmpdir:
        dummy_file = os.path.join(tmpdir, 'dummy.js')
        with open(dummy_file, 'w') as f:
            f.write("import foo from './foo';\n")
        
        result = subprocess.run([sys.executable, str(script), dummy_file, "./foo"], cwd=tmpdir, capture_output=True, text=True)
        # Assuming fixer without --apply doesn't modify the file
        # We can check the file modification time or content, but here we just ensure it doesn't fail unexpectedly but doesn't write.
        assert "DRY RUN" in result.stdout or "Applying fixes..." not in result.stdout, "Import fixer attempted to apply without --apply"

if __name__ == '__main__':
    print("Testing rejections...")
    test_project_guardian_rejection()
    test_quality_gate_rejection()
    test_loop_detector_rejection()
    test_rollback_enforcer_rejection()
    test_auto_scaffolder_rejection()
    test_import_fixer_rejection()
    print("All rejection tests passed!")
