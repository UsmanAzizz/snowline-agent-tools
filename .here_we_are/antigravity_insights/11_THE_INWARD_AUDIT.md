# Snowline V2: The Inward Audit (Sprint 6)

Dokumen ini adalah hasil forensik internal dari repositori `open_source_agents`. Setelah merumuskan teori *Bleeding Edge* di luar sana, kita menemukan bahwa arsitektur produksi kita saat ini sangat rentan dan melanggar prinsip-prinsip otonomi modern. 

Berikut adalah 3 Utang Arsitektur (*Architectural Debt*) terbesar yang wajib direfaktor:

## 1. Pelanggaran Semantic Routing (Obesitas Prompt)
Sistem Antigravity saat ini memiliki 18+ sub-direktori *skill* di `.agents/skills/`.
- **Temuan:** Orkestrator secara otomatis memindai seluruh file `SKILL.md` dan menyuntikkannya sekaligus sebagai *tool schema* ke dalam *system prompt* LLM. Meskipun kita memiliki *skill* `companion` yang bertugas sebagai *router*, sistem *host* tetap memaksa mendaftarkan semuanya.
- **Dampak:** Ini memboroskan ribuan token dan menghancurkan efisiensi kognitif agen.
- **Solusi Masa Depan:** Orkestrator harus dikonfigurasi murni sebagai **Skill Gateway**. Hanya *tool* yang dikurasi oleh `companion` yang boleh diinjeksikan secara dinamis ke *suffix* pesan.

## 2. Titik Buta Halusinasi (Raw Stack Trace Feedback)
Modul eksekutor kita (`snowline_run.py` dan `code_finder.py`) memiliki penanganan *error* yang sangat primitif.
- **Temuan:** `snowline_run.py` (Baris 60 & 106) secara eksplisit mencetak `stderr` mentah kembali ke LLM. Lebih parah lagi, `code_finder.py` memanggil `traceback.print_exc()` ketika terjadi *exception*.
- **Dampak:** Alih-alih mendapatkan *Structured Feedback* (seperti `"Parameter salah, coba lagi"`), LLM dihantam dengan ribuan baris teks merah Python. Ini adalah penyebab nomor satu dari *Cognitive Deadlocks* (Agen berhalusinasi dan mencoba memperbaiki kodenya sendiri dalam *infinite loop*).
- **Solusi Masa Depan:** Menghapus fungsi *print traceback* dan membungkus *output error* ke dalam JSON terstruktur (atau *XML tag* `<error>`) agar agen bisa memahaminya sebagai umpan balik logis.

## 3. Ketiadaan Pre-Flight Checks (Kegagalan Bisu)
Banyak *skill* kita yang sangat bergantung pada *binary* sistem operasi (seperti Node.js atau Git).
- **Temuan:** Skrip `project_guardian/guardian.py` menjalankan `subprocess.run('npm audit')` lalu menelannya mentah-mentah dengan `except: pass`. 
- **Dampak:** Jika laptop klien tidak memiliki `npm`, agen tidak akan komplain. Ia akan menganggap audit keamanan selesai dengan sukses (*Silent Failure*). Ini sangat mematikan kredibilitas agen.
- **Solusi Masa Depan:** Setiap *skill* yang memanggil dependensi eksternal wajib mengimplementasikan `shutil.which('npm')` atau melakukan *Graceful Degradation* (mencetak log spesifik: "NPM tidak ditemukan, beralih ke mode dasar").
