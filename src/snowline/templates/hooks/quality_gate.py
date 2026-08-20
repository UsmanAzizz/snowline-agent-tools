import sys
import json
import subprocess
import os
import platform

def main():
    try:
        input_data = json.load(sys.stdin)
    except Exception:
        print(json.dumps({"decision": "allow"}))
        return

    tool_name = input_data.get("toolName", "")
    tool_call = input_data.get("toolCall", {})
    
    # Deteksi eksekusi shell command
    if tool_name == "run_command" or "CommandLine" in tool_call:
        cmd = tool_call.get("CommandLine", "")
        
        # Intersepsi komando commit
        if "git commit" in cmd:
            workspace_paths = input_data.get("workspacePaths", [])
            if workspace_paths:
                # the path could be a URI starting with file:///, so clean it
                target_cwd = workspace_paths[0]
                if target_cwd.startswith("file:///"):
                    target_cwd = target_cwd[8:]
                    if platform.system() != "Windows":
                        target_cwd = "/" + target_cwd
                    else:
                        target_cwd = target_cwd.replace("%3A", ":").replace("/", "\\")
                        
                # Jalankan guardian secara sinkronus di background
                guardian_script = os.path.join(target_cwd, ".agents", "skills", "project_guardian", "guardian.py")
                
                if os.path.exists(guardian_script):
                    try:
                        # Jalankan dalam mode JSON
                        result = subprocess.run(
                            ["python", guardian_script, "--json"], 
                            cwd=target_cwd, 
                            capture_output=True, 
                            text=True
                        )
                        
                        if result.stdout:
                            try:
                                guardian_out = json.loads(result.stdout)
                                critical_count = guardian_out.get("summary", {}).get("critical", 0)
                                
                                # JEDA PAKSA (ARAH 6)
                                if critical_count > 0:
                                    print(json.dumps({
                                        "decision": "deny",
                                        "reason": f"[JEDA PAKSA - ARAH 6] project_guardian menemukan {critical_count} isu CRITICAL! Anda dilarang melakukan commit sebelum memperbaikinya atau menyertakan penanda abaikan (// guardian-ignore)."
                                    }))
                                    return
                            except json.JSONDecodeError:
                                print(json.dumps({
                                    "decision": "deny",
                                    "reason": f"[JEDA PAKSA - ARAH 6] Output guardian tidak valid (JSON error)."
                                }))
                                return
                        else:
                            print(json.dumps({
                                "decision": "deny",
                                "reason": f"[JEDA PAKSA - ARAH 6] project_guardian tidak menghasilkan output (returncode={result.returncode}, stderr={result.stderr})."
                            }))
                            return
                    except Exception as e:
                        # Gagal menjalankan guardian, GAGAL-TERTUTUP (DENY)
                        print(json.dumps({
                            "decision": "deny",
                            "reason": f"[JEDA PAKSA - ARAH 6] Gagal memvalidasi repositori dengan project_guardian (Exception: {str(e)}). Eksekusi ditolak untuk mencegah commit tanpa audit."
                        }))
                        return
                else:
                    # Guardian script tidak ditemukan, GAGAL-TERTUTUP (DENY)
                    print(json.dumps({
                        "decision": "deny",
                        "reason": "[JEDA PAKSA - ARAH 6] project_guardian/guardian.py tidak ditemukan di workspace ini. Eksekusi ditolak karena audit tidak bisa dilakukan."
                    }))
                    return
            else:
                # Tidak ada workspace_paths, GAGAL-TERTUTUP (DENY)
                print(json.dumps({
                    "decision": "deny",
                    "reason": "[JEDA PAKSA - ARAH 6] Parameter workspacePaths tidak ditemukan dalam konteks hook. Eksekusi ditolak karena lingkungan gagal diverifikasi."
                }))
                return

    # Jika aman atau bukan commit, izinkan eksekusi
    print(json.dumps({"decision": "allow"}))

if __name__ == "__main__":
    main()
