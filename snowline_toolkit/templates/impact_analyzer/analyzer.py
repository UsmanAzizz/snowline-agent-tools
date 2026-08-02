import os
import sys
import re
import json
import argparse

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def find_usages(project_root, target_name):
    """Scan all files to find import/require usages of target_name (no false positives from comments/strings)."""
    usages = set()
    exclude_dirs = {'.git', 'node_modules', 'dist', 'build', '.agents', 'vendor', '.history', 'quarantine'}

    escaped = re.escape(target_name)
    # Suffix pattern: target name can appear after ./ ../ or folder/ prefixes in quoted paths.
    # e.g. './Button', '../components/Button', 'utils/Button'
    quoted_suffix = rf"['\"](?:\.\/|\.\.\/|[^'\"]*/)?{escaped}['\"]"

    patterns = [
        # ES module named import (exact + suffix): import { Foo } from 'Foo' or import Foo from './Foo'
        re.compile(rf"import\s+(?:\{{[^}}]*}}|[^{{}};\n]+)\s+from\s+{quoted_suffix}"),
        re.compile(rf"import\s+{{[^}}]*}}\s+from\s+{quoted_suffix}"),
        # CommonJS require (exact + suffix): require('./Foo') or require('Foo')
        re.compile(rf"require\s*\(\s+{quoted_suffix}"),
        # Dynamic import (exact + suffix): import('./Foo') or import('Foo')
        re.compile(rf"import\s*\(\s+{quoted_suffix}"),
        # Export from (exact + suffix)
        re.compile(rf"export\s+.*?\s+from\s+{quoted_suffix}"),
        # Direct bareword import (exact + suffix): import 'Foo' or import './Foo'
        re.compile(rf"import\s+{quoted_suffix}"),
    ]

    for root, dirs, files in os.walk(project_root):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            if not file.endswith(('.js', '.jsx', '.ts', '.tsx', '.py', '.php'):
                continue

            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if any(p.search(content) for p in patterns):
                        usages.add(filepath)
            except Exception:
                pass
    return usages

def analyze_impact(target_path, project_root):
    target_filename = os.path.basename(target_path)
    target_base, _ = os.path.splitext(target_filename)

    if target_base.lower() == 'index':
        target_base = os.path.basename(os.path.dirname(target_path))

    # Level 1
    level_1 = find_usages(project_root, target_base)
    level_1.discard(target_path)

    # Level 2
    level_2 = set()
    for l1_file in level_1:
        l1_base, _ = os.path.splitext(os.path.basename(l1_file))
        if l1_base.lower() == 'index':
            l1_base = os.path.basename(os.path.dirname(l1_file))

        usages = find_usages(project_root, l1_base)
        usages.discard(l1_file)
        usages.discard(target_path)
        level_2.update(usages)

    level_2 = level_2 - level_1

    return {
        'target': target_filename,
        'target_path': target_path,
        'level_1': list(level_1),
        'level_2': list(level_2),
        'stats': {
            'level_1_count': len(level_1),
            'level_2_count': len(level_2),
            'total_impacted': len(level_1) + len(level_2)
        }
    }

def print_human(result, project_root):
    print(f"Analyzing Impact for: {result['target']}")
    print(f"Project Root: {project_root}")
    print("-" * 50)

    print("\n[Level 1] Direct Dependents:")
    if not result['level_1']:
        print("  No dependents found. Safe to modify/delete.")
    else:
        for f in result['level_1']:
            print(f"  - {os.path.relpath(f, project_root)}")

    print("\n[Level 2] Indirect Dependents:")
    if not result['level_2']:
        print("  No Level 2 dependents found.")
    else:
        for f in result['level_2']:
            print(f"  - {os.path.relpath(f, project_root)}")

    print("\n" + "=" * 50)
    print(f"Impact Summary: {result['stats']['level_1_count']} direct, {result['stats']['level_2_count']} indirect")

def main():
    parser = argparse.ArgumentParser(description="Impact Analyzer - Dependency Graph")
    parser.add_argument("target", help="Target file path")
    parser.add_argument("project_root", help="Project root directory")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    if not os.path.exists(args.target):
        print(f"[ERROR] Target file not found: {args.target}")
        sys.exit(1)

    result = analyze_impact(args.target, args.project_root)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_human(result, args.project_root)

if __name__ == '__main__':
    main()
