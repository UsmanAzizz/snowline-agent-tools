import os
import subprocess
import tempfile
import sys
import json

def get_root_dir():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

def run_cmd(cmd):
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True)
    out, err = p.communicate()
    return p.returncode, out, err

def test_selective_reader_extracted_items():
    root = get_root_dir()
    
    with tempfile.TemporaryDirectory(dir=root) as tmpdir:
        js_file = os.path.join(tmpdir, "test_component.jsx")
        content = """
import React, { useState, useEffect } from 'react';
import { Something } from './else';

export const MyComponent = (props) => {
    const [state, setState] = useState(0);
    const [other, setOther] = useState('');
    
    useEffect(() => {
        console.log('hi');
    }, []);
    
    return <div>Hello</div>;
}
"""
        with open(js_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        reader = os.path.join(root, "src", "snowline", "templates", "skills", "selective_reader", "reader.py")
        rc, out, err = run_cmd(f"{sys.executable} {reader} {js_file} --json")
        assert rc == 0, f"reader.py failed. Err: {err}"
        
        data = json.loads(out)
        toc = data.get("toc", [])
        
        imports = [t for t in toc if t["type"] == "Import"]
        states = [t for t in toc if t["type"] == "State"]
        effects = [t for t in toc if t["type"] == "Effect"]
        components = [t for t in toc if t["type"] == "Arrow Function"]
        
        assert len(imports) == 2, f"Expected 2 imports, got {len(imports)}"
        assert len(states) == 2, f"Expected 2 states, got {len(states)}"
        assert len(effects) == 1, f"Expected 1 effect, got {len(effects)}"
        assert len(components) == 1, f"Expected 1 component, got {len(components)}"
        assert "MyComponent(props)" in components[0]["name"], f"Expected signature MyComponent(props), got {components[0]['name']}"

