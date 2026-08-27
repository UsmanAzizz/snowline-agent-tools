import re
import os
import sys
from pathlib import Path

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
    if ' ' in topik:
        print("Batal: Nama topik tidak boleh memuat spasi. Gunakan huruf kecil dan tanda-hubung (misal: nama-topik).")
        sys.exit(1)
        
    lower_topik = topik.lower()
    if lower_topik.startswith('sprint') or lower_topik.startswith('entri') or lower_topik.startswith('qa'):
        print("Batal: Nama topik tidak boleh diawali dengan Sprint, entri, atau QA (mengulang judul entri).")
        sys.exit(1)

    # Setup paths
    here_we_are = Path(".here_we_are")
    agents_chamber = Path(".agents/chamber")
    
    chamber_dir = None
    if here_we_are.exists() and (here_we_are / "connector.md").exists():
        chamber_dir = here_we_are
    elif agents_chamber.exists() and (agents_chamber / "connector.md").exists():
        chamber_dir = agents_chamber
    else:
        print("Error: connector.md not found in .here_we_are or .agents/chamber.")
        sys.exit(1)
        
    connector_file = chamber_dir / "connector.md"
    state_file = chamber_dir / "STATE.md"
    
    history_dir = chamber_dir / "history" / topik
    history_dir.mkdir(parents=True, exist_ok=True)
    
    with open(connector_file, 'r', encoding='utf-8') as f:
        lines = f.read().splitlines()
        
    # Extract the first entry (top-most)
    first_divider_idx = -1
    for i in range(len(lines)):
        if lines[i].strip() == '---':
            # Skip the very first line if it's a divider
            if i == 0:
                continue
            first_divider_idx = i
            break
            
    if first_divider_idx == -1:
        # No divider found, the whole file is one entry
        entry_lines = lines
        new_connector_lines = []
    else:
        # Extract up to the first divider
        entry_lines = lines[:first_divider_idx]
        new_connector_lines = lines[first_divider_idx+1:]
        
    # Remove leading/trailing empty lines from entry
    while entry_lines and entry_lines[0].strip() == '':
        entry_lines.pop(0)
    while entry_lines and entry_lines[-1].strip() == '':
        entry_lines.pop()
    
    # Find the title for STATE.md
    first_line = ""
    for line in entry_lines:
        if line.startswith('#'):
            first_line = line
            break
            
    if not first_line:
        first_line = "Entri tanpa judul"
        
    lines_out = len(entry_lines)
    
    # Target file
    target_file = None
    existing_files = sorted([f for f in history_dir.iterdir() if f.suffix == '.md'])
    if not existing_files:
        target_file = history_dir / f"01-{topik}.md"
        existing_lines = 0
    else:
        target_file = existing_files[-1]
        with open(target_file, 'r', encoding='utf-8') as f:
            existing_lines = len(f.read().splitlines())
            
    if existing_lines + lines_out > 300:
        print(f"Batal: berkas {target_file} sudah mencapai {existing_lines} baris.")
        print(f"Menambahkan {lines_out} baris akan melanggar batas 300 baris.")
        print("Silakan pecah topik terlebih dahulu.")
        sys.exit(1)
        
    # Write to target
    append_text = '\n'.join(entry_lines) + '\n'
    with open(target_file, 'a', encoding='utf-8') as f:

        f.write(append_text)
        
    # Verify lines written
    with open(target_file, 'r', encoding='utf-8') as f:
        new_lines = len(f.read().splitlines())
        
    lines_added = new_lines - existing_lines
    print(f"Verifikasi: {lines_out} baris diekstrak, {lines_added} baris ditambahkan ke {target_file}.")
    if lines_added != lines_out:
        print("Batal: Jumlah baris tidak cocok!")
        sys.exit(1)
        
    if new_lines == 0:
        print("Batal: Berkas tujuan nol baris setelah ditulis!")
        if target_file.exists():
            target_file.unlink()
        sys.exit(1)
        
    # Rewrite connector.md
    # new_connector_lines was already determined above
    # Remove trailing blank lines from new connector so it stays clean
    while new_connector_lines and new_connector_lines[-1].strip() == '':
        new_connector_lines.pop()
        
    with open(connector_file, 'w', encoding='utf-8') as f:
        if new_connector_lines:
            f.write('\n'.join(new_connector_lines) + '\n')
        else:
            f.write('')
            
    # Update STATE.md (hanya jika topik belum ada di sana)
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
                print("Batal: Tabel 'TUTUP lewat chamber' tidak ditemukan di STATE.md")
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
