import os
import sys
import tempfile
import json
import shutil
import subprocess
from pathlib import Path

QG_SCRIPT = Path(__file__).parent.parent / "src" / "snowline" / "templates" / "hooks" / "quality_gate.py"

def run_qg(payload, cwd):
    res = subprocess.run(
        [sys.executable, str(QG_SCRIPT)],
        input=json.dumps(payload),
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8"
    )
    try:
        return json.loads(res.stdout.strip())
    except Exception:
        return {"decision": "error", "raw": res.stdout, "stderr": res.stderr}

def test_shell_tracking_directions():
    temp_dir = tempfile.mkdtemp(prefix="test_a3_")
    try:
        agents = os.path.join(temp_dir, ".agents")
        os.makedirs(agents)
        with open(os.path.join(agents, "scope_lock.json"), "w", encoding="utf-8") as f:
            json.dump({"task": "shell test", "allowed_files": ["app.js"], "allowed_patterns": []}, f)
            
        log_file = os.path.join(agents, "write_log.jsonl")

        # Arah b: Perintah baca-saja (ls) -> TIDAK tercatat
        payload_ls = {
            "toolName": "run_command",
            "toolCall": {"CommandLine": "ls -la"},
            "workspacePaths": [temp_dir]
        }
        res_ls = run_qg(payload_ls, temp_dir)
        assert res_ls.get("decision") == "allow"
        assert not os.path.exists(log_file), "Arah B gagal: ls tercatat di write_log.jsonl"
        print("PASS: Arah B (perintah baca-saja tidak tercatat)")

        # Arah a: Set-Content ke berkas -> tercatat, TIDAK diblokir
        payload_sc = {
            "toolName": "run_command",
            "toolCall": {"CommandLine": 'Set-Content -Path app.js -Value "console.log(1)"'},
            "workspacePaths": [temp_dir]
        }
        res_sc = run_qg(payload_sc, temp_dir)
        assert res_sc.get("decision") == "allow", f"Arah A gagal: diblokir ({res_sc})"
        assert os.path.exists(log_file), "Arah A gagal: write_log.jsonl tidak dibuat"
        with open(log_file, "r", encoding="utf-8") as f:
            lines = [json.loads(l) for l in f if l.strip()]
        assert len(lines) == 1, f"Harusnya 1 log, dapat {len(lines)}"
        assert lines[0]["alat"] == "shell"
        assert lines[0]["berkas"] == "app.js"
        assert lines[0]["dalam_lingkup"] is True
        print("PASS: Arah A (Set-Content tercatat dan diizinkan)")

        # Arah c: Perintah yang ditolak / gagal -> tidak tercatat sebagai tulisan berhasil
        # Misalnya smart_replace dengan parameter tidak lengkap (ditolak Companion Gate)
        payload_fail = {
            "toolName": "run_command",
            "toolCall": {"CommandLine": 'python .agents/skills/smart_replace/replace_text.py > out.txt'},
            "workspacePaths": [temp_dir]
        }
        res_fail = run_qg(payload_fail, temp_dir)
        assert res_fail.get("decision") == "deny", "Seharusnya ditolak oleh companion gate"
        with open(log_file, "r", encoding="utf-8") as f:
            lines = [json.loads(l) for l in f if l.strip()]
        assert len(lines) == 1, "Arah C gagal: perintah yang ditolak ikut tercatat"
        print("PASS: Arah C (perintah gagal tidak tercatat)")

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    test_shell_tracking_directions()
    print("\nALL ENTRI A3 DIRECTIONS PASSED!")