import os
import shutil
import argparse
from pathlib import Path

def init_snowline(dry_run: bool = False):
    """
    Copies the templates directory into the user's current working directory under .agents/skills.
    """
    # Find the templates directory relative to this script
    current_dir = Path(__file__).parent
    templates_dir = current_dir / "templates"
    
    if not templates_dir.exists():
        print(f"[FAIL] Templates directory not found at {templates_dir}")
        return

    # Target directory in the user's project
    target_dir = Path(os.getcwd()) / ".agents" / "skills"
    
    print("[Snowline Agent Tools - Initialization]")
    if dry_run:
        print("[WARN] Running in DRY-RUN mode. No files will be modified.")
        print("To actually apply changes, run: snowline-init --apply\n")
    else:
        print(f"[INFO] Initializing .agents/skills at {target_dir}...\n")
        
    if not dry_run:
        target_dir.mkdir(parents=True, exist_ok=True)
    else:
        print(f"[DRY-RUN] Would create directory: {target_dir}")

    # Process files
    file_count = 0
    dir_count = 0
    
    for root, dirs, files in os.walk(templates_dir):
        # Calculate relative path
        rel_path = Path(root).relative_to(templates_dir)
        target_root = target_dir / rel_path
        
        for d in dirs:
            if d == "__pycache__":
                continue
            target_d = target_root / d
            if not dry_run:
                target_d.mkdir(parents=True, exist_ok=True)
            else:
                print(f"[DRY-RUN] Would create directory: {target_d}")
            dir_count += 1
            
        for f in files:
            if f.endswith(".pyc") or f == ".DS_Store":
                continue
                
            src_file = Path(root) / f
            dest_file = target_root / f
            
            if not dry_run:
                shutil.copy2(src_file, dest_file)
            else:
                print(f"[DRY-RUN] Would copy file: {src_file.name} -> {dest_file}")
            file_count += 1
            
    if dry_run:
        print(f"\n[DRY-RUN] Summary: Would create {dir_count} directories and {file_count} files.")
    else:
        print(f"\n[SUCCESS] Snowline initialized successfully! ({file_count} files, {dir_count} directories)")
        print("Your project is now AI-Ready. Remember to follow the rules in AGENTS.md.")

def main():
    parser = argparse.ArgumentParser(description="Initialize Snowline Agent Ecosystem in the current project.")
    parser.add_argument("--apply", action="store_true", help="Apply changes to disk. Without this flag, it runs a dry-run.")
    args = parser.parse_args()
    
    # By default (no --apply), it's a dry-run
    init_snowline(dry_run=not args.apply)

if __name__ == "__main__":
    main()
