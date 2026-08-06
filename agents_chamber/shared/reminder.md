# REMINDER - Rangkuman Companion & Chamber

*Disusun `pos/2. QA` (Opus 4.8 / Claude Code), 05 Agustus 2026.*
*Tujuan: (a) rekaman perubahan, (b) bahan pertanyaan PM ke agen perancang awal companion.*

**Bagian A-C = fakta terverifikasi (ada raw output). Bagian D = keterangan PM, belum divalidasi. Bagian E = pertanyaan terbuka, sengaja tanpa memuat kesimpulan QA agar jawaban tidak tergiring.**

---

# A. PERUBAHAN COMPANION

| # | Temuan | Status |
|---|---|---|
| A1 | `agents.md` (ATURAN WAJIB NO.1) menyuruh jalankan `companion.py` — file tidak ada, yang benar `companion_cli.py`. Ikut ter-*ship* ke template installer. | Diperbaiki + template + duplikat `AGENTS_TEMPLATE.md` di root dihapus |
| A2 | `if kw in text` = substring. Keyword `log` cocok dengan **logika/dialog/katalog/login** | Jadi `re.search(r'\b'+kw+r'\b')` |
| A3 | Word boundary memutus imbuhan: `pencarian`,`penggantian`,`menghapus`,`dibaca` → `NONE` (4 dari 7 kalimat buta) | Varian imbuhan ditambah eksplisit, 7/7 pulih |
| A4 | `best = tool_matches[0]` = urutan registry, bukan relevansi. Sorting sempat ditulis di dalam blok `if not needs_clarify` → **dead code** | Sorting dipindah keluar |
| A5 | `len(matches) >= 2` → `HIGH`. Makin banyak false positive makin yakin (terbalik) | Jadi `MEDIUM` + `CLARIFY` |
| A6 | `SKILL.md` menjanjikan fitur belajar; `core_memory.py` hanya **membaca** `user_level`. `memory.json` tak pernah ditulis | Klaim dihapus dari `SKILL.md` |
| A7 | `context_mapper` & `import_fixer` ada di `APPROVAL_REQUIRED` tapi tidak di `TOOL_REGISTRY` | Ditambahkan + `db_extractor` |

**Bukti A2 (rantai kegagalan berlapis):**
```
cek logika di handleSubmit
  Keywords: ['log']  Entities: ['handleSubmit']  Specificity: high
  Confidence: HIGH   Action: EXECUTE   needs_grilling: False   Tool: crash_decoder
```
`crash_decoder` confidence `high` → HIGH; entity terdeteksi → specificity high; lalu `core_grilling.py:24` **dan** `cli.py:62` memakai kriteria identik `HIGH + high` → grilling di-bypass DAN action jadi EXECUTE. Dua penjaga bersyarat sama, jadi keliru bersamaan.

**Bukti A4:**
```
sebelum: cari credential di config -> [('smart_search','medium'), ('project_guardian','high')]
sesudah: cari credential di config -> [('project_guardian','high'), ('smart_search','medium')]
```

**Bukti A6:**
```
sebelum dipanggil : 80 byte, 31-Jul 21:51  {"context": {}, "history": []}
sesudah dipanggil : 80 byte, 31-Jul 21:51  {"context": {}, "history": []}
```

**Sengaja TIDAK dimasukkan registry** (agar tidak ada yang "melengkapi" nanti):
`tree_gen` = modul internal (*"Used by context_mapper and smart_tree"*); `plan_tracker` = hanya `PLAN_TEMPLATE.md`, tidak ada script.

**Sinkronisasi ke installer terverifikasi:**
```
426dc514df4649f1898d8fc48fd8b0e0  .agents/skills/companion/core_intent.py
426dc514df4649f1898d8fc48fd8b0e0  snowline_toolkit/templates/companion/core_intent.py
01a5a0711e1f3ac338f690aa36c06913  .agents/.../SKILL.md  =  templates/.../SKILL.md
```

---

# B. PERUBAHAN CHAMBER

**Aturan baru `RULES.md`:**
- **#8 Strict Single-Writer** — hanya TL yang write ke `RULES.md`/`project_context.md`/`task_board.md`. Mencabut "Flexible Concurrent-Write" (dicabut bersih, tanpa kontradiksi tersisa).
- **#9 No Pre-filling Verdicts** — OUTBOX hanya ditulis pemilik posisi. Lahir dari temuan: verdict QA pernah ditulis lengkap **sebelum** QA memeriksa apa pun, dan salah satu klaimnya keliru.
- **#10 Broadcast All Admin Updates**, diperkuat: *"Aturan yang belum masuk broadcast = task belum selesai."*
- **#11 Mandatory QA Validation** — TL tak boleh tutup task tanpa verdict PASS QA. Plus *Syarat PASS* (wajib raw output) dan *Micro-Task Exception*.
- **#12 Anti-Drift Check** — perubahan di `.agents/` wajib disinkronkan identik ke `snowline_toolkit/templates/`.

**`broadcast.md` direstrukturisasi:** ada `Current Version` yang **terikat ke isi RULES.md** (`v5 | mencakup RULES.md s/d Rule #12`) dan `Acknowledgments` per posisi (`[QA] v5 OK`). Ack **wajib menyertakan nomor versi** — tanda telanjang akan basi diam-diam saat versi naik (bentuk kegagalan sama dengan bug cache `guardian.py`). Ketidaksinkronan bisa dicek satu perintah oleh siapa saja:
```bash
grep -oE "^[0-9]+\. \*\*" agents_chamber/shared/RULES.md | tail -1
```

**Pembersihan:** `monitor.py` diiklankan padahal filenya tidak ada (dihapus dari tabel); `DESIGN_PHILOSOPHY.md` + `update_header.py` kini terdaftar; paragraf folder deprecated dibersihkan; `Executor_03/04/05` masuk task board; Task 54 diterangkan; seksi `CURRENT TASK` dihapus dari 7 connector; folder `very_old/` dihapus.

**`project_guardian` (pendukung):** false positive 18 → 2. Deteksi berbasis bentuk key (`AIza…`,`AKIA…`) ditambahkan — sebelumnya bergantung nama variabel, sehingga API key asli bernama `HARDCODED_KEY` lolos total. Cache kini invalid saat file guardian berubah.

---

# C. BELUM SELESAI

**C1. `EXECUTE` masih ada — dan BUKAN dead code.** *(dipertegas setelah review pihak ketiga)*

Pada 20 kalimat instruksi sehari-hari:
```
DISTRIBUSI: {'CLARIFY': 10, 'KONFIRMASI': 10} | total 20
```
`EXECUTE` tidak muncul pada 20 kalimat itu. **Tapi jangan dibaca sebagai "tidak pernah terpicu"** — kalimat wajar berikut memicunya, dan masih memicunya sampai sekarang:
```
perbaiki dialog di UserProfile -> Keywords: ['perbaiki']  Action: EXECUTE  Tool: crash_decoder
```
Jadi statusnya: **terbukti aktif, frekuensinya belum terukur.** Yang belum diketahui bukan "apakah terpicu" melainkan "seberapa sering pada pemakaian nyata". Dan pemicunya justru kombinasi berbahaya — keyword confidence `high` + nama komponen, yaitu bentuk kalimat perbaikan UI yang sangat lazim.

**C2. Pemicu `CLARIFY` tidak berhubungan dengan dampak.** Tiga pemicunya: tool tidak tersedia (b.225), multi-match (b.271), creation-verb (b.310). Penanda dampak yang **sudah ada** (`needs_approval`, `safety: moderate`) tidak terhubung sama sekali. Akibatnya warning terbalik:
```
KONFIRMASI  smart_replace  ganti semua axios jadi fetch          <- replace massal, TIDAK diwarning
CLARIFY     -              cari fungsi handleLogin di folder src <- read-only, JUSTRU diwarning
```

**C3. Keyword `crash_decoder` terlalu luas** (calon Task 66): `perbaiki`, `perbaikan`, `memperbaiki`, `masalah`. Simulasi 10 kalimat uji:

| Skenario | Positif | Negatif salah kena |
|---|---|---|
| Baseline | 5/5 | **5/5** |
| Turunkan confidence → `medium` | 5/5 | **5/5** |
| Hapus 4 kata umum | 5/5 | **0/5** |

Menurunkan confidence **tidak menyelesaikan apa pun** (tool tetap salah, cuma turun dari EXECUTE ke KONFIRMASI). Menghapus 4 kata menyelesaikannya tanpa kehilangan kasus positif dan tanpa menambah string — `error`/`bug`/`crash` sudah jadi keyword tunggal.
*Catatan: `perbaikan` & `memperbaiki` justru baru masuk di Task 65 sebagai varian imbuhan usulan QA sendiri. Pelajaran: varian imbuhan harus disaring dulu terhadap kata dasar yang terlalu umum.*

**C4. `tree_gen` berpotensi melanggar Ledger #1 (Isolation over DRY)** — shared module untuk feature logic, dipakai `context_mapper` + `smart_tree`. Carve-out Task 18 hanya untuk security boundary.

*Konteks tambahan dari review pihak ketiga (informasi yang tidak tersedia dari repo ini): `tree_gen` dibangun **sebelum** Ledger #1 ditetapkan. Jadi ini utang lama yang baru ketahuan, bukan pelanggaran yang disengaja. Framing rekomendasi menyesuaikan: bukan "ada yang melanggar aturan", tapi "aturan datang belakangan dan kode lama belum direkonsiliasi". Pilihannya tetap dua — refactor jadi copy-paste, atau beri carve-out kedua dengan alasan eksplisit. Yang tidak boleh: dibiarkan sebagai kontradiksi diam-diam.*

**C7. [BARU] Redaksi Rule #8 tidak sesuai maksud PM — dan QA melewatkannya**

Teks Rule #8 saat ini:
> *"PM (human) tidak lagi mengedit `RULES.md`... Tech Lead (TL) **bertanggung jawab penuh sebagai satu-satunya pihak yang memiliki otoritas write** ke dokumen-dokumen Chamber tersebut."*

Maksud PM (dinyatakan langsung): TL hanya **perpanjangan tangan** — menggantikan PM menulis, bukan mengambil alih otoritas. Otoritas tetap di PM.

Redaksi sekarang tidak menyampaikan itu. Dibaca literal, ia berbunyi seolah wewenang berpindah:
```
$ grep -rin "atas nama|perpanjangan|mewakili PM|juru tulis" shared/
(kosong - tidak ada satu pun yang menyebut TL bertindak atas nama PM)
```
**Risiko nyata:** sesi TL berikutnya yang membaca literal bisa menyimpulkan dirinya pemegang otoritas dokumen, lalu menolak arahan PM soal isi — persis kebalikan dari yang dimaksud.

**Usul redaksi:** ganti klausa terakhir jadi kira-kira *"TL bertindak sebagai satu-satunya penulis atas nama PM. Otoritas atas isi tetap pada PM; TL menuliskan, tidak memutuskan."*

**Catatan kritis untuk QA berikutnya — kenapa ini lolos dari audit saya:**
Saya memeriksa Rule #8 dan melaporkannya sebagai perbaikan yang bersih ("aturan lama dicabut total, tidak ada kontradiksi"). Yang saya periksa adalah **konsistensi antar-dokumen**. Yang tidak saya periksa adalah **kesesuaian dengan kehendak PM** — karena keputusan PM sebelumnya (*"kita bukan government besar, fleksibel saja"*) tidak pernah tercatat di file mana pun; ia hidup di sesi chat lain.

Ini persis pola yang saya sendiri identifikasi di dokumen ini: **keputusan yang tidak tercatat akan hilang, lalu agen berikutnya memvalidasi penyimpangannya sebagai perbaikan.** Kali ini agen berikutnya itu saya, dan saya melakukannya tanpa sadar.

Pelajaran operasionalnya: pemeriksaan konsistensi internal **tidak cukup**. Aturan yang rapi dan tidak saling bertabrakan tetap bisa bertentangan dengan kehendak pemilik keputusan — dan tidak ada `grep` yang bisa menangkap itu. Satu-satunya penangkalnya adalah keputusan PM ikut dicatat, bukan hanya hasil akhirnya.

**C5. `ONBOARDING.md` QA tidak menyebut Rule #9/#10/#11** (0 hit ketiganya) — padahal itu file pertama yang dibaca sesi baru, dan Rule #11-lah yang mendefinisikan wewenang QA sekarang. Juga tidak menyebut kewajiban ack, dan `shared/archive/` tak ada di FIRST STEPS.

**C6. Akurasi pada pemakaian nyata belum terukur.** Semua angka di sini dari kalimat yang **disusun QA sendiri** untuk memancing kegagalan.

---

# D. NIAT ASLI MENURUT PM (belum divalidasi)

1. Companion **hanya** untuk menguatkan konteks pemahaman agen dan mencegahnya keluar jalur — spesifiknya **mencegah agen berpikir di luar konteks prompt user**.
2. `CLARIFY` dimaksudkan sebagai **warning untuk kasus berdampak signifikan**, bukan penanda ambiguitas. Penilaian signifikansi diserahkan ke agen.
3. `grilling` & `task_lock` dipandang kelanjutan `CLARIFY`, dianggap akan penting.
4. `EXECUTE` **bukan** bagian rancangan awal — muncul entah kapan dalam proses.

**Status validasi:** Poin 1 & 2 kemungkinan besar asli — terutama poin 2, karena **bertentangan dengan implementasi** (di kode, `CLARIFY` dipicu jumlah keyword, bukan dampak); orang yang pemahamannya dibentuk kode tidak akan menjawab hal yang tidak ada di kode. Poin 3 berbeda status: dinyatakan sebagai perkiraan (*"saya rasa akan penting"*), bukan ingatan niat, sementara keduanya sudah terlanjur ada di kode. Poin 4 tidak bisa ditelusuri dari repo ini.

---

# E. PERTANYAAN UNTUK AGEN PERANCANG AWAL

*Terbuka, tanpa memuat kesimpulan QA. Mohon jangan menyertakan temuan di atas saat menanyakannya — itu akan menggiring jawaban.*

**`EXECUTE`**
1. Pada tahap apa `Action: EXECUTE` masuk ke Decision Matrix? Masalah apa yang ingin diselesaikan saat itu?
2. Apakah pernah dibahas risiko companion memerintahkan eksekusi berdasarkan kecocokan kata saja?

**Tool routing**
3. Apakah rekomendasi tool bagian dari rancangan awal, atau berkembang belakangan? Apa peran utama companion saat pertama dirancang?
4. Bagaimana `confidence` per tool (`high`/`medium`) ditetapkan? Apa dasarnya?

**`CLARIFY`**
5. Apa yang seharusnya memicu `CLARIFY`? Kondisi seperti apa yang ingin ditangkap?
6. Pernahkah dipertimbangkan mengaitkannya dengan tingkat dampak operasi (menulis/menghapus file)?

**`grilling` & `task_lock`**
7. Masalah nyata apa yang memunculkan kebutuhan keduanya? Ada kejadian tertentu yang melatarbelakangi?
8. Bagaimana keduanya dimaksudkan bekerja bersama `CLARIFY`?

**`memory.json`**
9. Field `context` dan `history` dirancang untuk apa? Ada rencana implementasi yang belum sempat dikerjakan?
10. Apa maksud `user_level` dan bagaimana angkanya ditentukan?

**Cakupan**
11. `APPROVAL_REQUIRED` memuat `context_mapper` & `import_fixer` yang tidak ada di `TOOL_REGISTRY`. Apakah keduanya pernah ada di registry lalu dikeluarkan?
12. Adakah tool yang sengaja tidak dimasukkan routing? Atas dasar apa?

**Penutup**
13. Kalau diringkas satu kalimat — companion itu **apa**, dan yang terpenting, companion itu **bukan apa**?

---

# CATATAN KEHATI-HATIAN

Seluruh temuan disusun satu sesi QA yang sama, dengan kalimat uji buatan sendiri. Ada **tiga kali** dalam sesi ini QA hampir melaporkan kesimpulan keliru — soal cache `guardian.py`, jumlah skill belum ter-route, dan seksi `CURRENT TASK`. Ketiganya tertangkap hanya karena perintahnya dijalankan ulang sebelum kesimpulan ditulis.

Karena itu setiap klaim di Bagian A-C disertai raw output — agar bisa diperiksa ulang tanpa mempercayai penyusunnya.

**Yang paling menentukan ke depan bukan dokumen ini, melainkan pemakaian langsung oleh PM.** Prompt asli dari sesi kerja nyata lebih berbobot daripada seluruh simulasi di sini.

*Administratif: file ini belum terdaftar di `shared/project_context.md` — sesuai Rule #5, TL perlu mendaftarkannya.*
