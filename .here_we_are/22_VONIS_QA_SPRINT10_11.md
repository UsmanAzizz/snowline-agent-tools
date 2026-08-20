# Vonis QA — Sprint 10 & 11

Diperiksa 20 Agustus 2026 ke kode, bukan ke laporannya.

## VONIS: Sprint 10 PASS. Sprint 11 REJECT.

Dan ada satu kehilangan yang perlu dibaca lebih dulu daripada keduanya.

---

# KEHILANGAN — pekerjaan Sprint 9 yang sudah lulus, hilang

Sprint 9 menghasilkan `orchestrator.py` 233 baris yang QA verifikasi dan
luluskan: privacy flag *fail-closed*, loop detector SHA-256, dual-agent
`QA_REVIEW`/`QA_REJECT`, dan `git clean -fd`.

Berkas itu **tidak pernah di-commit**. Perombakan Sprint 10/11 menimpanya.

**Yang ada di git (HEAD), versi pra-Sprint-9, 154 baris:**

```
PRIVACY_FLAG    0
sha256          0
QA_REJECT       0
taskkill        3   <- sudah ada sebelum Sprint 9
```

**Yang ada di disk sekarang, `src/snowline/chamber/orchestrator.py`, 160 baris:**

```
PRIVACY_FLAG        2      automation_granted  1
check_loop          1      QA_REVIEW           2
sha256              0      QA_REJECT           0
taskkill            0      git clean           0
subprocess          0
```

Versi 233 baris itu tidak ada di git dan tidak ada di disk. **Hilang.**

Yang tersisa hanya nama-namanya: `check_loop` ada tanpa `sha256`, `QA_REVIEW`
ada tanpa `QA_REJECT`. Separuh mekanisme, tanpa separuh yang membuatnya bekerja.

QA menyampaikan risiko ini dua giliran sebelum perombakan: *"Kalau `git checkout`
terjadi lagi seperti pagi tadi, vonisnya selamat dan kodenya hilang."* Yang
terjadi bukan `checkout`, melainkan penimpaan — akibatnya sama.

---

# Sprint 10 — Pematangan Package: PASS

Tiga klaim diperiksa, tiga-tiganya berdiri.

**Struktur `src/snowline/` ada**, dengan `pyproject.toml` yang benar:

```toml
[tool.setuptools.packages.find]
where = ["src"]
```

**Impor bekerja** — diuji, bukan dibaca:

```
$ python -c "import sys; sys.path.insert(0,'src'); import snowline.cli"
impor OK
```

**Jalur absolut hilang dari `src/`:**

```
$ grep -rln 'D:\\' --include=*.py src/
(kosong)
```

Ini menyelesaikan keberatan QA di Sprint 9 tentang `AGENT_PROJECT` yang dipaku.

**Dan tidak ada yang dihancurkan pada bagian yang diklaim:**

```
src/snowline/templates/rules/   bootstrapping_safety, communication,
                                guardrail_compliance, plan_first,
                                scope_guardian, session_control   -> pindah, utuh
archive/PROJECT_CONTEXT.md      -> pindah, utuh
archive/CURRENT_STATE.md        -> pindah, utuh
```

Berkas yang tampak terhapus di `git status` sebenarnya berpindah, bukan hilang.

---

# Sprint 11 — Chamber Orchestrator V3: REJECT

## Alasan tunggal: *service worker* paralelnya tidak memanggil apa pun

`src/snowline/chamber/orchestrator.py:77-84`

```python
async def dispatch_service_worker(self, role, prompt):
    ...
    await asyncio.sleep(2)  # Simulasi network call
```

`asyncio.gather` di `:100` benar, `class ChamberOrchestrator` di `:28` benar,
`import asyncio` di `:16` benar. Strukturnya nyata.

Tetapi pekerjanya **tidur dua detik lalu kembali.** Dan seluruh berkas tidak
memuat satu pun `subprocess` — jadi ia tidak bisa memanggil `claude`, tidak bisa
menjalankan `git`, tidak bisa mengeksekusi apa pun.

Laporan menyatakan ini menyelesaikan masalah nyata: *"memakan waktu 20 menit,
membuang kuota API, dan rawan macet (Error 429)."* Sesuatu yang tidak memanggil
API tidak menyelesaikan masalah kuota API — ia meniadakan pemanggilannya.

Ini kerangka, dan kerangka itu sah sebagai purwarupa. Yang tidak sah adalah
melaporkannya sebagai perombakan yang sudah menggantikan eksekusi serial.

## Klaim "tidak menghancurkan satu pun SOP maupun Skill.md"

Benar untuk `SKILL.md` dan `rules/` — keduanya berpindah utuh.

Tidak benar untuk orchestrator. Empat dari lima fitur yang QA luluskan di
Sprint 9 tidak ada lagi di mana pun.

---

## Catatan: duplikasi `SKILL.md` bertambah

```
$ find . -name "SKILL.md" | sed 's|/[^/]*$||' | ... | sort | uniq -c
  16  ./src/snowline/templates
  16  ./archive
  15  ./.agents/skills
  14  ./scratch/test2/.agents/skills
  14  ./scratch/test1/.agents/skills
  14  ./.venv/.../snowline_toolkit/templates
```

Di HEAD ada 32 `SKILL.md` terlacak; di disk sekarang 90. Rule #12 (Anti-Drift)
mengandaikan dua salinan — sumber dan templat. Sekarang ada enam pohon.
`archive/` dan `scratch/` mungkin memang tidak perlu ikut disinkronkan, tetapi
itu belum dinyatakan di mana pun.

---

# Syarat untuk PASS

1. **Commit dulu, sebelum apa pun.** 116 berkas belum ter-commit, dan
   perombakan ini sudah memakan satu pekerjaan yang lulus verifikasi.
2. **Pulihkan fitur Sprint 9 ke orchestrator baru** — privacy flag sudah ada,
   tetapi SHA-256, `QA_REJECT`, `taskkill`, dan `git clean -fd` perlu ditulis
   ulang. Tidak ada sumber untuk menyalinnya; hanya vonis QA di
   `21_VONIS_QA_SPRINT9.md` yang mencatat nomor barisnya dulu.
3. **`dispatch_service_worker` benar-benar memanggil**, atau laporannya
   dinyatakan sebagai purwarupa.

---

## Yang layak berdiri

Sprint 10 mengerjakan hal yang benar dan mengerjakannya dengan bersih. Struktur
package, resolusi relatif, dan pemindahan arsip semuanya rapi dan terverifikasi.
Keberatan QA tentang jalur yang dipaku — dua kali disampaikan — akhirnya selesai
sepenuhnya di sprint ini.
