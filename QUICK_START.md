# Quick Start - Gemini Integration

## Prerequisites

1. Install snowline-agent-tools
2. Initialize in project

## Installation

```bash
# 1. Install
pip install git+https://github.com/UsmanAzizz/snowline-agent-tools.git

# 2. Initialize project
cd your-project-folder
python -m snowline_toolkit.cli init --apply

# 3. Verify
ls .agents/
# Should see: AGENTS.md, memory.json, skills/
```

## Gemini Prompt Template

Paste ini ke Gemini untuk integrate companion:

```
 Saya menggunakan snowline-agent-tools untuk efisiensi.
 Rules ada di .agents/AGENTS.md dan .agents/skills/rules/

 Tools yang tersedia:
 - smart_search: cari kode
 - smart_replace: replace dengan backup
 - project_guardian: audit security
 - clean_sweeper: scan file sampah
 - deep_analyzer: overview proyek
 - selective_reader: baca file besar
 - crash_decoder: parse error
 - scope_guardian: validasi scope

 Gunakan tools ini jika sesuai dengan task.
 Untuk modifikasi, gunakan --apply hanya setelah konfirmasi saya.
```

## Test Scenarios

### Scenario 1: Find Bug
```
 User: "cari kode yang bikin error handleSubmit"

 Gemini should use: smart_search
 Command: python .agents/skills/smart_search/code_finder.py . "handleSubmit"
```

### Scenario 2: Replace
```
 User: "ganti semua 'submit' jadi 'handleSubmit'"

 Gemini should use: smart_replace
 Command: python .agents/skills/smart_replace/replace_text.py submit handleSubmit

 Wait for confirmation before --apply
```

### Scenario 3: Security Check
```
 User: "cek keamanan di project ini"

 Gemini should use: project_guardian
 Command: python .agents/skills/project_guardian/guardian.py --summary
```

### Scenario 4: Clean Project
```
 User: "bersihin file sampah"

 Gemini should use: clean_sweeper
 Command: python .agents/skills/clean_sweeper/sweeper.py .
```

## Verification Checklist

| Test | Expected | Pass? |
|------|----------|-------|
| Install | No errors | ☐ |
| Init | .agents/ created | ☐ |
| smart_search | Finds code | ☐ |
| smart_replace | Replaces with backup | ☐ |
| project_guardian | Shows issues | ☐ |
| Output format | JSON + readable | ☐ |

## Troubleshooting

### "Template not found"
```bash
pip uninstall snowline-agent-tools -y
pip install git+https://github.com/UsmanAzizz/snowline-agent-tools.git
```

### PATH not set
```bash
python -m snowline_toolkit.cli path
# Follow instructions to add to PATH
```

---

*Last Updated: 2026-07-29*
