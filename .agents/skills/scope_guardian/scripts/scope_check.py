import sys
import os
import json
import fnmatch
from datetime import datetime

# Umur maksimal scope_lock sebelum dianggap sisa tugas lama. Memperingatkan,
# tidak memblokir: lock yang basi menyesatkan, tetapi memblokir karenanya akan
# mematikan alat ini pada pemakaian pertama.
MAX_UMUR_JAM = 24


def peringatan_kesegaran(scope_data):
    """Kembalikan daftar peringatan bila scope_lock tampak sisa tugas lama."""
    peringatan = []
    created_at = scope_data.get('created_at')

    if not created_at:
        peringatan.append(
            "scope_lock.json tidak punya 'created_at' — umurnya tidak bisa diperiksa."
        )
        return peringatan

    try:
        umur_jam = (datetime.now() - datetime.fromisoformat(created_at)).total_seconds() / 3600
    except (ValueError, TypeError):
        peringatan.append(f"'created_at' tidak terbaca: {created_at!r}")
        return peringatan

    if umur_jam > MAX_UMUR_JAM:
        peringatan.append(
            f"scope_lock.json berumur {umur_jam / 24:.1f} hari (dibuat {created_at}). "
            f"Task: {scope_data.get('task', '?')!r}. Pastikan ini memang tugas yang "
            f"sedang dikerjakan, bukan sisa tugas sebelumnya."
        )

    return peringatan


def is_file_in_scope(filepath, allowed_files, allowed_patterns):
    """Check if filepath is allowed by allowed_files/patterns.

    Uses .lower() for case-insensitive comparison (normcase() was removed —
    it mangled '/' to '\\' on Windows, breaking path-relative matching).
    Both sides already forward-slash-normalized via .replace('\\\\', '/') before calling.
    Shared by scope_check.py and smart_replace/replace_text.py.
    """
    target = filepath.replace('\\', '/').lower()

    for allowed in allowed_files:
        allowed_lc = allowed.lower()
        if '/' not in allowed_lc:
            if os.path.basename(target) == allowed_lc:
                return True
        else:
            if target == allowed_lc or target.endswith('/' + allowed_lc):
                return True

    for pattern in allowed_patterns:
        if fnmatch.fnmatch(filepath, pattern):
            return True

    return False


def check_scope(target_file):
    # Normalize path separators for comparison
    target_file = target_file.replace('\\', '/')
    lock_file_path = os.path.join(os.getcwd(), '.agents', 'scope_lock.json')
    
    if not os.path.exists(lock_file_path):
        print(f"[BLOCKED] scope_lock.json not found in .agents/. Please create it first to define the scope.")
        print("Skema dan contohnya: .agents/skills/rules/scope_guardian.md")
        sys.exit(1)

    try:
        with open(lock_file_path, 'r', encoding='utf-8') as f:
            scope_data = json.load(f)
    except Exception as e:
        print(f"[BLOCKED] Failed to parse scope_lock.json: {e}")
        print("Skema dan contohnya: .agents/skills/rules/scope_guardian.md")
        sys.exit(1)

    for pesan in peringatan_kesegaran(scope_data):
        print(f"[WARN] {pesan}")

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
            # Path-relative entry: compare normalized paths (already forward-slash from .replace() above).
            # Use .lower() for case-folding ONLY — do NOT use normcase() or normpath() here.
            # normcase() on Windows also converts '/' to '\\', breaking endswith('/'+allowed_norm).
            # .lower() only lowercases, preserving forward-slash separators intact.
            allowed_norm = allowed.lower()
            target_norm = target_file.lower()
            if target_norm == allowed_norm or target_norm.endswith('/' + allowed_norm):
                print(f"[ALLOWED] File '{target_file}' is in allowed_files.")
                print(f"[RISK] {risk_label}")
                sys.exit(0)
        else:
            # Filename-only entry: compare basenames (case-insensitive)
            # Use .lower() not normcase() — normcase() also converts '/' to '\\' on Windows
            allowed_base = allowed.lower()
            target_base = os.path.basename(target_file).lower()
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
