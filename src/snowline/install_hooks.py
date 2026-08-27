import os
import sys
import stat
import shutil

def install_hook(project_dir=None, guardian_path=None, force=False, dry=True):
    if project_dir is None:
        project_dir = os.getcwd()
        
    git_dir = os.path.join(project_dir, '.git')
    if not os.path.exists(git_dir):
        print(f"[FAIL] {project_dir} bukan repositori git.")
        return False
        
    hooks_dir = os.path.join(git_dir, 'hooks')
    os.makedirs(hooks_dir, exist_ok=True)
    
    pre_commit_path = os.path.join(hooks_dir, 'pre-commit')
    
    if guardian_path is None:
        guardian_path = os.path.join(project_dir, '.agents', 'skills', 'project_guardian', 'guardian.py')
        
    guardian_path_posix = os.path.abspath(guardian_path).replace('\\', '/')
    
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
    if os.path.exists(pre_commit_path):
        if not force:
            print(f"[BLOCKED] .git/hooks/pre-commit sudah ada. Gunakan --force untuk menimpa.")
            return False
            
    if dry:
        print(f"[DRY RUN] Pre-commit hook akan {'ditimpa' if os.path.exists(pre_commit_path) else 'dipasang'} di {pre_commit_path}")
        print("Jalankan ulang dengan --apply untuk benar-benar memasang.")
        return True

    if os.path.exists(pre_commit_path) and force:
        backup_path = pre_commit_path + ".bak"
        shutil.copyfile(pre_commit_path, backup_path)
        print(f"[INFO] Berkas lama disalin ke {backup_path}")
        
    with open(pre_commit_path, 'w', encoding='utf-8') as f:
        f.write(hook_script)
        
    st = os.stat(pre_commit_path)
    os.chmod(pre_commit_path, st.st_mode | stat.S_IEXEC)
    
    print(f"[SUCCESS] Pre-commit hook berhasil dipasang di {pre_commit_path}")
    return True

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Install Project Guardian pre-commit hook")
    parser.add_argument("--apply", action="store_true", help="Apply installation")
    parser.add_argument("--force", action="store_true", help="Overwrite existing pre-commit hook")
    parser.add_argument("project_dir", nargs="?", default=None, help="Target project directory")
    args = parser.parse_args()
    
    success = install_hook(project_dir=args.project_dir, force=args.force, dry=not args.apply)
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
