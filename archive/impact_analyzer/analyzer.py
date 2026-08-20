import os
import sys
import re
import json
import argparse

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def find_usages(project_root, target_names):
    """Scan all files to find import/require usages of multiple target_names in a single pass."""
    if not target_names:
        return set()

    usages = set()
    exclude_dirs = {'.git', 'node_modules', 'dist', 'build', '.agents', 'vendor', '.history', 'quarantine'}

    escaped_targets = [re.escape(t) for t in target_names]
    targets_pattern = "(?:" + "|".join(escaped_targets) + ")"
    quoted_suffix = rf"['\"](?:\.\/|\.\.\/|[^'\"]*/)?{targets_pattern}(?:\.[a-zA-Z0-9]+)?['\"]"

    python_patterns = [
        re.compile(rf'import\s+{targets_pattern}\b'),
        re.compile(rf'from\s+{targets_pattern}\s+import'),
        re.compile(rf'from\s+{targets_pattern}\.\w+\s+import'),
        re.compile(rf'import\s+{targets_pattern}(?:\.\w+)*\b'),
    ]

    patterns = [
        re.compile(rf"import\s+(?:\{{[^}}]*}}|[^{{}};\n]+)\s+from\s+{quoted_suffix}"),
        re.compile(rf"import\s+{{[^}}]*}}\s+from\s+{quoted_suffix}"),
        re.compile(rf"require\s*\(\s*{quoted_suffix}"),
        re.compile(rf"import\s*\(\s*{quoted_suffix}"),
        re.compile(rf"export\s+.*?\s+from\s+{quoted_suffix}"),
        re.compile(rf"import\s+{quoted_suffix}"),
    ]

    for root, dirs, files in os.walk(project_root):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            if not file.endswith(('.js', '.jsx', '.ts', '.tsx', '.py', '.php')):
                continue

            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if file.endswith(('.py', '.php')):
                        if any(p.search(content) for p in python_patterns):
                            usages.add(filepath)
                    else:
                        if any(p.search(content) for p in patterns):
                            usages.add(filepath)
            except Exception:
                pass
    return usages

def _get_target_base(filepath):
    """Extract target base name from filepath, handling index.js -> parent folder."""
    base, _ = os.path.splitext(os.path.basename(filepath))
    if base.lower() == 'index':
        return os.path.basename(os.path.dirname(filepath))
    return base

def analyze_impact(target_path, project_root, max_depth=2):
    """Analyze dependency impact with configurable recursive depth.

    Args:
        target_path: Path to the target file
        project_root: Root directory of the project
        max_depth: Maximum recursion depth (default 2)
    Returns:
        Dict with levels and stats
    """
    levels = {}
    already_seen = {target_path}

    current_targets = {_get_target_base(target_path)}

    for depth in range(1, max_depth + 1):
        if not current_targets:
            break
        current_level = find_usages(project_root, current_targets) - already_seen
        if current_level:
            levels[depth] = sorted(current_level)
            already_seen.update(current_level)
            current_targets = {_get_target_base(f) for f in current_level}
        else:
            levels[depth] = []
            current_targets = set()

    total = sum(len(files) for files in levels.values())
    return {
        'target': os.path.basename(target_path),
        'target_path': target_path,
        'levels': levels,
        'stats': {'total': total, 'per_level': {d: len(files) for d, files in levels.items()}}
    }

def print_human(result, project_root):
    print(f"Analyzing Impact for: {result['target']}")
    print(f"Project Root: {project_root}")
    print("-" * 50)

    for depth, files in sorted(result['levels'].items()):
        label = "Direct" if depth == 1 else f"Level {depth}"
        print(f"\n[Level {depth}] {label} Dependents:")
        if not files:
            print("  None found.")
        else:
            for f in files:
                print(f"  - {os.path.relpath(f, project_root)}")

    print("\n" + "=" * 50)
    stats = result['stats']
    print(f"Impact Summary: {stats['total']} total")
    for depth, count in sorted(stats['per_level'].items()):
        label = "direct" if depth == 1 else f"level {depth}"
        print(f"  Level {depth}: {count} {label}")

def main():
    parser = argparse.ArgumentParser(description="Impact Analyzer - Dependency Graph")
    parser.add_argument("target", help="Target file path")
    parser.add_argument("project_root", help="Project root directory")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--depth", type=int, default=2, help="Maximum traversal depth (default: 2)")
    parser.add_argument("--max-radius", type=int, default=0, help="Maximum allowed impacted files. Skrip akan memblokir (exit 1) jika total dampak melebihi angka ini. (0 = tak terbatas)")
    args = parser.parse_args()

    if not os.path.exists(args.target):
        print(f"[ERROR] Target file not found: {args.target}")
        sys.exit(1)

    result = analyze_impact(args.target, args.project_root, max_depth=args.depth)
    
    total_impact = result['stats']['total']
    if args.max_radius > 0 and total_impact > args.max_radius:
        print(f"\n[BLOCKED] Impact Analyzer Guard: Radius Dampak Terlalu Besar!")
        print(f"Total file terdampak ({total_impact}) melebihi batas aman yang diizinkan ({args.max_radius}).")
        print("Tindakan ini diblokir untuk mencegah kerusakan meluas. Silakan revisi atau minta izin PM.")
        sys.exit(1)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_human(result, args.project_root)

if __name__ == '__main__':
    main()
