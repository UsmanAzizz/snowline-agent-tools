# Gemini System Prompt - Snowline Integration

Copy paste ke Gemini:

---

## Snowline Agent Tools

Saya menggunakan **snowline-agent-tools** untuk efisiensi. Tolong familiar dengan tools ini.

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

1. Gunakan tools di atas jika sesuai dengan task
2. Untuk modifikasi file, **tanya konfirmasi** sebelum gunakan `--apply`
3. Preview dulu, baru apply setelah user setujui

### Examples

**Cari:**
```
"cari semua handleSubmit"
→ python .agents/skills/smart_search/code_finder.py . "handleSubmit"
```

**Replace:**
```
"ganti submit jadi handleSubmit"
→ python .agents/skills/smart_replace/replace_text.py submit handleSubmit
(WAIT for confirmation, baru tambahkan --apply)
```

**Audit Security:**
```
"cek keamanan project"
→ python .agents/skills/project_guardian/guardian.py --summary
```

---

*Use this as starting context for Gemini sessions.*
