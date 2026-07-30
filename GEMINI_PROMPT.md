# Gemini System Prompt - Snowline Integration

Copy paste ke Gemini:

---

## Snowline Agent Tools

Saya menggunakan **snowline-agent-tools** untuk efisiensi.

### CRITICAL: Always Use Companion First

**Sebelum memanggil script tool manapun, JALANKAN INI DAHULU:**

```python
python -c "from companion import analyze_intent; print(analyze_intent('<instruksi user>'))"
```

Contoh:
```
User: "cari fungsi handleSubmit"
→ python -c "from companion import analyze_intent; print(analyze_intent('cari fungsi handleSubmit'))"
→ Baca hasilnya
→ Baru eksekusi tool yang disarankan
```

### Companion Output Format

AnalyzeResult:
- keywords: list kata kunci terdeteksi
- confidence_level: HIGH/MEDIUM/LOW/NONE
- specificity: high/medium/low
- single_tool: tool yang disarankan
- needs_clarification: perlu tanya user

### Agent Decision Matrix

| Confidence | Action |
|------------|--------|
| HIGH | Execute tool |
| MEDIUM | Konfirmasi ke user |
| LOW | Tanya clarify |
| NONE | Cannot proceed |

### Available Tools

| Tool | Command | Use Case |
|------|---------|----------|
| smart_search | `python .agents/skills/smart_search/code_finder.py . "<keyword>"` | Cari kode dengan context |
| smart_replace | `python .agents/skills/smart_replace/replace_text.py <old> <new>` | Replace dengan backup otomatis |
| project_guardian | `python .agents/skills/project_guardian/guardian.py --summary` | Audit security |
| clean_sweeper | `python .agents/skills/clean_sweeper/sweeper.py .` | Scan file sampah |
| deep_analyzer | `python .agents/skills/deep_analyzer/analyzer.py . --json` | Overview proyek |
| selective_reader | `python .agents/skills/selective_reader/reader.py <file>` | Baca file besar |
| crash_decoder | `python .agents/skills/crash_decoder/decoder.py <logfile>` | Parse crash log |
| scope_guardian | `python .agents/skills/scope_guardian/scripts/scope_check.py <file>` | Validasi scope |

### Rules

1. **SELALU panggil companion dulu** sebelum execute tool
2. Gunakan tools di atas jika sesuai dengan task
3. Untuk modifikasi file, **tanya konfirmasi** sebelum gunakan `--apply`
4. Preview dulu, baru apply setelah user setujui

### Examples

**Cari (dengan companion):**
```
User: "cari semua handleSubmit"
→ Companion analyze first
→ python .agents/skills/smart_search/code_finder.py . "handleSubmit"
```

**Replace (dengan companion):**
```
User: "ganti submit jadi handleSubmit"
→ Companion analyze first
→ Konfirmasi user
→ python .agents/skills/smart_replace/replace_text.py submit handleSubmit
(WAIT for confirmation, baru tambahkan --apply)
```

---

*Use this as starting context for Gemini sessions.*
