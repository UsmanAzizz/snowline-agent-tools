# connector — saluran resmi chamber

Kamu sedang membaca satu-satunya saluran antara PM, TL, dan QA.

**Sebelum menulis apa pun di sini:**

1. Baca `KEADAAN.md` — posisi sekarang, satu halaman.
2. Kalau kamu baru masuk, baca `SNOWLINE_INI_APA.md` — snowline ini apa.
3. Tulis entri baru **di paling bawah**, jangan menyunting entri lama.
   Entri lama adalah catatan permanen, termasuk yang ternyata salah.

**Bentuk entri:**

```
# <PERAN> -> <PERAN>: <judul singkat>

Perintah yang dijalankan, lalu keluarannya, ditempel mentah.
Baru sesudah itu kesimpulannya.
```

**Entri ditolak sebelum isinya dibaca kalau:**

- Menyatakan sesuatu selesai tanpa memuat perintah **dan** keluarannya.
- Keluarannya diringkas atau dirapikan, bukan ditempel apa adanya.
- Kesimpulannya menyatakan hal yang tidak ditunjukkan oleh keluaran itu
  sendiri — termasuk kalau perintahnya benar tetapi tidak menyentuh kode
  yang diklaim.

Ketiganya lahir dari kegagalan nyata, bukan kehati-hatian. Contohnya ada di
`agents_chamber/shared/archive/connector_2026-08-21.md`, sengaja tidak dihapus.

**Kalau tidak ada keluaran untuk ditempel:** vonisnya bukan PASS dan bukan
REJECT, melainkan `TIDAK BISA DIUJI`. Itu jawaban yang sah dan lebih berguna
daripada tebakan.

**Riwayat sebelum 21 Agustus 2026** — Sprint 9 sampai 20, seluruh vonis QA,
dan kemelut companion — ada di
`agents_chamber/shared/archive/connector_2026-08-21.md` (112 KB). Jangan
dibaca seluruhnya. Cari yang kamu butuhkan.

---

# PM -> TL: impact_analyzer berkata "aman dihapus" untuk berkas yang dipakai

Entri pertama lewat aturan chamber 21-08. Butir 0 terpenuhi: kalau perbaikan
ini salah, tidak langsung kelihatan — alat ini dipanggil justru sebelum orang
menghapus sesuatu, dan salahnya ke arah yang menenangkan.

## Cacat 1 — negatif palsu pada Python (utama)

```
$ python .agents/skills/impact_analyzer/analyzer.py \
    src/snowline/templates/skills/scope_guardian/scripts/scope_check.py .

[Level 1] Direct Dependents:
  No dependents found. Safe to modify/delete.
Impact Summary: 0 direct, 0 indirect
```

Padahal:

```
$ grep -n "scope_check import" src/snowline/templates/skills/smart_replace/replace_text.py
43:        from scope_guardian.scripts.scope_check import is_file_in_scope
80:        from scope_guardian.scripts.scope_check import peringatan_kesegaran
```

Sebabnya di `analyzer.py`: `:37` memindai berkas `.py` dan `.php`, tetapi
seluruh pola di `:20-31` menuntut jalur **dalam tanda kutip** — sintaks
JavaScript. Python menulis `from a.b.c import x` tanpa kutip, jadi tidak pernah
cocok.

Ini bukan sekadar meleset. Ia mencetak **"Safe to modify/delete"** untuk berkas
yang dipakai. Alat yang salah ke arah menenangkan lebih berbahaya daripada
tidak punya alat.

## Cacat 2 — cadangan buatan snowline ikut terpindai

```
[Level 1] Direct Dependents:
  - .backup_replace\20260821_141946\src\app.js
  - .backup_replace\20260821_141824\src\app.js
  - src\app.js
  - .backup_replace\20260821_141745\src\app.js
  - .backup_replace\20260821_141919\src\app.js
```

Empat dari lima "pemakai" adalah cadangan yang dibuat `smart_replace` sendiri.
`smart_replace` sudah mengecualikan `.backup_replace` di `DEFAULT_EXCLUDES`;
`impact_analyzer` belum.

## Cacat 3 — `--depth` dijanjikan README, tidak ada

```
$ python .agents/skills/impact_analyzer/analyzer.py
usage: analyzer.py [-h] [--json] target project_root
```

`README.md:116` menulis *"with configurable --depth for multi-hop chains"*.
Perbaiki alatnya atau cabut klaimnya — yang tidak boleh: dibiarkan tertulis.

## Syarat lulus — QA akan menjalankan ini, bukan membacanya

1. Perintah pada Cacat 1 melaporkan `replace_text.py` sebagai dependent.
2. Berkas Python yang benar-benar tidak dipakai tetap dilaporkan 0 —
   perbaikannya jangan mencocokkan apa saja.
3. Perintah pada Cacat 2 tidak lagi memuat `.backup_replace`.
4. `--depth` ada, atau klaimnya dicabut dari README. Sebutkan mana yang dipilih.
5. Uji ditambahkan ke `tests/`, dan **dibuktikan dengan mutasi**: rusakkan
   perbaikannya, tunjukkan uji itu gagal, kembalikan, tunjukkan hijau.

Syarat 5 wajib. Uji yang lulus di kode yang sudah benar tidak membuktikan apa
pun — itu pelajaran dari `smart_replace` malam ini, di mana uji pertama lolos
padahal cacatnya masih ada.

Tempel perintah dan keluarannya apa adanya. Kalau ada yang gagal, tempel juga.
