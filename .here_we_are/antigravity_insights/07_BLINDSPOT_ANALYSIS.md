# Snowline V2 Blindspot Analysis (Sprint 2)

Dokumen ini merangkum hasil riset 4 agen investigatif mengenai celah kritis (blind spots) pada ekosistem LLM modern. Meskipun *Snowline V2* telah aman dari pemborosan biaya dan *infinite loops*, 4 titik buta ini wajib dimitigasi dalam desain arsitektur lanjutan.

## 1. Sindrom "Lost in the Middle" (Degradasi Atensi)
LLM (termasuk Gemini 1.5 Pro dan Claude 3.5 Sonnet) mengalami amnesia pada kedalaman konteks 30%-70% dengan penurunan akurasi hingga 20-30%.
- **Solusi Arsitektural (Sandwich Prompting):** Selalu letakkan instruksi kritis di paling awal (Top) *system prompt*, dan ulangi instruksi spesifik tersebut di paling akhir (Bottom) dari konteks sebelum memanggil LLM.
- **XML Scaffolding:** Bungkus semua data mentah dengan `<context>...</context>` untuk memisahkan otoritasnya dari instruksi.

## 2. Prompt Injection (Pembajakan via Eksternal File)
Agen bisa disusupi (*hijacked*) jika ia membaca komentar kode berbahaya atau *log* instalasi `npm` yang memerintahkannya membocorkan API Key atau merusak sistem.
- **Solusi Arsitektural (Data Marking):** Setiap kali orkestrator menyerap data dari file eksternal atau perintah terminal, data tersebut harus dibatasi ketat (misal dengan penanda ```raw_untrusted_data```) sehingga LLM tahu itu bukan instruksi.
- **Dual-LLM (Critic):** Menerapkan pengawas ringan (*Flash Model*) untuk memonitor hasil panggilan *tool* sebelum dieksekusi secara nyata.

## 3. Schema Enforcement (Menyembuhkan Halusinasi Tool)
Melempar *stack trace error* Python mentah kepada LLM ketika JSON-nya rusak justru memperparah halusinasi.
- **Solusi Arsitektural (Structured Feedback):** Orkestrator harus menangkap *error*, menelannya, dan memuntahkan instruksi perbaikan yang sangat spesifik (misal: `"Error: Parameter 'target_file' hilang. Coba lagi."`).
- **Reasoning Scratchpad:** Memaksa parameter pertama dari setiap skema JSON menjadi `thought_process`, memaksa agen berpikir sebelum memutar tuas eksekusi (*Chain-of-Thought*).

## 4. Multi-Agent Handoff Protocol (Oper Tugas)
Memindahkan seluruh memori obrolan dari Agen A ke Agen B adalah bunuh diri ekonomi (merusak *cache* dan mempercepat *Lost in the Middle*).
- **Solusi Arsitektural (State Projection):** Gunakan fungsi *Summarizer* untuk mengekstrak intisari hasil kerja Agen A. Kemudian, proyeksikan hanya data yang relevan ke dalam "Konteks Internal" Agen B.
- **Prompt Caching Alignment:** Pertahankan *Golden Payload* (instruksi inti) agar tetap konstan, dan hanya ubah variabel status di memori tambahan agar diskon 90% tetap berlaku saat perpindahan agen.
