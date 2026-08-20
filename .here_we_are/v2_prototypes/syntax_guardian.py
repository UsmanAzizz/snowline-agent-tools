import ast
import sys
import os

def check_syntax(filepath):
    if not os.path.exists(filepath):
        print(f"[ERROR] Syntax Guardian: File {filepath} tidak ditemukan.")
        sys.exit(1)
        
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"[ERROR] Gagal membaca file: {e}")
        sys.exit(1)
        
    try:
        # Mencoba melakukan parsing AST secara statis
        ast.parse(content)
        print(f"[OK] Syntax Guardian: AST valid untuk {filepath}. Aman untuk dijalankan.")
        sys.exit(0)
    except SyntaxError as e:
        print(f"\n[BLOCKED] Syntax Guardian: Terdeteksi kesalahan Syntax (AST Invalid)!")
        print(f"File: {filepath}")
        print(f"Baris {e.lineno}: {e.msg}")
        print(f"Detail: {e.text.strip() if e.text else ''}")
        print("\nOperasi dihentikan. LLM dilarang menyimpan/mengeksekusi kode yang rusak secara statis.")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python syntax_guardian.py <filepath>")
        sys.exit(1)
        
    check_syntax(sys.argv[1])
