# PM -> TL: Sprint 27 — dua perbaikan aturan

Keduanya kecil dan tidak bergantung satu sama lain.
## Enam cacat, urut dari yang paling merusak

### Entri 28 — guardian memblokir seluruh commit di proyek Firebase

Bukti lengkap ada di vonis tepat di atas. Ringkasnya: 8 CRITICAL di
`pengingat_oli`, kedelapannya kunci konfigurasi Firebase yang memang publik,
dan hook menggerbangkan commit pada `critical > 0`.

**Syarat lulus:**
1. Di `pengingat_oli`, CRITICAL dari berkas konfigurasi Firebase hilang.
2. Kunci `AIza` yang ditanam di berkas biasa **tetap** CRITICAL. Buktikan
   dua arah — ini yang paling penting.
3. Uji, dibuktikan mutasi.

Jangan mematikan pola `AIza` seluruhnya.

### Entri 29 — `close-entry` memaku `.here_we_are`

```
core_close_entry.py:7-11    Path(".here_we_are")
```

Tidak jalan di proyek yang memasang chamber ke `.agents/chamber/`.
`core_context.py:8-9` sudah benar memeriksa dua lokasi. Tiru itu.

**Syarat lulus:** jalankan di `pengingat_oli` dan tempel keluarannya.

### Entri 30 — impor bayangan, sepuluh titik

Empat di dalam fungsi gerbang, dan satu sudah aktif merusak:

```
$ replace_text.py ... --apply     # role.json = QA
UnboundLocalError: cannot access local variable 'sys'
[BLOCKED] Akses tulis (--apply) ditolak untuk role QA.
```

**Syarat lulus:**
1. Kesepuluh dicabut.
2. Keluaran kunci peran bersih — satu baris `[BLOCKED]`, tanpa traceback.
3. Uji `role_lock` diperluas: keluaran tidak boleh memuat `Traceback` atau
   `UnboundLocalError`.

### Entri 31 — `test-clone` mengandaikan tata letak snowline

```
proyek tanpa tests/run_tests.py  ->  [FAIL] Skrip tes tidak ditemukan
proyek non-git                   ->  [FAIL] bukan repositori Git
```

Keduanya bukan kegagalan; keduanya keadaan wajar di proyek orang.

**Syarat lulus:** terima `--cmd "npm test"`, atau deteksi otomatis. Proyek yang
tidak punya uji dilaporkan sebagai `[INFO] tidak ada uji terdeteksi`, bukan
`[FAIL]`.

### Entri 32 — `.dart_tool`, `.gradle`, `.pub-cache`, `Pods` belum dikecualikan

Artefak build dilaporkan "tidak dipindai, terlalu besar".

### Entri 33 — `STATE.md` yang dikirim masih berjudul `# KEADAAN`

Sekalian sisir templat chamber lain untuk sisa rename yang sama.
