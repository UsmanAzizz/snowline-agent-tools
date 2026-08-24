import sys
import json
import os
import subprocess

def main():
    try:
        raw_data = sys.stdin.read()
        if not raw_data.strip():
            print(json.dumps({"decision": "deny", "reason": "[BLOCKED] Payload kosong"}))
            sys.exit(0)
            
        try:
            input_data = json.loads(raw_data)
        except json.JSONDecodeError as e:
            # Ini menangkap kasus BOM+{} atau JSON rusak
            print(json.dumps({"decision": "deny", "reason": f"[BLOCKED] JSON tidak valid atau terdapat karakter tak lazim (BOM): {e}"}))
            sys.exit(0)
            
        tool_call = input_data.get('toolCall')
        if not isinstance(tool_call, dict):
            print(json.dumps({"decision": "deny", "reason": "[BLOCKED] Objek toolCall tidak ditemukan atau bukan dictionary"}))
            sys.exit(0)
            
        # Menangani kedua bentuk (run_command via input_data vs alat native via toolCall.name)
        tool_name = input_data.get('toolName') or tool_call.get('name')
        if not tool_name:
            print(json.dumps({"decision": "deny", "reason": "[BLOCKED] Nama tool (toolName / toolCall.name) tidak ditemukan"}))
            sys.exit(0)
            
        args = tool_call.get('args')
        if not isinstance(args, dict):
            print(json.dumps({"decision": "deny", "reason": "[BLOCKED] Objek args tidak ditemukan di dalam toolCall"}))
            sys.exit(0)
            
        target_file = args.get('TargetFile')
        if not target_file:
            print(json.dumps({"decision": "deny", "reason": "[BLOCKED] Parameter TargetFile tidak ditemukan di dalam toolCall.args"}))
            sys.exit(0)
            
        # Pengecekan scope_lock.json
        scope_script = os.path.join(os.path.dirname(__file__), "..", "skills", "scope_guardian", "scripts", "scope_check.py")
        if not os.path.exists(scope_script):
            print(json.dumps({"decision": "deny", "reason": "[BLOCKED] Skrip scope_check.py tidak ditemukan. Integritas sistem terganggu."}))
            sys.exit(0)
            
        scope_lock_path = os.path.join(os.path.dirname(__file__), "..", "scope_lock.json")
        if not os.path.exists(scope_lock_path):
            print(json.dumps({"decision": "deny", "reason": "[BLOCKED] scope_lock.json tidak ditemukan di .agents/. Harap buat lock ini sebelum menulis berkas apa pun."}))
            sys.exit(0)
            
        # Menjalankan pengecekan
        result = subprocess.run(
            [sys.executable, scope_script, target_file],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(json.dumps({"decision": "allow"}))
        else:
            print(json.dumps({
                "decision": "deny",
                "reason": f"[BLOCKED] File '{target_file}' is OUT OF SCOPE.\n{result.stdout.strip()}\n{result.stderr.strip()}"
            }))
            
    except Exception as e:
        # Gagal-tertutup mutlak
        print(json.dumps({"decision": "deny", "reason": f"[BLOCKED] Error internal pada gerbang native: {e}"}))
        sys.exit(0)

if __name__ == "__main__":
    main()
