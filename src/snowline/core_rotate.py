import os
import sys
import re
from pathlib import Path
from snowline.core_close_entry import validate_topic_name

def rotate_command(topik: str, apply: bool = False):
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
        orig_content = f.read()
    orig_lines = orig_content.splitlines()
    total_orig = len(orig_lines)
    
    if total_orig == 0:
        print("Batal: connector.md kosong, tidak ada yang perlu dirotasi.")
        sys.exit(0)

    # Find divider: keep the active/top entry, archive the rest
    first_divider_idx = -1
    for i, line in enumerate(orig_lines):
        if line.strip() == '---':
            if i == 0:
                continue
            first_divider_idx = i
            break
            
    if first_divider_idx == -1:
        # Only 1 entry exists
        kept_lines = []
        archived_lines = list(orig_lines)
    else:
        kept_lines = orig_lines[:first_divider_idx]
        archived_lines = orig_lines[first_divider_idx:]
        
    lines_to_keep = len(kept_lines)
    lines_to_archive = len(archived_lines)
    
    # Target archive file
    existing_files = sorted([f for f in history_dir.iterdir() if f.suffix == '.md']) if history_dir.exists() else []
    if not existing_files:
        target_archive = history_dir / f"01-{topik}.md"
        existing_archive_lines = 0
    else:
        target_archive = existing_files[-1]
        with open(target_archive, 'r', encoding='utf-8') as f:
            existing_archive_lines = len(f.read().splitlines())
            
    if not apply:
        print("[DRY RUN] Pratinjau Rotasi Connector")
        print(f"  * Berkas connector  : {connector_file} ({total_orig} baris)")
        print(f"  * Baris dipertahankan: {lines_to_keep} baris")
        print(f"  * Baris dirotasi     : {lines_to_archive} baris -> {target_archive}")
        print(f"  * Validasi aritmatika: {lines_to_keep} + {lines_to_archive} = {total_orig} (cocok)")
        print()
        print("Jalankan ulang dengan --apply untuk menerapkan rotasi.")
        return

    # Apply mode: write archive first with transactional safety
    archive_text = ('\n'.join(archived_lines) + '\n')
    orig_target_content = None
    target_existed = False
    
    try:
        history_dir.mkdir(parents=True, exist_ok=True)
        target_existed = target_archive.exists()
        if target_existed:
            with open(target_archive, 'r', encoding='utf-8') as f:
                orig_target_content = f.read()
                
        with open(target_archive, 'a', encoding='utf-8') as f:
            f.write(archive_text)
            
        with open(target_archive, 'r', encoding='utf-8') as f:
            new_archive_lines = len(f.read().splitlines())
            
        added_archive = new_archive_lines - existing_archive_lines
        if added_archive != lines_to_archive:
            raise ValueError(f"Jumlah baris arsip tidak cocok! Diekstrak: {lines_to_archive}, Tertulis: {added_archive}")
            
    except Exception as e:
        # Rollback archive
        if target_existed and orig_target_content is not None:
            with open(target_archive, 'w', encoding='utf-8') as f:
                f.write(orig_target_content)
        elif not target_existed and target_archive.exists():
            target_archive.unlink()
            
        print(f"[FAIL] Gagal menulis arsip: {e}")
        print("[ABORT] Rotasi dibatalkan. connector.md tetap utuh.")
        sys.exit(1)

    # Now rewrite connector.md
    new_connector_text = ('\n'.join(kept_lines) + '\n') if kept_lines else ''
    with open(connector_file, 'w', encoding='utf-8') as f:
        f.write(new_connector_text)
        
    with open(connector_file, 'r', encoding='utf-8') as f:
        final_connector_lines = len(f.read().splitlines())
        
    # Final assertion: connector + arsip = total_orig
    if final_connector_lines + added_archive != total_orig:
        # Critical rollback
        with open(connector_file, 'w', encoding='utf-8') as f:
            f.write(orig_content)
        if target_existed and orig_target_content is not None:
            with open(target_archive, 'w', encoding='utf-8') as f:
                f.write(orig_target_content)
        elif not target_existed and target_archive.exists():
            target_archive.unlink()
        print("[FAIL] Validasi baris masuk != baris keluar! Seluruh perubahan dibatalkan.")
        sys.exit(1)

    # Update STATE.md if state_file exists
    if state_file.exists():
        try:
            with open(state_file, 'r', encoding='utf-8') as f:
                state_lines = f.read().splitlines()
                
            topic_path = f"history/{topik}/"
            if not any(topic_path in line for line in state_lines):
                table_start_idx = -1
                for i, line in enumerate(state_lines):
                    if "TUTUP lewat chamber, arsip per topik:" in line:
                        table_start_idx = i
                        break
                        
                if table_start_idx != -1:
                    insert_idx = -1
                    for i in range(table_start_idx + 2, len(state_lines)):
                        if state_lines[i].strip() == '```':
                            insert_idx = i
                            break
                    if insert_idx != -1:
                        new_line = f"{topik.ljust(20)} {'(entri baru)'.ljust(38)} {topic_path}"
                        state_lines.insert(insert_idx, new_line)
                        
                        try:
                            from snowline.core_close_entry import renumber_terbuka
                            state_lines = renumber_terbuka(state_lines)
                        except Exception:
                            pass
                            
                        with open(state_file, 'w', encoding='utf-8') as f:
                            f.write('\n'.join(state_lines) + '\n')
        except Exception:
            pass

    print(f"[SUCCESS] Rotasi berhasil: {added_archive} baris dipindah ke {target_archive}, {final_connector_lines} baris tersisa di {connector_file}.")
