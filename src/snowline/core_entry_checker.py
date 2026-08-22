import re
import sys
import os

def check_entry(content):
    blocks = re.findall(r'```(.*?)```', content, re.DOTALL)
    
    has_command = False
    has_output = False
    output_text = ""
    
    for b in blocks:
        lines = b.strip().split('\n')
        if any(line.strip().startswith('$') or line.strip().startswith('python') for line in lines):
            has_command = True
        # If it has lines that don't start with $ and are not comments, we can assume it has output
        if len(lines) > 1 and any(not (line.strip().startswith('$') or line.strip().startswith('python') or line.strip().startswith('#')) for line in lines):
            has_output = True
        
        output_text += b + "\n"
            
    # Include inline code blocks as well (e.g., `40/40 passed`)
    inline_blocks = re.findall(r'`([^`]+)`', content)
    for ib in inline_blocks:
        output_text += ib + "\n"

    if len(blocks) >= 2:
        # One is command, one is output
        has_command = True
        has_output = True

    claims = re.search(r'\b(selesai|berhasil|PASS)\b', content, re.IGNORECASE)
    
    if claims:
        if not (has_command and has_output):
            print(f"[REJECTED] Entri mengklaim selesai ('{claims.group(1)}'), tetapi tidak memiliki blok perintah dan keluaran.")
            return False

    # Pengecekan Kuantitatif (Entri 27)
    # Hapus blok kode dari teks narasi (baik block maupun inline)
    narrative_text = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
    narrative_text = re.sub(r'`[^`]+`', '', narrative_text)
    # Hapus header markdown (klaim kuantitatif di judul/header tidak dihitung, biasanya ringkasan)
    narrative_text = re.sub(r'^#+.*$', '', narrative_text, flags=re.MULTILINE)
    
    quantitative_claims = []
    # percentage
    quantitative_claims.extend(re.findall(r'\b\d+(?:,\d+)?%', narrative_text))
    # ratio
    quantitative_claims.extend(re.findall(r'\b\d+/\d+\b', narrative_text))
    quantitative_claims.extend(re.findall(r'\b\d+\s+dari\s+\d+\b', narrative_text, re.IGNORECASE))
    # duration
    quantitative_claims.extend(re.findall(r'\b\d+(?:,\d+)?\s+(?:detik|menit|jam|ms)\b', narrative_text, re.IGNORECASE))
    # count
    quantitative_claims.extend(re.findall(r'\b\d+(?:\.\d+)?\s+(?:berkas|baris|file|kesalahan|temuan)\b', narrative_text, re.IGNORECASE))

    for claim in quantitative_claims:
        # Kita hanya mencari angka/nilai aslinya di output_text.
        # Jika claim adalah "108 berkas", kita cari "108" di output_text.
        # Extract number from claim
        num_match = re.search(r'\d+(?:[.,]\d+)?', claim)
        if num_match:
            num_str = num_match.group(0)
            if num_str not in output_text:
                print(f"[REJECTED] Angka klaim pengukuran '{claim}' tidak ditemukan sumbernya di blok keluaran.")
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
