# Temuan

## A. Pengukuran ablasi — korpus Claude Code, 19 Agustus

Korpus: jejak sesi `abbd62e6-...jsonl`, 15.595 rekaman, 2.911 panggilan tool,
3.283 peristiwa injeksi teks.

### Populasi

| kategori | jumlah | total karakter | % |
|---|---:|---:|---:|
| baca berkas | 369 | 1.490.043 | 43,9 |
| keluaran perintah | 1.657 | 1.367.380 | 40,3 |
| lain-lain | 1.210 | 424.448 | 12,5 |
| hasil pencarian | 47 | 110.478 | 3,3 |
| **total** | **3.283** | **3.392.349** | |

### Penghematan

| kategori | kotor | % kategori |
|---|---:|---:|
| baca berkas | 1.222.937 | 82,1 |
| hasil pencarian | 29.582 | 26,8 |
| keluaran perintah | 22.550 | **1,6** |
| **kotor total** | **1.275.069** | **37,6** |

Uji kecukupan: **5 gagal dari 25 sampel (20%)**.
**Penghematan bersih = 30,1%.** Varian per-kategori yang lebih keras: 17,4%.
Proksi token 4,0 karakter/token (asumsi, belum tervalidasi).

### Tiga hal yang menajamkan angka itu

1. **95,9% penghematan datang dari satu aturan** — penyusunan kerangka berkas.
2. **Penyaring jejak tumpukan menghemat 1,6%.** Pada korpus ini praktis nol.
3. **Aturan yang paling hemat juga paling berbahaya.** Kelima kegagalan uji
   kecukupan seluruhnya baca-berkas: ketika aturan itu membuang sesuatu,
   **55,6%** kali yang dibuang ternyata dipakai di langkah berikutnya.

Contoh konkret: saat membaca laporan Gemini, kerangka hanya menyimpan 3 judul
(6.292 -> 128 karakter). Langkah berikutnya memakai ID arXiv dan nama
`impact_analyzer` yang keduanya ada di bagian yang dibuang — pemeriksaan
kutipan palsu tidak akan pernah terjadi.

## A2. Akuntansi cache — TERVERIFIKASI (20-08)

Jejak sesi Claude Code memuat akuntansi token per giliran. Diukur langsung dari
`abbd62e6-...jsonl` dengan model **claude-opus-5** (dikonfirmasi):

```
5.893 rekaman ber-usage
  cache_read_input_tokens        3.006.412.128  ($0,50/juta = $1.503,21)
  cache_creation_input_tokens      59.117.589
    - 1h TTL:                      59.049.867    ($10,00/juta = $590,50)
    - 5m TTL:                          67.722    ($6,25/juta  = $0,42)
  output_tokens                       6.285.003  ($25,00/juta = $157,13)
  input_tokens (non-cache)              48.800    ($5,00/juta = $0,24)
```

**TARIF (claude-opus-5):**
Sumber: https://platform.claude.com/docs/en/docs/build-with-claude/prompt-caching

| Jenis | $/juta | Kelipatan |
|-------|--------|-----------|
| Input | $5,00 | 1x |
| Cache Read | $0,50 | 0,1x |
| Cache Write 1h | $10,00 | 2x |
| Cache Write 5m | $6,25 | 1,25x |
| Output | $25,00 | - |

**PERBANDINGAN BIAYA:**

| Kondisi | Biaya |
|---------|-------|
| **Dengan Cache** | **$2.251,25** |
| **Tanpa Cache** | **$15.485,02** |
| **Penghematan** | **$13.233,76 (85,5%)** |

**PEMICU LONJAKAN CACHE_CREATION:**

| Kategori | Jumlah |
|----------|--------|
| Very High (>100k) | 95 events |
| High (20k-100k) | 24 events |
| Moderate (5k-20k) | 190 events |
| Total spikes | 309 events |

Pola:
- Lonjakan >900k: pergantian task/session baru
- Lonjakan ~25k: membaca banyak file dokumentasi sekaligus
- Lonjakan ~21k: menganalisis error logs

**INTI PERTANYAAN: DAMPAK ABLASI PADA CACHE**

Jika ablasi 37,6% diterapkan prospektif:

| Metric | Nilai |
|--------|-------|
| Karakter berubah | ~1.275.523 |
| Cache read terpengaruh | 1.130.410.960 token |
| Biaya cache read dihemat | $565,21 |
| Biaya cache write baru | $11.304,11 |
| **NET CHANGE** | **+$10.738,90** |

**KESIMPULAN: Ablasi karakter MENAMBAH biaya cache** karena:
- Cache write 1h = 20x biaya cache read
- Jika teks berubah → cache miss → tulis ulang mahal
- Rasio 50:1 (read:write) membuat write sangat mahal

**TTL BREAKDOWN:**
- 1h: 99,9% (59.049.867 token)
- 5m: 0,1% (67.722 token)

Semua cache creation dari Claude Code menggunakan TTL 1-jam.

**Bukti:** `D:\AAAAAAAAA\open_source_agents\.here_we_are\bukti\T2_BUKTI.md`
**Perintah:** `cd D:\AAAAAAAAA\cbt_master && python t2_complete_analysis.py`

## B. Literatur — semua ID sudah dibuka dan dicocokkan judulnya

| temuan | sumber | jenis |
|---|---|---|
| Kompresi agresif memangkas token keluaran 38,4% tapi **menaikkan biaya tagihan 6,8%**; korelasi token-biaya r=0,15 | [arXiv:2607.12161](https://arxiv.org/abs/2607.12161) | terukur, 2.908 sesi bertagihan |
| Pada 75% konteks tersisa: keberhasilan 92,4-92,7% vs 93,8% penuh. Di 35% memencar tajam. Di bawah 25% rapuh | [arXiv:2608.01056](https://arxiv.org/abs/2608.01056) | terukur, 15.525 run |
| Indeks struktural mengungguli agentic-grep, tanpa penalti biaya | [arXiv:2606.22417](https://arxiv.org/abs/2606.22417) | terukur |
| Pemangkasan adaptif 23-54% sambil **menaikkan** keberhasilan — pakai model terlatih 0,6B, bukan regex | [arXiv:2601.16746](https://arxiv.org/abs/2601.16746) | terukur |
| Pembuangan naif konteks rencana memotong keberhasilan **34,7 poin persen** | [arXiv:2606.22953](https://arxiv.org/abs/2606.22953) | terukur |
| Berkas konteks (AGENTS.md) buatan LLM menurunkan performa 2-3%, tulisan pengembang menaikkan 4%, keduanya menaikkan biaya >20%. Saran: di bawah ~30 baris | [arXiv:2605.10039](https://arxiv.org/pdf/2605.10039) | terukur, 138 repo |
| Strategi injeksi konteks tidak menggerakkan kebenaran (batas 10-15pp) | [arXiv:2607.27250](https://arxiv.org/abs/2607.27250) | terukur, 288 run |
| 7 bentuk misalignment: pelanggaran batasan 38,33%, salah baca maksud 26,95%, pelaporan tidak akurat 22,58%. 91,49% penyelesaian tetap butuh koreksi pengguna | [arXiv:2605.29442](https://arxiv.org/abs/2605.29442) | terukur, 20.574 sesi |
| Agen bias optimistis soal anggaran di 20 dari 20 pasangan model-lingkungan | [arXiv:2606.00198](https://arxiv.org/html/2606.00198v1) | terukur |
| Tidak ada karya yang menunjukkan koreksi-diri berhasil dengan umpan balik dari LLM yang di-prompt | Kamoi dkk. TACL 2024, [arXiv:2406.01297](https://arxiv.org/pdf/2406.01297) | tinjauan kritis |
| Pengembang berhenti memakai alat statis di atas ~20% positif palsu; Google membidik ~5% efektif | Johnson dkk. ICSE 2013; Sadowski dkk. CACM 2018 | terukur |

### Kemampuan bawaan harness (dokumentasi primer)

- **Claude Code**: `Read` berhalaman dengan `offset`/`limit`, memberi notis
  `PARTIAL view`. Tidak ada tampilan kerangka bawaan — `LSP` ada tapi mati
  sampai plugin bahasa dipasang. `Grep` mengembalikan baris, bukan badan
  fungsi. Pemadatan otomatis membuang keluaran tool lebih dulu. Keluaran Bash
  dipotong per jumlah karakter (~30.000), bukan per isi.
- **aider**: repo map berbasis tree-sitter, anggaran 1.000 token — padanan
  terdekat `selective_reader`, sudah bawaan.
- **opencode**: LSP ada tapi di balik flag eksperimental.

Kesimpulan Bagian A dokumentasi: kemampuan kerangka-alih-alih-baca-penuh
**tidak** tersedia bawaan di Claude Code, tapi sudah matang di aider.

## C. Mekanisme sukarela tidak bertahan — empat arah, satu temuan

1. Seluruh lapisan `src/backend/services` cbt_master (2.805 baris, 20 penjaga,
   170 dari 260 kasus tes, komentar 28%) dibangun 12-17 Agustus dengan **nol**
   jejak pemakaian snowline. Jejak terakhir tool apa pun: 9 Agustus.
2. Agen mendiagnosis sebabnya sendiri 8 Agustus, mengulangi kesalahan yang
   sama enam hari kemudian. Rasio verifikasi:mutasi justru memburuk 3,5:1 -> 2,0:1.
3. Literatur: koreksi-diri tanpa umpan balik eksternal terverifikasi tidak
   bekerja.
4. Tidak ditemukan satu pun contoh toolkit agen pribadi yang bertahan sebagai
   alat pribadi penulisnya lewat enam bulan.

Penegakan yang mengikat di Claude Code hanya `PreToolUse` (keluar kode 2
memblokir). `PostToolUse` tidak bisa membatalkan apa pun — hanya mencatat.

## D. Sumbangan snowline atas alat yang sudah ada

20 perbaikan bug terakhir cbt_master dinilai satu per satu:
`scope_guardian` 0, `project_guardian` 0, `companion` 0, `impact_analyzer` 0,
`smart_search` 2 — dan keduanya ditemukan `grep` biasa dengan kueri yang sama.

Sumbangan bersih: **0 dari 20**.

Pengecualian jujur: `project_guardian` menemukan kunci API ter-commit dalam 30
detik yang terlewat oleh pembacaan manual 12 jam.

## E. Catatan tentang laporan Gemini 19 Agustus

Kesimpulannya tentang chamber sepakat dan sampai lewat jalan berbeda — itu
nilai utamanya. Tiga buktinya tidak bertahan saat diperiksa:

- Dua kutipan arXiv (2310.13568, 2401.03662) adalah makalah fisika benda
  terkondensasi dan persamaan diferensial stokastik. Tidak berhubungan.
- Klaim "14 dari 18 tool terbukti dipakai" membaca penyebutan sebagai
  eksekusi. `session_cache.json` hanya memuat `search` 57, `reader` 4,
  `guardian` 1.
- "292 KB 100% birokrasi vs 0% output" mengukur hal yang salah: folder
  koordinasi memang tidak dimaksudkan memuat kode produksi. Ukuran yang benar:
  agen menulis 398.589 karakter ke agents_chamber vs 479.155 ke src/.
