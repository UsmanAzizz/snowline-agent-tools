import sys
import os
import json
import fnmatch

def check_scope(target_file):
    # Normalize path separators for comparison
    target_file = target_file.replace('\\', '/')
    lock_file_path = os.path.join(os.getcwd(), '.agents', 'scope_lock.json')
    
    if not os.path.exists(lock_file_path):
        print(f"[BLOCKED] scope_lock.json not found in .agents/. Please create it first to define the scope.")
        sys.exit(1)
        
    try:
        with open(lock_file_path, 'r', encoding='utf-8') as f:
            scope_data = json.load(f)
    except Exception as e:
        print(f"[BLOCKED] Failed to parse scope_lock.json: {e}")
        sys.exit(1)
        
    task = scope_data.get('task', 'Unknown task')
    allowed_files = [f.replace('\\', '/') for f in scope_data.get('allowed_files', [])]
    allowed_patterns = scope_data.get('allowed_patterns', [])
    
    # Calculate risk
    num_files = len(allowed_files)
    task_lower = task.lower()
    is_cosmetic = any(word in task_lower for word in ['styling', 'kosmetik', 'teks', 'css', 'margin', 'padding'])
    
    if num_files > 5:
        risk_label = "High — multiple files (>5)"
    elif num_files > 1 or not is_cosmetic:
        if num_files > 1:
            risk_label = f"Medium — {num_files} files"
        else:
            risk_label = "Medium — single file, functional/logic scope"
    else:
        risk_label = "Low — single file, cosmetic scope"
    

    # 1. Check exact matches (SECURITY-FIXED: use basename for filename-only, normalized path for path-relative)
    for allowed in allowed_files:
        if '/' in allowed or '\\' in allowed:
            # Path-relative entry: normalize and compare full paths
            allowed_norm = os.path.normcase(os.path.normpath(allowed))
            target_norm = os.path.normcase(os.path.normpath(target_file))
            if target_norm == allowed_norm or target_norm.endswith('/' + allowed_norm):
                print(f"[ALLOWED] File '{target_file}' is in allowed_files.")
                print(f"[RISK] {risk_label}")
                sys.exit(0)
        else:
            # Filename-only entry: compare basenames (case-insensitive on Windows)
            allowed_base = os.path.normcase(allowed)
            target_base = os.path.normcase(os.path.basename(target_file))
            if target_base == allowed_base:
                print(f"[ALLOWED] File '{target_file}' is in allowed_files.")
                print(f"[RISK] {risk_label}")
                sys.exit(0)
            
    # 2. Check patterns
    for pattern in allowed_patterns:
        if fnmatch.fnmatch(target_file, pattern):
            print(f"[ALLOWED] File '{target_file}' matches pattern '{pattern}'.")
            print(f"[RISK] {risk_label}")
            sys.exit(0)
            
    # 3. If no match
    print(f"[BLOCKED] File '{target_file}' is OUT OF SCOPE for the current task.")
    print(f"Task: {task}")
    print(f"Allowed files: {allowed_files}")
    print(f"Allowed patterns: {allowed_patterns}")
    print("To proceed, you MUST ask the user to explicitly approve expanding the scope.")
    sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python scope_check.py <file_path>")
        sys.exit(1)
    
    check_scope(sys.argv[1])
