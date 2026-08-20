# SPRINT 10: Dogfooding (Refaktor Produksi V2)

**Tanggal:** 20 Agustus 2026
**Fokus:** Membuktikan bahwa ekosistem Orchestrator V2 (Dual-Agent + Guardian) mampu merefaktor dirinya sendiri (Dogfooding) secara otonom tanpa merusak rantai komandonya sendiri.

## 1. Pertanyaan & Hipotesis
**Pertanyaan:** Bisakah sekelompok agen AI merefaktor repositori tempat mereka sendiri dieksekusi, menyatukan 3 modul independen (`snowline_toolkit`, `orchestrator`, `agents_chamber`) ke dalam satu _package_ `src/snowline`, tanpa memutus _path_ internal yang membuat mereka mati mendadak?
**Hipotesis:** Ya, dengan adanya perlindungan C2 (Rollback Git) dan C4 (Anti-Stalemate Loop), agen akan mampu menyelesaikan refaktor ini, dan agen Hakim (QA) akan berhasil mendeteksi jika agen Pekerja merusak fungsi dasar *import*.

## 2. Ambang Batas (Threshold) & Kriteria Sukses
1. **Keberhasilan Fungsional (0 Error):** Setelah agen selesai, menjalankan perintah `python -m snowline.orchestrator.orchestrator` tidak boleh menghasilkan `ModuleNotFoundError` atau `ImportError`.
2. **Kemandirian (No Human Intervention):** Refaktor harus mencapai status `QA_PASS` dari agen Pihak Kedua (Hakim) tanpa intervensi manual (pengeditan _path_ manual) dari manusia di tengah proses.
3. **Penyatuan Paket (100%):** File `setup.py` harus berhasil menginstal seluruh komponen (termasuk orchestrator) ketika `pip install .` dijalankan.

## 3. Syarat Berhenti (Stopping Conditions)
Sprint dihentikan dan dianggap **GAGAL** jika:
- Terjadi *infinite loop* halusinasi di mana Orchestrator V2 memicu batas `MAX_CONSECUTIVE_REPEATS` (3 kali berturut-turut).
- Agen QA (Pihak Kedua) memvonis `QA_REJECT` lebih dari 3 kali berturut-turut untuk isu yang sama (artinya agen Pekerja tidak mampu memperbaiki *bug* _path_ yang ia buat sendiri).
- Refaktor menghapus atau merusak Git Hook Guardian secara permanen.

## 4. Tugas untuk Konektor (`.agents/agents_connector.md`)
*(Ini akan diumpankan ke Orchestrator V2 untuk dieksekusi)*

**Tugas Utama:**
"Refaktor struktur repositori `open_source_agents` ini menjadi *Single Python Package* berstandar produksi.
1. Pindahkan `snowline_toolkit/`, `orchestrator/`, dan `agents_chamber/` ke dalam hierarki baru: `src/snowline/`.
2. Ubah semua referensi path statis absolut di dalam file Python (terutama `orchestrator.py` dan `cli.py`) menggunakan `__file__` relatif atau `importlib`.
3. Perbarui `setup.py` agar mendaftarkan `snowline` sebagai paket utamanya (bukan lagi `snowline_toolkit`).
Tugas dianggap selesai hanya jika paket bisa di-_import_ tanpa *error*."

---
*(Dokumen persiapan ini menunggu persetujuan PM sebelum konektor dijalankan)*
