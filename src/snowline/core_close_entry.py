import re
import os
import sys
from pathlib import Path

def validate_topic_name(topik: str) -> str:
    """Validasi nama topik bersama untuk close-entry dan rotate."""
    if topik is None or not str(topik).strip():
        print("Batal: Nama topik harus ditentukan dan tidak boleh kosong (misal: nama-topik).")
        sys.exit(1)
        
    topik_clean = str(topik).strip()
    if ' ' in topik_clean:
        print("Batal: Nama topik tidak boleh memuat spasi. Gunakan huruf kecil dan tanda-hubung (misal: nama-topik).")
        sys.exit(1)
        
    lower_topik = topik_clean.lower()
    if lower_topik.startswith('sprint') or lower_topik.startswith('entri') or lower_topik.startswith('qa'):
        print("Batal: Nama topik tidak boleh diawali dengan Sprint, entri, atau QA (mengulang judul entri).")
        sys.exit(1)
        
    return topik_clean

def renumber_terbuka(state_lines):
    """Nomori ulang daftar Terbuka dari 1 berurutan."""
    terbuka_idx = -1
    for i, line in enumerate(state_lines):
        if line.strip().startswith("## Terbuka"):
            terbuka_idx = i
            break
    if terbuka_idx == -1:
        return state_lines

    block_start = -1
    block_end = -1
    for i in range(terbuka_idx + 1, len(state_lines)):
        if state_lines[i].strip() == "```":
            if block_start == -1:
                block_start = i
            else:
                block_end = i
                break
    if block_start == -1 or block_end == -1:
        return state_lines

    current_num = 1
    new_lines = list(state_lines)
    for i in range(block_start + 1, block_end):
        line = new_lines[i]
        m = re.match(r'^(\s*)(\d+)(\s+)(.*)$', line)
        if m:
            prefix_space = m.group(1)
            old_num_str = m.group(2)
            mid_space = m.group(3)
            rest = m.group(4)
            total_width = len(old_num_str) + len(mid_space)
            new_num_str = str(current_num)
            space_needed = max(1, total_width - len(new_num_str))
            new_lines[i] = f"{prefix_space}{new_num_str}{' ' * space_needed}{rest}"
            current_num += 1

    return new_lines

def close_entry_command(topik: str):
    topik = validate_topic_name(topik)

    # Setup paths
    here_we_are = Path(".here_we_are")
    agents_chamber = Path(".agents/chamber")
    
    chamber_dir = None
    if here_we_are.exists() and (here_we_are / "connector.md").exists():
        chamber_dir = here_we_are
    elif agents_chamber.exists() and (agents_chamber / "connector.md").exists():
        chamber_dir = agents_chamber
    else:
        print("Error: connector.md tidak ditemukan di .here_we_are atau .agents/chamber.")
        sys.exit(1)
        
    connector_file = chamber_dir / "connector.md"
    state_file = chamber_dir / "STATE.md"
    history_dir = chamber_dir / "history" / topik
    
    with open(connector_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    lines = content.splitlines()
    if not lines:
        print("Batal: connector.md kosong.")
        sys.exit(0)
        
    first_divider = -1
    for i, line in enumerate(lines):
        if line.strip() == '---':
            first_divider = i
            break
            
    if first_divider == -1:
        extracted = list(lines)
        remaining = []
    else:
        extracted = lines[:first_divider]
        remaining = lines[first_divider+1:]
        
    extracted_text = ('\n'.join(extracted) + '\n')
    
    # Target history file
    history_dir.mkdir(parents=True, exist_ok=True)
    existing_files = sorted([f for f in history_dir.iterdir() if f.suffix == '.md'])
    if not existing_files:
        target_file = history_dir / f"01-{topik}.md"
    else:
        target_file = existing_files[-1]
        
    # Append
    with open(target_file, 'a', encoding='utf-8') as f:
        f.write(extracted_text)
        
    # Write remaining
    with open(connector_file, 'w', encoding='utf-8') as f:
        if remaining:
            f.write('\n'.join(remaining) + '\n')
        else:
            f.write('')
            
    # Update STATE.md
    if state_file.exists():
        with open(state_file, 'r', encoding='utf-8') as f:
            state_lines = f.read().splitlines()
            
        topic_path = f"history/{topik}/"
        if not any(topic_path in line for line in state_lines):
            table_start_idx = -1
            for i, line in enumerate(state_lines):
                if "TUTUP lewat chamber, arsip per topik:" in line:
                    table_start_idx = i
                    break
                    
            if table_start_idx == -1:
                print("Batal: Tabel 'TUTUP lewat chamber, arsip per topik:' tidak ditemukan di STATE.md")
                sys.exit(1)
                
            insert_idx = -1
            for i in range(table_start_idx + 2, len(state_lines)):
                if state_lines[i].strip() == '```':
                    insert_idx = i
                    break
            if insert_idx == -1:
                print("Batal: Penutup tabel 'TUTUP lewat chamber' tidak ditemukan di STATE.md")
                sys.exit(1)
                
            new_line = f"{topik.ljust(20)} {'(entri baru)'.ljust(38)} {topic_path}"
            state_lines.insert(insert_idx, new_line)
            
            state_lines = renumber_terbuka(state_lines)
            with open(state_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(state_lines) + '\n')
    
    print(f"Berhasil: Entri terakhir ditutup dan dipindah ke history/{topik}/{target_file.name}")
