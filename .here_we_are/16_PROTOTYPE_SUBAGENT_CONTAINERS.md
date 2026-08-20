# 16_PROTOTYPE_SUBAGENT_CONTAINERS.md — Blueprint Memori Sub-Agen Berlapis

Disusun 20 Agustus 2026. Mencatat standar arsitektur Kontainer Sub-Agen dan Rotasi Log (Memory Sharding).

## 1. Arsitektur Folder Mandiri (Micro-Agents)
Setiap agen dalam Snowline V2 tidak lagi sekadar skrip Python yang menerima argumen berbeda. Mereka diperlakukan sebagai **Kontainer Terisolasi** dengan hierarki absolut:

```text
.agents/subagents/
├── investigator/
│   ├── system_prompt.md     (Otak: Aturan Investigasi murni)
│   ├── allowed_tools.json   (Senjata: Hanya fungsi baca)
│   └── memory/              (Sub-direktori memori jangka panjang)
│       ├── index.json       (Penunjuk file aktif)
│       ├── history_001.md   (Arsip)
│       └── history_002.md   (Aktif)
```

## 2. Memory Sharding & Log Rotation (Anti-Bloat)
Untuk mencegah ledakan jumlah token (*Context Limit Exceeded*), sistem menerapkan aturan rotasi yang ketat:
- **Batas Maksimal:** Satu file `history_xxx.md` tidak boleh melebihi 300 baris.
- **Rotasi Otomatis:** Jika baris ke-300 tercapai, sistem akan mengarsipkan file tersebut, menaikkan nomor indeks (misal ke `002`), dan memulai file baru.
- **Dampak:** Agen tidak akan pernah menelan memori raksasa. Ia hanya selalu menelan file aktif terakhir yang berukuran sangat ringan, menjaga latensi baca (*TTFT - Time To First Token*) tetap rendah.

## 3. Konteks Memori Kaya (Rich Context Format)
Menulis log "File X diubah" tidak cukup. Setiap penyelesaian tugas oleh *Executor* wajib disuntikkan ke folder `memory/` dengan 3 komponen wajib (berformat Markdown ramah-LLM):

1. **Konteks Awal (Initial Context):** Apa keluhan/permintaan awal dari *User*? (Mencegah kehilangan fokus).
2. **Garis Besar (Outline):** File apa saja yang dimodifikasi dan bagaimana arsitektur logikanya berubah?
3. **Sejarah Perubahan Kode (Relevant Diff):** Potongan kode krusial yang dihapus/ditambah (`+`/`-`), sehingga agen penerus (*Reviewer* atau *Investigator* berikutnya) bisa langsung memvalidasi logika tanpa merayapi file dari nol.

## Kesimpulan
Struktur ini mewujudkan sistem *autonomous agent* yang tidak mudah pikun, kebal terhadap keracunan konteks, dan mampu berjalan selamanya (*infinite run*) tanpa menghanguskan kuota token.
