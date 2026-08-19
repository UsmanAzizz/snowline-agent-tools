# Cetak Biru Eksplorasi: Taktik Gerilya *Snowline 2.0*

Berdasarkan riset analitis mendalam yang mengutamakan presisi absolut, berikut adalah usulan landasan teknis tingkat rendah (*low-level*) untuk *Snowline 2.0*. Ini masih berupa temuan mentah yang menunggu validasi dari *Lead Agent*.

## 1. Hukum Mutlak Eksploitasi Cache (Anthropic API)
*Prompt Caching* bersifat non-semantik (menggunakan *Byte-Exact Cumulative Hash*). Perbedaan satu spasi, karakter *newline* (`\n` vs `\r\n`), atau urutan *key* JSON pada definisi *tools* akan **100% menghancurkan *cache***.

**Arsitektur *Payload* "Golden Order" (Satu Cache untuk Puluhan Agen):**
Agar dapat melempar 100.000 token kode mentah ke banyak agen berbeda secara bersamaan dengan biaya 0 (100% *cache hit*), hierarki *payload* API harus disusun baku:
1. **`tools`**: Fungsi didefinisikan dengan *custom JSON serializer* (urutkan *keys* secara alfabetis) agar susunan *byte*-nya deterministik statis.
2. **`system`**: Semua kode mentah, dokumentasi, dan peta arsitektur disuntikkan di sini sebagai "Ensiklopedia Proyek". **PENTING:** Jangan masukkan persona/instruksi spesifik agen di sini. Akhiri blok ini dengan `cache_control: {"type": "ephemeral"}`.
3. **`messages`**: Masukkan persona agen dinamis (misal: "Anda adalah agen UI") pada blok ini (setelah *breakpoint*). Ini menjamin bagian ensiklopedia tetap menggunakan *cache* untuk seluruh jenis agen.

## 2. Stateful Delta Firewall (Pencegat Loop LLM)
Untuk mencegah *infinite loop* dan *Context Bloat* akibat agen memuntahkan *output* terminal panjang berulang kali, direkomendasikan pemasangan *middleware interceptor*.

**Spesifikasi Hashing Khusus:**
- **Algoritma Utama:** `XXH3 (128-bit)`. Sangat optimal (bandwidth RAM maksimal) untuk menelan log raksasa tanpa mengganggu kecepatan I/O agen.
- **Prapemrosesan (Sanitization):** Sebelum teks di- *hash*, ia dibersihkan dari *noise* menggunakan Regex (Ubah *timestamp*, alamat memori HEX, dan UUID menjadi token statis seperti `<TIMESTAMP>`). 
- **Aksi Cegatan:** Jika *hash* dari *output* terminal sama dengan *turn* sebelumnya, tukar dengan peringatan sistem statis: `[FIREWALL: Output struktural identik dengan eksekusi sebelumnya. Tindakan diblokir.]`

## 3. Amunisi Auditor Senyap (Senjata Analisis Statis)
Disarankan untuk tidak lagi memakai LLM untuk tugas pencarian cacat dasar. Sebagai gantinya, kemas CLI *open-source* deterministik tinggi menjadi alat *Snowline*:
- **Knip:** Senjata khusus untuk proyek JS/TS. Menemukan *dead code*, *unused exports*, dan dependensi siklik dengan tingkat *false-positive* mendekati 0%. Hasil JSON-nya bisa langsung dibaca agen.
- **Semgrep:** Alat AST multi-bahasa pencari *anti-pattern* dan celah keamanan. Mengeluarkan format standar SARIF/JSON.
- **CodeQL:** Pemindai *data-flow* *source-to-sink* yang sangat presisi untuk analisis kerentanan kompleks, meski membutuhkan *overhead* eksekusi sedikit lebih lambat.
