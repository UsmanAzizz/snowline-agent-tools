import os
import sys
import argparse

# Force UTF-8 encoding for standard output to prevent crash on emojis
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def search_files(directory, keyword, extensions):
    results = []
    
    # Common directories to ignore
    ignore_dirs = {'node_modules', '.git', 'vendor', 'build', 'dist', '.idea', '.vscode'}
    
    for root, dirs, files in os.walk(directory):
        # Modify dirs in-place to skip ignored directories
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
            
        for file in files:
            if extensions:
                if not any(file.endswith(ext) for ext in extensions):
                    continue
                    
            filepath = os.path.join(root, file)
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
                # Merge overlapping contexts (5 lines before and after)
                context_lines = 5
                blocks = []
                current_block = None
                
                for m in matches:
                    start = max(0, m - context_lines)
                    end = min(len(lines), m + context_lines + 1)
                    
                    if current_block and start <= current_block['end']:
                        # Overlaps with previous block, extend it
                        current_block['end'] = max(current_block['end'], end)
                        current_block['matches'].append(m)
                    else:
                        if current_block:
                            blocks.append(current_block)
                        current_block = {'start': start, 'end': end, 'matches': [m]}
                
                if current_block:
                    blocks.append(current_block)
                    
                results.append({'file': filepath, 'blocks': blocks, 'lines': lines})
                
    return results

def main():
    parser = argparse.ArgumentParser(description="Smart Code Reference Finder: Search for keywords and extract context blocks.")
    parser.add_argument("directory", help="Absolute path to the directory to search in")
    parser.add_argument("keyword", help="The keyword (function, component, variable) to search for")
    parser.add_argument("--ext", help="Comma-separated extensions to filter by (e.g. .js,.jsx,.php)", default="")
    
    args = parser.parse_args()
    
    extensions = [ext.strip() for ext in args.ext.split(",")] if args.ext else []
    
    results = search_files(args.directory, args.keyword, extensions)
    
    if not results:
        print(f"No results found for '{args.keyword}' in {args.directory}")
        return
        
    print(f"Found '{args.keyword}' in {len(results)} files:\n")
    for res in results:
        print(f"### File: {res['file']}")
        for block in res['blocks']:
            print("```")
            for i in range(block['start'], block['end']):
                # Highlight the line containing the exact match with a '>' arrow
                prefix = "> " if i in block['matches'] else "  "
                print(f"{i+1:4d} | {prefix}{res['lines'][i].rstrip()}")
            print("```")
        print("\n")

if __name__ == "__main__":
    main()
