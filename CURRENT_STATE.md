# CURRENT STATE — Phase 4 (In Progress)

**Status:** Basic mechanism implemented. Grilling logic manual (agent writes questions), not auto-generated.

**Implemented:**
- `companion.py` v5.0 with task_lock functions
- `should_grill()` detection
- `start_task_lock()`, `add_grilling_qa()`, `load_task_lock()`, `update_task_lock()`, `get_task_status()`, `end_task_lock()`

---

## should_grill() Logic (Implemented)

```
IF entity spesifik terdeteksi AND specificity = high
   → should_grill = False (Micro Task, langsung eksekusi)

IF confidence = MEDIUM/LOW/NONE
   → should_grill = True (perlu clarify)

IF instruction >15 words AND no entity
   → should_grill = True (ambiguous)
```

**Catatan Penting:**
- "entity spesifik" = camelCase, PascalCase, snake_case, quoted string, $vars, React hooks
- Logic ini terlepas dari confidence level — ada entity spesifik = Micro Task
- Confidence mempengaruhi action (EXECUTE/KONFIRMASI/CLARIFY), bukan grilling decision

---

## should_grill() Live Test Results

```
"cari fungsi handleSubmit"      → needs_grilling: False (entity detected)
"tolong optimasi performa..."  → needs_grilling: True  (confidence MEDIUM)
"ganti handleSubmit jadi onSubmit" → needs_grilling: False (2 entities + HIGH)
```

---

## Phase 4 Scope (Locked)

**Implemented (DONE):**
- task_lock.json basic read/write
- should_grill() detection

**NOT Implemented (Future):**
- Auto-generate grilling questions (agent writes them manually)
- plan_summary generation
- grilling_log persistence across sessions

---

## Filosofi

Bukan meniru pipeline dokumentasi formal (technical-spec, api-spec ala referensi eksternal) yang mengasumsikan user paham baca/tulis spec teknis. Companion Reasoning Layer ini dirancang sebagai jembatan bahasa abstrak → eksekusi konkret, untuk user yang paham konsep (state, layer, session) tapi bukan expert syntax/implementasi.

**Target level programmer: 3/10** — paham state, layer, session secara konsep, tidak paham syntax/implementasi detail spesifik framework.

## Yang Sudah Ada (Fondasi, Jangan Dibangun Ulang)

- `task_state.json` — Plan-First Protocol (pseudocode_pending → approved → completed)
- `scope_lock.json` — Scope Guardian (allowed_files)
- `companion.py` — analyze_intent() (keywords, entities, confidence)

## Yang Baru: `task_lock.json`

Beda dari `scope_lock.json` (mengunci FILE) dan `task_state.json` (mengunci STATUS approval) — `task_lock.json` mengunci **konteks ide abstrak** sepanjang task, supaya companion tidak kehilangan pemahaman di tengah proses multi-langkah.

```json
{
  "task_id": "unique-id",
  "user_intent_raw": "kalimat asli user, verbatim",
  "clarified_understanding": "pemahaman companion setelah grilling, bahasa natural",
  "level_target": 3,
  "grilling_log": [
    {"question": "...", "answer": "..."}
  ],
  "plan_summary": "ringkasan rencana dalam bahasa natural, bukan pseudocode",
  "status": "clarifying | planning | approved | executing | done"
}
```

## Mekanisme Grilling (Level 3)

Ketika instruksi user ambiguous/kompleks (bukan Micro Task), companion:

1. Boleh pakai istilah: state, layer, session, komponen, endpoint, database, cache — konsep, bukan syntax
2. Tidak boleh asumsi paham: nama fungsi spesifik framework, syntax detail, struktur file internal library
3. Pertanyaan grilling harus dalam bentuk pilihan/skenario, bukan pertanyaan terbuka teknis

**Contoh benar (level 3):** "Fitur ini butuh nyimpen status di server (database) atau cukup sementara di browser (session)?"

**Contoh salah (terlalu teknis):** "Apakah ini perlu useEffect dengan dependency array kosong atau useState terpisah?"

## Definisi Selesai (Finish Line — Jangan Open-Ended)

Companion dianggap cukup untuk level 3 kalau, dengan SATU skenario uji nyata (contoh: "saya mau tambah fitur notifikasi WA kalau surat selesai"):

1. Companion mendeteksi ini bukan Micro Task → mulai grilling
2. Minimal 2-3 pertanyaan grilling muncul, dalam bahasa level 3 (dibuktikan lewat live-test, dibaca manual apakah bahasanya sesuai)
3. Setelah dijawab, companion tulis `plan_summary` dalam bahasa natural (bukan kode/pseudocode) — user harus bisa approve tanpa baca kode
4. `task_lock.json` menyimpan history grilling — dicoba interupsi di tengah (simulasi END/CONTINUE), buktikan konteks tidak hilang

**Bukan syarat selesai:** companion "selalu tepat menebak". Yang wajib: proses grilling konsisten dan bahasanya sesuai level, bukan hasil akhir 100% sempurna.

## Yang TIDAK Dikerjakan Dulu

- Multi-level support (level 1, level 8+) — setelah level 3 puas
- Pipeline dokumentasi formal ala referensi eksternal (technical-spec.md, dst) — beda filosofi, bukan prioritas sekarang
- Auto-deteksi level user secara otomatis — level di-hardcode 3 untuk sekarang

## Catatan Eksekusi

Task ini besar — mulai di sesi baru dengan fokus penuh, bukan disambung dari sesi yang sudah panjang. Ambil satu skenario nyata dulu, buktikan lewat live-test sesuai kriteria di atas, baru dianggap selesai. Jangan lanjut sampai reasoning "terasa sempurna" — itu tidak akan pernah selesai secara alami.

---

*Written: 2026-07-31*
