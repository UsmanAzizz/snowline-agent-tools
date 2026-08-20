import os
import sys
import tempfile
import ast
import subprocess

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

import json

def check_task_state():
    state_file = os.path.join(os.getcwd(), '.agents', 'task_state.json')
    if not os.path.exists(state_file):
        return
        
    try:
        with open(state_file, 'r', encoding='utf-8') as f:
            state = json.load(f)
    except Exception:
        return
        
    if state.get('phase') == 'pseudocode_pending':
        print("[BLOCKED] Pseudocode untuk task ini belum disetujui user.")
        print(f"Task: {state.get('task', 'Unknown')}")
        print("Minta user approve pseudocode dulu sebelum --apply bisa dijalankan.")
        sys.exit(1)

def validate_syntax(filepath, content):
    ext = os.path.splitext(filepath)[1].lower()
    
    if ext == '.py':
        try:
            import ast
            ast.parse(content)
            return True, None
        except SyntaxError as e:
            return False, f"Python Syntax Error: {e.msg} at line {e.lineno}"
            
    elif ext in ['.js', '.jsx', '.ts', '.tsx']:
        def check_brackets(text):
            stack = []
            pairs = {')': '(', '}': '{', ']': '['}
            lines = text.split('\n')
            for i, line in enumerate(lines):
                for char in line:
                    if char in '({[':
                        stack.append((char, i+1))
                    elif char in ')}]':
                        if not stack:
                            return False, f"Unmatched closing bracket '{char}' at line {i+1}"
                        top_char, _ = stack.pop()
                        if top_char != pairs[char]:
                            return False, f"Mismatched bracket '{char}' at line {i+1}, expected closing for '{top_char}'"
            if stack:
                top_char, line = stack.pop()
                return False, f"Unclosed bracket '{top_char}' opened at line {line}"
            return True, None

        import subprocess, tempfile, os
        
        # Cek ketersediaan Linter
        linter_available = False
        linter_cmd = []
        try:
            if subprocess.run(['npx', 'eslint', '-v'], capture_output=True, shell=True).returncode == 0:
                linter_available = True
                linter_cmd = ['npx', 'eslint', '--quiet']
            elif subprocess.run(['npx', 'tsc', '-v'], capture_output=True, shell=True).returncode == 0:
                linter_available = True
                linter_cmd = ['npx', 'tsc', '--noEmit']
        except Exception:
            pass
            
        if linter_available:
            with tempfile.NamedTemporaryFile(suffix=ext, delete=False, mode='w', encoding='utf-8') as f:
                f.write(content)
                temp_path = f.name
            
            try:
                # Need shell=True on Windows for npx
                cmd = linter_cmd + [temp_path]
                result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
                os.unlink(temp_path)
                if result.returncode != 0:
                    return False, f"Linter Syntax Error:\n{result.stdout.strip()}\n{result.stderr.strip()}"
                return True, None
            except Exception as e:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                return False, f"Failed to run linter: {e}"
        else:
            is_valid, err = check_brackets(content)
            if not is_valid:
                return False, err
            return True, "[WARN] Validasi menggunakan bracket-balancing dasar (Linter ESLint/TSC tidak ditemukan)."
            
    return True, "[WARN] Tipe file tidak dikenali untuk validasi syntax, pengecekan dilewati."

def main():
    check_task_state()  # Block if pseudocode not approved

    if len(sys.argv) < 3:
        print("Usage: python scaffolder.py <react|api> <ComponentName> [target_dir] [--apply]")
        sys.exit(1)
        
    file_type = sys.argv[1]
    name = sys.argv[2]
    
    args = sys.argv[3:]
    apply_mode = "--apply" in args
    target_dir = args[0] if len(args) > 0 and args[0] != "--apply" else os.getcwd()
    
    generate_scaffold(file_type, name, target_dir, apply_mode)

if __name__ == "__main__":
    main()
