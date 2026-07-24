import os
import sys

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

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

def generate_scaffold(file_type, name, target_dir):
    print("🏗️ AUTO-SCAFFOLDER 🏗️")
    print("=" * 60)
    
    if file_type.lower() not in ['react', 'api']:
        print("[FAIL] Invalid type. Choose 'react' or 'api'.")
        return
        
    if not os.path.exists(target_dir):
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
        print("Usage: python scaffolder.py <react|api> <ComponentName> [target_dir]")
        sys.exit(1)
        
    file_type = sys.argv[1]
    name = sys.argv[2]
    target_dir = sys.argv[3] if len(sys.argv) > 3 else os.getcwd()
    
    generate_scaffold(file_type, name, target_dir)

if __name__ == "__main__":
    main()
