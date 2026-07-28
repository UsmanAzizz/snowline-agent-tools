# Project Rules (Snowline Agent Ecosystem)

- Sebelum membuat fungsi baru, selalu definisikan semua variabel yang akan digunakan terlebih dahulu (untuk menghindari *ReferenceError* atau variabel yang belum di-*destructure*).

## 🛑 DAFTAR TOOLS INTI (MANDATORY)

Anda DILARANG KERAS menggunakan tool bawaan (seperti grep_search, cat, ls) jika ada tool custom Snowline yang lebih hemat token.
1. **Memulai Sesi**: deep_analyzer/analyzer.py
2. **Mencari Kode**: smart_search/code_finder.py <dir> <keyword>
3. **Edit Masal**: smart_replace/replace_text.py <dir> <search> <replace>
4. **Membaca File Besar**: selective_reader/reader.py <file>
5. **Audit Keamanan/Bug**: project_guardian/guardian.py
6. **Cari File Sampah**: clean_sweeper/sweeper.py <dir>
7. **Debug Crash**: crash_decoder/decoder.py <file>
8. **Buat File Baru**: uto_scaffolder/scaffolder.py <type> <name>
9. **Fix Import**: import_fixer/fixer.py <file> <import_string>

## 🟢 Aturan Universal (Selalu Berlaku Tanpa Syarat)

## ðŸŸ¢ Fast-Track Analytics (No Confirmation Needed)
For any Python tools that are strictly **Read-Only / Analytical** (such as `deep_analyzer`, `impact_analyzer`, `smart_search`, `selective_reader`, and `scope_check.py`), you are **FULLY AUTHORIZED** to execute them immediately in the background without asking for the user's permission. Do not wait for user approval or create a `PLAN.md` entry just to read or analyze files. You only need to ask for permission when executing modifying/write tools (e.g., `replace_text.py --apply`).



## Live Progress Tracker (PLAN.md)
- **MANDATORY**: For every significant task, you MUST maintain a `PLAN.md` file in the root directory.
- **Execution Rules**:
  1. APPEND ONLY. Do not rewrite the whole file just to add a log entry.
  2. Write concise, bulleted logs, not paragraphs.
  3. **CRITICAL**: Before executing any command that MODIFIES files (like replace_text.py --apply), write your intended action in the "Waiting for User Approval" section and STOP for user approval.
  4. Once a task is fully completed, archive the file to `plan_archive/PLAN_<date>_<task_name>.md`.




## 📁 INDEKS MODUL ATURAN KHUSUS

Silakan BACA file-file di bawah ini (menggunakan tool iew_file pada .agents/rules/...) HANYA JIKA tugas Anda berkaitan dengan topik tersebut:

- **
ules/scope_guardian.md** : Baca ini jika Anda akan melakukan modifikasi file (Aturan Scope Lock).
- **
ules/plan_first.md** : Baca ini sebelum mengeksekusi multi-langkah atau modifikasi (One-Task-One-Time).
- **
ules/tool_usage.md** : Baca ini untuk aturan ketat penggunaan tool modifikasi dan pencarian.
- **
ules/communication.md** : Baca ini untuk format Tag laporan, Mode Komunikasi, dan Anti-Hype.
- **
ules/session_control.md** : Baca ini untuk mekanisme END, CONTINUE, KILL, dan Caching.
- **
ules/guardrail_compliance.md** : Baca ini JIKA Anda diminta membuat/mengubah skrip tool baru.
- **
ules/tech_lead_disciplines.md** : Baca ini untuk panduan investigasi bug dan implicit grilling.
