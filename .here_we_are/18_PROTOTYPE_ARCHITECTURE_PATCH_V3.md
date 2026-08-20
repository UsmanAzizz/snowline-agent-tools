# 18_PROTOTYPE_ARCHITECTURE_PATCH_V3.md — Blueprint Penambalan SPOF (Patch V3)

Disusun 20 Agustus 2026. Mencatat solusi teknis untuk 4 titik kegagalan tunggal (Single Points of Failure - SPOF) yang ditemukan melalui audit arsitektural yang brutal.

## 1. Cyclic State Graph (Anti-Jebakan Satu Arah)
- **Varian Lama:** Investigator ➔ Executor ➔ QA ➔ (Gagal) ➔ Executor.
  - Kelemahan: Jika Investigator salah mendiagnosis letak *bug*, Executor terjebak mengedit file yang salah selamanya.
- **Varian V3:** Investigator ➔ Executor ➔ QA ➔ (Gagal) ➔ **Investigator**.
  - Solusi: Laporan *error* dari QA dikembalikan ke hulu (Investigator). Investigator dipaksa mengevaluasi ulang *error* tersebut, mengkoreksi *Handoff Context*, lalu menugaskan ulang Executor. Ini adalah siklus perbaikan sejati (*True Self-Correction Loop*).

## 2. Global State "Bulletin Board" (Anti-Isolasi Total)
- **Varian Lama:** Sub-Agen memiliki folder histori terisolasi (`memory/executor`, `memory/auditor`).
  - Kelemahan: Jika Auditor memodifikasi dependensi *global*, Executor tidak sadar dan *environment*-nya tidak sinkron.
- **Varian V3:** 
  - Solusi: Mempertahankan folder terisolasi untuk tugas harian. Namun, ditambahkan satu file `.agents/global_state.md`. Setiap perubahan pada `package.json`, `.gitignore`, atau `.env` wajib disiarkan ke papan ini. Semua sub-agen wajib membaca `global_state.md` sebelum bekerja. Ini mengawinkan prinsip *Zero-Bloat* dengan *Global Awareness*.

## 3. Native Linter Guardian (Kesesuaian Framework Modern)
- **Varian Lama:** *Syntax Guardian* menggunakan `node --check` atau Python `ast`.
  - Kelemahan: Langsung *crash* ketika membaca sintaks modern seperti React `.jsx` atau TypeScript `.tsx`.
- **Varian V3:** 
  - Solusi: *Syntax Guardian* mendelegasikan pengecekan ke *Linter* asli proyek (*ESLint* atau *TSC*). Orkestrator hanya membaca hasil keluarannya (`exit code 0/1`).

## 4. Deep Clean Rollback (Penyucian Total)
- **Varian Lama:** `git reset --hard HEAD`.
  - Kelemahan: File baru yang diciptakan agen (*untracked files*) tidak terhapus. Folder *cache* atau `node_modules` tetap berantakan.
- **Varian V3:**
  - Solusi: Orkestrator memanggil `git reset --hard HEAD` diikuti oleh `git clean -fd`. Ini memastikan repositori disucikan 100% dari noda agen, menjamin kondisi *environment* yang sama persis seperti sebelum eksekusi dimulai.

## Kesimpulan
Tambalan V3 ini adalah pengakuan atas kelemahan arsitektur statis dan bukti komitmen terhadap prinsip rekayasa perangkat lunak yang tangguh (Resilient Software Engineering). Celah teoretis terakhir telah ditutup.
