import os
import sys
from pathlib import Path

def close_entry_command(topik: str):
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
        # If target file is completely new and we append, we might not want a leading newline before ---
        # Actually, let's just append exactly what we removed
        # Wait, if we append to an existing file that doesn't end with a newline, we might need a newline.
        # But we assume well-formed markdown. We just append the joined lines + \n
        f.write(append_text)
        
    # Verify lines written
    with open(target_file, 'r', encoding='utf-8') as f:
        new_lines = len(f.read().splitlines())
        
    lines_added = new_lines - existing_lines
    print(f"Verifikasi: {lines_out} baris diekstrak, {lines_added} baris ditambahkan ke {target_file}.")
    if lines_added != lines_out:
        print("Batal: Jumlah baris tidak cocok!")
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
            state_text = f.read()
            
        topic_path = f"history/{topik}/"
        if topic_path not in state_text:
            with open(state_file, 'a', encoding='utf-8') as f:
                # Append in a structured way per topic
                f.write(f"{topik.ljust(15)} {'(entri baru)'.ljust(40)} {topic_path}\n")
    
    print(f"Berhasil: Entri terakhir ditutup dan dipindah ke history/{topik}/{target_file.name}")
