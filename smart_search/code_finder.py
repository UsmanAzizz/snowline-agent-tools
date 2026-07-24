import os
import sys
import argparse

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
                # Merge overlapping contexts (5 lines)
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

def main():
    parser = argparse.ArgumentParser(description="Smart Code Finder - Menemukan kode dengan konteks (Hemat Token)")
    parser.add_argument("target_dir", help="Direktori yang akan dipindai")
    parser.add_argument("keyword", help="Kata kunci yang dicari (contoh: 'nama_fungsi')")
    parser.add_argument("--ext", help="Filter ekstensi dipisah koma (contoh: .js,.jsx)", default="")
    args = parser.parse_args()

    extensions = [ext.strip() for ext in args.ext.split(",")] if args.ext else []
    
    results, scanned, skipped = search_files(args.target_dir, args.keyword, extensions)
    
    if not results:
        print(f"[OK] Pencarian '{args.keyword}' tidak ditemukan di {scanned} file.")
        sys.exit(0)
        
    print(f"🔎 HASIL PENCARIAN: '{args.keyword}'")
    print("=" * 60)
    
    total_matches = 0
    for r in results:
        rel_path = os.path.relpath(r['file'], args.target_dir)
        print(f"\n[WARN] Ditemukan di: {rel_path}")
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
    print(f"[OK] Selesai: {total_matches} kecocokan di {len(results)} file (dari {scanned} dipindai, {skipped} di-skip karena >500KB).")
    print("\n💡 PROMPT UNTUK AI (Copy-Paste ini):")
    print(f'"Tolong baca cuplikan kode di atas. Jika Anda perlu mengubah kode tersebut, perbaiki saja di fungsi terkait dan jelaskan."' )

if __name__ == "__main__":
    main()
