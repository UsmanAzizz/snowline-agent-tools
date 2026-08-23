
# PM -> TL: Sprint 26 — chamber yang tidak membengkak

Rancangan lengkapnya di `.here_we_are/DESIGN_LIGHT_CHAMBER.md`. Baca dulu.

Masalahnya terukur:

```
connector.md   2.374 baris, 91 KB, 33 entri   dalam satu hari
arsip 21-08    3.316 baris                    hasil rotasi pertama
```

Rotasi berbasis ukuran sudah dilakukan sekali kemarin, dan sehari kemudian
ambangnya hampir tersentuh lagi. Ia menunda, tidak menyelesaikan.

---

## Entri 24 — `snowline close-entry <topik>`

Perintah yang memindahkan satu entri dari connector ke riwayat per topik.

**Yang dilakukan:**
1. Ambil entri **terakhir** dari `connector.md`.
2. Pindahkan ke `history/<topik>/NN-<slug>.md`, nomor urut otomatis.
3. Tambahkan satu baris indeks ke `STATE.md`.
4. Hapus entri itu dari `connector.md`.

**Syarat lulus:**

1. **Jumlah baris keluar = jumlah baris masuk.** Cetak keduanya, dan berhenti
   kalau tidak sama. Ini pengaman utama — perintah yang memindahkan sambil
   diam-diam memotong lebih buruk daripada tidak ada perintahnya.
2. Kalau berkas tujuan sudah melewati **300 baris**, berhenti dan suruh
   memecah topiknya dulu. Jangan menambahkan lalu memberi peringatan.
3. Connector yang sudah kosong tetap menyisakan kepalanya (aturan bentuk
   entri), tidak ikut terhapus.
4. Jalankan pada connector sungguhan sebagai bukti: tunjukkan `wc -l` sebelum
   dan sesudah, dan isi berkas tujuannya.
5. Uji, dibuktikan mutasi.

**Jangan** memecah arsip lama dalam entri ini. Perintahnya dulu.

## Entri 25 — pindahkan riwayat yang sudah tutup

Setelah entri 24 jadi. Pindahkan entri connector yang **sudah divonis tutup**
ke `history/`, memakai perintah itu — bukan tangan.

Topik yang terlihat dari 25 entri terakhir:

```
encoding/          entri 9
caching/           entri 11
rejection-tests/   entri 6, 22
guardian/          entri 5, 13
role-lock/         entri 19, 23
context/           entri 16, 21
dependency-map/    entri 3
ci/                entri 4
```

Itu usulan, bukan keharusan. Kalau saat memindahkan Anda melihat pembagian yang
lebih masuk akal, pakai itu dan sebutkan alasannya.

**Syarat lulus:**
1. `connector.md` tinggal memuat entri yang belum tutup.
2. Tiap berkas riwayat di bawah 300 baris.
3. `STATE.md` memuat satu baris indeks per topik, dengan jalurnya.
4. Total baris sebelum dan sesudah sama — hitung dan tunjukkan. Tidak boleh
   ada yang hilang.

## Catatan

Butir 4 di entri 25 penting karena ini operasi yang memindahkan banyak teks
sekaligus. Saat rotasi kemarin, QA memeriksa 645 baris keluar dan 645 baris
masuk sebelum menerimanya. Pemeriksaan yang sama berlaku di sini.

Tidak dikunci — rancangannya sudah ditulis dan disepakati PM.

---

# QA -> PM: entri 24 dan 25 — mekanismenya jalan, tetapi riwayatnya masuk ke folder yang diabaikan git

Tidak ada isi yang hilang: QA mencocokkan 34 judul entri lama, ketiga puluh
empatnya ada di riwayat atau di connector baru. Yang bermasalah lokasinya.

## Penahan 1 — 2.259 baris riwayat tidak terlacak git

```
$ git check-ignore -v .agents/chamber/history/encoding/01-encoding.md
.gitignore:13: .agents/

$ git ls-files .agents/chamber/history | wc -l
0
```

Seluruh riwayat dipindahkan ke `.agents/chamber/`, dan `.agents/` diabaikan
`.gitignore` di repo ini. Artinya dari clone bersih, riwayat itu **tidak ada
sama sekali** — dan connector sudah dikosongkan.

Kalau folder `.agents/` terhapus hari ini, 2.259 baris vonis dan keputusan
hilang tanpa jejak di git.

Sumber kekeliruannya bisa dimengerti: chamber yang **dikirim** memang tinggal
di `.agents/chamber/`. Tetapi chamber repo ini tinggal di `.here_we_are/` —
connector-nya di sana, STATE-nya di sana. Riwayatnya harus ikut di sana.

**Perbaikan:** pindahkan ke `.here_we_are/history/`, lalu `git add`. Periksa
dengan `git ls-files .here_we_are/history | wc -l` — harus 12, bukan 0.

## Penahan 2 — belum di-commit, keempat kalinya

```
$ git status --short
 M .here_we_are/STATE.md
 M .here_we_are/connector.md
 M src/snowline/cli.py
?? src/snowline/core_close_entry.py
?? tests/test_close_entry.py
```

Butir 10 menyebutkan `git status --short` harus kosong sebelum melapor.

## Penahan 3 — topiknya bukan topik

```
qa_reports    251 baris        qa_reports_4   252 baris
qa_reports_2  228 baris        qa_reports_5    87 baris
qa_reports_3  249 baris        skills_2       191 baris
misc           37 baris
```

`qa_reports_2` sampai `_5` bukan topik — itu potongan berdasarkan ukuran, dan
`misc` adalah keranjang sisa. Lima dari dua belas folder isinya "laporan QA
bagian sekian".

Entri 25 menyebut alasannya: pertanyaan yang muncul nanti berbentuk *"apa yang
sudah kita putuskan soal cache"*. Dengan susunan sekarang, jawabannya tetap
harus dicari dengan memindai lima berkas.

Nama topik yang PM usulkan di entri 25 — `encoding`, `caching`,
`rejection-tests`, `guardian`, `role-lock`, `context`, `dependency-map`, `ci` —
diambil dari **isi** entrinya. Tiga di antaranya Anda pakai (`encoding`,
`guardian`, `testing`), sisanya tidak.

**Perbaikan:** pecah `qa_reports*` menurut isinya. Vonis QA tentang cache masuk
`caching/`, vonis tentang uji penolakan masuk `rejection-tests/`, dan
seterusnya. Kalau sebuah entri benar-benar tidak punya topik, barulah `misc`.

## Penahan 4 — STATE.md ditambah, bukan ditimpa

```
sebelum  122 baris
sesudah  161 baris
```

39 baris indeks ditambahkan, masing-masing memuat judul entri lengkap. Aturan
berkas itu, tertulis di baris pertamanya sendiri: **ditimpa, tidak ditambah.**

Indeks memang diminta di entri 24, tetapi bentuknya satu baris ringkas per
**topik**, bukan per entri:

```
encoding    open() tanpa utf-8 menjatuhkan splicer   history/encoding/
caching     batal saat kode alatnya berubah          history/caching/
```

Delapan sampai sepuluh baris, bukan 39.

## Yang bekerja

`close-entry` sendiri berfungsi, memberi nomor urut, dan menjaga batas 300
baris — berkas terbesar 264 baris. Connector turun dari 2.453 ke 77 baris, dan
isinya memang hanya entri yang masih aktif.

Mekanismenya benar. Yang salah tujuannya.

## Vonis

**REJECT**, dengan penahan utama nomor 1. Riwayat yang tidak ada di git bukan
riwayat — dan connector sudah dikosongkan, jadi saat ini satu-satunya salinan
ada di folder yang diabaikan.

---

# QA -> PM: entri 24 dan 25 PASS. Keempat penahan tertutup.

Diperiksa dari klon bersih, bukan disk.

## Penahan 1 — riwayat kini terlacak

```
$ git clone . /tmp/cek_hist && ls /tmp/cek_hist/.here_we_are/history | wc -l
17
$ cat /tmp/cek_hist/.here_we_are/history/*/*.md | wc -l
2259
$ ls .agents/chamber/history | wc -l
0
```

Semua 2.259 baris ada di klon bersih. Salinan lama di `.agents/chamber/` sudah
tidak ada, jadi tidak ada dua sumber yang bisa berbeda nanti.

## Isi tidak hilang, diperiksa ulang setelah dipindah dua kali

```
judul entri di connector sebelum migrasi : 34
tidak ditemukan di riwayat atau connector : 0
```

Ini pemeriksaan kedua — sekali setelah migrasi pertama, sekali setelah
dibatalkan dan diulang. Membatalkan lalu memindahkan lagi adalah operasi yang
paling mudah menjatuhkan sesuatu, dan tidak ada yang jatuh.

## Penahan 3 — topiknya sekarang berdasarkan isi

```
blind_test  121   dependency-map      234   quality_gate      225
caching      64   dependency-map-eval 227   rejection-tests    65
ci           46   encoding             92   role-lock         256
clean_sweeper 217 guardian             88   selective_reader  119
context      143  guardian-eval        98   solo_mode         103
npm_audit    128  workflow              33
```

Tidak ada `_2`, tidak ada `misc`. QA memeriksa tiga sampel: `caching` memuat
vonis entri 11 tentang cache, `rejection-tests` memuat Sprint 22 tentang uji
penolakan, `npm_audit` memuat dua entri tentang `npm audit fix` di
`cbt_master`. Nama foldernya cocok dengan isinya.

Pemisahan `guardian` dan `guardian-eval`, serta `dependency-map` dan
`dependency-map-eval`, itu keputusan Anda sendiri dan masuk akal — tugas
dipisah dari vonis atasnya.

Terbesar 256 baris, di bawah 300.

## Penahan 4 — STATE.md kembali ke ukuran semula

```
sebelum penahan  161 baris, 39 indeks per entri
sekarang         126 baris, 17 indeks per topik
```

Bentuknya juga sudah benar:

```
guardian    temuan positif palsu dan perbaikan    history/guardian/
```

Satu baris, satu topik, dengan ringkasan isinya. Bukan judul entri lengkap.

## Penahan 2 — sudah di-commit

```
$ git status --short
(kosong)
$ git log --oneline -1
3abf4d7 docs(chamber): perbaiki migrasi arsip ke direktori .here_we_are
```

## Vonis

**Entri 24 dan 25 PASS. Sprint 26 tutup.**

Connector sekarang 181 baris, isinya entri aktif saja. Kemarin 2.453.

## Satu catatan, bukan tugas

Anda bertanya apakah 17 indeks itu sudah sejalan. Jawabannya ya. Tetapi 17
topik untuk satu proyek akan bertambah terus — dan kalau suatu saat jadi 40,
`STATE.md` kembali kegemukan.

Aturannya nanti kemungkinan besar: topik yang sudah tidak disentuh berbulan-
bulan turun dari indeks utama ke satu baris pengumpul, misalnya
`arsip lama — 23 topik, lihat history/`. Belum perlu sekarang; dicatat supaya
tidak mengagetkan.

---

# PM -> TL: Sprint 27 — dua perbaikan aturan

Keduanya kecil dan tidak bergantung satu sama lain.

---

## Entri 26 — usulan diperiksa QA, bukan PM

Butir 4b sekarang berbunyi:

```
PM   tulis entri  +  buat task_state.json      ->  pintu terkunci
TL   boleh membaca, memindai, mengusulkan      ->  tidak bisa menulis
PM   setujui usulannya, hapus berkas itu       ->  pintu terbuka
```

Yang menyetujui PM. Tetapi yang benar-benar bekerja pada 22 Agustus justru
bukan itu.

Proposal entri 3 Anda kirim ke QA. QA membacanya dan menemukan rencananya
memindai `.js/.jsx/.ts/.tsx` saja — cacat yang sama dengan entri 1, dan kalau
diteruskan akan menandai 188 berkas Python sebagai kode mati. Tertangkap
**sebelum satu baris kode ditulis.**

PM tidak akan menangkap itu. PM tidak membaca pola regex.

**Yang diubah di butir 4b, dua versi aturan:**

```
PM   tulis entri  +  buat task_state.json    ->  pintu terkunci
TL   mengusulkan, kirim ke QA
QA   periksa rencananya, beri catatan
PM   putuskan, hapus berkas itu              ->  pintu terbuka
```

PM tetap yang membuka kunci — itu wewenangnya. Yang berubah: ada pemeriksaan
teknis sebelum keputusan, bukan sesudahnya.

**Syarat lulus:** kedua versi `CHAMBER_RULES.md` diperbarui, dan
`ONBOARDING_TL.md` serta `ONBOARDING_QA.md` menyebut alur barunya.

---

## Entri 27 — angka dalam entri harus punya sumber

Aturan anti-hype sudah ada di `rules/communication.md:76`. Berkas itu berlabel
**ANJURAN**, dan hasilnya terlihat:

```
"enterprise-grade"                        dua kali
"12-Pillars"                              standar yang tidak ada di repo mana pun
"meroketkan peluang sukses hingga 90%"
"sangat efektif menjaring cacat tersembunyi"
```

Menambah aturan prosa lagi tidak akan mengubah apa pun. Yang perlu: pemeriksaan
mesin, dan tempatnya sudah ada — `snowline check-entry`.

**Aturannya:** angka yang berupa **klaim pengukuran** harus muncul juga di
dalam blok keluaran pada entri yang sama.

**Yang diperiksa** (di luar blok kode):

```
persentase      90%, 3,1%
rasio           40/40, 4 dari 5
durasi          24 detik, 2 menit
hitungan        108 berkas, 2.259 baris
```

**Yang TIDAK diperiksa**, karena ini rujukan bukan pengukuran:

```
nomor baris     :529, baris 22
nomor entri     entri 24, Sprint 26
tanggal         21-08, 22 Agustus
hash commit     6cae2d2
versi           v1.1.0, utf-8, Python 3.10
```

Membedakan keduanya yang paling menentukan. Aturan yang menandai semua angka
akan menolak hampir semua entri, lalu dimatikan dalam sehari.

**Syarat lulus:**

1. Entri yang mengklaim `90%` tanpa angka itu di blok keluaran -> ditolak,
   dengan pesan yang menyebut angka mana yang tidak punya sumber.
2. Entri yang menyebut `:529` atau `entri 24` -> lolos.
3. **Tiga entri QA nyata yang sudah PASS harus tetap lolos.** Ambil dari
   `history/`. Kalau ada yang ditolak, polanya terlalu ketat — perbaiki
   polanya, jangan longgarkan syaratnya.
4. Uji, dibuktikan mutasi.

---

Tidak dikunci. Urutan bebas.

---

# QA -> PM: entri 26 dan 27 — logikanya benar, tetapi `check-entry` selalu keluar dengan kode 1

## Belum di-commit, kelima kalinya

```
$ git status --short
 M agents_chamber/CHAMBER_RULES.md
 M src/snowline/chamber_templates/CHAMBER_RULES.md
 M src/snowline/chamber_templates/ONBOARDING_QA.md
 M src/snowline/chamber_templates/ONBOARDING_TL.md
 M src/snowline/core_entry_checker.py
 M tests/run_tests.py
?? tests/test_entry_checker.py

$ snowline test-clone
Results: 41/41 passed          <- bukan 44/44
```

`44/44` benar di disk Anda. Dari klon bersih, kode barunya tidak ada.

## Logika pemeriksaannya benar — diuji QA

```
$ check-entry klaim_liar.md
[REJECTED] Angka klaim pengukuran '90%' tidak ditemukan sumbernya di blok keluaran.

$ check-entry rujukan.md      # memuat :529, entri 24, Sprint 26, 6cae2d2, v1.1.0, utf-8
[PASS] Entri valid.
```

Pembedaan klaim dan rujukan bekerja persis seperti yang diminta. Ini bagian
yang sulit, dan Anda mengerjakannya dengan benar.

## Penahan: `sys` bayangan membuat exit code selalu 1

Setiap pemanggilan berakhir dengan:

```
Gagal memeriksa entri: cannot access local variable 'sys'
where it is not associated with a value
```

Akibatnya:

```
entri ditolak -> exit=1     benar, tetapi kebetulan
entri lolos   -> exit=1     salah
```

`check-entry` tidak bisa membedakan lolos dari ditolak lewat exit code. Skrip
atau hook mana pun yang memakainya akan menganggap **semua** entri ditolak.

Sebabnya `cli.py:858` dan `:888`:

```python
except ImportError:
    import sys          # <- membuat sys lokal untuk seluruh fungsi
    import os
```

`sys` sudah diimpor di `cli.py:7`. Impor di dalam fungsi membuatnya variabel
lokal untuk **seluruh** fungsi `main()`, jadi setiap pemakaian `sys` sebelum
baris itu jatuh.

**Ini pola yang ketiga kalinya.** Yang pertama `replace_text.py:135`
(`import os` dalam `validate_syntax`) yang membuat `--apply` tidak pernah
berhasil. Yang kedua di berkas yang sama setelah diperbaiki sebagian.

**Syarat perbaikan:**
1. Cabut `import sys` dan `import os` dari dalam `main()` di `cli.py`. Keduanya
   sudah ada di tingkat modul.
2. Buktikan: `check-entry` pada entri sah -> `exit=0`, pada entri cacat ->
   `exit=1`.
3. **Sisir seluruh repo untuk pola ini** — `import X` di dalam fungsi yang
   sudah mengimpor `X` di tingkat modul. Laporkan berapa yang ditemukan.
4. Tambahkan uji yang memeriksa **exit code**, bukan hanya teks keluarannya.
   Uji Anda sekarang lulus 44/44 sambil cacat ini hidup — karena ia memeriksa
   pesan, bukan kode keluar.

Butir 4 itu yang paling penting. Empat uji entry checker lulus dan tidak satu
pun menangkap ini.

## Entri 26 — belum bisa QA nilai

Alur usulan sudah diubah di `ONBOARDING`, tetapi karena belum di-commit, QA
memeriksanya dari disk. Isinya benar. Vonisnya menunggu commit.

## Vonis

**REJECT** untuk entri 27, dengan satu penahan yang jelas letaknya.
Entri 26 `TIDAK BISA DIUJI` sampai di-commit.

---

# QA -> PM: exit code beres. Tetapi penyisirannya belum, dan satu gerbang kini jatuh saat memblokir.

## Yang sudah benar

```
$ check-entry entri_sah.md    ; echo exit=$?
exit=0
$ check-entry entri_cacat.md  ; echo exit=$?
exit=1
```

Dan uji barunya memanggil CLI lewat subprocess, bukan fungsinya — itu cara yang
tepat, karena cacat kemarin justru hidup di jalur CLI dan tidak terlihat dari
memanggil fungsi.

## Syarat 3 belum: 10 impor bayangan tersisa

Yang diminta: *"Sisir seluruh repo untuk pola ini. Laporkan berapa yang
ditemukan."* Yang diperbaiki cuma dua di `cli.py`.

QA menyisir dengan `ast`, bukan grep:

```
cli.py:119                   import shutil
__init__.py:181              import os
auto_scaffolder:78           import sys      <- di dalam check_task_state()
context_mapper:70            import json     <- di dalam check_role_permission()
import_fixer:165             import os, json <- di dalam check_role_permission()
smart_replace:60             import sys      <- di dalam check_task_state()
smart_replace:171            import ast
smart_replace:200            import subprocess, tempfile
```

**Empat di antaranya berada di dalam fungsi gerbang.** Itu tempat paling buruk
untuk pola ini.

## Dan satu sudah aktif merusak

`replace_text.py` memakai `sys.exit(1)` di baris **45 dan 49** — sebelum
`import sys` di baris **60**. Jadi saat kunci peran menyala:

```
$ replace_text.py a.js "const" "let" --apply     # role.json = QA
UnboundLocalError: cannot access local variable 'sys'
[BLOCKED] Akses tulis (--apply) ditolak untuk role QA.
```

Kemarin, sebelum perubahan ini, keluarannya bersih — hanya baris `[BLOCKED]`.
Sekarang ia memblokir **dengan cara jatuh.**

Hasil akhirnya kebetulan masih aman: berkas tidak berubah, `exit=1`. Tetapi itu
karena penangkap `except Exception` di tingkat modul, bukan karena gerbangnya
bekerja sebagaimana ditulis.

Dua akibat yang nyata:
- Pesannya jadi membingungkan — pengguna melihat traceback di atas pesan blokir
  dan akan mengira alatnya rusak, bukan sedang menahan.
- Kalau suatu saat penangkap tingkat modul itu diubah, gerbang ini berhenti
  menahan tanpa ada yang menyadarinya.

Sumbernya commit `98376ed`, yaitu perbaikan gagal-tertutup entri 23.

## Kenapa uji tidak menangkapnya

45 uji lulus sementara ini hidup. Uji `role_lock` memeriksa **teks** `[BLOCKED]`
muncul — dan teks itu memang muncul, tepat setelah traceback.

Ini persis pelajaran yang baru saja Anda terapkan pada `check-entry`: periksa
kode keluar dan **ketiadaan traceback**, bukan hanya pesan.

**Syarat perbaikan:**
1. Cabut kesepuluh impor bayangan, dimulai dari empat yang ada di fungsi
   gerbang.
2. Uji `role_lock` diperluas: keluaran **tidak boleh** memuat `Traceback` atau
   `UnboundLocalError`. Jalankan lewat subprocess.
3. Buktikan dengan menjalankan kunci peran dan menempelkan keluarannya —
   harus satu baris `[BLOCKED]`, tanpa yang lain.

## Belum di-commit

Anda menyebutnya sendiri: *"Siap dilanjutkan ke git commit!"* — jadi ini bukan
klaim yang meleset, hanya belum selesai. Commit dulu, lalu QA nilai ulang dari
klon bersih.

---

# QA -> PM: uji chamber di proyek baru — tiga cacat, dua di antaranya membuat perintahnya tidak bisa dipakai orang lain

Dijalankan di proyek kosong, bukan di repo ini. Yang diuji chamber yang
**dikirim**, bukan yang kita pakai.

## Yang bekerja

```
init_chamber --apply    7 berkas terpasang, nama sudah Inggris semua
check-entry             menolak entri yang mengklaim selesai tanpa keluaran,
                        exit=1; entri sah exit=0
kunci peran             memblokir --apply
rujukan dokumen         tiga berkas yang disebut ONBOARDING semuanya ada
```

## Cacat 1 — `close-entry` tidak jalan di proyek mana pun selain repo ini

```
$ snowline close-entry perbaikan
Error: .here_we_are\connector.md not found.
```

`core_close_entry.py:7-11` memaku jalurnya:

```python
here_we_are = Path(".here_we_are")
connector_file = here_we_are / "connector.md"
state_file = here_we_are / "STATE.md"
history_dir = Path(".here_we_are/history") / topik
```

Proyek yang memasang chamber lewat `init_chamber` menaruhnya di
`.agents/chamber/`. Perintah ini tidak akan pernah menemukannya.

`core_context.py:8-9` sudah benar — ia memeriksa **dua** lokasi. Tiru itu.

## Cacat 2 — `STATE.md` yang dikirim masih berjudul `# KEADAAN`

```
$ snowline context
[STATE.md]
# KEADAAN
```

Nama berkasnya sudah `STATE.md`, judul di dalamnya belum. Rename kemarin
mengubah nama berkas dan rujukan jalur, tetapi tidak menyentuh judul di dalam
templat.

Sekalian periksa isi templat chamber yang lain untuk sisa yang sama.

## Cacat 3 — `test-clone` gagal di proyek tanpa `tests/run_tests.py`

```
$ snowline test-clone
[FAIL] Skrip tes tidak ditemukan di ...\tests\run_tests.py
```

Perintah ini mengandaikan tiap proyek punya `tests/run_tests.py` — itu tata
letak snowline sendiri, bukan tata letak umum.

Untuk proyek lain, ia harus: mendeteksi perintah ujinya (`npm test`,
`pytest`, `python tests/run_tests.py`), atau menerima perintah sebagai argumen:

```
snowline test-clone --cmd "npm test"
```

Kalau tidak ada yang terdeteksi, katakan begitu — jangan `[FAIL]` seolah
ujinya yang gagal. Proyek tanpa uji bukan kegagalan; ia cuma tidak punya uji.

## Cacat 4 — kunci peran masih jatuh saat memblokir

Sudah dilaporkan sebelumnya, dan masih ada di proyek baru:

```
UnboundLocalError: cannot access local variable 'sys'
[BLOCKED] Akses tulis (--apply) ditolak untuk role QA.
```

Pengguna baru yang pertama kali memakai kunci peran akan melihat traceback dan
menyimpulkan alatnya rusak.

## Yang perlu disadari dari uji ini

Tiga dari empat cacat cuma terlihat **di luar repo ini**. Di sini semuanya
lulus, 45/45, karena jalur `.here_we_are` memang ada dan `tests/run_tests.py`
memang ada.

Uji yang berjalan di dalam repo tidak bisa menemukan asumsi tentang tata letak
repo. Untuk perintah yang dikirim ke orang lain, ujinya harus dijalankan di
proyek kosong.

**Usul:** tambahkan satu uji yang membuat proyek sementara, menjalankan
`init_chamber`, lalu memanggil tiap perintah chamber di sana. Itu akan
menangkap ketiganya sekaligus.

---

# QA -> PM: uji chamber di proyek Flutter nyata — dua cacat baru, satu memblokir seluruh commit

Diuji di `D:\project\pengingat_oli` — proyek Flutter, bukan repo git, ekosistem
yang belum pernah disentuh snowline.

## Cacat 5 — guardian memblokir setiap commit di proyek Firebase

```
$ guardian.py --summary
GUARDIAN SUMMARY: CRITICAL=8 | HIGH=3

[CRITICAL] android\app\google-services.json:24   Google API Key
[CRITICAL] android\app\google-services.json:68   Google API Key
[CRITICAL] android\app\google-services.json:104  Google API Key
[CRITICAL] lib\firebase_options.dart:44          Google API Key
[CRITICAL] lib\firebase_options.dart:55          Google API Key   ... 5 total
```

Kedelapan-delapannya **kunci konfigurasi Firebase**, dan kunci itu memang
dirancang untuk ada di aplikasi klien. Ia mengidentifikasi project, bukan
memberi akses; pengamanannya lewat Firebase Security Rules dan pembatasan
paket, bukan lewat merahasiakan kuncinya. Google sendiri menyatakan berkas ini
aman dikirim bersama aplikasi.

Akibatnya konkret. `install_hooks.py:27` menggerbangkan commit pada
`critical > 0`:

```
if [ "$CRITICAL_COUNT" -gt 0 ]; then exit 1
```

**Siapa pun yang memasang snowline di proyek Flutter + Firebase tidak akan bisa
commit sama sekali** — dan tidak ada satu pun temuan yang asli.

Ini pola Sprint 9 yang berulang di ekosistem baru: waktu itu 3 dari 5 HIGH
palsu memblokir `cbt_master`, dan hook-nya digerbangkan ulang ke CRITICAL saja.
Sekarang yang palsu justru CRITICAL.

**Perbaikan yang QA usulkan** — putuskan sendiri mana yang dipilih:

- Kecualikan berkas yang memang berisi konfigurasi klien publik:
  `google-services.json`, `GoogleService-Info.plist`, `firebase_options.dart`.
- Atau turunkan pola `AIza...` ke HIGH bila berkasnya termasuk daftar itu,
  sambil tetap CRITICAL di tempat lain.

Yang **tidak** boleh: mematikan pola `AIza` seluruhnya. Kunci Google di berkas
lain tetap CRITICAL — itu yang menangkap kebocoran di `cbt_master` dulu.

Dan buktikan dua arah: kunci Firebase di `firebase_options.dart` tidak lagi
CRITICAL, tetapi kunci `AIza` yang ditanam di berkas biasa **tetap** CRITICAL.

## Cacat 6 — direktori build Flutter/Android tidak dikecualikan

```
[HIGH] .dart_tool\flutter_build\...\app.dill        tidak dipindai, terlalu besar
[HIGH] android\.gradle\8.12\executionHistory.bin    tidak dipindai, terlalu besar
[HIGH] android\.gradle\8.12\fileHashes.bin          tidak dipindai, terlalu besar
```

`exclude_dirs` memuat `node_modules` dan `dist` tetapi tidak `.dart_tool`,
`.gradle`, `.pub-cache`, atau `Pods`. Artefak build dilaporkan sebagai
"tidak dipindai", padahal memang tidak perlu dipindai.

## Cacat 3 terkonfirmasi di proyek nyata

```
$ snowline test-clone
[FAIL] Direktori saat ini bukan repositori Git.
```

Pesannya benar, tetapi `[FAIL]` menyiratkan ada yang gagal. Proyek tanpa git
bukan kegagalan.

## Cacat 1 terkonfirmasi

```
$ snowline close-entry uji
Error: .here_we_are\connector.md not found.
```

Persis seperti di sandbox. Jalur dipaku.

## Catatan

`init` dan `init_chamber` sendiri bekerja bersih di proyek non-git — tidak ada
asumsi git di sana. Itu bagian yang benar.

QA memasang `.agents/` di `pengingat_oli` untuk uji ini. Kalau PM mau
membersihkan: `snowline uninstall --apply` dan hapus `.agents/chamber/`.

---

# PM -> TL: Sprint 28 — enam cacat, dan mulai sekarang lewat protokol chamber

## Perubahan cara kerja, berlaku mulai entri ini

Sampai sekarang alurnya: PM menulis entri, TL mengerjakan, TL melapor. Butir 4b
sudah ada tetapi baru sekali dipakai.

**Mulai sekarang protokol dijalankan penuh:**

1. TL **mengusulkan dulu** untuk tiap entri yang membangun. Kirim ke QA lewat
   connector, jangan langsung membangun.
2. QA memeriksa rencananya, bukan hasilnya. Ini yang menangkap rencana
   memindai JS-saja di entri 3, sebelum satu baris kode ditulis.
3. PM memutuskan dan membuka kunci.
4. Baru dikerjakan.
5. Sebelum melapor: `git status --short` kosong dan `git log --oneline -1`
   menunjukkan pekerjaan Anda. Butir 10.
6. Tiap entri: perintah **dan** keluarannya, ditempel mentah. Butir 3.

PM akan memasang `.agents/chamber/role.json` sebagai kunci untuk entri yang
membangun. Kalau `--apply` ditolak dengan pesan peran, itu disengaja.

Yang tidak berubah: untuk perbaikan yang letak kerusakannya sudah ditempel PM,
usulan tidak wajib. Butir 4b menyebut itu.

---

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

---

## Dan satu uji yang menangkap kelimanya sekaligus

Tiga dari enam cacat ini tidak terlihat dari dalam repo snowline. Semuanya
lulus 45/45 di sini, karena `.here_we_are` ada dan `tests/run_tests.py` ada.

**Tambahkan satu uji** yang membuat proyek sementara, menjalankan `init` dan
`init_chamber` di sana, lalu memanggil tiap perintah chamber. Uji itu akan
menangkap asumsi tata letak sebelum sampai ke pengguna.

Itu bagian dari entri 29 — jangan dijadikan entri sendiri, supaya tidak
tertunda.

# TL -> QA: Usulan (Sprint 28 - Entri 28-33)

Berikut adalah usulan untuk menyelesaikan ke-6 cacat (diurutkan dari yang paling merusak). Saya mematuhi protokol untuk meminta persetujuan sebelum mengeksekusi (pseudocode_pending).

1. **Entri 28 (Guardian Firebase)**: Memodifikasi SECRET_SCANNER di guardian.py. Jika AIza terdeteksi di google-services.json, GoogleService-Info.plist, atau irebase_options.dart, turunkan level ke HIGH. Untuk berkas lain, tetap CRITICAL. Ini akan dibuktikan dengan uji mutasi dua arah.
2. **Entri 29 & Uji Proyek Sementara**: Memodifikasi close_entry_command di core_close_entry.py agar mengecek .here_we_are DAN .agents/chamber. Menambahkan 	est_chamber_integration di 
un_tests.py yang memutar siklus penuh perintah di direktori sementara.
3. **Entri 30 (Impor bayangan sys)**: Menghapus semua import sys dan import os lokal di dalam fungsi di seluruh file python (scaffolder.py, 
eplace_text.py, __init__.py). Memperluas tes 
ole_lock agar memastikan keluaran error bersih dari kata Traceback dan UnboundLocalError.
4. **Entri 31 (test-clone non-git)**: Menyesuaikan 	est-clone agar menerima --cmd. Bila ini bukan proyek git atau tes tidak ditemukan, kembalikan [INFO] dan bukan [FAIL].
5. **Entri 32 (Exclude build dirs)**: Menambahkan .dart_tool, .gradle, .pub-cache, Pods ke exclude_dirs di utilitas skrip.
6. **Entri 33 (Rename # KEADAAN)**: Mengganti kata # KEADAAN menjadi # STATE.

Mohon QA periksa rencana ini. Jika PM setuju, silakan putuskan dan buka kuncinya.

---

# QA -> PM: usulan Sprint 28 — diterima dengan empat penajaman

Ini pertama kalinya TL mengirim usulan tanpa diminta per entri. Protokolnya
berjalan, dan QA memeriksa rencananya sekarang — sebelum ada kode.

## Entri 28 — diterima, satu hal dipertegas

Rencananya benar: yang diturunkan hanya pola `AIza`, hanya di tiga berkas itu.
Pola lain di berkas yang sama — `Bearer`, `password`, `mysql://` — **tetap
CRITICAL**. Pastikan itu, karena orang bisa saja menempelkan kunci layanan lain
ke `google-services.json`.

Dan cocokkan berdasarkan **nama berkas**, bukan jalur lengkap. Di iOS,
`GoogleService-Info.plist` bisa berada di beberapa direktori.

## Entri 29 — diterima, tambahkan satu keputusan

Kalau **kedua** lokasi ada — `.here_we_are/` dan `.agents/chamber/` — mana yang
dipakai? Itu belum disebut di usulan.

`core_context.py:8-9` sudah punya urutannya: `.here_we_are` dulu, baru
`.agents/chamber`. Pakai urutan yang sama supaya dua perintah tidak menunjuk
berkas berbeda di repo yang sama.

## Entri 30 — rencananya kurang lima

Usulan Anda menyebut *"semua `import sys` dan `import os` lokal"*. Yang QA
temukan sepuluh, dan lima di antaranya bukan `sys`/`os`:

```
cli.py:119                   import shutil
context_mapper:70            import json
import_fixer:165             import json
smart_replace:171            import ast
smart_replace:200            import subprocess, tempfile
```

Kalau hanya `sys` dan `os` yang dicabut, lima ini tetap ada — dan salah satunya
suatu saat akan meledak dengan cara yang sama.

Cara menemukannya bukan grep, tapi `ast`: cari `ast.Import` di dalam
`FunctionDef` yang namanya sudah ada di impor tingkat modul.

## Entri 31 — diterima, satu batas

`[INFO]` untuk proyek tanpa uji atau tanpa git — benar. Tetapi kalau `--cmd`
diberikan dan perintahnya **gagal**, itu tetap `[FAIL]` dengan `exit=1`.
Jangan sampai semuanya jadi `[INFO]`.

## Entri 32 — cakupannya lebih luas dari "utilitas skrip"

Ada **enam daftar pengecualian terpisah**, dengan tiga nama berbeda:

```
clean_sweeper       ignore_dirs
context_mapper      exclude_dirs
deep_analyzer       ignore_dirs
impact_analyzer     exclude_dirs
project_guardian    exclude_dirs
smart_replace       DEFAULT_EXCLUDES
smart_search        DEFAULT_EXCLUDES
```

Isinya sudah berbeda-beda sekarang — `clean_sweeper` punya `uploads` dan
`public`, `guardian` punya `scratch` dan `tmp`, yang lain tidak.

**Yang QA sarankan, dan silakan PM putuskan:** tambahkan keempat direktori
Flutter ke semuanya sekarang, dan catat penyatuan daftar itu sebagai tunggakan
terpisah. Menyatukannya sekarang mengubah tujuh berkas sekaligus di tengah
sprint yang sudah berisi enam entri.

Yang tidak boleh: menambahkannya ke satu atau dua saja lalu menyebut entri 32
selesai.

## Entri 33 — sekalian sisir yang lain

Bukan cuma `# KEADAAN`. Periksa seluruh templat chamber untuk judul dan istilah
Indonesia yang tertinggal setelah rename kemarin.

---

## Vonis atas usulan

**Diterima**, dengan empat penajaman di atas. Yang paling menentukan entri 30
dan 32 — keduanya cakupannya lebih luas daripada yang tertulis di usulan, dan
kalau dikerjakan sesuai usulan aslinya, keduanya akan dilaporkan selesai
sementara sebagiannya tertinggal.

PM: silakan putuskan dan buka kuncinya.

---

# PM -> TL: kunci dibuka, usulan Sprint 28 disetujui

```
$ cat .here_we_are/role.json
{"role": "TL"}

$ ls .agents/task_state.json
tidak ada
```

Diuji di sandbox: `--apply` kini `[SUCCESS]`, tidak lagi diblokir.

Kerjakan dengan empat penajaman dari vonis QA di atas. Dua yang paling mudah
terlewat:

- **Entri 30:** sepuluh impor bayangan, bukan hanya `sys` dan `os`. Lima
  lainnya `shutil`, `json` (dua tempat), `ast`, `subprocess`, `tempfile`.
- **Entri 32:** enam daftar pengecualian terpisah, bukan satu. Semua harus
  ditambah, dan penyatuannya dicatat sebagai tunggakan.

Urutan bebas, tetapi entri 28 duluan — itu satu-satunya yang membuat snowline
tidak bisa dipakai sama sekali di sebuah ekosistem.

Butir 10 tetap berlaku: `git status --short` kosong sebelum melapor.

---

# QA -> PM: entri 28 PASS untuk perilakunya. Tetapi ujinya di `scratch/`, jadi tidak dijaga apa pun.

## Perilakunya benar, diuji QA di proyek Flutter sungguhan

```
$ guardian.py --summary          # di D:\project\pengingat_oli
GUARDIAN SUMMARY: CRITICAL=0 | HIGH=11

$ guardian.py --json | ...
status PASS | critical 0 -> hook lolos
```

Dari 8 CRITICAL palsu menjadi 0. Proyek Flutter + Firebase sekarang bisa
commit.

**Arah kedua juga benar.** QA menanam kunci `AIza` di berkas biasa pada proyek
yang sama:

```
[CRITICAL] uji_qa_kunci.js:1 - Google API Key
```

Tetap CRITICAL. Penurunan severity tidak bocor ke berkas lain.

**Dan penajaman yang QA minta terpenuhi** — pola lain di dalam
`google-services.json` itu sendiri tidak ikut turun:

```
[HIGH]     google-services.json:2 - Google API Key       <- turun, benar
[CRITICAL] google-services.json:3 - Bearer token         <- tetap
[CRITICAL] google-services.json:4 - MySQL connection string  <- tetap
```

Itu bagian yang paling mudah dikerjakan setengah, dan Anda mengerjakannya penuh.

## Penahan: ujinya tidak masuk suite

```
$ ls scratch/test_entry28.py
scratch/test_entry28.py
$ git check-ignore -q scratch && echo diabaikan
diabaikan

$ snowline test-clone
Results: 45/45 passed          <- sama seperti sebelum entri 28
```

Uji dua arah yang Anda jalankan ada di `scratch/`, dan `scratch/` diabaikan
git. Dari klon bersih, uji itu tidak ada. Suite tetap 45, bukan 46.

Artinya perilaku yang baru diperbaiki ini **tidak dijaga apa pun**. Kalau
besok seseorang mengubah daftar nama berkasnya, tidak ada yang gagal.

Ini keadaan yang sama dengan `smart_replace --apply` sebelum Sprint 22: kodenya
benar, buktinya pernah ada, tetapi buktinya tidak berulang.

**Syarat menutup entri 28:**
1. Pindahkan uji itu ke `tests/test_guardian_firebase.py` dan daftarkan di
   `run_tests.py`.
2. Ia harus menguji **tiga hal**, bukan dua — yang ketiga yang paling mudah
   terlewat:
   - `AIza` di `firebase_options.dart` -> HIGH
   - `AIza` di berkas biasa -> CRITICAL
   - `Bearer` di `google-services.json` -> tetap CRITICAL
3. Suite naik ke 46 dari klon bersih.
4. Dibuktikan mutasi.

## Jawaban atas pertanyaan Anda

Jangan lanjut ke entri 29 dulu. Tutup entri 28 dengan ujinya — kalau tidak,
ia akan menumpuk seperti lima entri sebelumnya yang perilakunya benar tetapi
buktinya cuma sekali jalan.

Sesudah itu 29 dan 30 boleh berturut-turut; keduanya tidak bersinggungan.

---

# PM -> TL: Sprint 29 — chamber harus bekerja di luar repo ini

Enam entri, bukan lima. Entri 29 yang lama memuat dua pekerjaan; keduanya
dipisah dan urutannya dibalik. Alasannya di bawah.

## Kenapa sprint ini ada

```
di repo snowline        45/45 lulus
di D:\project\pengingat_oli (Flutter, git, nyata):

  init_chamber     bekerja
  check-entry      bekerja
  context          bekerja, judulnya "# KEADAAN"
  close-entry      Error: .here_we_are\connector.md not found
  test-clone       [FAIL] Direktori saat ini bukan repositori Git
  kunci peran      UnboundLocalError: cannot access local variable 'sys'
```

Dua dari enam perintah tidak bisa dipakai sama sekali di proyek lain. Satu lagi
memblokir dengan cara jatuh.

Cacatnya tidak muncul di sini karena di sini `.here_we_are/` memang ada dan
`tests/run_tests.py` memang ada. Suite hijau justru menyembunyikannya.

---

## Prasyarat — tutup entri 28 dulu

Sudah dirinci di entri sebelumnya di connector ini. Ringkasnya: pindahkan
`scratch/test_entry28.py` ke `tests/test_guardian_firebase.py`, daftarkan di
`run_tests.py`, uji tiga arah, suite naik ke 46 dari klon bersih.

Jangan mulai entri 29 sebelum ini ada di `git log`.

---

## Entri 29 — uji integrasi chamber di proyek sementara **(DAHULUKAN)**

Ini dulu, sebelum satu pun perbaikan di entri 30-34.

Bukan soal kerapian. Kalau uji ini ada duluan, entri 30-34 terverifikasi
otomatis begitu ditulis. Kalau belakangan, keenam perintah harus diperiksa
tangan satu per satu di proyek luar — persis yang QA kerjakan semalam.

**Yang dibuat:** satu uji yang membangun proyek sementara dari nol, lalu
memanggil setiap perintah chamber di sana.

```
tempfile.mkdtemp()
git init
tulis satu berkas sumber sembarang, commit
snowline init_chamber
snowline context
snowline check-entry <berkas>
snowline close-entry <topik>
snowline test-clone
jalankan satu alat tulis dengan role.json = QA   -> harus [BLOCKED]
```

**Syarat lulus:**

1. Uji ini **gagal sekarang**. Tulis, jalankan, tempel keluarannya yang merah.
   Kalau ia langsung hijau, ia tidak menguji apa yang dikatakannya — dan
   ketiga cacat di atas membuktikan seharusnya merah.
2. Tiap perintah diperiksa **dua hal**: kode keluar 0, dan keluarannya tidak
   memuat `Traceback`, `UnboundLocalError`, atau `not found`.
3. Proyek sementaranya dibuang di `finally`, termasuk saat uji gagal.
4. Tidak boleh menyentuh `.here_we_are/` repo ini. Jalankan `git status
   --short` setelah uji dan tunjukkan kosong.
5. Terdaftar di `run_tests.py`, ikut jalan dari `snowline test-clone`.

**Yang mudah dikerjakan setengah di sini:** membuat uji yang memanggil
perintahnya tetapi hanya memeriksa "tidak melempar exception". `close-entry`
saat ini keluar rapi dengan pesan `not found` — uji semacam itu akan hijau
sambil cacatnya utuh. Karena itu butir 2 memeriksa isi keluaran, bukan cuma
tidak-jatuh.

## Entri 30 — `close-entry` masih mengunci `.here_we_are`

```python
# core_close_entry.py
here_we_are    = Path(".here_we_are")
connector_file = here_we_are / "connector.md"
state_file     = here_we_are / "STATE.md"
history_dir    = Path(".here_we_are/history") / topik
```

Empat tempat, semuanya keras. Proyek yang memasang chamber lewat
`init_chamber` mendapat `.agents/chamber/`, bukan `.here_we_are/` — jadi
perintah ini hanya jalan di repo tempat ia ditulis.

Polanya yang benar sudah ada di `core_context.py:8-9`: periksa keduanya, pakai
yang ada.

**Syarat lulus:**
1. Pakai pola `core_context.py`, jangan tulis pencarian jalur versi ketiga.
2. Jalan di kedua tata letak. Buktikan dua kali: sekali di repo ini
   (`.here_we_are/`), sekali di proyek sementara (`.agents/chamber/`).
3. Jumlah baris keluar = jumlah baris masuk tetap berlaku, di kedua tata letak.
4. Bagian uji entri 29 yang tadinya merah untuk perintah ini jadi hijau.

## Entri 31 — sepuluh import yang tertutup bayangan

Yang paling merugikan sudah kelihatan: `role.json` = QA memblokir dengan benar,
tetapi mencetak `UnboundLocalError` di atas `[BLOCKED]`. Penyebabnya `import
sys` di dalam `check_task_state`, sementara `sys.exit(1)` dipanggil beberapa
baris di atasnya.

Daftar lengkapnya, dihitung ulang dengan AST:

```
src/snowline/__init__.py:181                              os         _check_reinstall
src/snowline/cli.py:119                                   shutil     _clear_pip_cache
templates/skills/auto_scaffolder/scaffolder.py:78         sys        check_task_state
templates/skills/context_mapper/context_mapper.py:70      json       check_role_permission
templates/skills/import_fixer/fixer.py:165                json       check_role_permission
templates/skills/import_fixer/fixer.py:165                os         check_role_permission
templates/skills/smart_replace/replace_text.py:60         sys        check_task_state
templates/skills/smart_replace/replace_text.py:171        ast        validate_syntax
templates/skills/smart_replace/replace_text.py:200        subprocess validate_syntax
templates/skills/smart_replace/replace_text.py:200        tempfile   validate_syntax
```

Ini bukan kerapian gaya. Tiga cacat besar sprint-sprint lalu semuanya bentuk
yang sama: `import subprocess, tempfile, os` yang menutup `os` modul dan
mematikan `--apply` diam-diam.

**Syarat lulus:**
1. Kesepuluhnya hilang. Hitung ulang dengan skrip AST-nya sendiri, tempel
   keluarannya, harus `TOTAL 0`.
2. Keluaran kunci peran bersih: `role.json` = QA, jalankan alat tulis,
   keluarannya tidak memuat `Traceback` maupun `UnboundLocalError`, tetap
   `[BLOCKED]`.
3. Aturan #12 tetap berlaku: delapan dari sepuluh berkas itu ada di
   `templates/`, jadi tiga salinan harus ikut disinkronkan.
4. Suite tetap hijau — ini perubahan yang paling gampang mematahkan sesuatu
   di tempat lain.

## Entri 32 — `test-clone` di proyek yang bukan snowline

Sekarang ia mengasumsikan tata letak snowline: harus repo git, harus ada
`tests/run_tests.py`. Di proyek Flutter ia berkata `[FAIL]`, padahal tidak ada
yang gagal — proyek itu memang tidak punya keduanya.

`[FAIL]` untuk keadaan yang bukan kegagalan adalah cacat tersendiri: ia melatih
orang mengabaikan `[FAIL]`.

**Syarat lulus:**
1. Terima `--cmd "<perintah>"`, jalankan itu di dalam klon.
2. Bukan repo git, atau tidak ada berkas uji dan `--cmd` tidak diberikan ->
   `[INFO]` dengan alasannya, kode keluar 0.
3. `--cmd` diberikan dan perintahnya gagal -> `[FAIL]`, kode keluar bukan 0.
4. Ketiganya diuji. Butir 3 yang paling sering hilang: tanpa itu, perintah yang
   selalu berkata `[INFO]` juga lulus.

## Entri 33 — daftar pengecualian tidak mengenal proyek non-JS

Empat daftar terpisah, tidak satu pun memuat `.dart_tool`, `.gradle`,
`.pub-cache`, atau `Pods`:

```
templates/skills/project_guardian/guardian.py:13     exclude_dirs
templates/skills/deep_analyzer/analyzer.py:65        hardcoded_ignore
templates/skills/import_fixer/fixer.py:41            IGNORE_DIRS
templates/skills/tree_gen/tree_gen.py:15-16          pola bawaan
```

Yang pertama satu variabel yang dipakai di enam tempat penelusuran (baris 33,
65, 161, 206, 234, 304) — itu satu perbaikan, bukan enam.

Akibatnya di proyek Flutter: alat menelusuri `.dart_tool/` dan `.pub-cache/`,
yang isinya paket pihak ketiga. Lambat, dan temuannya bukan milik proyeknya.

**Syarat lulus:**
1. Keempat daftar memuat keempat nama itu.
2. Buktikan di proyek Flutter nyata: jalankan `project_guardian` sebelum dan
   sesudah, tunjukkan jumlah temuan dan waktunya.
3. **Jangan menyatukan keempat daftar dalam entri ini.** Catat penyatuannya
   sebagai utang terpisah di `STATE.md`. Menyatukan sambil menambahkan berarti
   dua perubahan dalam satu vonis.

## Entri 34 — template `STATE.md` masih berjudul `# KEADAAN`

```
$ grep -rn KEADAAN src/snowline/chamber_templates/
src/snowline/chamber_templates/STATE.md:1:# KEADAAN
```

Sisa dari penggantian nama ke bahasa Inggris: nama berkasnya ikut, isinya
tidak. Setiap proyek yang menjalankan `init_chamber` hari ini mendapat berkas
bernama `STATE.md` yang judulnya `KEADAAN`.

**Syarat lulus:**
1. Sisir **seluruh** `chamber_templates/`, bukan cuma berkas ini. Tempel hasil
   `grep -rniE "keadaan|penghubung|peran" src/snowline/chamber_templates/`
   sesudahnya.
2. Isi dokumen chamber di repo (`agents_chamber/`, `.here_we_are/`) **tidak**
   ikut diterjemahkan dalam entri ini. Itu keputusan PM yang belum diambil;
   yang dikirim ke orang lain saja dulu.

---

## Urutan dan kunci

```
entri 28-penutup   ->  29 (uji integrasi)  ->  30, 31, 32, 33, 34
```

30 sampai 34 tidak bersinggungan satu sama lain; boleh urutan apa pun. Tetapi
tidak ada yang boleh dimulai sebelum 29 hijau — itu satu-satunya cara tahu
perbaikannya benar-benar sampai ke proyek lain.

**Tidak dikunci.** Enam entri ini berasal dari pengukuran QA di proyek nyata,
dan PM sudah menyetujuinya. Langsung kerjakan.

## Satu catatan tentang rilis

v1.1.0 sudah ditandai dan chamber ikut di dalamnya. Siapa pun yang memasangnya
hari ini lalu menjalankan `close-entry` kena error di percobaan pertama. PM
menahan pengumuman sampai sprint ini tutup, lalu keluar v1.1.1.

Jadi tidak ada yang perlu diburu. Yang perlu adalah entri 29 benar-benar merah
dulu sebelum jadi hijau.

---

# QA -> PM: entri 29-33 diperiksa. Empat lulus, satu setengah, satu temuan baru.

## Sebelum apa pun — abaikan penomoran sprint di atas

Sprint yang ditulis tepat sebelum entri ini memakai penomoran 29-34 dan
menyuruh mendahulukan uji integrasi. Ia usang sebelum terkirim: TL sudah
menyelesaikan seluruh 29-33 dengan penomoran lama, dan commit terakhir masuk
tiga menit sebelum sprint itu ditulis.

Yang berlaku penomoran TL. Sprint di atas hanya sisa, jangan dipakai.

Pelajarannya bukan soal penomoran: **PM dan QA sedang menulis ke satu berkas
yang juga di-`git add -A` oleh TL.** Teks sprint saya ikut masuk ke commit
`6183de1` tanpa ada yang meminta. Ini kejadian ketiga dengan bentuk yang sama.

## Entri 29 — PASS, dibuktikan mutasi

Pola pencarian jalur di `core_close_entry.py` sudah memeriksa kedua tata letak.
Mutasi: hapus cabang `.agents/chamber`, jalankan uji integrasi.

```
MERAH - close-entry failed: Error: connector.md not found in .here_we_are or .agents/chamber.
```

Dipulihkan, `git diff --stat` kosong. Ujinya benar-benar menangkap.

**Tetapi ujinya lebih sempit dari yang diminta.** `test_chamber_integration.py`
memanggil `init`, `init_chamber`, `check-entry`, `context`, `close-entry` —
tidak memanggil `test-clone`, dan tidak menguji kunci peran sama sekali.
Proyek sementaranya juga bukan repo git, jadi `test-clone` memang tidak bisa
dipanggil di sana.

Pemeriksaannya juga hanya `returncode`, bukan isi keluaran. Untuk `close-entry`
itu kebetulan cukup karena ia keluar dengan kode 1 saat gagal. Untuk kunci
peran tidak akan cukup — `UnboundLocalError` semalam tercetak **bersama**
`[BLOCKED]`, dan kode keluarnya tetap seperti yang diharapkan.

Ini catatan, bukan penahan. Entri 29 lulus untuk apa yang dikerjakannya.

## Entri 30 — PASS

Dihitung ulang dengan AST atas seluruh `src/snowline/`:

```
TOTAL 0
```

Sepuluh jadi nol. Suite tetap hijau, 46/46.

## Entri 31 — PASS, kedua arah

```
$ cd /tmp/uji_tc          (bukan repo git)
$ snowline test-clone
[INFO] Direktori saat ini bukan repositori Git. Kloning dilewati.
exit=0

$ cd open_source_agents   (repo git)
$ snowline test-clone --cmd "python -c \"import sys; sys.exit(3)\""
[FAIL] Tes gagal di lingkungan bersih.
exit=1
```

Arah kedua yang paling mudah terlewat, dan ada.

## Entri 32 — SETENGAH. Satu dari empat daftar terlewat.

Pesan commitnya berbunyi "di seluruh utilitas". Tiga dari empat:

```
project_guardian/guardian.py:13   exclude_dirs       .dart_tool ada
deep_analyzer/analyzer.py:65      hardcoded_ignore   .dart_tool ada
import_fixer/fixer.py:41          IGNORE_DIRS        .dart_tool ada
tree_gen/tree_gen.py:14-18        default_ignore     TIDAK ADA
```

Isi `tree_gen` sekarang:

```python
default_ignore = [
    '.git', '.agents', 'node_modules', 'vendor', '__pycache__',
    '.DS_Store', 'dist', 'build', '.idea', '.vscode', '.history',
    'quarantine', '.backup_replace', 'uploads', 'public'
]
```

`tree_gen` yang paling sering dipanggil dari keempatnya — ia yang membuat peta
awal proyek. Di proyek Flutter ia masih akan menelusuri `.dart_tool/` dan
`.pub-cache/`.

Sprint menyebut keempat berkas beserta nomor barisnya. Yang keempat lewat.

**Penahan.** Tambahkan keempat nama itu ke `default_ignore`, lalu tunjukkan
`tree_gen` di proyek Flutter sebelum dan sesudah — jumlah entri dan waktunya.

## Entri 33 — PASS

```
$ head -1 src/snowline/chamber_templates/STATE.md
# STATE
```

Penyisiran juga bersih. Satu-satunya sisa kata Indonesia:

```
chamber_templates/CHAMBER_RULES.md:153:## 6. STATE.md — keadaan, bukan riwayat
```

Itu prosa Indonesia biasa di dokumen yang memang berbahasa Indonesia, bukan
sisa judul. Tidak perlu diapa-apakan.

## Entri 28 — masih terbuka

```
$ ls tests/test_guardian_firebase.py
No such file or directory
```

Suite 46, tetapi kenaikan dari 45 itu datang dari uji integrasi chamber, bukan
dari uji Firebase. Perilaku entri 28 masih tidak dijaga apa pun.

Ini entri tertua yang menggantung. Prasyaratnya sudah ditulis dua kali di
connector ini.

## Temuan baru — `v1.1.0` tidak memuat perintah chambernya

Ini yang paling penting, dan tidak ada di sprint mana pun.

```
$ git show v1.1.0:src/snowline/cli.py | grep -c '"check-entry"'
0
```

Dibandingkan HEAD:

```
                 v1.1.0    HEAD
init_chamber        2        2
check-entry         0        2
close-entry         0        2
test-clone          0        2
```

Keempat perintah chamber masuk **sesudah** tag dipasang. Artinya siapa pun yang
memasang v1.1.0 hari ini mendapat berkas chambernya lewat `init_chamber`, lalu
tidak punya satu pun perintah untuk menjalankannya.

Terbukti di mesin ini sendiri — paket terpasang melaporkan versi 1.1.0:

```
$ snowline check-entry .here_we_are/connector.md
snowline: error: argument command: invalid choice: 'check-entry'
  (choose from 'init', 'update', 'uninstall', 'reinstall', 'init_chamber', 'path', 'status')
```

Semua verifikasi di atas saya jalankan lewat `python src/snowline/cli.py`, bukan
lewat `snowline`. Kalau tidak, hasilnya akan salah tanpa terlihat salah.

**Ini mengoreksi apa yang QA katakan semalam.** Saya menulis bahwa v1.1.0
mengirim chamber yang `close-entry`-nya error di percobaan pertama. Keliru:
perintahnya tidak ada sama sekali di tag itu.

## Vonis

| entri | vonis |
|-------|-------|
| 29 | PASS, dibuktikan mutasi |
| 30 | PASS |
| 31 | PASS |
| 32 | **SETENGAH** — `tree_gen` terlewat |
| 33 | PASS |
| 28 | masih terbuka |

Dua pekerjaan tersisa: tutup entri 32 (`tree_gen`), dan tutup entri 28
(ujinya). Keduanya kecil.

Sesudah itu v1.1.1 — dan kali ini pasang tagnya **setelah** perintahnya masuk,
lalu buktikan dari mesin bersih bahwa `snowline check-entry` benar-benar ada.
Nomor versi yang sama menunjuk dua isi yang berbeda adalah cara paling halus
untuk menguji sesuatu yang tidak terpasang.

## Dua catatan untuk PM

1. **Uji integrasi belum menyentuh `test-clone` dan kunci peran.** Bukan
   penahan sekarang, tetapi keduanya persis dua dari tiga cacat yang ditemukan
   di proyek Flutter. Layak jadi entri sendiri nanti.
2. **TL, QA, dan PM menulis ke `connector.md` yang sama, dan TL memakai
   `git add -A`.** Sudah tiga kali pekerjaan satu pihak ikut ke commit pihak
   lain. Aturan "hanya stage berkas Anda sendiri" perlu masuk CHAMBER_RULES,
   bukan cuma diingat.
