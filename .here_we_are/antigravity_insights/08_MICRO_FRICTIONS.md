# Snowline V2: The Micro-Frictions (Sprint 3)

Dokumen ini merangkum tiga pedoman arsitektur mikroskopis (Micro-Frictions) yang membedakan orkestrator amatir dari orkestrator *Enterprise-grade*. Celah ini berkaitan dengan kecepatan (latensi), perutean (routing), dan ketahanan lingkungan (resilience).

## 1. Latency & TTFA (Time-To-First-Action)
Membiarkan LLM mengoceh (basa-basi) sebelum memanggil *tools* akan membakar *Output Token* yang sangat mahal dan memperburuk latensi.
- **Solusi Arsitektural (Assistant Prefill):** Jangan gunakan *system prompt* negatif ("Jangan mengoceh"). Gunakan teknik injeksi di tingkat API dengan menambahkan `{role: "assistant", content: "{"}` pada akhir pesan untuk memaksa LLM langsung mengetik format JSON.
- **Solusi Arsitektural (Internal Scratchpad):** Jangan membunuh logika *Chain-of-Thought*. Pindahkan area berpikir tersebut ke dalam struktur JSON sebagai *key* pertama (misal: `"_thought": "..."`).
- **Solusi Arsitektural (Streaming Execution):** Orkestrator tidak boleh menunggu seluruh JSON selesai (*blocking*). Gunakan *Streaming Parser*; begitu *key* `action` dan `arguments` tercetak dari API, alat langsung dieksekusi di *background*.

## 2. Semantic Routing (Nasib Cache saat Tools Bertambah)
Menukar susunan *tools* di *system prompt* secara dinamis untuk menyembunyikan fungsi yang tidak dipakai akan **memecahkan struktur Prefix Cache**, memicu lonjakan harga *prefill* 20x lipat.
- **Solusi Arsitektural (The Swarm / Specialist Agents):** Jangan pernah merotasi *tools* secara dinamis di dalam satu agen. Jika Anda memiliki 100 *tools*, pecah menjadi 20 agen spesialis di mana masing-masing agen memegang 5 *tools* statis miliknya secara permanen.
- **Solusi Arsitektural (Static Prefix + Logit Masking):** Letakkan seluruh 100 *tools* di dalam *system prompt* (agar 100% *cache hit*). Penganalisis intensi (*Router*) hanya bertugas mematikan probabilitas eksekusi (*Logits Masking*) untuk 95 *tools* yang tidak relevan di lapisan deterministik, sehingga agen hanya bisa "melihat" 5 *tools* target.

## 3. Resilience (Graceful Degradation)
Sistem otonom yang bergantung pada *binary* sistem operasi (*git*, `npm`, *python*) rentan *crash* beruntun jika dieksekusi di lingkungan lokal pengguna yang tidak lengkap.
- **Solusi Arsitektural (Pre-Flight Checks):** Orkestrator harus memiliki fungsi `check_env()` sebelum agen dihidupkan.
- **Solusi Arsitektural (Layered Fallback):** Jika `knip` atau `semgrep` tidak ditemukan, orkestrator tidak boleh *crash*. Ia harus otomatis menghapus *tool* tersebut dari daftar *prompt*, memunculkan peringatan kuning, dan menyediakan alat pengganti bawaan Python (seperti *Regex Search*) agar agen tetap bisa bekerja meskipun dalam mode terdegradasi (*degraded mode*).
