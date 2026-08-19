# Sintesis: Kelemahan Kritis Ekosistem Orkestrator Raksasa (2026)

Melalui pemindaian paralel oleh 3 subagent riset terhadap ekosistem orkestrator terkemuka (AutoGen, CrewAI, LangGraph, OpenHands, SWE-agent, Aider), kami telah menemukan pola **"kelemahan struktural" (loopholes)** yang diderita oleh industri saat ini. Kelemahan ini menjadi peluang besar bagi arsitektur *snowline 2.0*.

Berikut adalah 3 kelemahan terbesar yang dibagi berdasarkan domain arsitekturnya:

## 1. Domain Multi-Agent (AutoGen, CrewAI)
Orkestrator berbasis obrolan agen gagal total dalam memelihara kebersihan konteks dan alur logika.
- **Conversational Deadlocks (Debat Kusir):** Agen sering terjebak dalam putaran tanpa batas. Agen A mengirim kode, Agen B menolak karena *error*, Agen A membalas dengan kode yang sama persis. Tanpa interupsi berbasis *hash*, debat ini membakar puluhan ribu token.
- **Circular Delegation (Lempar Tanggung Jawab):** Di CrewAI, jika hierarki tidak kaku, Agen A mendelegasikan ke Agen B, lalu Agen B yang kebingungan melempar kembali masalah itu ke Agen A.
- **Context Accumulation:** Seluruh sejarah perdebatan diakumulasi tanpa *summarization* (peringkasan) yang ketat, mempercepat kehancuran memori *cache*.

## 2. Domain State Machine (LangGraph, LlamaIndex)
Grafik alur kerja (DAG) disukai karena mudah diaudit, tetapi pendekatannya membunuh otonomi dan merugikan manajemen *cache*.
- **Append-Only Context Bloat:** Setiap putaran gagal (misal *self-correction*) menyebabkan seluruh histori lama disalin ulang. Tidak ada mekanisme otomatis untuk "membuang masa lalu" yang tidak relevan.
- **Tool Output Flooding:** Hasil alat berukuran masif (seperti log terminal 10.000 baris) langsung disuntikkan ke status (*state*) global tanpa disaring (filter).
- **Kekakuan Ekstrem (Rigidity):** Jika skenario spesifik tidak diprogram secara *hardcode* dalam sebuah simpul (*node*), agen tidak bisa berimprovisasi.

## 3. Domain Coding Agents (OpenHands, SWE-agent, Aider)
Metode pembacaan file dan skalabilitas kode untuk basis data besar (*enterprise*) masih memiliki titik buta.
- **Tunnel Vision (SWE-agent):** Menggunakan pembatas layar (e.g. hanya melihat 100 baris per halaman) menghemat token, tetapi membuat agen gagal melihat arsitektur perangkat lunak secara keseluruhan (kesulitan melakukan *refactoring* global).
- **One-Hop Blindness (OpenHands/RAG):** Mengandalkan RAG (pemotongan dokumen berbasis *embedding*) sering kali memotong kode tepat di tengah logika fungsi. Agen LLM diberi konteks yang terpotong, berujung pada halusinasi logika.
- **Limitasi Semantik (Aider):** Mengandalkan pemetaan struktur sintaks (AST / *Tree-sitter*) memang sangat ringkas (Peta Direktori), tetapi AST buta terhadap *data flow* dan *runtime behavior*. Agen tahu fungsi itu ada, tetapi buta arah aliran datanya.

---
## 💡 Rekomendasi Antisipasi untuk *Snowline 2.0*
Dari celah-celah di atas, ini yang **wajib dihindari dan dievaluasi lebih lanjut**:
1. **Delegasi Bisu (Silent Delegation):** Hindari *Agent Chatter*. Delegasi tugas harus kaku: input dari Induk -> output dari Bawahan.
2. **Stateful Delta Filter:** Perlu ada mekanisme cegat keluaran *tool* (seperti terminal atau file mentah) di level eksekusi sistem.
3. **Full-File Context Pumping (dengan Cache):** Manfaatkan **Prompt Caching 1-Jam** daripada memotong kode secara kaku yang memicu halusinasi.
