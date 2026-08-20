# 17_PROTOTYPE_RISK_MITIGATION.md — Blueprint Mitigasi Risiko (The Iron Patch)

Disusun 20 Agustus 2026. Mencatat mekanisme pertahanan tambahan (The Iron Patch) untuk mengamankan kelemahan operasional dari Automated Chamber 2.0.

Penerapan AI otonom di dunia nyata memiliki risiko inherent. Berdasarkan evaluasi brutal terhadap arsitektur Snowline V2, kita telah menetapkan 4 protokol mitigasi wajib sebelum sistem ini dirilis ke produksi:

## 1. Protokol HITL Fallback (Melawan Halusinasi Reviewer)
- **Risiko:** Sub-Agen *Reviewer* (LLM) menolak kode yang sebenarnya sudah berjalan sempurna secara mesin, memicu *Rollback* sia-sia.
- **Mitigasi:** Jika Executor berhasil melewati **Gate 1 (Sintaks)** dan **Gate 2 (Unit Test Mesin)**, namun di-veto oleh **Gate 3 (Reviewer LLM)**, Orkestrator TIDAK akan memicu *Git Rollback*. Orkestrator akan menangguhkan proses dan memicu *Human-in-the-Loop* (HITL) *Fallback*—mengirimkan log peringatan kepada Manusia untuk memvalidasi apakah sang Reviewer sedang berhalusinasi atau memang benar.

## 2. Injeksi Impact Analyzer (Melawan Tunnel Vision)
- **Risiko:** Isolasi folder Sub-Agen membuat Executor buta terhadap gambaran makro, berisiko merusak dependensi file lain.
- **Mitigasi:** Tepat sebelum *System Prompt* Executor dikirim, Orkestrator wajib menjalankan *skill* `impact_analyzer` pada file target. Hasilnya disuntikkan secara dinamis: *"PERINGATAN: File target ini diimpor oleh A, B, dan C. Jangan ubah struktur return-nya!"*. Ini memberikan kewaspadaan global tanpa membebani *context window* dengan RAG.

## 3. Asymmetric Routing (Melawan High Latency)
- **Risiko:** Menjalankan birokrasi *Investigator ➔ Executor ➔ QA* memakan waktu >30 detik per tugas.
- **Mitigasi:** *Companion Router* tidak boleh bersikap demokratis. 80% dari kueri harian (misal: "tambahkan komentar", "cari fungsi X") **HARUS** dipaksa masuk ke rute `SOLO_AGENT` yang mengeksekusi secara instan. Birokrasi Chamber hanya dibangkitkan untuk tugas yang mengandung modifikasi logika lintas-file atau perbaikan bug kritis.

## 4. Smart Reflexion Retry (Melawan Rollback Trap)
- **Risiko:** Agen mengulangi kesalahan yang persis sama 3 kali berturut-turut, membakar kuota token API sia-sia.
- **Mitigasi:** Ketika agen ditolak oleh Gate QA, ia dilarang langsung melakukan *retry*. Agen wajib melalui *node* **Reflexion**. Ia harus membaca *Error Log* dan menulis *"Lesson Learned"* (Apa yang salah, dan apa yang HARUS dihindari di percobaan selanjutnya). *Prompt* di percobaan kedua akan dibubuhi "Catatan Tobat" ini, meroketkan peluang sukses agen hingga 90% dan menghindari *infinite loop* bodoh.

## Kesimpulan
Keempat pelat baja (*Iron Patch*) ini menambal kelemahan fatal arsitektur agen LLM modern. Dengan ini, Snowline V2 resmi menjadi kerangka kerja *Enterprise-Grade* yang tidak hanya indah secara teori, namun juga tangguh menghadapi kerasnya anomali dunia nyata.
