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

        node_available = False
        try:
            subprocess.run(['node', '-v'], capture_output=True, check=True)
            node_available = True
        except Exception:
            pass
            
        if node_available and ext == '.js':
            with tempfile.NamedTemporaryFile(suffix='.js', delete=False, mode='w', encoding='utf-8') as f:
                f.write(content)
                temp_path = f.name
            
            try:
                result = subprocess.run(['node', '--check', temp_path], capture_output=True, text=True)
                os.unlink(temp_path)
                if result.returncode != 0:
                    if "Unexpected token '<'" in result.stderr:
                        is_valid, err = check_brackets(content)
                        if not is_valid:
                            return False, err
                        return True, "[WARN] Validasi JS fallback ke bracket-balancing dasar."
                    return False, f"Node.js Syntax Error:\n{result.stderr.strip()}"
                return True, None
            except Exception as e:
                os.unlink(temp_path)
                return False, f"Failed to run node --check: {e}"
        else:
            is_valid, err = check_brackets(content)
            if not is_valid:
                return False, err
            return True, "[WARN] Validasi menggunakan bracket-balancing dasar (bukan full syntax check)."
            
    return True, "[WARN] Tipe file tidak dikenali untuk validasi syntax, pengecekan dilewati."

REACT_TEMPLATE = """import React, { useState, useEffect } from 'react';

const {name} = () => {
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        // Fetch data logic here
    }, []);

    return (
        <div className="{name.lower()}-container">
            <h2>{name} Component</h2>
            {loading ? <p>Loading...</p> : <p>Content goes here.</p>}
        </div>
    );
};

export default {name};
"""

API_TEMPLATE = """const express = require('express');
const router = express.Router();

// GET endpoint
router.get('/', async (req, res) => {
    try {
        // Logic here
        res.status(200).json({ success: true, data: [] });
    } catch (error) {
        console.error(error);
        res.status(500).json({ success: false, message: 'Server Error' });
    }
});

// POST endpoint
router.post('/', async (req, res) => {
    try {
        // Logic here
        res.status(201).json({ success: true, message: 'Created' });
    } catch (error) {
        console.error(error);
        res.status(500).json({ success: false, message: 'Server Error' });
    }
});

module.exports = router;
"""

def generate_scaffold(file_type, name, target_dir, apply_mode):
    # Path traversal check: ensure target_dir is inside project root
    abs_target = os.path.abspath(target_dir)
    project_root = os.getcwd()

    if not (abs_target == project_root or abs_target.startswith(project_root + os.sep)):
        print(f"[BLOCKED] Target directory '{abs_target}' is outside the project root.")
        print(f"Project root: {project_root}")
        print("File operations are only allowed within the current project directory.")
        if apply_mode:
            sys.exit(1)
        return

    print("🏗️ AUTO-SCAFFOLDER 🏗️")
    print("=" * 60)
    
    if file_type.lower() not in ['react', 'api']:
        print("[FAIL] Invalid type. Choose 'react' or 'api'.")
        return
        
    if not os.path.exists(target_dir) and apply_mode:
        os.makedirs(target_dir, exist_ok=True)
        
    if file_type.lower() == 'react':
        filename = f"{name}.jsx"
        content = REACT_TEMPLATE.replace("{name}", name).replace("{name.lower()}", name.lower())
    else:
        filename = f"{name.lower()}.js"
        content = API_TEMPLATE
        
    filepath = os.path.join(target_dir, filename)
    
    if os.path.exists(filepath):
        print(f"[FAIL] File {filename} already exists at {target_dir}!")
        return
        
    risk_label = "Medium (Component/Logic File)" if file_type.lower() in ['react', 'api'] else "Low (Config/Simple File)"
        
    if not apply_mode:
        print("[DRY-RUN MODE] Auto-Scaffolder Preview")
        print("=" * 50)
        print(f"Target File: {filepath}")
        print(f"Risk Label : {risk_label}")
        print("--- Content Preview ---")
        print(content)
        print("=" * 50)
        print("\n💡 PROMPT UNTUK AI (Copy-Paste ini):")
        print(f'"Pratinjau berhasil. Silakan jalankan ulang perintah dengan tambahan flag --apply untuk membuat file {filename}."')
    else:
        print(f"[INFO] Risk terdeteksi sebagai {risk_label}")
        print("[INFO] Melakukan validasi syntax pada konten yang akan dibuat...")
        
        is_valid, msg = validate_syntax(filepath, content)
        if not is_valid:
            print(f"\n[BLOCKED] Syntax validation failed for {filename}")
            print(msg)
            print("Eksekusi DIBATALKAN. File tidak dibuat.")
            sys.exit(1)
        elif msg:
            print(f"  - {filename}: {msg}")
        print("[OK] Validasi syntax lolos.")
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"[OK] Successfully generated {filename} at {target_dir}")
            print("\n" + "=" * 60)
            print("💡 PROMPT UNTUK AI (Copy-Paste ini):")
            print(f'"Berdasarkan hasil Auto-Scaffolder di atas, tolong gunakan tool replace_file_content untuk mulai mengisi logika yang sesungguhnya di dalam {filename}."')
        except Exception as e:
            print(f"[FAIL] Error generating file: {e}")

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
