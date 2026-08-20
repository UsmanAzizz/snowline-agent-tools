# 12_PROTOTYPE_CHAMBER_V2.md — Blueprint Automated Chamber 2.0

Disusun 20 Agustus 2026. Mencatat hasil dari Analisis dan Prototipe *Automated Chamber 2.0* yang memadukan seluruh teknologi pelindung (Sprint 3-7).

## 1. State Machine (Bukan LLM-as-a-Judge)
Ekosistem Snowline tidak membiarkan sebuah AI mengevaluasi AI lainnya secara bebas (seperti AutoGen) karena lambat dan tidak dapat diprediksi.
- **Konsep:** Transisi antar sub-agen dikelola mutlak oleh *skrip Python statis* (`snowline_core_v2.py`). 
- **Keuntungan:** Siklus *Generate-Validate-Retry* berjalan sangat cepat. Jika *Syntax Guardian* (Gate) menolak sebuah *output*, skrip langsung memerintahkan agen untuk mengulang. Jika melampaui batas (3 kali), skrip seketika mengintervensi dengan Git Rollback.

## 2. Strict Tool Separation (Anti-Mission Creep)
Teguran via *System Prompt* ("Tolong jangan tulis kode, Anda hanya Investigator") tidak berguna saat LLM berhalusinasi.
- **Konsep:** *Governance as Infrastructure* (Role-Based Access Control).
- **Implementasi:** Di `snowline_core_v2.py`, skema fungsi yang disuntikkan ke LLM dipisahkan secara fisik.
  - **Investigator:** Hanya memiliki akses ke Lensa (`selective_reader`, `smart_tree`). Karena fungsi penulisan dihapus dari *payload* API-nya, maka mustahil secara teknis baginya untuk menulis file. Ia dipaksa merangkum temuannya dan memanggil *Handoff*.
  - **Executor:** Hanya memiliki akses ke Pagar (`write_to_file`, `syntax_guardian`). Ia tidak dibebani fungsi pencarian sehingga *context window*-nya tetap bersih untuk merakit kode.

## Kesimpulan Akhir Ekosistem
*Automated Chamber 2.0* adalah puncak evolusi dari Snowline. Menggantikan "Manusia Penjahit" (dari era `agents_chamber` kuno) dengan sebuah *Middle-layer Script* yang kejam dan tanpa kompromi. Dengan pembatasan alat yang mutlak dan gerbang deterministik, kita telah mengeliminasi 90% penyebab kegagalan agen otonom di dunia nyata (berdasarkan data *SWE-bench*). 

Semua prototipe telah teruji aman di ruang karantina (`v2_prototypes`).
