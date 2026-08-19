# Pre-Requirement Analysis: Snowline v2.0

Dokumen ini merangkum status kesiapan arsitektur saat ini (berdasarkan sprint evaluasi T0-T6) dan peta jalan menuju pembangunan *Snowline 2.0*.

## 1. Apa yang Sudah Ada (Aset Teruji)
*Snowline* tidak dimulai dari nol. Kita sudah memiliki fondasi yang terbukti lolos uji tekanan (stress test):
- **Dasar Ekonomi yang Absolut:** Kita sudah tahu pasti apa yang **tidak boleh** dilakukan (memotong/mengablasi teks) berkat penemuan rasio biaya baca/tulis *Prompt Caching* (50:1).
- **Protokol *Special Ops***: Skrip berbasis Python murni seperti `project_guardian`, `context_mapper`, dan `smart_search`. Mereka membuktikan bahwa pencarian deterministik (tanpa LLM) ribuan kali lebih cepat dan murah.
- **Arsitektur Pemantauan Transparan:** Sistem `PLAN.md` dan *Hybrid Validation* (Persetujuan Pengguna sebelum eksekusi).
- **Paralelisme Bawaan:** Pemahaman yang solid tentang cara memanfaatkan *Subagent* untuk menyelesaikan riset secara bersamaan tanpa memenuhi memori agen utama.

## 2. Apa yang Belum Ada (Kepingan yang Hilang)
Ini adalah komponen-komponen kritis tingkat rendah yang saat ini sama sekali belum diimplementasikan di basis kode *Snowline*:
- **The Golden Payload Router (Cache Manager):** Saat ini, sistem *harness* LLM masih menggabungkan *prompt* secara sembarangan. Kita belum memiliki *middleware* yang secara kaku memaksa urutan `Tools -> System (Big Code) -> Messages (Dynamic)` dengan injeksi `cache_control` yang presisi.
- **Stateful Delta Firewall (Pencegat Loop):** Pseudo-code *hashing* menggunakan `XXH3` sudah dirancang, tetapi skrip Python aktual yang mencegat *output* terminal (mencegah agen memutar kode yang sama berkali-kali) belum dibuat.
- **Silent Delegation Schema:** Kita belum memiliki pembatas ketat (*parser*) yang memaksa *Subagent* untuk hanya memuntahkan `JSON` murni tanpa sapaan ramah atau penjelasan logis panjang lebar.
- **Integrasi Senjata Statis Baru:** Alat seperti `Semgrep` (pencari celah) atau `Knip` (pembersih ekosistem JS/TS) belum dibungkus (*wrapped*) ke dalam direktori `.agents/skills`.

## 3. Apa yang Bisa Kita Lakukan Setelah Ini (Next Steps)
Langkah-langkah taktis sebelum menulis baris kode pertama untuk v2.0:

1. **Sesi Sparing (Peer Review):** Menyerahkan dokumen-dokumen di folder `antigravity_insights` kepada *Lead* utama (Claude Code). Biarkan Claude mencari celah logika dari temuan ini. Jika teori *Cache* dan *Delta Firewall* kita bertahan dari kritikannya, barulah teori ini disahkan.
2. **Purifikasi (Pembersihan Skill Lama):** Mengaudit direktori `.agents/skills/` saat ini. Mematikan atau menghapus secara permanen skrip-skrip yang berkaitan dengan "pemotongan teks" (seperti `selective_reader` versi lama) karena terbukti membakar uang.
3. **Prototipe Firewall (Proof of Concept):** Membangun skrip Python kecil yang murni bertugas melakukan *hashing* pada *string* panjang dengan `XXH3`, lalu mengujinya pada *output* terminal palsu untuk melihat seberapa cepat ia mendeteksi duplikat.
4. **Membangun "The Golden Payload":** Mulai memodifikasi inti *Agent Harness* agar memahami cara merangkai *Prompt* khusus Anthropic yang menjamin tingkat *Cache Hit* 100%.
