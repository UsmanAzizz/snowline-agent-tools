import os
import sys
import stat

def install_hook(project_dir, guardian_path):
    git_dir = os.path.join(project_dir, '.git')
    if not os.path.exists(git_dir):
        print(f"[FAIL] {project_dir} is not a git repository.")
        return False
        
    hooks_dir = os.path.join(git_dir, 'hooks')
    os.makedirs(hooks_dir, exist_ok=True)
    
    pre_commit_path = os.path.join(hooks_dir, 'pre-commit')
    
    guardian_path_posix = guardian_path.replace('\\', '/')
    
    hook_script = f"""#!/bin/sh
# Snowline Project Guardian Pre-Commit Hook

echo "[Snowline] Menjalankan pemindaian keamanan (Project Guardian)..."

OUTPUT=$(python "{guardian_path_posix}" --json)

CRITICAL_COUNT=$(echo "$OUTPUT" | python -c "import sys, json; data=json.load(sys.stdin); print(data.get('summary', {{}}).get('critical', 0))")

if [ "$CRITICAL_COUNT" -gt 0 ]; then
    echo "[BLOCKED] Project Guardian mendeteksi kerentanan CRITICAL!"
    echo "[BLOCKED] Commit digagalkan. Silakan jalankan 'python {guardian_path_posix}' untuk melihat detailnya."
    exit 1
fi

echo "[Snowline] Pemindaian keamanan lolos. Melanjutkan commit..."
exit 0
"""
    
    with open(pre_commit_path, 'w', encoding='utf-8') as f:
        f.write(hook_script)
        
    st = os.stat(pre_commit_path)
    os.chmod(pre_commit_path, st.st_mode | stat.S_IEXEC)
    
    print(f"[SUCCESS] Pre-commit hook berhasil di-install di {pre_commit_path}")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python install_hooks.py <project_dir> <guardian_py_path>")
        sys.exit(1)
        
    install_hook(sys.argv[1], sys.argv[2])
