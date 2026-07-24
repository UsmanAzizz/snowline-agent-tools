import os
import sys
import subprocess

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

TOOLS = [
    {
        "name": "Project Guardian (Security & Health Auditor)",
        "script": "project_guardian/guardian.py",
        "args": ["--summary"]
    },
    {
        "name": "Clean Sweeper (Leftover & Tech Debt Scanner)",
        "script": "clean_sweeper/sweeper.py",
        "args": [os.getcwd()]
    },
    {
        "name": "Context Mapper (Knowledge Catalog Builder)",
        "script": "context_mapper/context_mapper.py",
        "args": []
    },
    {
        "name": "Smart Replace (Pure Python RegEx Replacer)",
        "script": "smart_replace/replace_text.py",
        "args": [os.getcwd(), "<search_string>", "<replace_string>"]
    },
    {
        "name": "Smart Search (5-Lines Context Code Finder)",
        "script": "smart_search/code_finder.py",
        "args": [os.getcwd(), "<keyword>"]
    },
    {
        "name": "Selective Reader (TOC Extractor)",
        "script": "selective_reader/reader.py",
        "args": ["<absolute_file_path>"]
    },
    {
        "name": "Deep Analyzer (Project Profiler)",
        "script": "deep_analyzer/analyzer.py",
        "args": [os.getcwd()]
    },
    {
        "name": "Crash Decoder (Error Trace Analyzer)",
        "script": "crash_decoder/decoder.py",
        "args": ["<path_to_error_log.txt>"]
    },
    {
        "name": "Auto-Scaffolder (Pattern Generator)",
        "script": "auto_scaffolder/scaffolder.py",
        "args": ["<react_or_api>", "<ComponentName>"]
    },
    {
        "name": "Smart Import Fixer",
        "script": "import_fixer/fixer.py",
        "args": ["<source_file>", "<broken_import_string>"]
    },
    {
        "name": "Smart Tree Viewer (Compact Directory Mapper)",
        "script": "smart_tree/scripts/tree_viewer.py",
        "args": ["<directory_path>"]
    },
    {
        "name": "Database Extractor (Schema Parser)",
        "script": "db_extractor/scripts/extractor.py",
        "args": ["<project_root_dir>"]
    },
    {
        "name": "Impact Analyzer (Dependency Graph)",
        "script": "impact_analyzer/analyzer.py",
        "args": ["<target_file_path>", "<project_root_dir>"]
    }
]

def print_menu():
    print("\n" + "=" * 60)
    print("🚀 SNOWLINE AGENT TOOLS - INTERACTIVE DASHBOARD 🚀")
    print("=" * 60)
    print("Select a tool to run (Powered by 13-Pillars Vision):")
    for i, tool in enumerate(TOOLS, 1):
        print(f"[{i}] {tool['name']}")
    print("[0] Exit")
    print("=" * 60)

def main():
    while True:
        print_menu()
        try:
            choice = input("\nEnter your choice (0-13): ").strip()
        except KeyboardInterrupt:
            break
            
        if choice == '0':
            print("Exiting dashboard.")
            break
            
        if not choice.isdigit() or not (1 <= int(choice) <= len(TOOLS)):
            print("[FAIL] Invalid choice.")
            continue
            
        idx = int(choice) - 1
        tool = TOOLS[idx]
        
        script_path = os.path.join(os.path.dirname(__file__), tool["script"])
        if not os.path.exists(script_path):
            print(f"[FAIL] Script not found at {script_path}")
            continue
            
        args = []
        for arg in tool["args"]:
            if arg.startswith("<") and arg.endswith(">"):
                val = input(f"Enter {arg}: ").strip()
                args.append(val)
            else:
                args.append(arg)
                
        cmd = [sys.executable, script_path] + args
        print(f"\nRunning: {' '.join(cmd)}")
        print("-" * 60)
        
        try:
            subprocess.run(cmd, check=False)
        except Exception as e:
            print(f"[FAIL] Error during execution: {e}")
            
        input("\nPress Enter to return to main menu...")

if __name__ == "__main__":
    main()
