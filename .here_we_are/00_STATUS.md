# Status — 19 Agustus 2026

## Pertanyaan induk

Apakah snowline-agent-tools punya alasan untuk terus ada, dan di mana
sebenarnya nilai perkakas agen mengendap?

## SELESAI — jangan diteliti ulang

### 1. agents_chamber berhenti

Dua tinjauan independen (Claude Code dan Gemini, korpus dan metode berbeda)
sampai ke kesimpulan yang sama. Gemini memutuskannya melawan kepentingannya
sendiri sebagai Tech Lead yang mengelola chamber itu.

Bukti pendukung: commit terakhir `open_source_agents` 6 Agustus; `cbt_master`
terus jalan sampai 17 Agustus. Lima tugas chamber terakhir (83-87) seluruhnya
mengurus aturan chamber sendiri, dua di antaranya berakhir tanpa perubahan.

### 2. Sebagian besar kemampuan snowline sudah jadi bawaan

Pencarian kode, sunting dengan pratinjau, pembatas lingkup, pemindai keamanan,
penganalisis maksud, orkestrasi subagen, plafon anggaran — semuanya sudah ada
di perkakas arus utama. Rinciannya di `01_TEMUAN.md`.

### 3. Mekanisme yang dipanggil atas keputusan agen tidak bertahan

Terbukti empat kali dari empat arah berbeda. Lihat `01_TEMUAN.md` bagian C.

## SELESAI — Seluruh Sprint Evaluasi (20 Agustus 2026)

### Pertanyaan Induk Terjawab Secara Definitif

**Apakah pengurangan karakter berubah menjadi pengurangan biaya tertagih?**

Status: **SELESAI (Hipotesis Mati).**
Jawabannya: **TIDAK.** Pengurangan karakter melalui ablasi deterministik justru **MENAMBAH** biaya tagihan secara masif karena merusak *prefix* Prompt Caching Anthropic. Penulisan *cache* (1h TTL) terbukti 20x lebih mahal daripada pembacaan *cache*.

Seluruh tugas papan ukur (T1 hingga T6) telah dieksekusi, diverifikasi, dan ditutup:
- **T6 (Penyelarasan Angka):** Penghematan karakter bersih memang mencapai 30%-37%, tapi angka ini tidak relevan lagi secara ekonomi.
- **T2 (Analisis Cache):** Membuktikan secara matematis bahwa memodifikasi konteks demi menghemat token baca akan memicu *cache miss* yang merugikan hingga $10.000+ dalam skala korpus.
- **T3 (Uji Kecukupan Pencarian):** Aturan pemangkasan baris duplikat terbukti **BERBAHAYA** (tingkat kegagalan uji kecukupan mencapai 21,4%).
- **T4 (Kategori 'Other'):** Pendelegasian antar-agen (Tool: `Agent`) adalah pemborosan terbesar di luar pembacaan berkas karena mengembalikan seluruh *chain of thought* bawahan.
- **T5 (Injeksi Berulang):** Pengulangan injeksi masif (>500 karakter) murni akibat mekanisme sinkronisasi UI/harness, bukan LLM.

### Implikasi untuk `snowline-agent-tools`
Satu-satunya nilai nyata yang tersisa dari *snowline* bukanlah fitur pemangkasan token, melainkan kemampuannya untuk melakukan **pemindaian aktif (Active Auditing)**, seperti `project_guardian` yang terbukti menemukan kebocoran *API key* dalam hitungan detik. Semua aturan ablasi konteks harus dihapus.
