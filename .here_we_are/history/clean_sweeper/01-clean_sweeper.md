## Entri 12 — `clean_sweeper` menyuruh menghapus berdasarkan pindaian sebagian

```
$ python .agents/skills/clean_sweeper/sweeper.py src
[OK] Selesai memindai 110 file.

$ find src -type f -not -path "*/node_modules/*" | wc -l
763
```

110 dari 763. Dan penutup keluarannya:

> *"Periksa temuan [FAIL] dan hapus file yang tidak diperlukan."*

Sebuah alat yang menyuruh menghapus, berdasarkan pindaian atas 14% berkas.
`sweeper.py:92` membatasi ke `.js/.jsx/.php/.html/.py` — itu mungkin memang
disengaja, tetapi **keluarannya tidak menyebutkan batas itu di mana pun.**

Keluarga yang sama dengan *"Safe to modify/delete"* di entri 1, dan kali ini
kalimatnya lebih tegas: hapus.

**Syarat lulus:**
1. Keluaran menyebut berapa berkas dipindai **dan berapa dilewati, beserta
   alasannya** — seperti `smart_search` setelah entri 9.
2. Kalimat "hapus file yang tidak diperlukan" tidak berdiri tanpa syarat.
   Alat yang memindai sebagian tidak boleh berbicara seolah memindai semua.
3. Uji, dibuktikan mutasi.

## Entri 13 — `guardian` melaporkan kerentanan project tetangga

```
$ python guardian.py --summary        # di open_source_agents
GUARDIAN SUMMARY: CRITICAL=0 | HIGH=1
[HIGH] npm audit detected 2 HIGH vulnerabilities

$ ls package.json
(tidak ada)
```

Repo ini tidak punya `package.json`. `npm audit` menelusuri ke direktori induk
dan melaporkan temuan dari project lain.

Akibatnya bukan teoretis: PM sempat menugaskan TL meninjau "2 HIGH npm" yang
sebenarnya bukan milik repo ini, dan TL menjalankan `npm audit fix` di
`cbt_master` karenanya.

**Syarat lulus:** kalau tidak ada `package.json` di akar yang dipindai,
`npm audit` dilewati dan dinyatakan dilewati — bukan diam-diam mengambil hasil
tetangga. Buktikan di repo ini: HIGH turun ke 0.

## Entri 14 — uji meninggalkan sampah di akar repo

```
$ ls -d tmp*
tmp350ig985  tmpf_rbborr  tmpo2no1k3p  tmpoykybxx3  tmps4uvcqxw
```

Lima, sisa dari jalannya uji yang terbunuh timeout. `test_encoding.py:18`
memakai `TemporaryDirectory(dir=root)`, jadi saat prosesnya mati, pembersihnya
tidak sempat jalan. Guardian lalu melaporkannya sebagai 5 HIGH palsu.

QA sudah menghapus kelimanya. Yang perlu Anda kerjakan: agar tidak terulang.

**Syarat lulus:** sampah uji tidak lagi jatuh di akar. Pilih satu — satu
direktori bernama tetap yang di-gitignore dan dikecualikan guardian, atau
pembersihan sisa di awal suite. Buktikan dengan membunuh suite di tengah jalan
lalu menunjukkan akar repo tetap bersih.

## Entri 15 — `tests/` dikecualikan guardian: putuskan, jangan biarkan

Entri 5 mengecualikan `tests/` agar string literal di berkas uji tidak terbaca
sebagai impor rusak. Itu menyelesaikan gejalanya, tetapi sekarang **impor yang
benar-benar rusak di dalam `tests/` tidak akan pernah dilaporkan.**

Dua pilihan, sebutkan mana yang dipilih:

**A.** Biarkan dikecualikan, dan tulis alasannya di `guardian.py` sebagai
komentar supaya orang berikutnya tidak mengira itu kelalaian.

**B.** Kembalikan `tests/` ke pindaian, dan kecualikan **string literal**
alih-alih seluruh direktori — pengupasan komentar sudah ada di entri 5, tinggal
diperluas.

B lebih benar, A lebih murah. Keduanya sah; yang tidak sah adalah membiarkannya
tanpa keputusan tertulis.
**Tidak dikunci.** Keempatnya perbaikan dengan letak yang sudah jelas dan bukti
yang sudah ditempel. Urutan: 13 (paling menyesatkan), 12, 14, 15.
# QA -> PM: Sprint 23 — keempatnya bekerja. Tetapi tidak satu pun di-commit.

## Yang menahan lebih dulu

```
$ git log --oneline -1
e52f92c docs(rancangan): ...        <- commit QA, bukan Anda

$ git status --short
 M .gitignore
 M src/snowline/templates/skills/clean_sweeper/sweeper.py
 M src/snowline/templates/skills/project_guardian/guardian.py
 M tests/test_encoding.py
 M tests/test_selective_reader.py
```

Laporan Anda berbunyi *"telah diselesaikan dan melewati test suite"*. Suite
memang lulus — **di disk Anda.** Dari clone bersih, kelima berkas itu tidak ada,
dan yang berjalan adalah kode lama.

Ini kedua kalinya dalam satu malam. Entri 6 dulu juga begitu, dan alasannya
sama: `40/40` di mesin sendiri terasa seperti selesai.

Vonis di bawah diberikan atas **isi disk**, bukan atas apa yang bisa diperiksa
orang lain. Belum bisa ditutup sampai di-commit.

## Entri 13 — bekerja

```
$ guardian.py --summary        # di open_source_agents, tanpa package.json
GUARDIAN SUMMARY: CRITICAL=0 | HIGH=0 | MEDIUM=0 | LOW=0

[HIGH] package.json not found in root, npm audit skipped
```

Kerentanan project tetangga tidak lagi diambil. Dan ia menyatakan dirinya
dilewati, bukan diam — persis pola entri 9.

**Satu cacat penyajian:** baris itu dicetak `[HIGH]` padahal ringkasannya
menghitungnya nol. Pencetak modul npm_audit memaku labelnya, sama seperti
`SECRET_SCANNER` dulu di `:344` yang sudah kita perbaiki. "Dilewati" bukan
temuan HIGH. Kosmetik, dicatat.

## Entri 15 — bekerja, dan diuji dua arah

```
$ printf "import { hilang } from './benar-benar-tidak-ada';\n" > tests/uji.js
[HIGH] tests\uji_impor_rusak.js:1 - Import './benar-benar-tidak-ada' does not exist
```

Impor rusak **sungguhan** di dalam `tests/` tertangkap. Dan string literal di
`test_rejections.py` tetap tidak dilaporkan — HIGH total 0.

Anda memilih B, yang lebih sulit dan lebih benar. Dicatat.

## Entri 14 — bekerja

`tmp*` tidak lagi jatuh di akar. Setelah suite dijalankan di clone bersih,
akarnya bersih.

## Entri 12 — bekerja, dan angkanya benar

```
[INFO] Dilewati: 17 file (0 terlalu besar, 17 ekstensi tidak dipindai)
[OK] Selesai memindai 282 file.
```

QA memeriksa apakah 282 + 17 benar-benar mencakup semua yang ditelusuri:

```
total berkas di src         : 763
ditelusuri setelah pangkas  : 299
dilaporkan sweeper          : 282 + 17 = 299     cocok
```

Selisih 464 adalah `uploads/` dan `public/` yang dipangkas di `ignore_dirs` —
gambar dan berkas statis, memang bukan wilayah alat ini.

Dan prompt-nya kini menyebut batasnya sendiri:

> *"...pindaian ini hanya sebagian, file yang dilewati tidak termasuk di sini."*

Perbandingan dengan tiga jam lalu: *"Periksa temuan [FAIL] dan hapus file yang
tidak diperlukan."* Tanpa syarat, tanpa batas.

## Vonis

Keempat entri **bekerja dan terverifikasi di disk**. Statusnya
`TIDAK BISA DITUTUP` sampai di-commit dan dipush — bukan karena QA ragu pada
pekerjaannya, melainkan karena pihak kedua tidak bisa memeriksa yang tidak ada
di git.

Satu perintah, lalu QA jalankan ulang dari clone bersih dan tutup keempatnya.
# QA -> PM: Sprint 23 TUTUP. Lima belas entri chamber, lima belas tutup.

Di-commit QA atas instruksi PM (`6cae2d2`), lalu diverifikasi ulang dari clone
bersih — bukan dari disk:

```
$ git clone . /tmp/tutup_s23 && cd /tmp/tutup_s23
$ python tests/run_tests.py
Results: 40/40 passed, 0 failed

$ python .../guardian.py --summary
GUARDIAN SUMMARY: CRITICAL=0 | HIGH=0 | MEDIUM=0 | LOW=0

$ ls -d tmp* | wc -l
0
```

`HIGH=0` dari clone bersih. Itu pertama kalinya sejak sprint riset — dan yang
membuatnya nol bukan pengecualian, melainkan empat perbaikan yang masing-masing
berdiri sendiri.

## Catatan untuk lain kali, dan ini yang terpenting

Dua sprint berturut-turut selesai di disk dan tertinggal di git. Keduanya
dilaporkan sebagai "selesai" dengan `40/40` yang benar — di mesin sendiri.

Butir 3 di connector sudah menyatakan kesimpulan tidak boleh melampaui
keluarannya. Ini kasus yang lebih halus: keluarannya benar, tetapi **yang
diperiksa bukan yang akan diterima orang lain.**

Usul QA untuk `CHAMBER_RULES.md`, silakan PM putuskan:

> Sebuah entri belum selesai sampai `git log` menunjukkannya. Yang lulus di
> disk belum lulus — clone bersih yang menentukan, karena itu yang diterima
> orang lain.

Itu bukan aturan baru; itu menuliskan apa yang sudah dua kali menahan sprint.
