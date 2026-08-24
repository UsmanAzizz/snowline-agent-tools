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
    # Test 1: Clean directory should PASS
    with tempfile.TemporaryDirectory() as tmpdir:
        script = SKILLS / "project_guardian" / "guardian.py"
        result_pass = subprocess.run([sys.executable, str(script), "--json"], cwd=tmpdir, capture_output=True, text=True, encoding='utf-8')
        assert '"status": "PASS"' in result_pass.stdout, "Guardian did not accept a clean directory"
        
        # Test 2: Dirty directory should FAIL
        dummy_file = os.path.join(tmpdir, 'secret.js')
        with open(dummy_file, 'w') as f:
            f.write("const password = 'my_super_secret_password';\n")
        
        result_fail = subprocess.run([sys.executable, str(script), "--json"], cwd=tmpdir, capture_output=True, text=True, encoding='utf-8')
        assert '"status": "FAIL"' in result_fail.stdout, "Guardian did not reject exposed secret"
        assert 'CRITICAL' in result_fail.stdout, "Guardian did not flag secret as CRITICAL"

def test_quality_gate_rejection():
    # Arity check should fail without required args
    script = HOOKS / "quality_gate.py"
    with tempfile.TemporaryDirectory() as tmpdir:
        input_data = '{"toolName": "run_command", "toolCall": {"CommandLine": "python .agents/skills/import_fixer/fixer.py dummy_file"}, "workspacePaths": ["' + tmpdir.replace('\\', '\\\\') + '"]}'
        result = subprocess.run([sys.executable, str(script)], capture_output=True, text=True, input=input_data)
        assert '"decision": "deny"' in result.stdout, "Quality gate did not reject"
        assert "Parameter kritis tidak lengkap" in result.stdout, "Quality gate rejected for the wrong reason (not arity check)"

        # Mock companion to avoid import error
        companion_dir = os.path.join(tmpdir, '.agents', 'skills', 'companion')
        os.makedirs(companion_dir)
        with open(os.path.join(companion_dir, 'core_intent.py'), 'w') as f:
            f.write("class MockAnalysis:\n    confidence_level = 'HIGH'\n    clarification_note = ''\n\ndef analyze_intent(text):\n    return MockAnalysis()\n")

        # Arity check should accept with required args
        input_data_accept = '{"toolName": "run_command", "toolCall": {"CommandLine": "python .agents/skills/import_fixer/fixer.py dummy_file dummy_import --apply"}, "workspacePaths": ["' + tmpdir.replace('\\', '\\\\') + '"]}'
        result_accept = subprocess.run([sys.executable, str(script)], capture_output=True, text=True, input=input_data_accept)
        assert '"decision": "allow"' in result_accept.stdout, "Quality gate did not accept complete parameters"

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
    # Should reject writing if --apply is not passed, but write if passed
    script = SKILLS / "auto_scaffolder" / "scaffolder.py"
    with tempfile.TemporaryDirectory() as tmpdir:
        # Buat fake scope_lock.json agar tidak diblokir scope_guardian
        agents_dir = os.path.join(tmpdir, '.agents')
        os.makedirs(agents_dir)
        with open(os.path.join(agents_dir, 'scope_lock.json'), 'w') as f:
            f.write('{"task_id": "1", "task_description": "test", "allowed_files": ["MyButton.jsx"], "allowed_patterns": []}')

        # Test 1: Reject without --apply (dry-run)
        result_reject = subprocess.run([sys.executable, str(script), "react", "MyButton", tmpdir], cwd=tmpdir, capture_output=True, text=True, encoding='utf-8')
        assert result_reject.returncode == 0
        assert "tanpa flag --apply" in result_reject.stdout or "run again with --apply" in result_reject.stdout or "tambahan flag --apply" in result_reject.stdout, "Scaffolder did not output dry-run warning"
        assert not os.path.exists(os.path.join(tmpdir, "MyButton.jsx")), "Scaffolder wrote file without --apply"

        # Test 2: Accept with --apply
        result_accept = subprocess.run([sys.executable, str(script), "react", "MyButton", tmpdir, "--apply"], cwd=tmpdir, capture_output=True, text=True, encoding='utf-8')
        assert result_accept.returncode == 0
        assert os.path.exists(os.path.join(tmpdir, "MyButton.jsx")), "Scaffolder did not write file with --apply"

def test_import_fixer_rejection():
    # Should reject writing if --apply is not passed, but write if passed
    script = SKILLS / "import_fixer" / "fixer.py"
    with tempfile.TemporaryDirectory() as tmpdir:
        # Buat fake scope_lock.json agar tidak diblokir scope_guardian
        agents_dir = os.path.join(tmpdir, '.agents')
        os.makedirs(agents_dir)
        with open(os.path.join(agents_dir, 'scope_lock.json'), 'w') as f:
            f.write('{"task_id": "1", "task_description": "test", "allowed_files": ["dummy.js"], "allowed_patterns": []}')

        # Bikin target file 'foo.js' agar tidak gagal lebih awal
        with open(os.path.join(tmpdir, 'foo.js'), 'w') as f:
            f.write("export default {};\n")

        dummy_file = os.path.join(tmpdir, 'dummy.js')
        original_content = "import foo from '../foo';\n"
        with open(dummy_file, 'w') as f:
            f.write(original_content)
        
        # Test 1: Reject without --apply (dry-run)
        result_reject = subprocess.run([sys.executable, str(script), dummy_file, "../foo"], cwd=tmpdir, capture_output=True, text=True, encoding='utf-8')
        assert "tambahan flag --apply" in result_reject.stdout or "DRY RUN" in result_reject.stdout, "Import fixer did not output dry-run warning"
        with open(dummy_file, 'r') as f:
            assert f.read() == original_content, "Import fixer modified file without --apply"

        # Test 2: Accept with --apply
        result_accept = subprocess.run([sys.executable, str(script), dummy_file, "../foo", "--apply"], cwd=tmpdir, capture_output=True, text=True, encoding='utf-8')
        with open(dummy_file, 'r') as f:
            assert f.read() != original_content, "Import fixer did not modify file with --apply"

if __name__ == '__main__':
    print("Testing rejections...")
    test_project_guardian_rejection()
    test_quality_gate_rejection()
    test_loop_detector_rejection()
    test_rollback_enforcer_rejection()
    test_auto_scaffolder_rejection()
    test_import_fixer_rejection()
    print("All rejection tests passed!")
