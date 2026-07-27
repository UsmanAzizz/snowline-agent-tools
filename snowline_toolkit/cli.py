import os
import shutil
import argparse
import filecmp
from datetime import datetime
from pathlib import Path
import sysconfig

def is_symlink_or_junction(path):
    if not os.path.exists(path):
        return False
    if os.path.islink(path):
        return True
    if hasattr(os.path, 'isjunction') and os.path.isjunction(path):
        return True
    import stat
    try:
        attrs = os.stat(path, follow_symlinks=False).st_file_attributes
        return bool(attrs & stat.FILE_ATTRIBUTE_REPARSE_POINT)
    except AttributeError:
        pass
    return False

def check_and_update_path(dry_run: bool):
    if os.name != 'nt':
        return
    
    scripts_path = sysconfig.get_path('scripts')
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_READ | winreg.KEY_WRITE)
        current_path, _ = winreg.QueryValueEx(key, "Path")
        normalized_target = os.path.normpath(scripts_path).lower()
        normalized_paths = [os.path.normpath(p.strip()).lower() for p in current_path.split(';') if p.strip()]
        
        if normalized_target not in normalized_paths:
            if dry_run:
                print(f"[DRY-RUN] Would prompt to add '{scripts_path}' to your User PATH Registry.")
            else:
                print(f"\n[WARN] The directory '{scripts_path}' is NOT in your User PATH.")
                print("Without this, the 'snowline' command will not be recognized by your terminal.")
                ans = input("Do you want to automatically add it to your User PATH Registry now? (y/n): ")
                if ans.lower() == 'y':
                    new_path = f"{scripts_path};{current_path}"
                    winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, new_path)
                    print("[SUCCESS] PATH berhasil diupdate. Harap RESTART terminal Anda agar perintah 'snowline' dikenali tanpa awalan.")
                else:
                    print("[INFO] Skipped PATH modification. You must add it manually.")
        winreg.CloseKey(key)
    except Exception as e:
        print(f"[WARN] Gagal mengecek/mengupdate PATH otomatis: {e}")

def check_and_scaffold_agents_md(dry_run: bool):
    cwd = Path(os.getcwd())
    agents_md = cwd / ".agents" / "AGENTS.md"
    template = Path(__file__).parent / "templates" / "AGENTS_TEMPLATE.md"
    
    if not template.exists():
        return

    needs_update = False
    if not agents_md.exists():
        needs_update = True
    else:
        try:
            with open(agents_md, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if len(lines) < 10:
                    needs_update = True
        except:
            needs_update = True
            
    if needs_update:
        if dry_run:
            print(f"[DRY-RUN] Would auto-scaffold {agents_md.relative_to(cwd)} (file missing or too short)")
        else:
            agents_md.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(template, agents_md)
            print(f"[INFO] Auto-scaffolded {agents_md.relative_to(cwd)} from template.")

def init_snowline(dry_run: bool = False):
    current_dir = Path(__file__).parent
    templates_dir = current_dir / "templates"
    
    if not templates_dir.exists():
        print(f"[FAIL] Templates directory not found at {templates_dir}")
        return

    target_dir = Path(os.getcwd()) / ".agents" / "skills"
    
    print("[Snowline Agent Tools - Initialization]")
    if dry_run:
        print("[WARN] Running in DRY-RUN mode. No files will be modified.")
        print("To actually apply changes, run: snowline init --apply\n")
    else:
        print(f"[INFO] Initializing .agents/skills at {target_dir}...\n")
        
    if not dry_run:
        target_dir.mkdir(parents=True, exist_ok=True)
    else:
        print(f"[DRY-RUN] Would create directory: {target_dir}")

    file_count = 0
    dir_count = 0
    
    for root, dirs, files in os.walk(templates_dir):
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
        
    check_and_scaffold_agents_md(dry_run)
    check_and_update_path(dry_run)

def update_snowline(dry_run: bool = False):
    target_dir = Path(os.getcwd()) / ".agents" / "skills"
    if not target_dir.exists():
        print("[FAIL] .agents/skills directory not found. Please run 'snowline init' first.")
        return

    print("[Snowline Agent Tools - Update]")
    if is_symlink_or_junction(str(target_dir)):
        print("[INFO] Project ini menggunakan symlink. Tidak perlu melakukan update lokal — cukup jalankan 'git pull' di folder sumber (open_source_agents), dan semua project yang symlink ke situ otomatis dapat versi terbaru.")
        return

    current_dir = Path(__file__).parent
    templates_dir = current_dir / "templates"
    
    if dry_run:
        print("[WARN] Running in DRY-RUN mode. No files will be modified.")
        print("To actually apply changes, run: snowline update --apply\n")
    else:
        print(f"[INFO] Updating .agents/skills at {target_dir}...\n")

    diff_files = []
    new_files = []
    
    for root, dirs, files in os.walk(templates_dir):
        rel_path = Path(root).relative_to(templates_dir)
        target_root = target_dir / rel_path
        
        for f in files:
            if f.endswith(".pyc") or f == ".DS_Store":
                continue
            src_file = Path(root) / f
            dest_file = target_root / f
            
            if not dest_file.exists():
                new_files.append((src_file, dest_file))
            elif not filecmp.cmp(src_file, dest_file, shallow=False):
                diff_files.append((src_file, dest_file))

    if not diff_files and not new_files:
        print("[OK] All files are up to date.")
        return
        
    print(f"Found {len(new_files)} new files and {len(diff_files)} modified files.")
    
    for _, dest in new_files:
        print(f"  [NEW] {dest.relative_to(os.getcwd())}")
    for _, dest in diff_files:
        print(f"  [MODIFIED] {dest.relative_to(os.getcwd())}")
        
    if dry_run:
        print("\n[DRY-RUN] Use --apply to execute the update.")
        return

    backup_dir = Path(os.getcwd()) / ".backup_replace" / datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n[INFO] Creating backups in {backup_dir}...")
    for _, dest in diff_files:
        rel_path = dest.relative_to(os.getcwd())
        backup_path = backup_dir / rel_path
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(dest, backup_path)

    for src, dest in new_files + diff_files:
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        
    print("\n[SUCCESS] Snowline update completed successfully!")

def uninstall_snowline(dry_run: bool = False):
    target_dir = Path(os.getcwd()) / ".agents" / "skills"
    
    print("[Snowline Agent Tools - Uninstall]")
    if dry_run:
        print("[WARN] Running in DRY-RUN mode. No files will be deleted.")
        print("To actually apply changes, run: snowline uninstall --apply\n")
    
    to_delete = []
    if target_dir.exists():
        to_delete.append(target_dir)

    if not to_delete:
        print("[OK] No Snowline skills found to uninstall.")
        return

    if dry_run:
        print("The following directories will be deleted:")
        for d in to_delete:
            print(f"  - {d.relative_to(os.getcwd())}")
            
        print("\nNote: PLAN.md, plan_archive/, and AGENTS.md will NOT be deleted by default.")
        print("If you want to remove history files as well, you will be prompted when running with --apply.")
        return
        
    print("The following directories will be deleted:")
    for d in to_delete:
        print(f"  - {d.relative_to(os.getcwd())}")
        
    ans = input("Do you want to proceed? (y/n): ")
    if ans.lower() != 'y':
        print("Aborted.")
        return
        
    ans2 = input("Do you also want to remove PLAN.md, plan_archive/, and AGENTS.md? (y/n): ")
    
    for d in to_delete:
        if is_symlink_or_junction(str(d)):
            try:
                import _winapi
                _winapi.RemoveDirectory(str(d))
            except Exception:
                os.rmdir(d)
        else:
            shutil.rmtree(d)
        print(f"Deleted {d.relative_to(os.getcwd())}")
        
    if ans2.lower() == 'y':
        plan = Path(os.getcwd()) / "PLAN.md"
        plan_arc = Path(os.getcwd()) / "plan_archive"
        agents = Path(os.getcwd()) / ".agents" / "AGENTS.md"
        
        for item in [plan, plan_arc, agents]:
            if item.exists():
                if item.is_file():
                    item.unlink()
                else:
                    shutil.rmtree(item)
                print(f"Deleted {item.relative_to(os.getcwd())}")
                
    print("\n[SUCCESS] Snowline uninstalled successfully.")

def main():
    parser = argparse.ArgumentParser(description="Manage Snowline Agent Ecosystem in the current project.")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    init_parser = subparsers.add_parser("init", help="Initialize Snowline")
    init_parser.add_argument("--apply", action="store_true", help="Apply changes to disk.")

    update_parser = subparsers.add_parser("update", help="Update Snowline")
    update_parser.add_argument("--apply", action="store_true", help="Apply changes to disk.")

    uninstall_parser = subparsers.add_parser("uninstall", help="Uninstall Snowline")
    uninstall_parser.add_argument("--apply", action="store_true", help="Apply changes to disk.")

    args, unknown = parser.parse_known_args()
    
    if args.command == "init":
        init_snowline(dry_run=not args.apply)
    elif args.command == "update":
        update_snowline(dry_run=not args.apply)
    elif args.command == "uninstall":
        uninstall_snowline(dry_run=not args.apply)
    else:
        if unknown and unknown[0] == "--apply":
            init_snowline(dry_run=False)
        else:
            init_snowline(dry_run=not args.apply)

if __name__ == "__main__":
    main()
