# Gemini Integration - Snowline

## Quick Start

Untuk Gemini session, paste ini:

---

```
Saya menggunakan snowline-agent-tools.
Baca aturan lengkap di: .agents/AGENTS.md
```

---

## Kenapa Perlu AGENTS.md?

**Insiden:** Aturan "Always Call Companion First" tidak efektif kalau ditaruh di prompt terpisah. AI hanya mengikuti aturan yang ada di AGENTS.md (workspace context).

**Solusi:** Gemini cukup baca AGENTS.md seperti Claude Code.

## Companion Usage

```
python -c "from companion import analyze_intent; print(analyze_intent('<instruksi>'))"
```

Hasil: keywords, entities, confidence, suggested_tool

## Tool Execution

- **READ tools** (analisa, search): langsung jalan tanpa izin
- **WRITE tools** (replace, scaffold): butuh konfirmasi dengan `--apply`

---

*Untuk detail lengkap, lihat AGENTS.md*
