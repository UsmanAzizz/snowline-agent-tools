# Antigravity Insights (Side Quest Data)

Folder ini berisi kumpulan data mentah dan sintesis arsitektur yang dikumpulkan oleh agen *Antigravity* melalui serangkaian *Side Quest* mandiri (menggunakan *Subagents* lintas web) di luar metrik utama sprint ablasi.

> [!WARNING]
> **Status: SUDAH DITINJAU (Claude Code, 20-08). Bukan peta jalan.**
> Isi folder ini turun status menjadi **petunjuk yang belum diverifikasi**.
> Jangan diimplementasikan. Satu benang diangkat ke papan tugas (lihat T7);
> sisanya dibiarkan sebagai bahan, bukan keputusan.

## Hasil tinjauan — 20 Agustus 2026

Penilaian awal saya keliru dan saya betulkan di sini: dinilai dari nama
berkasnya, folder ini terkesan bertele-tele. Ternyata 308 baris untuk 12
berkas — padat, dan statusnya ditandai jujur oleh penulisnya sendiri.

### Yang BERTENTANGAN dengan hasil ukur — jangan dipakai

**`03_PRE_REQUIREMENT_ANALYSIS.md`** menyebut dirinya berdasar "sprint evaluasi
T0-T6", lalu menyebut perkakas yang ada sebagai *"aset teruji, lolos uji
tekanan"*.

Sprint yang sama mengukur kebalikannya:
- 11 dari 23 perkakas tanpa bukti pernah dijalankan di luar tesnya sendiri
- Sumbangan atas 20 perbaikan bug terakhir `cbt_master`: **0 dari 20**
- Seluruh lapisan `src/backend/services` dibangun tanpa satu pun jejak pemakaian

**`04_V2_ROADMAP.md`** berdiri di atas premis yang sama. Peta jalannya tidak
batal karena salah tulis — landasannya yang gugur.

### Yang BELUM BERUJUKAN — verifikasi dulu sebelum dikutip

- **`07`** memakai "Gemini 1.5 Pro dan Claude 3.5 Sonnet" sebagai dasar angka
  degradasi atensi. Dua generasi tertinggal; angkanya belum tentu berlaku.
- **`09`** menyebut "Devin dan SWE-agent gagal >70% pada kasus GitHub nyata"
  tanpa rujukan dan tanpa tanggal. Angka SWE-bench bergerak cepat.

Keduanya sekelas dengan dua kutipan arXiv 19-08 yang ternyata makalah fisika:
terdengar meyakinkan, belum ditelusuri. Aturan 2 di `../README.md` berlaku.

### Yang DIANGKAT — satu, ke papan tugas sebagai T7

**`02_GUERRILLA_TACTICS.md` bagian 1 (eksploitasi cache).** Ini satu-satunya
bagian yang menunjuk ke angka terukur: cache menghemat 85,5% biaya sesi, dan
98% token masukan adalah cache read. Lihat `../01_TEMUAN.md` bagian A2.

Dua koreksi atas isinya sebelum dipakai:
- "100% menghancurkan cache" berlebihan. Cache batal **dari titik perbedaan ke
  belakang**, bukan seluruhnya.
- Klaim mekanisme cache di situ belum punya rujukan ke dokumentasi primer.

### Sisanya

`01`, `05`, `06`, `08`, `10`, `11` tidak ditinjau butir per butir dan tidak
diapa-apakan. Bukan disetujui, bukan ditolak — dibiarkan sebagai bahan.

## Daftar Isi
1. **[01_ORCHESTRATOR_LOOPHOLES.md](./01_ORCHESTRATOR_LOOPHOLES.md)**: Analisis kelemahan fatal (loopholes) pada orkestrator raksasa (AutoGen, CrewAI, LangGraph, OpenHands, Aider).
2. **[02_GUERRILLA_TACTICS.md](./02_GUERRILLA_TACTICS.md)**: Usulan cetak biru tingkat rendah (*low-level*) untuk mengeksploitasi *Prompt Caching*, mendesain *Delta Firewall*, dan memanfaatkan penganalisis statis murni.
