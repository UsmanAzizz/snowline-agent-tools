"""
Core Role - Manajemen Peran Chamber (TL/QA/PM)
"""

import json
import os
from pathlib import Path

def print_info(msg):
    print(f"[*] {msg}")

def print_success(msg):
    print(f"[SUCCESS] {msg}")

def print_warning(msg):
    print(f"[WARN] {msg}")

def print_header(title):
    print("=" * 50)
    print(f"  {title}")
    print("=" * 50)

def get_role_file_path(cwd: Path = None):
    if cwd is None:
        cwd = Path.cwd()
        
    chamber_file = cwd / ".agents" / "chamber" / "role.json"
    here_file = cwd / ".here_we_are" / "role.json"
    
    if chamber_file.exists():
        return chamber_file, True
    if here_file.exists():
        return here_file, True
        
    return chamber_file, False

def role_command(role_name: str = None, apply: bool = False, cwd: Path = None):
    if cwd is None:
        cwd = Path.cwd()
        
    role_file, exists = get_role_file_path(cwd)

    # 1. Tampilkan peran saat ini jika tidak ada argumen nama peran
    if not role_name:
        if not exists:
            print_info("Peran belum diatur (role.json belum ditemukan).")
            return
        
        try:
            raw = role_file.read_text(encoding="utf-8").strip()
            if not raw:
                print_info("Peran belum diatur (role.json kosong).")
                return
            data = json.loads(raw)
            current_role = data.get("role") or data.get("peran")
            if not current_role:
                print_info("Peran belum diatur (nilai peran null/kosong).")
            else:
                print(f"Peran sekarang: {current_role}")
        except Exception as e:
            print_warning(f"Gagal membaca role.json: {e}")
        return

    # 2. Normalisasi nama peran
    clean_role = role_name.strip()
    if clean_role.upper() in ["QA", "TL", "PM", "EXECUTOR"]:
        clean_role = clean_role.upper()

    # 3. Dry-run jika tanpa --apply
    if not apply:
        print_info(f"[DRY-RUN] Peran akan diubah menjadi: {clean_role}")
        print_info(f"Target berkas: {role_file}")
        print_info("Jalankan dengan --apply untuk menerapkan perubahan peran.")
        return

    # 4. Terapkan perubahan (--apply)
    role_file.parent.mkdir(parents=True, exist_ok=True)
    role_data = {"role": clean_role, "peran": clean_role}
    role_file.write_text(json.dumps(role_data, indent=2) + "\n", encoding="utf-8")
    
    print_success(f"Peran berhasil diubah menjadi: {clean_role}")
    print()
    print_header("INSTRUKSI UNTUK MANUSIA / OPERATOR BERIKUTNYA")
    if clean_role == "QA":
        print("Sesi TL telah selesai dan peran diserahkan ke QA.")
        print("Langkah yang harus dilakukan operator:")
        print("  1. Tutup / akhiri sesi agen TL saat ini.")
        print("  2. Buka sesi agen BARU yang terpisah untuk QA.")
        print("  3. Tempelkan berkas ONBOARDING_QA.md (.agents/chamber/ONBOARDING_QA.md) ke sesi QA baru.")
        print("  4. Minta QA memeriksa entri connector terbaru dan memverifikasi pekerjaan TL.")
    elif clean_role == "TL":
        print("Peran diserahkan kembali ke TL.")
        print("Langkah yang harus dilakukan operator:")
        print("  1. Tutup sesi saat ini jika diperlukan.")
        print("  2. Buka sesi agen untuk TL.")
        print("  3. Tempelkan berkas ONBOARDING_TL.md (.agents/chamber/ONBOARDING_TL.md).")
        print("  4. Minta TL membaca arahan/vonis terbaru di .here_we_are/connector.md.")
    elif clean_role == "PM":
        print("Peran diserahkan ke PM.")
        print("Langkah yang harus dilakukan operator:")
        print("  1. Buka sesi panduan ONBOARDING_PM.md (.agents/chamber/ONBOARDING_PM.md).")
        print("  2. Tuliskan sprint atau entri tugas baru di .here_we_are/connector.md.")
    else:
        print(f"Peran diserahkan ke {clean_role}.")
        print("Langkah yang harus dilakukan operator:")
        print("  1. Tutup sesi agen saat ini.")
        print(f"  2. Buka sesi agen baru dengan peran {clean_role}.")
        print("  3. Siapkan konteks tugas yang relevan dari .agents/chamber/.")
