import os
import sys

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

IGNORE_DIRS = {'node_modules', '.git', 'vendor', 'dist', 'build', '.history', 'quarantine', '.backup_replace'}
KNOWLEDGE_DIR = '.agents/knowledge'

def generate_tree(dir_path, prefix=""):
    tree_str = ""
    try:
        entries = sorted(os.listdir(dir_path))
    except Exception:
        return ""
        
    entries = [e for e in entries if e not in IGNORE_DIRS]
    for i, entry in enumerate(entries):
        path = os.path.join(dir_path, entry)
        is_last = (i == len(entries) - 1)
        connector = "└── " if is_last else "├── "
        
        if os.path.isdir(path):
            tree_str += f"{prefix}{connector}📁 {entry}/\n"
            extension = "    " if is_last else "│   "
            tree_str += generate_tree(path, prefix + extension)
        else:
            if not entry.startswith('.'): # Skip hidden files for cleanliness
                tree_str += f"{prefix}{connector}📄 {entry}\n"
    return tree_str

def main():
    target_dir = os.getcwd()
    knowledge_path = os.path.join(target_dir, KNOWLEDGE_DIR)
    
    os.makedirs(knowledge_path, exist_ok=True)
    
    # 1. Generate PROJECT_STRUCTURE.md
    struct_path = os.path.join(knowledge_path, 'PROJECT_STRUCTURE.md')
    tree = generate_tree(target_dir)
    
    with open(struct_path, 'w', encoding='utf-8') as f:
        f.write("# 🗺️ Peta Struktur Proyek\n\n")
        f.write("Peta ini dibuat otomatis oleh `context_mapper.py`. AI diinstruksikan untuk membaca file ini saat pertama kali masuk ke proyek untuk memahami arsitektur tanpa harus me-scan seluruh folder.\n\n")
        f.write("```text\n")
        f.write(f"📁 {os.path.basename(target_dir)}/\n")
        f.write(tree)
        f.write("```\n")

    # 2. Generate COMMON_PATTERNS.md if not exists
    patterns_path = os.path.join(knowledge_path, 'COMMON_PATTERNS.md')
    if not os.path.exists(patterns_path):
        with open(patterns_path, 'w', encoding='utf-8') as f:
            f.write("# 🧩 Konvensi & Pola Kode (Common Patterns)\n\n")
            f.write("File ini berisi aturan-aturan dasar proyek. AI WAJIB membaca file ini sebelum menulis kode.\n\n")
            f.write("## 1. Arsitektur\n- Tulis konvensi arsitektur di sini (misal: semua API ada di `src/services`).\n\n")
            f.write("## 2. Gaya Kode (Code Style)\n- Tulis aturan styling (misal: dilarang pakai Tailwind, gunakan Vanilla CSS).\n\n")
            f.write("## 3. Keamanan\n- Dilarang menyimpan credential di dalam kode. Selalu gunakan `.env`.\n")

    print(f"[OK] Knowledge Catalog berhasil dibuat/diperbarui di folder `{KNOWLEDGE_DIR}/`.")
    print("\n💡 PROMPT UNTUK AI (Copy-Paste ini):")
    print('"Mulai sekarang, setiap kali Anda menangani proyek ini, tolong panggil view_file pada .agents/knowledge/PROJECT_STRUCTURE.md dan COMMON_PATTERNS.md terlebih dahulu sebelum melakukan pencarian atau menulis kode."')

if __name__ == "__main__":
    main()
