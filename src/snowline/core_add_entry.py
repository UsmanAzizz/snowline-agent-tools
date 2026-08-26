import os
import sys
import re
from pathlib import Path

def get_connector_path() -> Path | None:
    for base in [".here_we_are", ".agents/chamber"]:
        p = Path(base) / "connector.md"
        if p.exists():
            return p
    return None

def add_entry(from_file: str = None, use_stdin: bool = False) -> int:
    if not from_file and not use_stdin:
        print("Batal: Gunakan --from-file <berkas> atau --stdin.")
        return 1
        
    if from_file and use_stdin:
        print("Batal: Tidak bisa menggunakan --from-file dan --stdin bersamaan.")
        return 1

    content = ""
    if from_file:
        try:
            with open(from_file, "r", encoding="utf-8") as f:
                content = f.read()
        except UnicodeDecodeError:
            try:
                with open(from_file, "r", encoding="utf-16") as f:
                    content = f.read()
            except Exception as e:
                print(f"Gagal membaca berkas: {e}")
                return 1
    else:
        content = sys.stdin.read()

    if not content:
        print("Batal: Masukan kosong.")
        return 1

    content = content.lstrip('\ufeff')

    pattern = r'^#\s+[A-Za-z0-9_]+\s+->\s+[A-Za-z0-9_]+:\s+[^\n]+'
    if not bool(re.search(pattern, content.strip())):
        print("Batal: Entri ditolak. Masukan harus diawali dengan bentuk '# <PERAN> -> <PERAN>: <judul>'.")
        return 1

    connector = get_connector_path()
    if not connector:
        print("Batal: connector.md tidak ditemukan di .here_we_are/ atau .agents/chamber/")
        return 1

    with open(connector, "a", encoding="utf-8", newline="\n") as f:
        f.write("\n\n" + content.strip() + "\n")

    print(f"Berhasil menambahkan entri ke {connector}.")
    return 0
