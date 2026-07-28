import os
import sys
import fnmatch

def parse_gitignore(dir_path):
    ignore_patterns = [
        '.git', '.agents', 'node_modules', 'vendor', '__pycache__', 
        '.DS_Store', 'dist', 'build', '.idea', '.vscode'
    ]
    gitignore_path = os.path.join(dir_path, '.gitignore')
    if os.path.exists(gitignore_path):
        with open(gitignore_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Remove trailing slash for directory patterns to match effectively
                    if line.endswith('/'):
                        line = line[:-1]
                    ignore_patterns.append(line)
    return ignore_patterns

def is_ignored(name, ignore_patterns):
    for pattern in ignore_patterns:
        if fnmatch.fnmatch(name, pattern) or fnmatch.fnmatch(name, pattern + '/*'):
            return True
    return False

def generate_tree(dir_path, prefix="", depth=0, max_depth=3, ignore_patterns=None):
    if depth > max_depth:
        print(f"{prefix}└── ... (max depth reached)")
        return
        
    if ignore_patterns is None:
        ignore_patterns = parse_gitignore(dir_path)

    try:
        entries = sorted(os.listdir(dir_path))
    except PermissionError:
        print(f"{prefix}└── [Permission Denied]")
        return

    # Filter out ignored entries
    entries = [e for e in entries if not is_ignored(e, ignore_patterns)]
    
    entries_count = len(entries)
    for i, entry in enumerate(entries):
        is_last = (i == entries_count - 1)
        entry_path = os.path.join(dir_path, entry)
        
        connector = "└── " if is_last else "├── "
        print(f"{prefix}{connector}{entry}")
        
        if os.path.isdir(entry_path):
            extension = "    " if is_last else "│   "
            generate_tree(entry_path, prefix + extension, depth + 1, max_depth, ignore_patterns)

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    if len(sys.argv) < 2:
        print("Usage: python tree_viewer.py <directory_path> [max_depth]")
        sys.exit(1)
        
    target_dir = sys.argv[1]
    max_depth = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    
    if not os.path.isdir(target_dir):
        print(f"Error: Directory '{target_dir}' does not exist.")
        sys.exit(1)
        
    print(f"Directory Tree for: {os.path.abspath(target_dir)} (Max Depth: {max_depth})")
    print(".")
    generate_tree(target_dir, max_depth=max_depth)
