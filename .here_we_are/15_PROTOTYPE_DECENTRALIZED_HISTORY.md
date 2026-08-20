# 15_PROTOTYPE_DECENTRALIZED_HISTORY.md — Blueprint History Tracker Terdesentralisasi

Disusun 20 Agustus 2026. Mencatat hasil perancangan sistem pengganti RAG, yaitu *Changelog Guardian* yang dipartisi berdasarkan peran Sub-Agen.

## 1. Zero-Bloat Context Retrieval
Alih-alih menyuruh agen mencari ke seluruh file menggunakan pencarian vektor (RAG) yang memakan RAM tinggi, Orkestrator memberikan *"Cheat Sheet"* (catatan ringkas) berisi 5 perubahan terakhir di dalam *System Prompt* agen sesaat sebelum agen menyala. Ini bertindak sebagai pengganti ingatan kronologis yang efisien.

## 2. Compartmentalized Memory (Memori Tersekat) & Subagent Containers
Kejeniusan dari arsitektur ini terletak pada lokalisasi histori yang digabung dengan konsep **Subagent Containers (Folder Mandiri)**.
- **Konsep:** Sistem tidak hanya sekadar memisahkan riwayat, melainkan mendedikasikan satu **Folder Fisik** utuh untuk setiap sub-agen.
- **Struktur Folder:**
  ```text
  .agents/subagents/
  ├── investigator/
  │   ├── system_prompt.md   (Otak: Aturan Investigasi)
  │   ├── allowed_tools.json (Senjata: Hanya alat baca)
  │   └── history.json       (Memori: Jejak pencarian)
  ├── executor/
  │   ├── system_prompt.md   (Otak: Aturan Koding)
  │   ├── allowed_tools.json (Senjata: Alat tulis)
  │   └── history.json       (Memori: File yang dimodifikasi)
  ```
- **Dampak Arsitektural:** 
  1. **Isolasi Mutlak:** Saat Orkestrator memanggil `executor`, ia memuat folder `executor/`. *Executor* benar-benar terputus dari eksistensi agen lain (Buta terhadap *System Prompt* Auditor maupun memorinya).
  2. **Pluggability (Bongkar-Pasang):** Menambah Sub-Agen baru semudah membuat folder baru berisi 3 file tersebut, tanpa perlu merombak ribuan baris skrip inti Orkestrator.

## Kesimpulan Akhir
Ini adalah potongan kepingan terakhir. Kita resmi membuang kebutuhan atas server *Vector Database* raksasa. Ekosistem Snowline V2 sekarang tidak hanya kedap air dalam hal memori, namun juga sangat modular melalui arsitektur *Subagent Containers* (Satu Agen = Satu Folder).
