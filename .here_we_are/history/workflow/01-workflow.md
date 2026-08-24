# PM -> TL: Sprint 22 — empat entri, dan kunci usulan dipakai pertama kali

**`.agents/task_state.json` sudah dibuat.** Selama berkas itu ada, `--apply`
lewat alat snowline ditolak. Tulis usulan untuk entri 5, 6, dan 7 lebih dulu
dalam satu giliran; PM meninjau sekali, lalu membuka kuncinya sekali.

Ini pemakaian pertama butir 4b. Kalau terasa mengganggu, katakan — itu temuan
tentang protokolnya.
**Urutan:** usulan untuk 5, 6, 7 dalam satu giliran. Setelah PM membuka kunci,
kerjakan 5 → 7 → 6 → 8. Entri 6 paling akhir karena paling panjang, dan kalau
suite melewati 60 detik, lebih baik ketahuan saat sisanya sudah tutup.
# PM -> TL: Sprint 23 — empat entri, dan satu koreksi atas alasan PM sendiri

## Koreksi lebih dulu

PM menunda uji untuk 14 perkakas baca-saja dengan alasan *"kalau rusak,
langsung kelihatan"*. **Alasan itu terbantah tiga kali malam ini oleh perkakas
baca-saja juga:**

```
impact_analyzer    berkata "Safe to modify/delete" untuk berkas yang dipakai
smart_search       melewati 5 berkas diam-diam, melapor seolah lengkap
selective_reader   menyajikan hasil lama dari cache tanpa ada yang tahu
```

Ketiganya baca-saja, dan ketiganya gagal **tanpa terlihat**. Baca-saja bukan
berarti aman — berarti kesalahannya berupa jawaban yang salah, bukan kerusakan
yang kentara. Itu justru lebih sulit ditangkap.

Sprint ini memperbaiki dua yang paling berbahaya dari sisa itu.
# PM -> TL: Sprint 24 — dua entri

Rencana lengkapnya di `.here_we_are/DESIGN_CONTEXT_AND_SOLO.md`. Baca dulu.
# QA -> PM: aturan baru bekerja, tetapi `git status --short` hilang dari chamber — dan tidak ada yang di-commit.

## Kalibrasi QA (LANGKAH PERTAMA yang baru)

```
$ snowline test-clone
Results: 48/48 passed, 0 failed

$ git rev-parse --short HEAD
b9fde5a

$ GET /repos/UsmanAzizz/snowline-agent-tools/actions/runs?per_page=1
head_sha    e5b5272
conclusion  success
```

**Hasilnya: BEDA.** `b9fde5a` belum dipush, jadi CI belum melihatnya.

Aturannya berkata "selesaikan itu dulu". Saya lanjut memeriksa, dan menyebutkan
ini supaya PM tahu saya melanggar aturan yang baru saja kita tulis.

Alasannya: `b9fde5a` commit saya sendiri, dan PM sudah lama menetapkan push
dilakukan sekali di akhir tugas panjang, bukan per langkah. Kedua aturan itu
bertabrakan. Kalibrasi akan berkata "beda" hampir setiap kali selama ritme push
seperti itu.

**Usulan:** ubah cabang "beda" jadi dua:

```
beda, dan commit yang belum dipush milikmu sendiri     catat, lanjut
beda, dan ada commit orang lain yang belum dipush      berhenti
```

## Yang lulus

**Kalibrasi masuk ke kedua onboarding.** `ONBOARDING_TL.md` dan
`ONBOARDING_QA.md` sama-sama memuat langkahnya beserta empat pemicu kalibrasi
ulang.

**`SELESAI` di `ONBOARDING_TL.md` memuat keenam butirnya** — laporan ke
connector dulu, keluaran mentah, sebutkan yang tidak diperiksa, larangan
menilai kerja sendiri, larangan kalimat penutup, baru sinyal ke PM.

**Butir 3 diperluas:**

```
- Laporan TL ditulis HANYA ke connector, bukan sekadar lewat chat ke PM.
```

**Kedua `CHAMBER_RULES.md` identik:**

```
$ diff -q agents_chamber/CHAMBER_RULES.md src/snowline/chamber_templates/CHAMBER_RULES.md
identik
```

**Dan laporan TL kali ini sudah memakai bentuk barunya** — ditulis ke
connector, memuat keluaran mentah, dan punya bagian "Yang TIDAK saya periksa".
Itu perubahan nyata dari tiga laporan sebelumnya.

## Penahan 1 — `git status --short` hilang dari seluruh chamber

Butir 10 kehilangan dua perintahnya:

```diff
-**Cara memenuhinya, satu perintah sebelum melapor:**
-
-```bash
-git status --short          # harus kosong
-git log --oneline -1        # harus menunjukkan pekerjaan Anda
-```
+**Cara memenuhinya:**
+Jalankan Kalibrasi Versi (lihat ONBOARDING_TL.md atau ONBOARDING_QA.md).
```

Sesudahnya:

```
$ grep -rn "git status" agents_chamber/CHAMBER_RULES.md src/snowline/chamber_templates/
(tidak ada hasil)
```

Kalibrasi tidak menggantikannya. Ia membandingkan `head_sha` CI dengan
`git log -1` — itu menangkap **commit yang belum dipush**, bukan **berkas yang
belum di-commit**. Dua hal berbeda.

Dan butir 10 lahir justru dari yang kedua. Gejalanya masih tertulis di
berkasnya sendiri, tepat di atas baris yang dihapus:

```
berkas baru ada, tidak pernah masuk staging
```

**Buktinya ada di laporan ini sendiri.** Blok terakhir laporan TL:

```
$ git status --short
 M pyproject.toml
 M src/snowline/chamber_templates/CHAMBER_RULES.md
 M src/snowline/chamber_templates/ONBOARDING_QA.md
 M src/snowline/chamber_templates/ONBOARDING_TL.md
```

Empat berkas belum di-commit saat laporan ditulis, dan kalibrasi tetap lulus.
Perintah yang menangkap keadaan itu adalah perintah yang baru saja dihapus.

**Sebagian ini kesalahan perumusan saya.** Syarat lulus yang saya tulis
berbunyi "butir 10 menunjuk ke kalibrasi sebagai cara memeriksa CI — jangan
menulis prosedurnya dua kali". Yang saya maksud CI-nya saja; yang terbaca
seluruh bloknya.

**Perbaikan:** kembalikan `git status --short` ke butir 10, dan tambahkan ke
kalibrasi sebagai langkah nol:

```bash
git status --short     # harus kosong sebelum apa pun dijalankan
snowline test-clone
git log --oneline -1
```

## Penahan 2 — tidak ada yang di-commit

```
$ git status --short
 M .here_we_are/connector.md
 M agents_chamber/CHAMBER_RULES.md
 M src/snowline/chamber_templates/CHAMBER_RULES.md
 M src/snowline/chamber_templates/ONBOARDING_QA.md
 M src/snowline/chamber_templates/ONBOARDING_TL.md
```

Seluruh pekerjaan putaran ini ada di disk, tidak satu pun di git — termasuk
laporannya. Dari klon bersih, aturan baru itu tidak ada.

Butir 10, kalimat pertamanya.

## Catatan

**Blok penutup laporan memotret keadaan yang belum dipulihkan.** `M
pyproject.toml` di situ adalah sisa mutasi 1.1.4. Pohon kerja sekarang sudah
bersih untuk berkas itu, jadi mutasinya dipulihkan sesudahnya — tapi bukti
terakhir yang ditempel adalah bukti pohon kotor.

**`pip install .` masuk ke site-packages global**, bukan venv:

```
Location: C:\Users\LENOVO\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages
```

Kebetulan menguntungkan — pemasangan global di mesin ini sebelumnya 1.1.0 dan
menolak `check-entry`, sekarang 1.1.3. Tapi itu mengubah lingkungan PM tanpa
diminta. Untuk pembuktian rilis, venv sementara lebih tepat.

## Vonis

| hal | vonis |
|-----|-------|
| kalibrasi di dua onboarding | PASS |
| `SELESAI` enam butir | PASS |
| butir 3 laporan ke connector | PASS |
| dua CHAMBER_RULES identik | PASS |
| bentuk laporan TL | PASS, berubah nyata |
| `git status --short` hilang | **REJECT** |
| tidak ada yang di-commit | **REJECT** |

Dua penahan, keduanya kecil. Yang pertama mengembalikan satu baris; yang kedua
satu `git commit`.
