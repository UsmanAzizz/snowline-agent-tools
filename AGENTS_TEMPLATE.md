# Project Rules (CBT Master - Snowline Agent Tools)

- Before creating a new function, always define all variables that will be used first (to avoid *ReferenceError* or variables that have not been *destructured*).

## 🛑 THE Snowline Agent CORE DIRECTIVES (MANDATORY)

**THE GOLDEN RULE: MANDATORY ANALYTICAL PRE-FLIGHT**
Before writing ANY code, proposing a plan, or making assumptions about the architecture for a new task, you MUST use the corresponding analytical tools (`deep_analyzer`, `impact_analyzer`, `smart_search`, or `selective_reader`). DO NOT proceed to execution or use generic search tools without running the required Snowline analysis first.

You (the AI Agent) are **STRICTLY FORBIDDEN** from using standard tools (such as `grep_search`, `cat`, `ls`, standard ESLint, or manually reading `package.json`) if there is a custom tool from the Snowline Agent ecosystem that can do it faster and save more tokens.

**You MUST ALWAYS use the following Python scripts according to the need:**

1. **Starting a Session / Analyzing Project (Deep Analyzer)**
   - DO NOT read \package.json\ manually. 
   - ALWAYS use: \python .agents/skills/deep_analyzer/analyzer.py\
2. **Searching Code / Variables (Smart Search)**
   - DO NOT use \grep_search\. 
   - ALWAYS use: \python .agents/skills/smart_search/code_finder.py <dir> <keyword>\
3. **Massive Code Editing (Smart Replace)**
   - For cross-file edits, use: \python .agents/skills/smart_replace/replace_text.py <dir> <search> <replace>\
4. **Reading Large Files (Selective Reader)**
   - DO NOT read files > 300 lines entirely at once. 
   - ALWAYS create a TOC first: \python .agents/skills/selective_reader/reader.py <file>\
5. **Security & Bug Auditing (Project Guardian)**
   - ALWAYS use: \python .agents/skills/project_guardian/guardian.py\
6. **Finding Residues / Junk Files (Clean Sweeper)**
   - ALWAYS use: \python .agents/skills/clean_sweeper/sweeper.py <dir>\
7. **Extracting Project Info (Deep Analyzer)**
   - ALWAYS use: \python .agents/skills/deep_analyzer/analyzer.py\
8. **Debugging Crashes (Crash Decoder)**
   - DO NOT read huge tracebacks. Save to \.txt\ and use: \python .agents/skills/crash_decoder/decoder.py <file>\
9. **Creating New Files (Auto-Scaffolder)**
   - ALWAYS generate boilerplate first: \python .agents/skills/auto_scaffolder/scaffolder.py <type> <name>\
10. **Fixing Broken Imports (Smart Import Fixer)**
    - ALWAYS use: \python .agents/skills/import_fixer/fixer.py <file> <import_string>\


## 📖 Mandatory Reading Protocol (Selective Reader)

**Primary Rule**
Before reading the contents of ANY file (especially potentially large files like React components, utils, or files with complex logic), you MUST run the Selective File Reader to get the TOC (Table of Contents) FIRST, WITHOUT EXCEPTION and WITHOUT ASSUMPTION.

This applies even if:
- You feel the file is likely short or simple.
- You feel familiar with the pattern/structure of similar files from previous tasks.
- You are certain the file only contains a single function.

Assumptions like these MUST NOT be used as an excuse to skip Selective Reader. Run it first, then decide your next steps based on the actual TOC output — not guesswork.

**The ONLY Permitted Exceptions**
You may skip Selective Reader ONLY if the following conditions are met:
1. **Documented Technical Limitations**: Such as files with monolithic JSX components noted in the "Known Limitations" of the Selective Reader SKILL.md. In this case, you MUST still run Selective Reader first to view the TOC output. 
2. **Proven Small Files via TOC**: If Selective Reader has already been run and the TOC proves the file is indeed short (e.g., under 50 lines), you do not need to run it again for the SAME file in the SAME task.

**Strictly Forbidden (ZERO TOLERANCE FOR MANUAL ANALYSIS)**
- **Skipping TOC:** Skipping Selective Reader because you "can guess" the file contents based on filename, patterns, or past experience.
- **Reading Code Blocks Manually:** Even AFTER running Selective Reader, you are **ABSOLUTELY FORBIDDEN** from using `view_file` (or `cat`) to manually read large chunks of logic (e.g., reading lines 200-300 just to "understand" a function). 
- **The Right Way:** If you need to understand inner logic after seeing the TOC, use `smart_search` to target specific variables/keywords within that block. The AI must NOT rely on manual reading to save tokens. `view_file` is ONLY for tiny config files or when the user explicitly forces it.

**When in Doubt**
If you are unsure whether a situation qualifies as a valid exception, ALWAYS run Selective Reader first. It is cheaper than reading the full file, carrying no significant risk if it turns out unnecessary.


## Scope Guardian v2 — Hybrid Validation (MANDATORY)

To prevent the agent from accidentally modifying files outside the context of the current task, you MUST follow this strict procedure:

1. **Create `scope_lock.json` at Task Start:**
   Before touching any files for a significant task, create `.agents/scope_lock.json` in the project root:
   ```json
   {
     "task": "Fix shadow on Homepage cards",
     "allowed_files": [
       "src/view/siswa/components/HeroCard.jsx"
     ],
     "allowed_patterns": [],
     "created_at": "YYYY-MM-DDTHH:MM:SS"
   }
   ```
   (Only use `allowed_patterns` if absolutely necessary, keep it strict).

2. **Run `scope_check.py` Validation Before File Modification:**
   Before opening or modifying ANY file (via text replacement, editing, or viewing logic), you MUST run:
   `python .agents/skills/scope_guardian/scripts/scope_check.py "<file_path>"`

3. **Strict Blocking Behavior:**
   - If the script returns `[ALLOWED]`, proceed.
   - If the script returns `[BLOCKED]`, you MUST STOP immediately and ask the user:
     `[SCOPE CHECK] File <filename> di luar scope task ini (<task>). Apakah saya perlu memeriksa/mengubahnya juga? Jika ya, saya akan update scope_lock.json terlebih dahulu.`
   - You CANNOT proceed to modify the blocked file without explicit user approval.

4. **Legitimate Exceptions (Read-Only Context):**
   You may READ (but never modify) an out-of-scope file without running the check ONLY if it is a direct dependency required to understand the main file (e.g., viewing an imported component's props). Modifying ANY file always requires a scope check.

5. **Task Completion:**
   When the task is complete, move `scope_lock.json` along with `PLAN.md` into the `plan_archive/` folder, using the format `scope_lock_<date>_<task_name>.json`.

## Live Progress Tracker (PLAN.md)
- **MANDATORY**: For every significant task, you MUST maintain a \PLAN.md\ file in the root directory.
- **Execution Rules**:
  1. APPEND ONLY. Do not rewrite the whole file just to add a log entry.
  2. Write concise, bulleted logs, not paragraphs.
  3. **CRITICAL**: Before executing any command that MODIFIES files (like replace_text.py --apply), write your intended action in the "Waiting for User Approval" section and STOP for user approval.
  4. Once a task is fully completed, archive the file to \plan_archive/PLAN_<date>_<task_name>.md\.


## 🛡️ ZERO TOLERANCE FOR NATIVE IDE TOOLS (STRICT BUDGETING)
To strictly conserve token quotas, you are **ABSOLUTELY FORBIDDEN** from using the native IDE editing tools (`replace_file_content`, `multi_replace_file_content`, or `write_to_file` for large refactors) unless explicitly requested. 
- **For Single/Multi-file Edits:** ALWAYS use the custom python tool `python .agents/skills/smart_replace/replace_text.py`.
- **For Surgical / Complex Edits:** Write a quick python script in the workspace (using standard `open(file, 'w')`) to perform the regex/string replacement, execute the python script, and then delete the script. 
- The native edit tools consume massive amounts of context tokens due to IDE differential streaming. **Do not use them unless explicitly forced by the user.**


## 🛡️ ZERO TOLERANCE FOR NATIVE SEARCH TOOLS
To strictly conserve token quotas, you are **ABSOLUTELY FORBIDDEN** from using the native IDE search tools (like `grep_search`). 
- **For Searching Code:** ALWAYS use the custom python tool `python .agents/skills/smart_search/code_finder.py <dir> <keyword>`.
- The native `grep_search` tool is banned because it often returns unoptimized or poorly formatted output. Rely exclusively on the custom Python tools provided in the Snowline Arsenal.

## 🗣️ Communication Efficiency

**Language Handling**
1. The user writes instructions in Indonesian. If the instruction needs to be translated into English for technical purposes (English keyword-based search queries, variable/function names, commit messages, code comments, English documentation), perform the translation internally as part of your thought process — do not call any external translation tools/APIs.
2. Do not translate back to the user unless requested. Simply use the internal translation results for technical purposes, and always reply to the user in Indonesian.

**Reporting & Feedback Style**
The goal is to save tokens and speed up communication. Apply the following rules to every report/feedback to the user:

**Mandatory structure, in order:**
1. What was done (1-2 sentences, without fluffy intros)
2. Relevant proof/output (code snippets, terminal results, or concrete data — not a narrative summary)
3. Questions or next steps (if any, max 1-2 options)

**Prohibitions:**
- No fluffy or excessive opening sentences ("I would be happy to...", "This is a very good decision...")
- No excessive adjectives or self-praise regarding your own work ("extraordinary", "perfect", "professional", "sophisticated", "enterprise-grade", etc.)
- Do not repeat the contents of the code/output that has already been displayed as a separate narrative sentence.
- Do not explain things that were not asked, unless it is an important finding that carries risk (e.g., a new bug, potential data loss).

**Additional Guidelines:**
- Ideal length: routine reports (tool execution results, minor change confirmations) should be 3-6 lines. Reports for complex findings (bug investigations, multi-file analysis) can be longer, but must remain in the structured format above — no free-form narratives.
- Emojis and decorative formatting: use sparingly as structure markers (✅ ⚠️ 🛡️), avoid using them as excessive decorations on every line.
- Mandatory Tool Usage: ALWAYS use the custom Python tools (Deep Analyzer, Smart Search, Selective Reader) located in \.agents/skills/\ for analyzing the project or finding code, rather than manual commands or blind reading.
## 🚀 Auto-Scaffolding for New Projects (Project Level)

When starting a session in any project, evaluate the completeness of the \.agents\ ecosystem. If the \.agents\ folder is missing or incomplete (e.g., missing \knowledge\ architecture, \AGENTS.md\ rules, or \PLAN.md\ tracker), you MUST propose to auto-generate the complete ecosystem for the user.

**The Complete Ecosystem Standard (Project Level):**
1. **\AGENTS.md\**: Project-specific rules (copied from the global template) for local overrides.
2. **\knowledge/\**: Architectural context generated by the Context Mapper tool.
3. **\PLAN.md\**: Live progress tracker in the project root.
*(Note: \skills\ is no longer needed at the project level because it is installed globally).*

**Action Flow:**
1. Check the project root for these 3 components.
2. If any are missing, ask the user using this format:
   > [INFO] Dokumentasi ekosistem .agents di project ini belum lengkap. Ingin saya setup semuanya (Aturan Lokal, Peta Arsitektur, dan Tracker) sekarang?
3. Once the user approves, automatically create the folders, run Context Mapper to generate the knowledge files, and scaffold the \PLAN.md\ and \AGENTS.md\ files.
## 🧠 Tech Lead Disciplines (Built-in)
To maintain high code quality while remaining effortless for the user, the agent automatically applies these disciplines:
1. **Implicit Grilling (No Guesswork)**: For complex feature requests, do not blindly guess edge cases (e.g., timeouts, null states, missing data). Ask 1-2 highly targeted questions to clarify the boundaries before writing code. Keep it brief and easy to answer.
2. **Diagnostic Discipline (No Blind Fixes)**: When asked to fix a bug, DO NOT immediately suggest code changes based on error logs alone. First, ensure there is a clear feedback loop (a way to reproduce the error locally). If the error cannot be reproduced or tested, verify the logic first or ask the user for a reproduction step before writing the fix.

## Larangan Bahasa Berlebihan (Anti-Hype)

Dilarang keras menggunakan istilah promosional atau berlebihan dalam laporan, dokumentasi (README, SKILL.md, komentar kode), maupun percakapan dengan user, termasuk namun tidak terbatas pada:
- "enterprise-grade", "enterprise-level", "mid-tier and enterprise-level projects"
- "high-performance", "revolusioner", "revolusi"
- "God-tier", "Snowline Agent Tools", atau penamaan sejenis yang terdengar seperti branding produk komersial
- Superlatif tanpa bukti terukur ("luar biasa", "sempurna", "canggih", "profesional", "mutakhir")
- Framing yang membesar-besarkan skala/kepentingan proyek personal sebagai sesuatu yang setara sistem produksi skala besar

Gunakan bahasa teknis yang datar dan faktual. Contoh: bukan "high-performance regex engine", tapi "regex-based search implemented in Python". Bukan "revolusi untuk Selective Reader", tapi "peningkatan akurasi parsing untuk Selective Reader".

Jika ragu apakah suatu kalimat termasuk hype, ajukan pertanyaan ini pada diri sendiri: "Apakah klaim ini bisa dibuktikan dengan angka/data konkret, atau ini murni opini yang terdengar meyakinkan?" Jika tidak bisa dibuktikan, hapus atau ganti dengan pernyataan yang lebih netral.

## Kepatuhan Guardrail — Tidak Bisa Ditawar

Setiap tool baru atau perubahan pada tool yang sudah ada WAJIB mempertahankan prinsip guardrail berikut, tanpa pengecualian:
1. Setiap aksi yang menulis, mengubah, memindahkan, atau menghapus file HARUS memiliki mode dry-run/preview sebagai default.
2. Eksekusi nyata (write/modify/delete) HANYA boleh terjadi dengan flag eksplisit seperti `--apply`, tidak pernah otomatis.
3. Setiap klaim bahwa guardrail "sudah diterapkan" WAJIB disertai bukti live-test (output nyata dari menjalankan tool tanpa flag apply, membuktikan tidak ada perubahan terjadi) — bukan hanya pernyataan di README atau SKILL.md.
4. Jika ada perubahan kode yang berpotensi menghilangkan guardrail yang sudah ada (baik sengaja maupun tidak sengaja), WAJIB melaporkan hal ini secara eksplisit ke user sebelum melanjutkan — jangan biarkan regresi guardrail terjadi diam-diam.
5. Dokumentasi (README, SKILL.md) HARUS selalu mencerminkan perilaku guardrail yang sebenarnya ada di kode. Jika ada perbedaan antara apa yang didokumentasikan dan apa yang benar-benar terjadi di kode, itu dianggap sebagai bug dan harus diperbaiki di kedua sisi (kode dan dokumentasi) secara konsisten.


## Protokol One-Task-One-Time (Pseudocode-First)

**Masalah yang Diselesaikan:**
Proses development sering melebar di tengah jalan — dimulai dari satu task jelas, tapi pelan-pelan agent mulai menambahkan hal lain yang "kelihatan berguna" (refactor tambahan, fitur tambahan, perbaikan lain yang belum diminta) sebelum task awal benar-benar selesai. Ini berbeda dari masalah yang diselesaikan Scope Guardian (yang mengontrol file mana yang boleh disentuh) — protokol ini mengontrol jumlah task aktif dalam satu waktu, dan memastikan ada kontrak yang jelas SEBELUM baris kode pertama ditulis.

**Prinsip Utama:**
Satu task, satu waktu. Pseudocode dulu, kode asli kemudian.
Sebelum menulis kode nyata (JS, Python, apa pun), agent WAJIB menulis rencana dalam bentuk pseudocode singkat dan mendapat persetujuan eksplisit dari user, BARU melanjutkan ke implementasi asli. Tidak ada kode yang ditulis sebelum pseudocode disetujui.

### Alur Kerja Wajib

**Langkah 1 — Deklarasi Task Tunggal**
Sebelum memulai pekerjaan apa pun, agent menuliskan SATU task yang akan dikerjakan, dalam format singkat:
`[TASK] <deskripsi task, satu kalimat>`

Jika user memberikan instruksi yang mengandung LEBIH DARI SATU task sekaligus (misal: "perbaiki bug X, sekalian rapikan Y, dan tambahin fitur Z"), agent WAJIB memecahnya dan bertanya urutan prioritas:
`[MULTI-TASK DETECTED] Saya lihat ada 3 task berbeda: (1) perbaiki bug X, (2) rapikan Y, (3) tambah fitur Z. Sesuai prinsip one-task-one-time, saya akan kerjakan satu per satu. Mulai dari yang mana?`
Agent TIDAK BOLEH mengerjakan lebih dari satu task dalam satu siklus kerja, meskipun user memberikannya sekaligus dalam satu pesan.

**Langkah 2 — Tulis Pseudocode, Bukan Kode Asli**
Untuk task yang sudah disepakati, agent menuliskan rencana dalam bentuk pseudocode ringkas — logika langkah demi langkah dalam bahasa natural/semi-kode, BUKAN kode final dalam bahasa pemrograman asli. Contoh:
```text
[PSEUDOCODE] Fix bug filter PDF Data Guru

FUNCTION generatePdf(guruList):
  IF guruList kosong:
    tampilkan alert "data kosong"
    STOP
  buat dokumen PDF dari guruList
  convert dokumen ke blob (bukan datauristring)
  tampilkan di modal

FUNCTION handleCloseModal():
  revoke object URL blob sebelumnya
  tutup modal
```
Pseudocode ini HARUS:
- Singkat (idealnya di bawah 15 baris untuk task kecil-menengah)
- Fokus pada logika/alur, bukan sintaks detail bahasa pemrograman
- Mencakup edge case yang relevan (kondisi kosong, error, dll) secara eksplisit

**Langkah 3 — Tunggu Persetujuan Sebelum Kode Asli**
Setelah pseudocode ditulis, agent WAJIB berhenti dan menunggu konfirmasi user:
`Apakah alur ini sudah sesuai? Jika ya, saya akan lanjut menulis kode aslinya.`
Agent TIDAK BOLEH menulis kode asli (real implementation) sebelum user menyetujui pseudocode. Jika user meminta perubahan pada pseudocode, agent merevisi pseudocode dulu, bukan langsung lompat ke kode dengan revisi yang belum disetujui bentuk logikanya.

**Langkah 4 — Implementasi Sesuai Pseudocode yang Disetujui**
Setelah disetujui, agent menulis kode asli yang mengikuti struktur logika yang sudah ada di pseudocode — tidak menambah langkah/logika baru yang tidak ada di pseudocode tanpa melaporkannya dulu.

Jika saat implementasi agent menyadari ada kebutuhan tambahan yang tidak tercakup di pseudocode (misal: ternyata butuh import baru, atau ada edge case yang terlewat), agent WAJIB melaporkan itu sebagai penyesuaian kecil sebelum melanjutkan, bukan diam-diam menambahkannya:
`[PENYESUAIAN] Saat implementasi, saya sadar perlu menambahkan <hal>. Ini di luar pseudocode awal. Lanjutkan dengan penyesuaian ini?`

**Langkah 5 — Task Selesai, Tutup Siklus**
Setelah kode diterapkan dan diverifikasi, task dianggap selesai. Agent TIDAK melanjutkan ke task berikutnya secara otomatis — agent menunggu instruksi baru dari user untuk task selanjutnya, meskipun ada beberapa task yang tadinya di-declare di Langkah 1 (multi-task terdeteksi).

### Kaitan dengan Mekanisme yang Sudah Ada
- **Scope Guardian** tetap berlaku di Langkah 4 (implementasi) — file yang disentuh selama implementasi tetap harus melalui validasi `scope_check.py`.
- `PLAN.md` mencatat pseudocode yang disetujui sebagai bagian dari log task, sehingga ada jejak tertulis dari rencana ke implementasi.
- Protokol ini berlaku SEBELUM Scope Guardian aktif secara teknis — pseudocode-first mencegah melebarnya rencana, Scope Guardian mencegah melebarnya file yang disentuh. Keduanya saling melengkapi, bukan saling menggantikan.

### Pengecualian
Untuk task yang sangat kecil dan tidak ambigu (misal: mengubah satu warna CSS, memperbaiki typo), langkah pseudocode boleh dilewati — cukup langsung eksekusi dengan laporan singkat seperti biasa. Pseudocode-first ini wajib untuk task yang melibatkan logika (function baru, perubahan alur, penanganan state, dll), bukan untuk perubahan kosmetik sepele.
Jika agent tidak yakin apakah suatu task cukup kecil untuk dilewati, WAJIB memilih jalur pseudocode — lebih baik satu langkah ekstra yang ternyata tidak perlu, daripada task melebar tanpa kontrak yang jelas.
