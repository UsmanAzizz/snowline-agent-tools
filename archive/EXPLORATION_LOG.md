# Exploration Log — Celah Ditemukan, Belum Dikerjakan

Format tiap entri:
- **Tanggal:**
- **Celah ditemukan:**
- **Ditemukan saat:** (task apa yang sedang dikerjakan)
- **Prioritas:** (Low/Medium/High — High hanya untuk isu keamanan)
- **Status:** Belum dikerjakan / Menunggu keputusan user

---

- **Tanggal:** 2026-07-30
- **Celah ditemukan:** Regresi companion/approval flow
- **Ditemukan saat:** Audit rutin
- **Masalah:** Companion hasil --apply langsung di params_map, tidak tanya approval dulu
- **Akar:** __init__.py tidak mengekspos needs_approval() dan build_execution_command() dengan benar
- **Fix diterapkan:** 3771242
- **Prioritas:** High (security-relevant)
- **Status:** Fixed

---

- **Tanggal:** 2026-07-30
- **Celah ditemukan:** Tidak ada regression test otomatis untuk companion flow
- **Ditemukan saat:** Regresi yang kedua kalinya
- **Masalah:** Perbaikan bisa revert tanpa terlihat
- **Saran:** Butuh automated test untuk approval flow
- **Prioritas:** Medium
- **Status:** Simple test (tests/test_approval.py) sudah ada

---

- **Tanggal:** 2026-07-30
- **Celah ditemukan:** Full regression suite
- **Ditemukan saat:** Regression detection
- **Masalah:** tests/test_approval.py baru cek 2 hal saja. Ide untuk test suite lengkap:
  - Test semua tool routing (smart_search, project_guardian, dll)
  - Test edge cases (keyword matching)
  - Test cache expiry
  - Test approval flow end-to-end genuine (bukan simulasi satu script)
- **Prioritas:** Low
- **Status:** Simpan ide ini di sini sampai ada demand aktual
- **Catatan:** Tests kecil yang sering jalan lebih baik dari test besar yang jarang jalan. Start small.
- **Status:** Belum dikerjakan
