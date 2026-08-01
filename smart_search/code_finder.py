import os
import sys
import argparse
import json
import hashlib

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

MAX_FILE_SIZE = 500 * 1024 # 500 KB
DEFAULT_EXCLUDES = {'node_modules', '.git', 'vendor', 'build', 'dist', '.idea', '.vscode', '.history', '.backup_replace', '.agents'}

def search_files(directory, keyword, extensions):
    results = []
    scanned = 0
    skipped = 0

    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d not in DEFAULT_EXCLUDES]

        for file in files:
            if extensions and not any(file.endswith(ext) for ext in extensions):
                continue

            filepath = os.path.join(root, file)
            if os.path.getsize(filepath) > MAX_FILE_SIZE:
                skipped += 1
                continue

            scanned += 1
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
            except Exception:
                continue

            matches = []
            for i, line in enumerate(lines):
                if keyword in line:
                    matches.append(i)

            if matches:
                context_lines = 5
                blocks = []
                current_block = None

                for m in matches:
                    start = max(0, m - context_lines)
                    end = min(len(lines), m + context_lines + 1)

                    if current_block and start <= current_block['end']:
                        current_block['end'] = max(current_block['end'], end)
                        current_block['matches'].append(m)
                    else:
                        if current_block:
                            blocks.append(current_block)
                        current_block = {'start': start, 'end': end, 'matches': [m]}

                if current_block:
                    blocks.append(current_block)

                results.append({'file': filepath, 'blocks': blocks, 'lines': lines})

    return results, scanned, skipped

def get_project_root(start_path):
    current = os.path.abspath(start_path)
    while True:
        if os.path.exists(os.path.join(current, 'package.json')) or os.path.exists(os.path.join(current, '.git')):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            return os.path.abspath(start_path)
        current = parent

def load_cache(cache_file):
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def clean_cache(cache_data, project_root):
    """Remove entries where source file no longer exists or is too old."""
    import time
    MAX_AGE_DAYS = 7
    before = len(cache_data)
    now = time.time()
    cleaned = []
    for key, entry in list(cache_data.items()):
        filepath = entry.get('file', '')
        mtime = entry.get('mtime', 0)
        if filepath and not os.path.exists(filepath):
            cleaned.append(key)
            continue
        if mtime and float(mtime) > 0:
            age_days = (now - float(mtime)) / 86400
            if age_days > MAX_AGE_DAYS:
                cleaned.append(key)
    for k in cleaned:
        del cache_data[k]
    return len(cleaned), before - len(cache_data)

def save_cache(cache_file, data):
    try:
        os.makedirs(os.path.dirname(cache_file), exist_ok=True)
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass

def get_dir_signature(directory, extensions):
    mtimes = []
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d not in DEFAULT_EXCLUDES]
        for file in files:
            if extensions and not any(file.endswith(ext) for ext in extensions):
                continue
            filepath = os.path.join(root, file)
            try:
                if os.path.getsize(filepath) <= MAX_FILE_SIZE:
                    mtimes.append(str(os.path.getmtime(filepath)))
            except Exception:
                pass
    return hashlib.md5("".join(sorted(mtimes)).encode()).hexdigest()

def print_human(results, keyword, scanned, skipped):
    total_matches = 0
    for r in results:
        rel_path = os.path.relpath(r['file'], os.getcwd())
        print(f"\n[WARN] Found in: {rel_path}")
        print("-" * 60)

        for block in r['blocks']:
            for i in range(block['start'], block['end']):
                line_str = r['lines'][i].rstrip()
                prefix = ">>" if i in block['matches'] else "  "
                print(f"{i+1:5d} | {prefix} {line_str}")
                if i in block['matches']:
                    total_matches += 1
            print("-" * 30)

    print("\n" + "=" * 60)
    print(f"[OK] Selesai: {total_matches} kecocokan di {len(results)} file (dari {scanned} dipindai, {skipped} dilewati karena >500KB).")
    print("\n💡 PROMPT:")
    print('"Tolong baca cuplikan kode di atas. Jika Anda perlu mengubah kode tersebut, gunakan tool replace_file_content."')

def print_json(results, keyword, scanned, skipped):
    total_matches = 0
    output = {
        'status': 'FOUND' if results else 'NOT_FOUND',
        'keyword': keyword,
        'stats': {
            'total_matches': 0,
            'files_with_matches': len(results),
            'scanned': scanned,
            'skipped': skipped
        },
        'results': []
    }

    for r in results:
        rel_path = os.path.relpath(r['file'], os.getcwd())
        file_result = {
            'file': rel_path,
            'absolute_path': r['file'],
            'matches': []
        }

        for block in r['blocks']:
            for i in range(block['start'], block['end']):
                line_str = r['lines'][i].rstrip()
                is_match = i in block['matches']
                file_result['matches'].append({
                    'line': i + 1,
                    'content': line_str,
                    'is_match': is_match
                })
                if is_match:
                    total_matches += 1

        output['results'].append(file_result)

    output['stats']['total_matches'] = total_matches
    print(json.dumps(output, indent=2))

def main():
    parser = argparse.ArgumentParser(description="Smart Code Finder - Find code with context (Token Efficient)")
    parser.add_argument("target_dir", help="Directory to scan")
    parser.add_argument("keyword", help="Search keyword (e.g., 'function_name')")
    parser.add_argument("--ext", help="Comma-separated extensions to filter (e.g., .js,.jsx)", default="")
    parser.add_argument("--json", action="store_true", help="Output as JSON (machine-readable)")
    args = parser.parse_args()

    extensions = [ext.strip() for ext in args.ext.split(",")] if args.ext else []

    project_root = get_project_root(args.target_dir)
    cache_file = os.path.join(project_root, '.agents', 'session_cache.json')
    cache_data = load_cache(cache_file)
    removed, _ = clean_cache(cache_data, project_root)
    save_cache(cache_file, cache_data)

    dir_signature = get_dir_signature(args.target_dir, extensions)
    cache_key = f"search_{hashlib.md5((args.target_dir + args.keyword + ''.join(extensions)).encode()).hexdigest()}"

    if cache_key in cache_data:
        cached_entry = cache_data[cache_key]
        if cached_entry.get('signature') == dir_signature:
            print("[INFO] Menggunakan hasil cache dari session_cache.json (tidak ada file yang berubah)")
            results = cached_entry['results']
            scanned = cached_entry['scanned']
            skipped = cached_entry['skipped']
        else:
            results, scanned, skipped = search_files(args.target_dir, args.keyword, extensions)
            cache_data[cache_key] = {
                'signature': dir_signature,
                'results': results,
                'scanned': scanned,
                'skipped': skipped
            }
            save_cache(cache_file, cache_data)
    else:
        results, scanned, skipped = search_files(args.target_dir, args.keyword, extensions)
        cache_data[cache_key] = {
            'signature': dir_signature,
            'results': results,
            'scanned': scanned,
            'skipped': skipped
        }
        save_cache(cache_file, cache_data)

    if not results:
        if args.json:
            print(json.dumps({
                'status': 'NOT_FOUND',
                'keyword': args.keyword,
                'stats': {'scanned': scanned, 'skipped': skipped}
            }, indent=2))
        else:
            print(f"[OK] Keyword '{args.keyword}' not found in {scanned} files.")
        sys.exit(0)

    if args.json:
        print_json(results, args.keyword, scanned, skipped)
    else:
        print(f"🔎 SEARCH RESULTS: '{args.keyword}'")
        print("=" * 60)
        print_human(results, args.keyword, scanned, skipped)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        import traceback
        print()
        print("[TOOL ERROR] Ini bug internal snowline, BUKAN masalah di kode project Anda.")
        print(f"Error: {type(e).__name__}: {e}")
        print()
        print("Traceback (untuk dilaporkan ke developer):")
        traceback.print_exc()
        sys.exit(1)
