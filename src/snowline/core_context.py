import os
import sys
import json
import re

def get_keadaan_content(root_dir):
    paths = [
        os.path.join(root_dir, '.here_we_are', 'STATE.md'),
        os.path.join(root_dir, '.agents', 'chamber', 'STATE.md')
    ]
    for p in paths:
        if os.path.exists(p):
            with open(p, 'r', encoding='utf-8') as f:
                return f.read().strip(), "STATE.md"
    return "", "STATE.md (Tidak ditemukan)"

def get_scope_lock_content(root_dir):
    lock_path = os.path.join(root_dir, '.agents', 'scope_lock.json')
    if not os.path.exists(lock_path):
        return "", "scope_lock.json (Tidak ditemukan)"
        
    try:
        with open(lock_path, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)
    except Exception:
        return "", "scope_lock.json (Gagal diparse)"
        
    lines = []
    
    temuan = data.get('temuan', [])
    if temuan:
        lines.append("### Temuan:")
        for t in temuan:
            lines.append(f"- {t}")
            
    pertanyaan = data.get('pertanyaan_terbuka', [])
    if pertanyaan:
        lines.append("### Pertanyaan Terbuka:")
        for p in pertanyaan:
            lines.append(f"- {p}")
            
    berkas = data.get('berkas_terkait', [])
    if berkas:
        lines.append("### Berkas Terkait:")
        for b in berkas:
            lines.append(f"- {b}")
            
    return '\n'.join(lines), "Irisan tugas (scope_lock.json)"

def get_last_connector_entry(root_dir):
    paths = [
        os.path.join(root_dir, '.here_we_are', 'connector.md'),
        os.path.join(root_dir, '.agents', 'chamber', 'connector.md'),
        os.path.join(root_dir, 'qa_handoff_connector_final.md'),
        os.path.join(root_dir, 'connector.md')
    ]
    
    content = ""
    for p in paths:
        if os.path.exists(p):
            with open(p, 'r', encoding='utf-8') as f:
                content = f.read()
            break
            
    if not content:
        return "", "connector.md (Tidak ditemukan)"
        
    # Split by '## Entri'
    parts = re.split(r'^(?=## Entri)', content, flags=re.MULTILINE)
    if len(parts) > 1:
        # The last part is the last entry
        return parts[-1].strip(), "Entri Terakhir Connector"
    else:
        return content.strip(), "Entri Terakhir Connector"

def show_context():
    root_dir = os.getcwd()
    
    keadaan, k_name = get_keadaan_content(root_dir)
    scope, s_name = get_scope_lock_content(root_dir)
    connector, c_name = get_last_connector_entry(root_dir)
    
    sections = [
        (keadaan, k_name),
        (scope, s_name),
        (connector, c_name)
    ]
    
    total_lines = 0
    full_output = []
    
    for text, name in sections:
        if not text:
            continue
        full_output.append(f"\n{'='*50}\n[{name}]\n{'='*50}\n{text}")
        total_lines += len(text.split('\n'))
        
    if total_lines > 250:
        # Find the longest section
        longest = max(sections, key=lambda x: len(x[0].split('\n')) if x[0] else 0)
        longest_lines = len(longest[0].split('\n'))
        print(f"[FATAL] Perintah dihentikan. Konteks melebihi batas 250 baris (Total: {total_lines}).", file=sys.stderr)
        print(f"Bagian yang kegemukan: {longest[1]} ({longest_lines} baris).", file=sys.stderr)
        sys.exit(1)
        
    for out in full_output:
        print(out)
        
if __name__ == '__main__':
    show_context()
