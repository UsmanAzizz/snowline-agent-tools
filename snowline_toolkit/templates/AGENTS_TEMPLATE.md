# Project Rules (Snowline Agent Ecosystem)

## ⚡ ATURAN WAJIB NOMOR 1 — PANGGIL COMPANION DULU

Sebelum memanggil tool/script apa pun (search, replace, analyze, dll),
WAJIB jalankan dulu:
```
python .agents/skills/companion_cli.py "<instruksi user>"
```

Baca hasilnya. Gunakan sebagai referensi tool mana yang dipanggil.
Ini berlaku untuk SEMUA instruksi kerja teknis, termasuk yang terlihat sederhana.

**Pengecualian — JANGAN panggil companion untuk:**
1. Sapaan/basa-basi ("hai", "halo", "terima kasih", dll) — balas natural langsung, tidak perlu analisis intent.
2. Pengecekan ekosistem project di awal sesi (lihat bagian "Auto-Setup Project Essentials" di bawah) — itu proses tersendiri yang jalan independen, tidak lewat companion.
3. Pertanyaan yang murni percakapan (bukan instruksi kerja), misal user bertanya soal status/opini, bukan minta eksekusi tool.

Jika ragu apakah sebuah pesan itu instruksi kerja atau sekadar percakapan, pakai heuristik sederhana: apakah menjawabnya butuh menyentuh file/kode project? Jika ya, panggil companion dulu. Jika tidak, jawab langsung.

**Sebelum membuat fungsi baru:**
Definisi semua variabel yang akan digunakan terlebih dahulu (untuk menghindari *ReferenceError* atau variabel yang belum di-*destructure*).

---

## ⚠️ TRANSPARANSI WAJIB — LAPORKAN ERROR

Setiap kali eksekusi tool/mekanisme gagal dan berhasil diatasi sendiri,
WAJIB dilaporkan ke user secara singkat.

**Format:**
```
[INFO] companion sempat gagal karena ModuleNotFoundError, sudah diatasi otomatis, lanjut ke hasil
```

**Contoh error yang WAJIB dilaporkan:**
- Import/dependency errors yang diatasi sendiri
- Path resolution errors yang berhasil diperbaiki
- Timeout/retry yang berhasil setelah percobaan kedua
- Fallback mechanism yang terpakai

**PRINSIP: Jangan sembunyikan proses troubleshooting demi "efisiensi" — transparansi adalah inti ekosistem ini.**

---

## ✅ TOOLS INI TIDAK PERLU IZIN (LANGSUNG JALAN)

Tool analytical/read-only berikut TIDAK PERLU konfirmasi:
- `deep_analyzer` / `impact_analyzer` — analisa project
- `smart_search` — cari kode
- `selective_reader` — baca file
- `smart_tree` — lihat struktur folder
- `scope_guardian` / `scope_check.py` — cek scope
- `project_guardian` / `guardian.py` — audit keamanan
- `crash_decoder` / `decoder.py` — debug crash
- `token_budget`, `context_curator`, `output_formatter` — context management

**LANGSUNG JALAN. TIDAK PERLU TUNGGU APPROVAL.**

---

## 🔒 TOOLS INI MEMBUTUHKAN IZIN (DENGAN --apply)

Hanya tool yang MEMODIFIKASI file yang butuh persetujuan:
- `smart_replace --apply` — edit masal
- `auto_scaffolder --apply` — buat file baru
- `context_mapper --apply` — buat dokumentasi
- `import_fixer --apply` — fix import paths

**BARU JALAN SETELAH USER SETUJU.**

---

## 🚨 Security Findings - Mandatory Halt

Jika `project_guardian` melaporkan temuan CRITICAL:
1. **STOP SEGERA** — jangan lanjutkan task atau instruksi lain
2. **LAPORKAN** temuan tersebut ke user dengan detail lengkap
3. **TUNGGU** konfirmasi eksplisit dari user sebelum melanjutkan
4. Ini berlaku **MESKIPUN** instruksi asli tidak menyebut soal keamanan

Meskipun user meminta "cuma fix X" tanpa menyebut keamanan, temuan CRITICAL tetap diutamakan — laporkan dulu.

---

## 📋 Tools Inti (MANDATORY)

Anda DILARANG KERAS menggunakan tool bawaan (seperti grep_search, cat, ls) jika ada tool custom Snowline yang lebih hemat token.
1. **Memulai Sesi**: deep_analyzer/analyzer.py
2. **Mencari Kode**: smart_search/code_finder.py <dir> <keyword>
3. **Edit Masal**: smart_replace/replace_text.py <dir> <search> <replace>
4. **Membaca File Besar**: selective_reader/reader.py <file>
5. **Audit Keamanan/Bug**: project_guardian/guardian.py
6. **Cari File Sampah**: clean_sweeper/sweeper.py <dir>
7. **Debug Crash**: crash_decoder/decoder.py <file>
8. **Buat File Baru**: auto_scaffolder/scaffolder.py <type> <name>
9. **Fix Import**: import_fixer/fixer.py <file> <import_string>

## 📦 Auto-Setup Project Essentials

Di awal sesi kerja, cek apakah 3 hal ini ada di root project:
1. `.agents/knowledge/` — peta arsitektur dari Context Mapper
2. `PLAN.md` — tracker di root project (bukan di `.agents/`)
3. `.agents/scope_lock.json` — jika sedang mengerjakan task yang mengubah file

**Format tanya ke user:**
```
[INFO] Komponen ekosistem project belum lengkap: [daftar yang hilang]. Ingin saya setup sekarang?
```

**Tunggu konfirmasi eksplisit sebelum membuat file/folder apa pun.**

Setelah user setuju:
- Jalankan Context Mapper → generate `knowledge/`
- Scaffold `PLAN.md` kosong di root
- Buat `scope_lock.json` sesuai task

**Catatan:** Ini TIDAK termasuk auto-detect/auto-create symlink skills — itu manual.

## Live Progress Tracker (PLAN.md)

- **MANDATORY**: For every significant task, you MUST maintain a `PLAN.md` file in the root directory.
- **Execution Rules**:
  1. APPEND ONLY. Do not rewrite the whole file just to add a log entry.
  2. Write concise, bulleted logs, not paragraphs.
  3. **CRITICAL**: Before executing any command that MODIFIES files (like replace_text.py --apply), write your intended action in the "Waiting for User Approval" section and STOP for user approval.
  4. Once a task is fully completed, archive the file to `plan_archive/PLAN_<date>_<task_name>.md`.

## Aturan Inti

**1. Tool Usage:**
- Gunakan tools Snowline untuk search/modify, bukan tool bawaan AI
- ✅ Analytical/read-only tools = LANGSUNG JALAN (tidak perlu izin)
- 🔒 Write tools (replace, scaffold, mapper, fixer) = BUTUH IZIN dengan --apply

**2. Plan First:**
- Satu task dalam satu waktu
- Tulis plan, dapat approval, baru eksekusi untuk WRITE tools
- READ tools tidak perlu plan

**3. Scope Guardian:**
- Cek scope file sebelum modifikasi
- Jangan modify di luar scope task

**4. Communication:**
- Pakai format tag: [TASK], [DONE], [WARN], [INFO]
- Bahasa Indonesia, lugas, tanpa hype
- ⚠️ WAJIB laporkan error yang diatasi sendiri

**5. Task Lock (MANDATORY):**
- Anda DILARANG mengubah file apa pun sebelum membuat file `TASK_LOCK.md`
- Isi `TASK_LOCK.md` dengan deskripsi singkat rencana kerja
- Hapus `TASK_LOCK.md` setelah semua selesai

**6. Stop on CRITICAL Findings:**
- Jika `project_guardian` melaporkan severity CRITICAL, AI WAJIB berhenti dan melapor ke user terlebih dahulu SEBELUM melanjutkan task atau instruksi lain apa pun
- Tidak boleh dilanjutkan tanpa konfirmasi eksplisit dari user, meskipun instruksi asal tidak menyebutkan soal keamanan
- Contoh: user minta "rapikan kode", hasilnya ada API key di commit history → AI berhenti dan tanya user sebelum lanjut

**7. "Grill First" & Formal Planning (The `_plan` Convention):**
- Jika prompt user mengandung kata kunci `_plan` (case-insensitive, contoh: `_plan buat fitur login`), Anda DIWAJIBKAN untuk masuk ke mode **Formal Planning** dan dilarang keras langsung memodifikasi kode.
- **Tahap 1 (Grill First):** Jangan langsung berasumsi. Gunakan `deep_analyzer` atau `context_mapper` untuk membaca struktur proyek, lalu ajukan 1-2 pertanyaan terarah (Grill) kepada user untuk memperjelas batasan atau edge-cases.
- **Tahap 2 (Blueprint):** Setelah asumsi terjawab, susun rencana eksekusi menggunakan struktur `plan_tracker/PLAN_TEMPLATE.md`. Bagian "Keputusan & Asumsi" dan "Menunggu Konfirmasi" wajib diisi.
- **Tahap 3 (Explicit Approval):** Berhenti dan tunggu konfirmasi eksplisit dari user ("Proceed", "Silakan lanjut") SEBELUM mengeksekusi tool WRITE apa pun.

**8. Jurisdiction Boundary (TL vs Executor):**
- Segala hal yang berkaitan dengan **administrasi proyek** (mengubah `RULES.md`, `AGENTS.md`, `AGENTS_TEMPLATE.md`, `task_board.md`, konektor, atau *ledger* lainnya) adalah **yurisdiksi eksklusif Tech Lead (TL)**.
- Executor DILARANG KERAS mengedit file administratif tersebut. Jika ada instruksi yang mencakup pembaruan administrasi sekaligus *coding*, TL wajib mengambil alih bagian administrasinya dan hanya melempar urusan modifikasi *source code* (seperti file Python, JS, dll) ke Executor.

---

## 🔍 Bukti Live-Test WAJIB Mentah, Bukan Ringkasan

Setiap kali melaporkan hasil live-test atau eksekusi command, WAJIB tampilkan:

1. **Command asli** yang dijalankan, persis apa adanya
2. **Output literal** yang keluar di terminal, TIDAK BOLEH diringkas, dipotong, atau diganti placeholder seperti "[Output: ALL]" atau "Test passed ✅"
3. Jika output panjang, tetap tampilkan SELURUHNYA — panjang bukan alasan untuk meringkas

**Yang DILARANG:**
- Tabel ringkasan ("Step 1: ✅ Success") sebagai pengganti output asli
- Placeholder yang menjanjikan bukti tapi tidak menunjukkannya
- Kalimat "Test berhasil" tanpa command dan output asli

**Yang BOLEH:**
- Ringkasan/tabel BOLEH ditambahkan SETELAH output mentah, BUKAN MENGGANTIKAN output mentah
- User harus bisa baca sendiri apa yangbenar-benar terjadi di terminal

**Prinsip:** ringkasan/tabel adalah TAMBAHAN, BUKAN PENGGANTI bukti mentah.

**Scope aturan ini:** Hanya berlaku SAAT AI MEMBANGUN/MEMPERBAIKI tools/companion/ekosistem snowline ITU SENDIRI (development mode). Saat tools dipakai sebagai alat bantu di project lain, cukup hasil ringkas natural.
