# Project Context - Key Findings

## Insiden Kunci

### Insiden: Companion Rule Hanya Efektif di AGENTS.md

**Masalah:**
- Aturan "Always Call Companion First" ditaruh di GEMINI_PROMPT.md → Antigravity tidak mengikuti
- Aturan yang sama di AGENTS.md → Antigravity BENERAN mengikuti

**Kronologi:**
1. Instruksi di GEMINI_PROMPT.md → companion tidak dipanggil
2. Instruksi di AGENTS.md → companion BENERAN dipanggil

**Kesimpulan:**
```
"Always Call Companion First" ONLY WORKS if placed in AGENTS.md,
NOT in GEMINI_PROMPT.md or separate files.
```

**Alasan:**
- AGENTS.md adalah file yang DIBACA oleh AI saat sesi dimulai
- GEMINI_PROMPT.md adalah prompt manual yang perlu copy-paste
- AI lebih patuh pada aturan di AGENTS.md karena itu bagian dari workspace context

**Implikasi:**
- Semua aturan utama HARUS di AGENTS.md
- GEMINI_PROMPT.md cukup jadi pointer ke AGENTS.md
- CLAUDE.md sudah mengikuti pola ini (pointer ke AGENTS.md)

---

### Insiden: File Corruption (2026-07-30)

**Masalah:**
- Python script gagal parse regex → file syntax error
- companion_v2.py korup
- Di-restore via `git checkout`

**Solusi:**
- Manual line replacement, bukan Python string manipulation
- Backup sebelum edit besar-besaran

---

### Insiden: Duplikasi companion/

**Masalah:**
- `companion.py` (single-file) vs `companion/` (multi-file)
- Potensi konflik import

**Solusi:**
- Hapus folder `companion/` lama
- Backup ke `.backup_replace/companion/`
- Gunakan single-file `companion.py`

---

### Insiden: pip Cache Menyebabkan Fix Tidak Kepakai

**Masalah:**
- Fix sudah di-push ke GitHub
- User melaporkan hasil install masih versi lama
- Template di local pip cache tidak ter-update

**Kronologi:**
1. Push fix ke GitHub
2. `pip install git+...` → pakai cache lokal
3. Template lama dari cache ter-install
4. User dapat agents.md versi lama

**Solusi WAJIB setiap kali ada fix:**
```bash
pip uninstall snowline-toolkit -y
pip cache purge
pip install git+https://github.com/UsmanAzizz/snowline-agent-tools.git --force-reinstall --no-cache-dir
```

**Catatan CRITICAL:**
- `--no-cache-dir` SAJA tidak cukup
- `--force-reinstall` WAJIB untuk memastikan package di-overwrite
- pip install biasa (tanpa --force-reinstall) tidak selalu menimpa package yang sudah terinstal
- Ini yang menyebabkan fix tidak kepakai meski sudah push

**Pola yang sama dengan safe_print:**
- Fix sudah push → masih error di user
- Penyebab: pip install tidak menimpa package existing
- Solusi: purge + force-reinstall + no-cache-dir

---

### Insiden: ModuleNotFoundError untuk companion

**Masalah:**
- `python -c "from companion import analyze_intent"` → ModuleNotFoundError
- Companion.py ada di `.agents/skills/companion.py`
- Tapi tidak bisa di-import dari project root

**Penyebab (Fundamental Python Limitation):**
```
python -c "from companion import..."
    ↓
Python LIHAT sys.path untuk cari module 'companion'
    ↓
companion.py TIDAK ADA di sys.path
    ↓
ModuleNotFoundError (SEBELUM kode file dibaca)
```

Ini BUKAN bug. Python sudah gagal import SEBELUM execute kode file. Tidak ada auto-discovery yang bisa jalan karena kode tidak pernah dieksekusi.

**Solusi: Opsi A (Jalankan sebagai script)**
```bash
# Cara yang bekerja:
python .agents/skills/companion.py "cari axios"

# Bukan import:
python -c "from companion import..."  # Tidak akan pernah jalan
```

**Kesimpulan:**
- Companion auto-discovery tidak mungkin untuk import statement
- Gunakan `python .agents/skills/companion.py "<input>"` sebagai script
- AGENTS.md sudah diupdate dengan instruksi ini

---

## Arsitektur Companion

### Alur Decision-Making

```
User Input → companion.analyze_intent() → AnalyzeResult
                                        ↓
                    keywords, entities, confidence_level
                                        ↓
                    Agent decides tool based on result
```

### Companion = Pure Data Processor

Companion HANYA return DATA:
- keywords
- entities
- confidence_level
- specificity
- single_tool (suggestion)

Agent yang MEMUTUSKAN tool apa dipakai.

### Tools yang Tidak Perlu Izin (READ)

- deep_analyzer, smart_search, selective_reader
- project_guardian, scope_guardian
- crash_decoder, impact_analyzer
- smart_tree

### Tools yang Butuh Izin (WRITE)

- smart_replace --apply
- auto_scaffolder --apply
- context_mapper --apply
- import_fixer --apply

---

## Dokumentasi Terkait

| File | Fungsi |
|-------|--------|
| AGENTS.md | Aturan utama (WAJIB dibaca AI) |
| CLAUDE.md | Pointer ke AGENTS.md |
| GEMINI_PROMPT.md | Pointer ke AGENTS.md |
| companion.py | Single-file companion v5.0 |
