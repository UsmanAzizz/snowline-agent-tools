# Task 64 - Audit Final Task 63 (Guardian Cache Invalidation & Template Sync)

*Diarsipkan oleh: `pos/2. QA` (Opus 4.8 / Claude Code), 05 Agustus 2026*
*Sesuai SOP `shared/archive/README.md`. Status: DONE - verdict QA PASS, Task 7.3 & 63 ditutup TL.*

---

## INBOX (instruksi asli dari TL)

**[Tech Lead Assignment] - Task 64: Audit Final Task 63**

Konteks: Sesuai Rule #11 (Mandatory QA Validation) yang baru ditetapkan, TL tidak lagi berhak menutup task secara sepihak. Task 63 yang dilaporkan selesai oleh Executor harus diaudit QA sebelum diresmikan DONE.

Tindakan Executor_01 di Task 63 yang perlu diverifikasi:
1. Menyisipkan `guardian_hash = hashlib.md5(open(__file__,'rb').read()).hexdigest()` ke perhitungan cache `dir_sig`.
2. Mengganti filter `if file == 'guardian.py'` menjadi filter path-based.
3. Mengopi perubahan ke `snowline_toolkit/templates/...` dan `project_guardian/...`.

Misi QA: (1) verifikasi versi aktif dan template benar-benar identik + cache invalidation bekerja, (2) uji regresi false positive, (3) beri keputusan akhir.

---

## OUTBOX - VERDICT: **PASS**

### 1. Sinkronisasi 3 salinan - PASS, identik byte per byte
```
6edf8d03d3cb300bc0dce8fa4ba21113 20408 project_guardian/guardian.py
6edf8d03d3cb300bc0dce8fa4ba21113 20408 snowline_toolkit/templates/project_guardian/guardian.py
6edf8d03d3cb300bc0dce8fa4ba21113 20408 .agents/skills/project_guardian/guardian.py
IDENTIK SEMUA? YA
```

### 2. Cache invalidation - PASS, diuji 4 langkah dua arah

Rancangan uji: guardian ditaruh DI LUAR folder target supaya mtime-nya tidak ikut masuk `dir_sig`. Nama file dijaga tetap sama supaya meniru "guardian diperbarui", bukan "file baru". Target `leak.py` (berisi Google + AWS key palsu) tidak disentuh sepanjang 4 langkah.

```
LANGKAH 1: guardian versi BARU (punya pola Google)
[CRITICAL] leak.py:1 - Google API Key
[CRITICAL] leak.py:2 - AWS Access Key
-> cache tertulis di .agents/session_cache.json

LANGKAH 2: guardian DIPERBARUI (pola Google dinonaktifkan), leak.py TIDAK disentuh
[CRITICAL] leak.py:2 - AWS Access Key
-> Google HILANG. Scan ulang, cache lama tidak dipakai.

LANGKAH 3: dikembalikan ke versi BARU
[CRITICAL] leak.py:1 - Google API Key
[CRITICAL] leak.py:2 - AWS Access Key
-> invalidate lagi, hasil kembali benar.

LANGKAH 4: dijalankan lagi tanpa mengubah apapun
[CRITICAL] leak.py:1 - Google API Key
[CRITICAL] leak.py:2 - AWS Access Key
-> hasil sama, cache dipakai sebagaimana mestinya.
```
Langkah 2-3 membuktikan cache di-invalidate saat guardian berubah. Langkah 4 membuktikan cache TETAP dipakai saat tidak ada perubahan - perbaikan ini tidak mengorbankan fungsi cache.

Implementasi di `guardian.py:41-46`:
```python
    # Include guardian.py source hash to invalidate cache when the tool itself changes
    try:
        guardian_hash = hashlib.md5(open(__file__, 'rb').read()).hexdigest()
        mtimes.append(guardian_hash)
    except Exception:
        pass
```

### 3. Regresi false positive - PASS
Baseline repo tetap 2 CRITICAL (keduanya dari `SKILL.md`), sama dengan hasil Task 62. Live-test 4 kasus:
```
[CRITICAL] scratch\task64_regresi.py:7  - Google API Key
[CRITICAL] scratch\task64_regresi.py:10 - AWS Access Key
[CRITICAL] scratch\task64_regresi.py:17 - Bearer token
```
Kontrol negatif (komentar `# Bearer token` dan `# Authorization: Bearer abc` di baris 13-15) TIDAK dilaporkan - false positive tetap hilang.

### 4. Filter path-based - PASS, lebih presisi dari yang diminta
`guardian.py:69-73` hanya melewati file `guardian.py` yang berada di dalam folder `project_guardian`, bukan mengecualikan seluruh folder. Terbukti: `SKILL.md` tetap di-scan. File bernama `guardian.py` milik user di lokasi lain kini tetap diperiksa.

### Catatan - bukan penghalang
1. `except Exception: pass` (baris 45-46): kalau `open(__file__)` gagal, `guardian_hash` tidak jadi ditambahkan dan cache kembali berperilaku seperti versi lama, tanpa peringatan. Mekanisme keamanan yang gagal diam-diam. Saran ringan: cetak `[WARN]` di blok except.
2. `open(__file__,'rb')` tidak memakai `with` - tidak ada bug nyata di CPython, hanya tidak rapi.
3. Salinan `guardian.py` di luar folder `project_guardian` akan dilaporkan CRITICAL (regex-nya sendiri terbaca sebagai secret). Konsekuensi wajar dari filter path-based; lebih baik over-report daripada membuat celah berbasis nama.

**Kebersihan:** seluruh artefak uji (`scratch/task64_target/`, `scratch/task64_tools/`, `scratch/task64_regresi.py`) sudah dihapus dan diverifikasi nihil. Repo kembali ke baseline 2 CRITICAL.

---

## Riwayat verifikasi QA sebelumnya (dipulihkan dari ARCHIVE connector yang terhapus)

- **[Task 62]** Audit ulang remediasi Task 61: false positive 18 -> 2. Menemukan 2 penghalang: perbaikan tidak sampai ke template installer, dan cache guardian tidak memperhitungkan versi guardian. Keduanya jadi Task 63.
- **[Task 59]** Audit Task 7.3: FAIL. Aturan Mandatory Halt tidak sinkron di 3 salinan; `.agents/agents.md` tidak punya aturannya sama sekali. Menemukan guardian mendeteksi lewat nama variabel, bukan bentuk key.
- **[Task 52]** Verifikasi reset chamber: reset bersih. Menemukan verdict QA di-prefill sebelum QA memeriksa (kemudian jadi Rule #9), nomor task didaur ulang, dan API key hidup di `scratch/real_grader.py`.
- **[Task 50 & 51]** Desain `_plan` Convention & Grill-First: APPROVED WITH REVISION (ganti intercept `startswith` jadi substring `in`).
- **[Task 48]** Verifikasi eksekusi JSX Slash & Governance v2.1: VERIFIED & PASSED.
- **[Task 44]** Verifikasi splicer.py indentation fallback: VERIFIED & PASSED -> `task_44_splicer_fallback.md`
- **[Task 43]** Verifikasi chamber optimization: VERIFIED & PASSED -> `task_43_verify_chamber.md`
- **[Task 42]** Evaluasi 3 konsep optimasi chamber: setuju Decentralized Archiving & Ledger, tolak Semaphores.
- **[Task 41]** Review blueprint Surgical Code Splicer: mandat Pure Copy-Paste over Shared Module -> `task_41_splicer.md`
- **[Task 40]** Evaluasi 3 konsep arsitektur: Option 2 (Splicer) prioritas, 1 & 3 ditolak karena risiko false positive.
- **[Task 39]** Uji independen implementasi `--depth`: VERIFIED & PASSED.
