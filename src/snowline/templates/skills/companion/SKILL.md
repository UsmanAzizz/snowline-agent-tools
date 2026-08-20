---
name: companion
description: Intent analyzer and tool router. Evaluates ambiguity and enforces safety via Arity Check.
---

# Companion Skill

## CRITICAL: Integration & Architecture (Sprint 18)

Companion kini tidak lagi mengandalkan agen untuk dipanggil secara sukarela. Ia telah diintegrasikan langsung ke dalam **Pre-Prompt Hook (quality_gate.py)** untuk alat-alat yang membutuhkan persetujuan (*approval required*).

### 1. Deterministik (Mengikat & Memblokir)
Bagian dari Companion yang **mengikat** secara mutlak adalah **Arity Check (Kelengkapan Argumen Posisi)**.
Hook akan menghitung jumlah argumen secara matematis tanpa campur tangan LLM.
- `smart_replace`: Wajib minimal 3 argumen (`<dir>`, `<old>`, `<new>`).
- `auto_scaffolder`: Wajib minimal 2 argumen (`<type>`, `<name>`).
**Ambang batas:** Jika jumlah argumen `<` batas minimal, eksekusi **PASTI DITOLAK** dengan status `DENY` karena niat dianggap belum lengkap.

### 2. Heuristik (Menilai & Menyarankan)
Bagian dari Companion yang **menilai** adalah fungsi `analyze_intent()`. Ini murni heuristik (menebak maksud berdasarkan kata kunci dan entitas).
**Ambang batas:** Jika agen memaksa mode destruktif (`--apply`), Hook akan memanggil fungsi ini. Jika *confidence_level* berada di tingkat `LOW` atau `NONE`, Hook akan **menolak eksekusi destruktif** dan menyarankan agen untuk melakukan *dry-run* (tanpa `--apply`) terlebih dahulu.
**Catatan:** Fungsi ini tidak bersifat mutlak (karena bisa tertipu oleh padanan kata baru yang tidak ada di kamus), sehingga perannya adalah *fail-safe* tingkat kedua.

## Agent Decision Matrix (Heuristik)

| Confidence | Specificity | Action |
|------------|-------------|--------|
| HIGH | high | KONFIRMASI |
| HIGH | medium | KONFIRMASI |
| MEDIUM | any | KONFIRMASI |
| LOW | any | CLARIFY |
| NONE | any | CLARIFY |

## Usage (Manual Fallback)

Jika Anda perlu merumus niat secara manual, Anda bisa menggunakan CLI:
```python
from companion import analyze_intent, get_agent_action

result = analyze_intent("ganti fungsi login")
print(result.keywords)
print(result.confidence_level)
print(get_agent_action(result))  # KONFIRMASI/CLARIFY
```

## Fast-Path (Alat Aman)
Alat-alat *read-only* seperti `smart_search`, `selective_reader`, `tree_viewer`, dan `deep_analyzer` kini diizinkan secara instan tanpa melalui evaluasi Companion untuk memangkas latensi.
