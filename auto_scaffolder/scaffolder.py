import os
import sys

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
