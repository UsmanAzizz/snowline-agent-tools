import os
import re
import sys
import json
import hashlib
import argparse

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

MAX_FILE_SIZE = 500 * 1024
ignore_dirs = {'node_modules', '.git', 'build', 'dist', 'uploads', 'public', '.vscode', '.history', 'quarantine', '.native_browser', '.exambro_android', '.plan', '.skills', '.backup_replace', '.agents'}

def get_dir_signature(target):
    mtimes = []
    for root, dirs, files in os.walk(target):
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        for f in files:
            filepath = os.path.join(root, f)
            try:
                if os.path.getsize(filepath) <= MAX_FILE_SIZE:
                    rel_path = os.path.relpath(filepath, target).replace(os.sep, '/')
                    mtimes.append(f"{rel_path}:{os.path.getmtime(filepath)}")
            except Exception:
                pass
    return hashlib.md5("".join(sorted(mtimes)).encode()).hexdigest()

def sweep(target):
    residue_files = []
    todo_count = 0
    comment_blocks = []
    scanned_files = 0

    for root, dirs, files in os.walk(target):
        dirs[:] = [d for d in dirs if d not in ignore_dirs]

        for d in dirs:
            if d.lower() in ['aa', 'arsip', 'temp', 'backup', 'old', 'scratch']:
                residue_files.append({
                    'path': os.path.join(root, d),
                    'type': 'backup_folder',
                    'description': 'Suspected Backup/Temp Folder'
                })

        for f in files:
            filepath = os.path.join(root, f)
            if os.path.getsize(filepath) > MAX_FILE_SIZE:
                continue

            scanned_files += 1
            f_lower = f.lower()

            if f_lower.endswith(('.bak', '.old', '.log', '.db', '.sqlite', '.tmp')) or re.search(r'(?<=[_\- /])copy(?=[_\-. /])', f_lower, re.IGNORECASE):
                if f_lower not in ['database.db'] and not f_lower.endswith('.test.js'):
                    residue_files.append({
                        'path': filepath,
                        'type': 'leftover_file',
                        'description': 'Suspected Leftover File'
                    })

            if f == 'database.db' and root == target:
                residue_files.append({
                    'path': filepath,
                    'type': 'local_sqlite',
                    'description': 'Local SQLite DB in MySQL project'
                })

            if f_lower.endswith(('.js', '.jsx', '.php', '.html', '.py')):
                try:
                    with open(filepath, 'r', encoding='utf-8') as file:
                        content = file.read()
                        todos = re.findall(r'(?i)\b(TODO|FIXME)\b', content)
                        todo_count += len(todos)

                        lines = content.split('\n')
                        consecutive_comments = 0
                        in_block_comment = False
                        block_start_line = None
                        block_type = None

                        for i, line in enumerate(lines):
                            stripped = line.strip()

                            # Handle block comment start/end (/* */, <!-- -->, """ """, ''' ''')
                            if not in_block_comment:
                                opener = None
                                if stripped.startswith('/*'):
                                    opener = '/*'
                                elif stripped.startswith('<!--'):
                                    opener = '<!--'
                                elif stripped.startswith('"""'):
                                    opener = '"""'
                                elif stripped.startswith("'''"):
                                    opener = "'''"

                                if opener:
                                    in_block_comment = True
                                    block_start_line = i + 1
                                    block_type = opener
                                    # Check if block closes on same line (match opener to closer)
                                    if opener == '/*':
                                        closer = '*/'
                                    elif opener == '<!--':
                                        closer = '-->'
                                    else:  # """ or '''
                                        closer = opener  # same as opener

                                    if closer in stripped[len(opener):]:
                                        in_block_comment = False
                                        consecutive_comments += 1
                                        if consecutive_comments >= 7:
                                            comment_blocks.append({
                                                'path': filepath,
                                                'start_line': block_start_line,
                                                'end_line': i + 1,
                                                'count': consecutive_comments,
                                                'description': 'Large commented block'
                                            })
                                        consecutive_comments = 0
                                        block_type = None
                                    continue

                            # Inside block comment - check for specific closer
                            if in_block_comment:
                                if block_type == '/*' and '*/' in line:
                                    in_block_comment = False
                                    consecutive_comments += 1
                                    if consecutive_comments >= 7:
                                        comment_blocks.append({
                                            'path': filepath,
                                            'start_line': block_start_line,
                                            'end_line': i + 1,
                                            'count': consecutive_comments,
                                            'description': 'Large commented block'
                                        })
                                    consecutive_comments = 0
                                    block_type = None
                                elif block_type == '<!--' and '-->' in line:
                                    in_block_comment = False
                                    consecutive_comments += 1
                                    if consecutive_comments >= 7:
                                        comment_blocks.append({
                                            'path': filepath,
                                            'start_line': block_start_line,
                                            'end_line': i + 1,
                                            'count': consecutive_comments,
                                            'description': 'Large commented block'
                                        })
                                    consecutive_comments = 0
                                    block_type = None
                                elif (block_type == '"""' or block_type == "'''") and block_type in line:
                                    in_block_comment = False
                                    consecutive_comments += 1
                                    if consecutive_comments >= 7:
                                        comment_blocks.append({
                                            'path': filepath,
                                            'start_line': block_start_line,
                                            'end_line': i + 1,
                                            'count': consecutive_comments,
                                            'description': 'Large commented block'
                                        })
                                    consecutive_comments = 0
                                    block_type = None
                                else:
                                    consecutive_comments += 1
                                continue

                            # Single-line comment detection
                            if stripped.startswith(('//', '#')):
                                consecutive_comments += 1
                            else:
                                if consecutive_comments >= 7:
                                    comment_blocks.append({
                                        'path': filepath,
                                        'start_line': i - consecutive_comments + 1,
                                        'end_line': i,
                                        'count': consecutive_comments,
                                        'description': 'Large commented block'
                                    })
                                consecutive_comments = 0
                except Exception:
                    pass

    return residue_files, todo_count, comment_blocks, scanned_files

def print_human(residue_files, todo_count, comment_blocks, scanned_files):
    print("CLEAN SWEEPER REPORT")
    print("=" * 50)

    if residue_files:
        for r in residue_files:
            rel = os.path.relpath(r['path'], os.getcwd())
            print(f"[FAIL] {rel} [{r['description']}]")

    if todo_count > 0:
        print(f"[WARN] Found {todo_count} TODO/FIXME tags in the code.")

    if comment_blocks:
        for c in comment_blocks:
            rel = os.path.relpath(c['path'], os.getcwd())
            print(f"[WARN] {rel} (Lines {c['start_line']}-{c['end_line']}): {c['count']} consecutive commented lines")

    print("\n" + "=" * 50)

    total_issues = len(residue_files) + (1 if todo_count > 0 else 0) + len(comment_blocks)
    if total_issues == 0:
        print(f"[OK] Proyek bersih! {scanned_files} file dipindai tanpa ada temuan residu.")
    else:
        print(f"[OK] Selesai memindai {scanned_files} file.")
        print("\n💡 PROMPT:")
        print('"Periksa temuan [FAIL] dan hapus file yang tidak diperlukan. Untuk [WARN], periksa apakah bisa dihapus."')

def print_json(residue_files, todo_count, comment_blocks, scanned_files):
    result = {
        'status': 'CLEAN' if len(residue_files) == 0 and todo_count == 0 and len(comment_blocks) == 0 else 'NEEDS_CLEANUP',
        'stats': {
            'scanned_files': scanned_files,
            'residue_files': len(residue_files),
            'todo_count': todo_count,
            'large_comment_blocks': len(comment_blocks),
            'total_issues': len(residue_files) + (1 if todo_count > 0 else 0) + len(comment_blocks)
        },
        'issues': {
            'residue_files': residue_files,
            'todo_tags': todo_count,
            'large_comment_blocks': comment_blocks
        }
    }
    print(json.dumps(result, indent=2))

def main():
    parser = argparse.ArgumentParser(description="Clean Sweeper - Project Health Scanner")
    parser.add_argument("target", help="Target directory to scan")
    parser.add_argument("--json", action="store_true", help="Output as JSON (machine-readable)")
    args = parser.parse_args()

    target = os.path.abspath(args.target)
    cache_file = os.path.join(target, '.agents', 'session_cache.json')
    dir_sig = get_dir_signature(target)
    cache_key = f"sweeper_{hashlib.md5(target.encode()).hexdigest()}"

    cache_data = {}
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
        except: pass

    if cache_key in cache_data and cache_data[cache_key].get('signature') == dir_sig:
        print("[INFO] Menggunakan hasil cache dari session_cache.json (tidak ada file yang berubah)")
        cached = cache_data[cache_key]
        residue_files = cached['residue_files']
        todo_count = cached['todo_count']
        comment_blocks = cached['comment_blocks']
        scanned_files = cached['scanned_files']
    else:
        residue_files, todo_count, comment_blocks, scanned_files = sweep(target)
        cache_data[cache_key] = {
            'signature': dir_sig,
            'residue_files': residue_files,
            'todo_count': todo_count,
            'comment_blocks': comment_blocks,
            'scanned_files': scanned_files
        }
        try:
            os.makedirs(os.path.dirname(cache_file), exist_ok=True)
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2)
        except: pass

    if args.json:
        print_json(residue_files, todo_count, comment_blocks, scanned_files)
    else:
        print_human(residue_files, todo_count, comment_blocks, scanned_files)

if __name__ == "__main__":
    main()
