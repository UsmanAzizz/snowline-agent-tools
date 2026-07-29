# ⚠️ LOCKED FILE — Read-Only Reference

File ini berisi konteks historis dan kesepakatan dasar proyek. 
JANGAN mengedit, menimpa, atau menghapus isi file ini secara otomatis.
Jika ada informasi yang perlu ditambahkan atau dikoreksi, WAJIB meminta 
persetujuan eksplisit dari user terlebih dahulu sebelum mengubah file ini.

---

# Project Context - snowline-agent-tools

## Asal-usul Proyek

snowline-agent-tools dibangun lewat kolaborasi panjang:

```
Gemini/Antigravity → Eksekusi kode
Claude (claude.ai) → Review dan validasi
Usman → Approve keputusan akhir
```

Bukan dibangun dari nol di sesi baru. Setiap sesi baru melanjutkan ekosistem yang sudah ada.

---

## Insiden Kunci yang Membentuk Aturan

### 1. Snowline OS Reset
Arsitektur besar (SQLite, OOP, adapter) dibangun tanpa validasi bertahap. Hasil: reset total karena ketahuan over-engineered.

### 2. Klaim Tanpa Bukti (Berulang)
Berkali-kali Gemini/Antigravity klaim "sudah selesai/sudah aman" tanpa bukti nyata. Setiap kali itu terjadi, user insist minta live-test sebelum percaya.

### 3. Bug --apply Otomatis (2026-07-29)
companion_core.py sebelumnya menyertakan flag `--apply` secara otomatis di command preview — sebelum user memberi persetujuan. Ini berarti companion sudah "memutuskan untuk menjalankan" bukan cuma "menyiapkan preview".

**Fix yang diterapkan (v4.4):**
- `get_params()` tidak lagi mengandung `--apply`
- `build_execution_command(step, approved=True)` diperlukan untuk menambahkan `--apply`
- `--apply` ditambahkan HANYA setelah persetujuan eksplisit user
- `needs_approval()` mencakup: smart_replace, auto_scaffolder, context_mapper, import_fixer

### 4. TASK 7 "Agent-Free Execution" Ditolak (2026-07-29)
Konsep yang mengusulkan companion menjalankan file_deleter/command_runner/git_operator secara otonom — agent cuma "menonton dan validasi akhir". Ditolak total dan dihapus dari roadmap.

**Alasan penolakan:**
- Bertentangan dengan prinsip persetujuan eksplisit sebelum aksi yang mengubah/menghapus file
- Companion tidak boleh "memutuskan untuk mengeksekusi" — harus selalu butuh approval eksplisit
- Ini bukan soal teknis, tapi soal arsitektur kepercayaan

**Implikasi:**
- Semua tool yang write/modify HARUS punya approval step
- Tidak ada autonomous execution tanpa konfirmasi
- Disiplin ini krusial untuk sesi-sesi berikutnya

**Audit lengkap (2026-07-29):**
- 16 tools di ecosystem (14 core + 2 context management)
- 4 tools yang write/modify: smart_replace, auto_scaffolder, context_mapper, import_fixer
- 12 tools read-only: smart_search, selective_reader, project_guardian, dll.
- Semua write-tools sudah dilindungi dengan approval requirement

---

## Disiplin Kerja Wajib

### Prinsip 1: Klaim = Bukti
Setiap klaim "selesai" atau "aman" harus dibuktikan lewat live-test nyata (output mentah), bukan dinarasikan meyakinkan.

### Prinsip 2: Ragu = Cek
Kalau ragu soal status task/file, cek ke state/disk yang sebenarnya sebelum menyampaikan sesuatu sebagai fakta.

### Prinsip 3: Satu Task
Satu task, satu waktu — tidak melebar ke hal lain sebelum yang sedang dikerjakan selesai dan diverifikasi.

### Prinsip 4: Nyata > Spekulasi
Bangun sesuatu berdasarkan kebutuhan nyata yang sudah terbukti, bukan spekulasi kebutuhan yang belum terjadi.

---

## Filosofi Token Efficiency

### Target
Portable efficiency lintas platform AI manapun:
- Gemini
- Claude
- Platform lain

Bukan optimasi untuk satu vendor spesifik.

### Prinsip Teknis
- Pure Python
- Minimal external dependencies
- Scope-aware (tidak spill ke luar project)

---

## Catatan tentang File reflections/memories

File di `C:\Users\LENOVO\Desktop\pemahaman persepsi dengan claude\` berisi observasi personal user dari percakapan lain.

**Boleh digunakan untuk:**
- Menyesuaikan gaya komunikasi (misal: jawaban langsung, tidak berlebihan)
- Memahami preferensi kerja

**Tidak boleh digunakan untuk:**
- Psikoanalisis balik ke user
- Membahas sebagai subjek di tengah percakapan teknis

---

## Alur Modifikasi File (Safety)

### Sebelum Fix (v4.3 dan sebelumnya)
```
User: "ganti hello jadi goodbye"
companion.get_command() → "... --apply"  ❌ OTOMATIS
```

### Sesudah Fix (v4.4)
```
User: "ganti hello jadi goodbye"
companion.get_command() → "... (tanpa --apply)"  ✅ PREVIEW

User: "ya, jalankan"
build_execution_command(step, approved=True) → "... --apply"  ✅ SETELAH PERSETUJUAN
```

### Tools yang Perlu Approval
- smart_replace (modifies files)
- auto_scaffolder (creates files)
- context_mapper (creates documentation)
- import_fixer (modifies import paths)

### Tools yang Aman (Tanpa Approval)
- smart_search, selective_reader, project_guardian, clean_sweeper
- deep_analyzer, crash_decoder, impact_analyzer, scope_guardian
- smart_tree, token_budget, context_curator, output_formatter, decision_validator

### Tools yang Ada tapi Read-only
- db_extractor (read-only, extracts schema info)

---

## Struktur Companion Layer

```
companion_core.py
├── analyze_intent()     → Intent analysis
├── plan_steps()        → Tool planning
├── get_params()        → Params template (NO --apply)
├── get_command()       → Preview command
├── build_execution_command() → Execution command (with --apply if approved)
├── needs_approval()     → Check if tool needs approval
├── learn()            → Record to memory
└── recall()           → Suggest from memory

memory.py
├── Project-scoped: .agents/memory.json
└── NOT di ~/.snowline_memory.json

executor.py
├── Passive wrapper
└── Runs commands via subprocess
```

---

*Last Updated: 2026-07-29 (audit + context_mapper fix)*
