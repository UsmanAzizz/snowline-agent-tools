import sys
import json
import subprocess
import os
import tempfile

def run_interceptor(payload_str):
    interceptor_path = os.path.join(os.path.dirname(__file__), "..", "src", "snowline", "templates", "hooks", "intercept_native.py")
    env = os.environ.copy()
    env["PYTHONPATH"] = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
    
    result = subprocess.run(
        [sys.executable, interceptor_path],
        input=payload_str,
        text=True,
        capture_output=True,
        encoding='utf-8',
        env=env,
        cwd=os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src", "snowline", "templates"))
    )
    
    if result.returncode != 0:
        return {"decision": "crash", "output": result.stderr}
    try:
        return json.loads(result.stdout)
    except:
        return {"decision": "crash", "output": result.stdout}

def test_bom_empty_payload():
    payload = "\ufeff{}"
    res = run_interceptor(payload)
    assert res.get("decision") == "deny"
    assert "BOM" in res.get("reason", "") or "tidak valid" in res.get("reason", "")

def test_missing_fields():
    res = run_interceptor('{"toolName":"write_to_file"}')
    assert res.get("decision") == "deny"
    assert "objek toolcall" in res.get("reason", "").lower()

    res2 = run_interceptor('{"toolCall":{"name":"write_to_file", "args":{}}}')
    assert res2.get("decision") == "deny"
    assert "targetfile" in res2.get("reason", "").lower()

def test_malformed_json():
    res = run_interceptor('{"toolCall": ')
    assert res.get("decision") == "deny"
    assert "tidak valid" in res.get("reason", "").lower() or "error" in res.get("reason", "").lower()

def test_missing_scope_lock():
    valid_payload = json.dumps({
        "toolCall": {
            "name": "write_to_file",
            "args": {
                "TargetFile": "some_file.txt"
            }
        }
    })
    res = run_interceptor(valid_payload)
    assert res.get("decision") == "deny"
    assert "scope_lock.json tidak ditemukan" in res.get("reason", "")

def test_in_and_out_of_scope():
    from pathlib import Path
    import shutil
    
    with tempfile.TemporaryDirectory() as temp_dir:
        tmp_path = Path(temp_dir)
        agents_dir = tmp_path / ".agents"
        agents_dir.mkdir()
    
        hooks_dir = agents_dir / "hooks"
        hooks_dir.mkdir()
    
        interceptor_src = os.path.join(os.path.dirname(__file__), "..", "src", "snowline", "templates", "hooks", "intercept_native.py")
        shutil.copy(interceptor_src, hooks_dir / "intercept_native.py")
    
        rules_dir = agents_dir / "skills" / "scope_guardian" / "scripts"
        rules_dir.mkdir(parents=True)
        scope_check_src = os.path.join(os.path.dirname(__file__), "..", "src", "snowline", "templates", "skills", "scope_guardian", "scripts", "scope_check.py")
        shutil.copy(scope_check_src, rules_dir / "scope_check.py")
    
        lock_data = {
            "allowed_files": ["src/allowed.txt"],
            "allowed_patterns": []
        }
        with open(agents_dir / "scope_lock.json", "w") as f:
            json.dump(lock_data, f)
    
        def run_dummy(target_file):
            payload = json.dumps({
                "toolCall": {
                    "name": "write_to_file",
                    "args": {
                        "TargetFile": target_file
                    }
                }
            })
            result = subprocess.run(
                [sys.executable, str(hooks_dir / "intercept_native.py")],
                input=payload,
                text=True,
                capture_output=True,
                encoding='utf-8',
                cwd=str(agents_dir.parent)
            )
            return json.loads(result.stdout)
    
        res_in = run_dummy("src/allowed.txt")
        assert res_in.get("decision") == "allow"
    
        res_out = run_dummy("src/blocked.txt")
        assert res_out.get("decision") == "deny"
        assert "OUT OF SCOPE" in res_out.get("reason", "")