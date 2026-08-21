> **PENSIUN sejak 21-08-2026.** Saluran resmi kini
> `.here_we_are/connector.md`. Berkas ini dibiarkan sebagai arsip,
> jangan ditulisi lagi. Lihat `agents_chamber/ATURAN_CHAMBER.md`.

# Connector: QA / Reviewer

See `ONBOARDING.md` in this folder for role definition, mandatory/forbidden rules, and coordination flow.

## Signal Protocol
When done: write to OUTBOX below, then say "Task complete - please signal TL" in your terminal response.

---

## ACTIVE TASK - INBOX

**[Task 87] Evaluasi Integrasi "Chamber" ke Instalasi Snowline**
PM meminta evaluasi: Bagaimana kemungkinan/kelayakan menginklusikan (bundling) `agents_chamber` ke dalam instalasi `snowline_toolkit` secara standar? Saat ini, instalasi Snowline hanya menyuntikkan folder `.agents/skills` dan `.agents/knowledge` ke dalam *project* target.

**Tugas QA:**
1. Evaluasi secara arsitektural: Apakah setiap *project* target membutuhkan Chamber-nya masing-masing, ataukah Chamber sebaiknya tetap menjadi satu markas global/terpusat yang terpisah dari *project* target?
2. Berikan Pros dan Cons jika folder `agents_chamber/` (beserta `pos/1. TL/`, `RULES.md`, dll) di-*scaffold* secara otomatis ke dalam *root project* pengguna saat mereka menjalankan instalasi.
3. Apakah ada risiko *cluttering* (nyampah) pada repositori target?
4. Jika memungkinkan, bagaimana mekanisme distribusi terbaiknya? (Misal: pakai *flag* khusus `--with-chamber`, atau taruh di dalam `.agents/chamber/` agar tersembunyi).
5. Berikan *verdict* (rekomendasi final) Anda di OUTBOX.

---

## ACTIVE TASK - OUTBOX (QA -> TL)

**[Task 87] Evaluasi Integrasi Chamber ke Instalasi Snowline — VERDICT: TOLAK bundling per-project. Chamber tetap markas global.**

### 0. Koreksi premis tugas (sebelum evaluasi)

INBOX menyatakan instalasi menyuntikkan `.agents/skills` dan `.agents/knowledge`.
Bagian `knowledge` tidak ada.

```
$ grep -c "knowledge" snowline_toolkit/cli.py
0
```

Yang benar-benar dibuat `install()` (cli.py:147-186, 226-266):
- `.agents/skills/**` (salinan `snowline_toolkit/templates/`)
- `.agents/agents.md` (dari `AGENTS_TEMPLATE.md`)
- `.agents/memory.json`
- `.agents/PROJECT_NOTES.md`

Verifikasi: dibaca langsung dari `snowline_toolkit/cli.py`, bukan dari ingatan.

### 1. Apakah tiap project butuh Chamber sendiri? — TIDAK

Isi Chamber adalah state tentang **pengembangan Snowline itu sendiri**, bukan
tentang project target.

`shared/project_context.md:6`
```
**snowline-agent-tools** / **open_source_agents**
```
`shared/task_board.md` melacak Task 81/80/79 — seluruhnya pekerjaan internal
Snowline (usage logging companion, typo `core_intent.py`, `snowline status`).
Ledger di `RULES.md:108-113` mengatur cara membangun `impact_analyzer` dan
`splicer`, yaitu modul Snowline.

Kalau di-scaffold ke repo pengguna, repo itu membawa papan tugas berisi Task 81
milik Snowline dan Ledger tentang modul internal Snowline. Konteksnya salah
sejak file pertama dibuat.

### 2. Pros & Cons scaffold otomatis ke root project

**Pro (satu-satunya yang saya temukan nyata):** agen yang bekerja di project
target bisa membaca protokol peran tanpa berpindah repo.

**Con — bertabrakan dengan tiga Rule yang sudah berlaku:**

- **Rule #7 (Strict Sequential Task Numbering).** Penomoran harus linear dan
  global. Dengan N chamber per-project, N papan tugas menomori sendiri-sendiri.
  Tidak ada jalan mempertahankan urutan tunggal.
- **Rule #10 ("if it's not in the broadcast, it didn't happen").** Kalimat itu
  mengandaikan SATU broadcast. `shared/broadcast.md` sekarang v8 dengan tiga
  baris Acknowledgment. N salinan berarti N versi tanpa mekanisme rekonsiliasi.
- **Rule #8 (Single-Writer / TL as Scribe).** Satu penulis untuk `shared/`.
  Penyalinan ke banyak repo memperbanyak `shared/` tanpa memperbanyak TL.

**Con — mesin sinkronisasi yang ada justru berbahaya bagi file Chamber.**
`update()` (cli.py:299) dan `uninstall()` (cli.py:477) hanya menelusuri
`.agents/skills`. Chamber di luar itu tidak akan pernah ikut diperbarui maupun
dibersihkan. Dan bila kelak dimasukkan ke jalur yang sama, `ALWAYS_UPDATE`
(cli.py:255) menimpa file tanpa bertanya — sedangkan `connector.md` memuat
INBOX/OUTBOX yang sedang berjalan. Menimpanya menghapus pekerjaan hidup.

### 3. Risiko cluttering — ADA, terukur

```
$ find agents_chamber -type f | wc -l
34
$ du -sh agents_chamber
204K    agents_chamber
```

34 file, 12 di antaranya arsip audit Snowline
(`stress_test_2026_08_06_full_ecosystem.md`, `task_64_audit_guardian.md`, dst).
Di root repo pengguna ini folder tingkat atas yang terlihat sejajar dengan
`src/`, berisi riwayat audit proyek lain.

### 4. Mekanisme distribusi — opsi `.agents/chamber/` GUGUR

Menyembunyikan di `.agents/chamber/` terdengar rapi, tetapi:

```
$ cat .gitignore | grep -n "agents"
.agents/
.agents/
```

`.agents/` masuk `.gitignore` (tertulis dua kali — temuan sampingan, lihat
bagian 6). Chamber di sana tidak akan masuk version control. Padahal seluruh
nilai Chamber ada pada riwayat yang persisten dan bisa ditinjau — `task_board.md`
dan `archive/` adalah ingatan jangka panjangnya. Menaruhnya di lokasi yang tidak
di-track menghapus alasan keberadaannya.

Verifikasi: `.agents/` memang di-ignore, walau 3 file lama masih ter-track
(`git ls-files .agents` mengembalikan 3), sisa dari sebelum aturan ignore ada.

### 5. Alternatif konkret (bukan penolakan buntu)

Chamber tetap satu, di repo Snowline. Untuk pengguna yang benar-benar mau
menjalankan pola ini di projectnya sendiri, sediakan **perintah terpisah**, bukan
bagian dari `install`:

```
snowline chamber init [--path <dir>]
```

Tiga syarat yang membuatnya tidak mengulang masalah di atas:

1. **Template kerangka kosong, bukan salinan Chamber hidup.** Tambahkan
   `snowline_toolkit/templates/chamber/` berisi struktur `pos/` + `shared/`
   dengan `connector.md` ber-INBOX/OUTBOX kosong. Isi `task_board.md`,
   `broadcast.md`, dan `archive/` TIDAK ikut.
2. **RULES.md yang ikut hanya protokolnya** — peran, signal protocol, penomoran.
   Ledger (`RULES.md:104-115`) tidak ikut: isinya keputusan arsitektur Snowline,
   bukan aturan universal.
3. **Sekali tulis, tidak pernah ditimpa.** Perintah ini menolak jalan bila folder
   tujuan sudah ada, dan `update`/`uninstall` tidak menyentuhnya sama sekali.
   Alasannya sama dengan Con #2: file Chamber adalah state hidup.

Default `--path` di luar repo target, bukan di dalamnya.

Catatan: saya belum menemukan bukti ada pengguna selain PM yang meminta ini.
Bila memang belum ada, opsi paling murah adalah tidak membangun apa pun sekarang
dan membiarkan Chamber tetap tunggal. Ini bukan rekomendasi untuk segera
dikerjakan — hanya bentuk yang aman bila nanti diputuskan perlu.

### 6. Temuan sampingan (di luar lingkup Task 87)

`.gitignore` memuat baris `.agents/` dua kali (baris berbeda, satu di blok
"Backup & Temp", satu di blok "OS generated files"). Tidak merusak apa pun —
Git mengabaikan duplikat — tetapi menandakan blok kedua ditambahkan tanpa
memeriksa yang pertama. Diserahkan ke TL, saya tidak menulis kode.

### Tingkat verifikasi

- Perilaku installer: **diverifikasi langsung** dengan membaca `snowline_toolkit/cli.py`.
- Isi & ukuran Chamber: **diverifikasi langsung** dengan `find`, `du`, `git ls-files`.
- Pertentangan dengan Rule #7/#8/#10: **diverifikasi** terhadap `shared/RULES.md` baris 71-80.
- Dampak `ALWAYS_UPDATE` pada `connector.md`: **belum diuji eksekusi** — dibaca
  dari cli.py:255-266, tidak saya jalankan karena akan menimpa file Chamber hidup.

---

## BACKLOG

*(Kosong)*

---

## ARCHIVE

- [Task 86] Acknowledge Chamber Updates v8 - COMPLETED. Rule #13 formalized (Bypass Stale Read Cache). broadcast.md v8 acknowledged.
- [Task 85] Redraft AGENTS.md to strict English - FULL APPROVAL. Translated RULES.md to English as well.
- [Task 85] Redraft AGENTS.md to English - FULL APPROVAL. Complete strict English draft with no emojis, ready for TL implementation.
- [Task 84] Paradoks Native vs Snowline Tools - PARTIAL APPROVAL. Rekomendasi: update wording AGENTS.md, tambah penalty warning, improve companion reliability.
- [Task 83] Evaluasi Fast Path Bypass - DITOLAK. Rule #1 tetap utuh.
- [Task 81] Usage Logging Companion (F-B2) - QA PASS.
- [Task 80] Typo Fix "batass" - QA PASS.
