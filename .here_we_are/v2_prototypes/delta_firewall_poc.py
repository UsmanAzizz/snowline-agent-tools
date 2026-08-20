import re
import sys
import os

# Tier 1 Defense: Known Attack Signatures (Regex/Keywords)
INJECTION_SIGNATURES = [
    r"(?i)ignore\s+(all\s+)?(previous\s+)?instructions",
    r"(?i)forget\s+(all\s+)?context",
    r"(?i)system\s+override",
    r"(?i)you\s+are\s+now\s+(a\s+)?(different\s+)?agent"
]

DANGEROUS_COMMANDS = [
    r"(?i)rm\s+-rf",
    r"(?i)curl\s+.*-d",
    r"(?i)wget\s+",
    r"(?i)chmod\s+(777|o\+w)"
]

def scan_text(text):
    """Scan text against known malicious signatures."""
    for sig in INJECTION_SIGNATURES:
        if re.search(sig, text):
            return False, f"Instruction Smuggling Detected ({sig})"
            
    for cmd in DANGEROUS_COMMANDS:
        if re.search(cmd, text):
            return False, f"Dangerous Command Pattern Detected ({cmd})"
            
    return True, "Clean"

def mark_data(text):
    """Wrap content to enforce it as passive data."""
    return f"\n<untrusted_file_content>\n{text}\n</untrusted_file_content>\n"

def read_file_safe(filepath):
    """Read a file safely through the LLM Firewall."""
    if not os.path.exists(filepath):
        print(f"[ERROR] Firewall: File {filepath} tidak ditemukan.")
        sys.exit(1)
        
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"[ERROR] Gagal membaca file: {e}")
        sys.exit(1)
        
    is_safe, reason = scan_text(content)
    
    if not is_safe:
        print(f"\n[BLOCKED] LLM Firewall Mencegat Potensi Prompt Injection!")
        print(f"File: {filepath}")
        print(f"Reason: {reason}")
        print("Teks ini TIDAK BOLEH masuk ke dalam jendela memori agen.")
        sys.exit(1)
        
    # Jika aman, bungkus sebagai passive data
    marked_content = mark_data(content)
    print(f"[OK] Firewall: {filepath} lolos pemindaian. Berikut output terbungkus:")
    print(marked_content)
    sys.exit(0)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python delta_firewall_poc.py <filepath>")
        sys.exit(1)
        
    read_file_safe(sys.argv[1])
