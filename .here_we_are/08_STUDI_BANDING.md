# 08_STUDI_BANDING.md — Lensa & Pagar Ekosistem Agen

Disusun 20 Agustus 2026. Berdasarkan riset eksternal (via pencarian web) dan komparasi dengan kapabilitas bawaan Antigravity.

## A. Perbandingan Lensa (Noise Filtering)
Bagaimana agen menangani *noise* dari direktori berukuran masif?

1. **Antigravity (Default)**
   - Mengandalkan alat bantu `list_dir` untuk memetakan ruang file, yang menghasilkan *output JSON* besar dan sulit dibaca (menyertakan setiap file `.git` atau `node_modules` jika tidak di-*ignore* secara manual oleh agen).
   - `view_file` memiliki batasan *byte* mutlak untuk mencegah konteks meluap.

2. **Snowline / CBT Master (`smart_tree` & `crash_decoder`)**
   - **`smart_tree` vs `tree`**: Hasil uji membuktikan `smart_tree` menghemat 84% token murni dibanding `tree` karena ia mengerti `.gitignore`. Ini adalah lensa yang sangat unggul untuk agen AI, mengeliminasi ratusan baris derau.
   - **`crash_decoder` vs Jejak Mentah**: Mampu membuang 100% *noise* internal (seperti fungsi bawaan `node:internal`) dan secara langsung menyajikan kepingan kode aplikasi milik pengguna.

**Kesimpulan A:** Perkakas observasi Snowline (awalnya diremehkan dengan julukan "hanya mencatat") sejatinya adalah filter sinyal-tinggi (*high-signal filters*) yang mutlak dibutuhkan AI.

## B. Perbandingan Pagar (Scope Guarding)
Bagaimana ekosistem mutakhir mencegah agen merusak sistem operasi atau proyek?

1. **Aider (Pendekatan Kepercayaan Penuh)**
   - Tidak menggunakan *Docker/sandbox*. Agen hidup di sistem inang (*host*).
   - Pengamanan murni dilakukan lewat kendali versi (Git) dan *explicit inclusion* pengguna (file baru disentuh jika di `/add`).
2. **OpenHands / OpenDevin (Pendekatan Kontainer)**
   - Menggunakan lingkungan *Docker*. Mereka mengurung agen di dalam sistem operasi virtual, dan hanya menautkan folder *workspace* spesifik. Tidak mungkin merusak file di luar *container*.
3. **SWE-agent (Pendekatan ACI - Agent Computer Interface)**
   - Selain mesin isolasi, SWE-agent membekali agen dengan lapisan jembatan (*interface*). Modifikasi file melewati *syntax checker* statis sebelum disimpan.
4. **Snowline / CBT Master**
   - **Gaya Hibrida**: Menyerupai Aider (berjalan di inang), tetapi meniru SWE-agent dengan menyuntikkan *linter* dan *gatekeeper* berbasis kode Python (seperti validasi *syntax* pada `auto_scaffolder` atau pembatasan penulisan jalur lintang direktori).

**Kesimpulan B:** Ekosistem ini sejalan dengan tren mutakhir. Alih-alih membungkus dalam Docker, kita memasang "Gembok Lembut" (*soft-locks*) pada perkakas. Transformasi `impact_analyzer` dan `plan_tracker` menjadi alat MEMERIKSA (dengan `exit 1`) menyempurnakan posisi ekosistem kita di ranah agen berkinerja tinggi.
