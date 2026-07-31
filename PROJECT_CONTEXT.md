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
