# Task 65 - Perbaikan Logika Companion (REJECT -> Revisi -> PASS)

*Diarsipkan oleh: `pos/2. QA` (Opus 4.8 / Claude Code), 05 Agustus 2026*
*Sesuai SOP `shared/archive/README.md`. Status: DONE - verdict QA PASS setelah satu siklus REJECT.*

---

## LATAR BELAKANG - deep dive audit companion (pemicu Task 65)

QA membaca seluruh 1006 baris modul companion atas permintaan PM. Lima temuan yang melanggar visi companion sendiri:

- **A1 [KRITIS]** `core_intent.py` memakai `if kw in text` (substring, bukan kata utuh). Keyword `log` cocok dengan **logika**, **dialog**, **katalog**, **login**. Digabung `crash_decoder` confidence `high` + entity terdeteksi -> `HIGH + high` -> `core_grilling.py:24` dan `cli.py:62` **sama-sama** mem-bypass ke `Action: EXECUTE`. Companion aktif memerintahkan tool yang salah - kebalikan dari fungsinya sebagai pagar.
- **A2** Pemilihan tool memakai `tool_matches[0]` = urutan penulisan registry, bukan confidence. `cari credential` -> `smart_search` (medium), bukan `project_guardian` (high).
- **A3** `len(tool_matches) >= 2` -> HIGH. Makin banyak false positive, makin tinggi keyakinan. Logika terbalik.
- **A4** `SKILL.md` menjanjikan fitur belajar; `core_memory.py` hanya MEMBACA `user_level`. `memory.json` tidak pernah ditulis (80 byte, tidak berubah sejak 31-Jul).
- **A5** `context_mapper` & `import_fixer` ada di `APPROVAL_REQUIRED` tapi tidak di `TOOL_REGISTRY` - tidak pernah bisa di-route.

**Risiko yang SENGAJA diterima** (konsekuensi sah dari visi, jangan "diperbaiki"): companion tidak paham makna hanya kata; tidak punya kosakata verifikasi/QA (memang dirancang untuk agen tunggal); kadang CLARIFY berlebihan (arah kesalahan yang benar).

---

## EKSEKUSI & AUDIT

### Putaran 1 - VERDICT: REJECT

Executor menerapkan C1 (word boundary), C2 (sort confidence), C3 (multi-match -> CLARIFY), C4 (hapus klaim Memory), D (3 tool baru).

**Alasan REJECT - 2 masalah:**

**C2 ternyata dead code.** Sorting diletakkan di dalam `if tool_matches and not needs_clarify:` (baris 316), sementara C3 yang ditambahkan di task yang sama membuat `needs_clarify = True` setiap ada >=2 match. Jadi sorting dilewati justru saat dibutuhkan, dan jalan saat hanya ada 1 elemen. **C2 dan C3 saling meniadakan.** Bukti:
```
cari credential di config -> [('smart_search','medium'), ('project_guardian','high')]   <- tidak terurut
```

**C1 memperkenalkan regresi yang belum diuji.** Word boundary memutus kata berimbuhan bahasa Indonesia - 4 dari 7 kalimat wajar jadi buta total:
```
lakukan pencarian fungsi login -> Keywords: []  NONE
penggantian nama variabel      -> Keywords: []  NONE
menghapus file lama            -> Keywords: []  NONE
dibaca file config             -> Keywords: []  NONE
```
Catatan penilaian: arah trade-off-nya BENAR (false negative lebih aman daripada false positive), jadi ini bukan langkah mundur - hanya belum lengkap.

### Putaran 2 - VERDICT: PASS

**Fix 1 - sorting dipindah keluar blok `needs_clarify`:**
```
SEBELUM: cari credential di config -> [('smart_search','medium'), ('project_guardian','high')]
SESUDAH: cari credential di config -> [('project_guardian','high'), ('smart_search','medium')]
         lihat schema database     -> [('db_extractor','high'), ('selective_reader','medium')]
         fix import rusak          -> [('import_fixer','high'), ('smart_search','medium')]
```
Efek sampingnya menyelesaikan masalah D sekaligus - `db_extractor` & `import_fixer` yang sebelumnya tidak pernah tampil kini berada di urutan pertama `clarification_context`.

**Fix 2 - varian berimbuhan ditambahkan ke keyword (bukan membangun stemmer):**
```
menganalisa struktur project   -> ['struktur','menganalisa']  MEDIUM
lakukan pencarian fungsi login -> ['pencarian']               MEDIUM
penggantian nama variabel      -> ['penggantian']             HIGH
menghapus file lama            -> ['menghapus']               MEDIUM
dibaca file config             -> ['dibaca']                  MEDIUM
```
7 dari 7 kalimat regresi pulih. Tidak ada lagi yang `NONE`.

**Pemeriksaan regresi balik - bersih:**
```
cek logika di handleSubmit            -> Keywords: []          CLARIFY
rapikan katalog produk di ProductList -> Keywords: ['rapikan'] KONFIRMASI  clean_sweeper
cari important                        -> Keywords: ['cari']    KONFIRMASI  smart_search
ganti dan cari                        -> MEDIUM                CLARIFY      (C3 utuh)
```

**Sinkronisasi ke versi yang di-install user:**
```
426dc514df4649f1898d8fc48fd8b0e0  .agents/skills/companion/core_intent.py
426dc514df4649f1898d8fc48fd8b0e0  snowline_toolkit/templates/companion/core_intent.py
01a5a0711e1f3ac338f690aa36c06913  .agents/skills/companion/SKILL.md
01a5a0711e1f3ac338f690aa36c06913  snowline_toolkit/templates/companion/SKILL.md
```

---

## SISA TEMUAN - BELUM JADI TASK, jangan sampai hilang

1. **Keyword `perbaiki` terlalu luas untuk `crash_decoder`.**
   ```
   perbaiki dialog di UserProfile -> Keywords: ['perbaiki']  Action: EXECUTE  Tool: crash_decoder
   ```
   Bukan false positive substring (word boundary bekerja benar). Masalahnya desain: `perbaiki`/`perbaikan`/`memperbaiki` berlaku untuk segala perbaikan (UI, logika, teks), sementara `crash_decoder` hanya membaca file log - dan confidence-nya `high` sehingga langsung EXECUTE.
   **Usul:** sempitkan jadi frasa `perbaiki error` / `perbaiki bug` / `perbaiki crash`, atau turunkan confidence `crash_decoder` ke `medium`. Yang pertama lebih tepat sasaran.

2. **`tree_gen` melanggar Ledger butir 1 (Isolation over DRY).**
   ```
   context_mapper/context_mapper.py:6  from tree_gen.tree_gen import generate_simple_tree, get_tree_stats
   smart_tree/scripts/tree_viewer.py:12 from tree_gen.tree_gen import generate_tree, generate_simple_tree, parse_gitignore
   ```
   Shared module untuk **feature logic**, bukan security boundary - carve-out Task 18 tidak berlaku. Perlu keputusan TL: rekonsiliasi kode, atau tambahkan carve-out kedua ke Ledger.

3. **`plan_tracker` & `tree_gen` sengaja TIDAK dimasukkan ke `TOOL_REGISTRY`** - `plan_tracker` hanya berisi `PLAN_TEMPLATE.md` (tidak ada script), `tree_gen` adalah modul internal yang dipakai `context_mapper` & `smart_tree`. Dicatat supaya tidak ada yang "melengkapi" keduanya di kemudian hari dan justru menambah bloat.

4. **Companion belum diukur akurasinya pada pemakaian nyata.** Seluruh pengujian di task ini memakai sekitar 20 kalimat yang QA rancang khusus untuk memancing kegagalan. Angka akurasi pada instruksi sehari-hari belum pernah diukur.
