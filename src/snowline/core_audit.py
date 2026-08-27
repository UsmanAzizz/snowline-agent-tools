import os
import sys
import json
from collections import defaultdict
from datetime import datetime

def parse_iso(dt_str):
    if not dt_str:
        return None
    try:
        return datetime.fromisoformat(dt_str)
    except Exception:
        try:
            return datetime.strptime(dt_str[:10], "%Y-%m-%d")
        except Exception:
            return None

def run_audit(sejak=None, hanya_luar_lingkup=False, root_dir=None):
    if root_dir is None:
        cur = os.path.abspath(os.getcwd())
        while True:
            candidate = os.path.join(cur, '.agents')
            if os.path.isdir(candidate):
                root_dir = cur
                break
            parent = os.path.dirname(cur)
            if parent == cur:
                break
            cur = parent
        if root_dir is None:
            root_dir = os.path.abspath(os.getcwd())

    log_file = os.path.join(root_dir, '.agents', 'write_log.jsonl')
    
    if not os.path.exists(log_file):
        print("Belum ada catatan tulisan di .agents/write_log.jsonl.")
        return 0

    sejak_dt = None
    if sejak:
        sejak_dt = parse_iso(sejak)
        if sejak_dt is None:
            print(f"[WARN] Format tanggal --sejak tidak valid: {sejak}")

    valid_entries = []
    corrupt_count = 0

    with open(log_file, 'r', encoding='utf-8') as f:
        for line in f:
            line_str = line.strip()
            if not line_str:
                continue
            try:
                data = json.loads(line_str)
                if isinstance(data, dict) and "berkas" in data:
                    valid_entries.append(data)
                else:
                    corrupt_count += 1
            except Exception:
                corrupt_count += 1

    if corrupt_count > 0:
        print(f"[WARN] {corrupt_count} baris log rusak dilewati.")

    if not valid_entries:
        print("Belum ada catatan tulisan yang valid.")
        return 0

    if sejak_dt:
        filtered = []
        for e in valid_entries:
            e_dt = parse_iso(e.get("waktu", ""))
            if e_dt and e_dt >= sejak_dt:
                filtered.append(e)
        valid_entries = filtered
        if not valid_entries:
            print(f"Tidak ada catatan tulisan sejak {sejak}.")
            return 0

    total_tulisan = len(valid_entries)
    luar_lingkup_entries = [e for e in valid_entries if not e.get("dalam_lingkup", True)]
    total_luar = len(luar_lingkup_entries)
    shell_count = sum(1 for e in valid_entries if e.get("alat") == "shell")

    if not hanya_luar_lingkup:
        print(f"{total_tulisan} tulisan, {total_luar} di luar lingkup\n")
    else:
        print(f"{total_luar} tulisan di luar lingkup (dari {total_tulisan} total)\n")

    if luar_lingkup_entries:
        print("di luar lingkup:")
        counts = defaultdict(int)
        for e in luar_lingkup_entries:
            b = e.get("berkas", "unknown")
            t = e.get("tugas", "")
            counts[(b, t)] += 1
            
        for (berkas, tugas), count in sorted(counts.items()):
            tugas_str = f'tugas "{tugas}"' if tugas else 'tanpa tugas'
            print(f"  {berkas:<20} {tugas_str:<25} {count} kali")
        print()
    elif hanya_luar_lingkup:
        print("Tidak ada tulisan di luar lingkup.\n")

    if not hanya_luar_lingkup:
        print(f"lewat shell (deteksi best-effort): {shell_count}")

    return 0
