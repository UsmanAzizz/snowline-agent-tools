import sys
import os
import argparse
import re

def main():
    parser = argparse.ArgumentParser(description="Inject/Update structured header in a connector.md file")
    parser.add_argument("--status", type=str, required=True, help="Status to set (e.g. READY, WAITING)")
    parser.add_argument("--task", type=str, required=True, help="Task ID or name")
    parser.add_argument("--owner", type=str, default="None", help="Owner of the task")
    parser.add_argument("--depends", type=str, default="None", help="Task dependency")
    
    args = parser.parse_args()
    
    fpath = "connector.md"
    if not os.path.exists(fpath):
        sys.stderr.write(f"Error: {fpath} not found in current directory.\n")
        sys.exit(1)
        
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()
        
    header = f"Task ID: {args.task}\nStatus: [{args.status}]\nOwner: {args.owner}\nDepends-on: {args.depends}\n"
    
    inbox_marker = "## ACTIVE TASK - INBOX"
    if inbox_marker not in content:
        sys.stderr.write("Error: '## ACTIVE TASK - INBOX' not found in connector.md\n")
        sys.exit(1)
        
    header_pattern = re.compile(r"(## ACTIVE TASK - INBOX\s*?\n)```(?:\w*\n)?Task ID:.*?```\n", re.DOTALL)
    formatted_header = f"```\n{header}```\n"
    
    if header_pattern.search(content):
        new_content = header_pattern.sub(rf"\1{formatted_header}", content)
    else:
        new_content = content.replace(inbox_marker, inbox_marker + "\n\n" + formatted_header, 1)
        
    with open(fpath, "w", encoding="utf-8") as f:
        f.write(new_content)
        
    print(f"[OK] Header updated for Task {args.task} with status {args.status}")

if __name__ == "__main__":
    main()
