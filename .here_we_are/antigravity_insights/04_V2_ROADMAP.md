# Master Roadmap: Snowline v2.0 (The Guerrilla Architecture)

Dokumen ini merupakan peta jalan (roadmap) strategis berskala makro untuk pembangunan *Snowline v2.0*. Berdasarkan temuan analitis tingkat tinggi, pembangunan arsitektur ini dipecah menjadi 4 Fase yang saling mengunci. 

Setiap fase harus dieksekusi secara terisolasi sebagai purwarupa (Proof of Concept) sebelum diintegrasikan secara masif ke dalam orkestrator utama.

---

## Phase 1: Foundation of Defense (Pertahanan Konteks)
Fase ini berfokus murni pada perlindungan memori agen dari pendarahan token (*context bleeding*) dan jebakan *infinite loop*.
- **Target Komponen:** 
  1. `Stateful Delta Firewall` (Pencegat Hashing XXH3)
  2. `Silent Delegation Parser` (Enforcer JSON Ketat)
- **Analisis Kritis:** Sebelum kita memikirkan kecerdasan, kita harus memastikan agen tidak bisa menyakiti dirinya sendiri. LLM secara bawaan rawan memuntahkan teks berulang ketika panik (error beruntun). Membangun *Firewall* di level *middleware* yang mendeteksi tabrakan *hash* adalah satu-satunya jaminan matematis untuk menghentikan loop kematian ini.
- **Rencana Eksekusi (Implementation Plan P1):** Menulis skrip Python mandiri yang menguji kecepatan *hashing* pada simulasi *output* terminal 10.000 baris.

---

## Phase 2: Economic Exploitation (Eksploitasi Cache API)
Fase ini berfokus pada eksploitasi rasio biaya 50:1 (Read vs Write) dari *Prompt Caching* modern.
- **Target Komponen:** 
  1. `Golden Payload Router` (Penyusun *Prompt* Spesifik Cache)
  2. `Agnostic Adapter` (Lapisan Abstraksi untuk Gemini & Claude)
- **Analisis Kritis:** Industri saat ini membakar token dengan merusak *prefix cache* lewat rotasi pesan yang ceroboh. *Payload Router* ini akan memberlakukan hierarki "Besi": *Tools* harus deterministik alfabetis, *System Prompt* berisi ensiklopedia utuh 100k token dengan *breakpoint*, dan instruksi dinamis dikarantina murni di dalam *User Message*.
- **Rencana Eksekusi (Implementation Plan P2):** Membuat struktur pembuat (*builder*) muatan JSON REST yang mengembalikan susunan API yang divalidasi kebal mutasi.

---

## Phase 3: The Guerrilla Arsenal (Gudang Senjata Senyap)
Fase ini membuang kebiasaan lama (menyuruh LLM menganalisis cacat kode dasar) dan menggantinya dengan komputasi deterministik tingkat milidetik.
- **Target Komponen:** 
  1. `Static Scavenger Wrappers` (Integrasi *Knip*, *Semgrep*, *CodeQL*)
  2. Pembersihan *Skill* Lama (Menghapus *selective_reader* dan pemotong teks LLM)
- **Analisis Kritis:** Menggunakan LLM untuk mencari *dead code* atau *cyclic dependency* seperti menanam pohon pakai *excavator*. Pada fase ini, kita akan membungkus pemindai *open-source* CLI ke dalam standar *tools* (*Skill*) *Snowline*, di mana *output*-nya disaring menjadi JSON bersih yang bisa dicerna agen induk.
- **Rencana Eksekusi (Implementation Plan P3):** Membangun satu purwarupa (*wrapper*) untuk `Knip` dan menguji pemformatan *output*-nya sebelum mengimplementasikan yang lain.

---

## Phase 4: Full Orchestrator Integration (Sintesis Utama)
Fase ini adalah penggabungan (*merging*) dari seluruh purwarupa (PoC) ke dalam *harness* agen produksi yang sesungguhnya.
- **Target Komponen:**
  1. `snowline_core_v2.py`
  2. Implementasi *Cross-Agent Workflow* (Delegasi Murni)
- **Analisis Kritis:** Setelah P1 hingga P3 terbukti tahan banting secara individual, mereka akan dikunci (di-*import*) ke dalam pembuluh darah utama agen. Di sinilah *Agent Chamber* lama akan digantikan oleh arsitektur *Silent Delegation* yang diawasi penuh oleh *Delta Firewall*.
- **Rencana Eksekusi (Implementation Plan P4):** Refaktor total atas mesin *routing* lama menuju kerangka kerja v2.0 yang deterministik.
