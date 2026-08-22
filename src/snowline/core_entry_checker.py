import re
import sys
import os

def check_entry(content):
    blocks = re.findall(r'```(.*?)```', content, re.DOTALL)
    
    has_command = False
    has_output = False
    
    for b in blocks:
        lines = b.strip().split('\n')
        if any(line.strip().startswith('$') or line.strip().startswith('python') for line in lines):
            has_command = True
        # If it has lines that don't start with $ and are not comments, we can assume it has output
        # Or if there are multiple blocks, some might be output
        if len(lines) > 1 and any(not (line.strip().startswith('$') or line.strip().startswith('python') or line.strip().startswith('#')) for line in lines):
            has_output = True
            
    if len(blocks) >= 2:
        # One is command, one is output
        has_command = True
        has_output = True

    claims = re.search(r'\b(selesai|berhasil|PASS)\b', content, re.IGNORECASE)
    
    if claims:
        if not (has_command and has_output):
            print(f"[REJECTED] Entri mengklaim selesai ('{claims.group(1)}'), tetapi tidak memiliki blok perintah dan keluaran.")
            return False
            
    print("[PASS] Entri valid.")
    return True

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python core_entry_checker.py <entry_file.md>")
        sys.exit(1)
        
    try:
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Gagal membaca file: {e}")
        sys.exit(1)
        
    if not check_entry(content):
        sys.exit(1)
