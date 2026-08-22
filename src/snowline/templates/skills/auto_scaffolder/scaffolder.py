import os
import sys
import json

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

import json


def check_scope_write(write_target):
    """Block if write target is outside allowed scope (security gate, fail-closed)."""
    # Ensure .agents/skills is in sys.path so scope_guardian can be found
    _SKILLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # -> .agents/skills
    if _SKILLS not in sys.path:
        sys.path.insert(0, _SKILLS)
    from scope_guardian.scripts.scope_check import is_file_in_scope

    lock_file = os.path.join(os.getcwd(), '.agents', 'scope_lock.json')
    if not os.path.exists(lock_file):
        print("[BLOCKED] scope_lock.json not found in .agents/. Create it first to define scope.")
        sys.exit(1)
    try:
        with open(lock_file, 'r', encoding='utf-8') as f:
            scope_data = json.load(f)
    except Exception:
        print("[BLOCKED] Failed to parse scope_lock.json.")
        sys.exit(1)
    allowed_files = scope_data.get('allowed_files', [])
    allowed_patterns = scope_data.get('allowed_patterns', [])
    task = scope_data.get('task', 'Unknown task')
    if not is_file_in_scope(write_target, allowed_files, allowed_patterns):
        print(f"[BLOCKED] Write target is OUT OF SCOPE.")
        print(f"Task: {task}")
        print(f"Target: {write_target}")
        print(f"Allowed: {allowed_files}")
        sys.exit(1)


def check_task_state(is_apply=False):
    if is_apply:
        root_dir = os.getcwd()
        paths = [
            os.path.join(root_dir, '.here_we_are', 'role.json'),
            os.path.join(root_dir, '.agents', 'chamber', 'role.json')
        ]
        for p in paths:
            if os.path.exists(p):
                role_data = None
                with open(p, 'rb') as f:
                    raw_bytes = f.read()
                
                err_msg = ""
                for enc in ['utf-8-sig', 'utf-16']:
                    try:
                        role_data = json.loads(raw_bytes.decode(enc))
                        break
                    except Exception as e:
                        err_msg = str(e)
                        
                if role_data is None:
                    print(f"[BLOCKED] Role lock file ada tetapi gagal dibaca (mungkin format rusak atau encoding salah): {err_msg}")
                    sys.exit(1)
                    
                if role_data.get('role') == 'QA':
                    print("[BLOCKED] Akses tulis (--apply) ditolak untuk role QA.")
                    sys.exit(1)

    state_file = os.path.join(os.getcwd(), '.agents', 'task_state.json')
    if not os.path.exists(state_file):
        return
        
    try:
        with open(state_file, 'r', encoding='utf-8') as f:
            state = json.load(f)
    except Exception as e:
        print(f"[BLOCKED] Gagal membaca state file: {e}")
        import sys
        sys.exit(1)
        
    if state.get('phase') == 'pseudocode_pending':
        print("[BLOCKED] Pseudocode untuk task ini belum disetujui user.")
        print(f"Task: {state.get('task', 'Unknown')}")
        print("Minta user approve pseudocode dulu sebelum --apply bisa dijalankan.")
        sys.exit(1)

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

    # Check scope before writing (file-level, not directory)
    check_scope_write(filepath)
    
    if os.path.exists(filepath):
        print(f"[FAIL] File {filename} already exists at {target_dir}!")
        return
        
    if not apply_mode:
        print("[DRY-RUN MODE] Auto-Scaffolder Preview")
        print("=" * 50)
        print(f"Target File: {filepath}")
        print("--- Content Preview ---")
        print(content)
        print("=" * 50)
        print("\n💡 PROMPT UNTUK AI (Copy-Paste ini):")
        print(f'"Pratinjau berhasil. Silakan jalankan ulang perintah dengan tambahan flag --apply untuk membuat file {filename}."')
    else:
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
    apply_mode = "--apply" in sys.argv
    check_task_state(is_apply=apply_mode)  # Block if pseudocode not approved
    
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
