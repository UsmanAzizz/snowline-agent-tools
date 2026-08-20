# Status — 19 Agustus 2026

## Pertanyaan induk

Apakah snowline-agent-tools punya alasan untuk terus ada, dan di mana
sebenarnya nilai perkakas agen mengendap?

> [!IMPORTANT]
> **Sebelum memakai angka mana pun di folder ini**, baca bagian "BATASAN
> KESIMPULAN" di `05_APA_YANG_MASIH_BERDIRI.md`. Sprint ini mengukur adopsi
> lalu menyimpulkan tentang kegunaan. Angka adopsi sah; angka kegunaan
> (0 dari 20) hasil pembacaan, belum diuji lapangan.

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

Status: **SELESAI — hipotesis mati, tetapi bukan karena alasan yang semula
ditulis.** Dihitung ulang 20-08 setelah dua dasarnya tidak bertahan. Rincian di
T2r dan T5r pada papan tugas.

```
biaya sekarang    $2.262,50
biaya tandingan   $2.193,73
SELISIH             -$68,77   (-3,0%)  PENGHEMATAN
```

Pemangkasan konteks **menghemat**, bukan menambah — tetapi hanya 3,0%, jauh di
bawah ambang 15%. Sebabnya teks suntikan tool cuma **8,7%** dari awalan
rata-rata; sisanya prompt sistem, riwayat percakapan, dan keluaran agen sendiri.
Memangkas 37,6% dari 8,7% hanya menyusutkan awalan 3,3%.

**Angka $10.738,90 salah dan jangan dipakai.** Perhitungan lama menghargai token
cache-read dengan tarif cache-write — model penyuntingan retroaktif, bukan
pemroses yang berjalan langsung.

Yang tetap berdiri dan tidak dibantah: cache menghemat 85,5%, dan 98% token
masukan adalah cache read.

- **T2 salah model.** Perhitungannya menghargai token cache-read dengan tarif
  cache-write. Itu model penyuntingan retroaktif. Pemroses yang berjalan
  langsung tidak memasukkan teksnya sama sekali, jadi teks itu tidak dibaca
  DAN tidak ditulis. Tanda efeknya belum diketahui — bukan naik, bukan turun.
- **T5 premisnya tidak reproduksi.** Diukur ulang: 2 salinan berlebih / 6.195
  karakter, bukan 32 / 132.261. Dua definisi populasi, hasil sama. Jadi
  kesimpulan "pengulangan masif akibat sinkronisasi UI" tidak punya bahan.

Yang masih berdiri: cache memang menghemat 85,5%, dan 98% token masukan adalah
cache read. Itu terukur dan tidak dibantah. Yang dibantah adalah kesimpulan
bahwa pemangkasan otomatis menaikkan biaya.

Kalimat di bawah ini dipertahankan apa adanya sebagai catatan versi sebelumnya:

~~Jawabannya: **TIDAK.**~~ Pengurangan karakter melalui ablasi deterministik justru **MENAMBAH** biaya tagihan secara masif karena merusak *prefix* Prompt Caching Anthropic. Penulisan *cache* (1h TTL) terbukti 20x lebih mahal daripada pembacaan *cache*.

Seluruh tugas papan ukur (T1 hingga T6) telah dieksekusi, diverifikasi, dan ditutup:
- **T6 (Penyelarasan Angka):** Penghematan karakter bersih memang mencapai 30%-37%, tapi angka ini tidak relevan lagi secara ekonomi.
- **T2 (Analisis Cache):** Membuktikan secara matematis bahwa memodifikasi konteks demi menghemat token baca akan memicu *cache miss* yang merugikan hingga $10.000+ dalam skala korpus.
- **T3 (Uji Kecukupan Pencarian):** Aturan pemangkasan baris duplikat terbukti **BERBAHAYA** (tingkat kegagalan uji kecukupan mencapai 21,4%).
- **T4 (Kategori 'Other'):** Pendelegasian antar-agen (Tool: `Agent`) adalah pemborosan terbesar di luar pembacaan berkas karena mengembalikan seluruh *chain of thought* bawahan.
- **T5 (Injeksi Berulang):** Pengulangan injeksi masif (>500 karakter) murni akibat mekanisme sinkronisasi UI/harness, bukan LLM.

### Implikasi untuk `snowline-agent-tools`
Satu-satunya nilai nyata yang tersisa dari *snowline* bukanlah fitur pemangkasan token, melainkan kemampuannya untuk melakukan **pemindaian aktif (Active Auditing)**, seperti `project_guardian` yang terbukti menemukan kebocoran *API key* dalam hitungan detik. Semua aturan ablasi konteks harus dihapus.
