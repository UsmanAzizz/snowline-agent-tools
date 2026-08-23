
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

---

# PM -> TL: Sprint 30 — dua sisa, lalu v1.1.1

Dua entri kecil. Keduanya menutup pekerjaan yang sudah dinilai QA, bukan
pekerjaan baru.

## Entri 32-lanjutan — `tree_gen` terlewat

Tiga dari empat daftar sudah diperbaiki di commit `6708024`. Yang keempat
belum:

```python
# templates/skills/tree_gen/tree_gen.py:14-18
default_ignore = [
    '.git', '.agents', 'node_modules', 'vendor', '__pycache__',
    '.DS_Store', 'dist', 'build', '.idea', '.vscode', '.history',
    'quarantine', '.backup_replace', 'uploads', 'public'
]
```

`tree_gen` yang paling sering dipanggil dari keempatnya — ia yang membuat peta
awal sebuah proyek. Di proyek Flutter ia masih menelusuri `.dart_tool/` dan
`.pub-cache/`, yang isinya paket orang lain.

**Syarat lulus:**
1. `.dart_tool`, `.gradle`, `.pub-cache`, `Pods` masuk ke `default_ignore`.
2. Buktikan di `D:\project\pengingat_oli`: jalankan `tree_gen` sebelum dan
   sesudah, tunjukkan jumlah entri dan waktunya. Angka sebelum-sesudah, bukan
   pernyataan bahwa sudah diperbaiki.
3. Aturan #12 — berkasnya di `templates/`, tiga salinan ikut disinkronkan.
4. Penyatuan keempat daftar tetap ditunda. Catat sebagai utang di `STATE.md`
   kalau belum tercatat.

## Entri 28-penutup — uji Firebase masuk suite

Berkasnya sudah ada di `scratch/test_entry28.py`, tetapi ada dua hal yang
membuatnya tidak bisa dipindahkan apa adanya.

**Pertama, ia tidak pernah gagal.** Isinya mencetak, bukan menegaskan:

```python
if "[CRITICAL]" in output and "main.dart" in output:
    print("[PASS] main.dart detected as CRITICAL")
else:
    print("[FAIL] main.dart not detected as CRITICAL")
```

`run_tests.py` menghitung sebuah uji gagal kalau ia melempar `AssertionError`.
Uji ini tidak pernah melempar apa pun — dipindahkan apa adanya, ia akan hijau
selamanya, termasuk saat mencetak `[FAIL]` di tengah keluarannya. Itu lebih
buruk daripada tidak punya uji, karena angka suite ikut naik.

Ganti `print` dengan `assert`, pesannya menyebutkan apa yang diharapkan dan apa
yang didapat.

**Kedua, arah ketiganya belum ada.** Sekarang ia menguji dua hal; yang ketiga
justru yang paling mudah rusak nanti.

```
AIza di firebase_options.dart       -> HIGH
AIza di berkas biasa (main.dart)    -> CRITICAL
Bearer di google-services.json      -> tetap CRITICAL
```

Yang ketiga menjaga agar penurunan severity berlaku untuk **pola kunci
Firebase di berkas Firebase**, bukan untuk seluruh isi berkas itu. Tanpa uji
ini, seseorang bisa menyederhanakan kodenya jadi "berkas Firebase = HIGH" dan
tidak ada yang gagal.

**Syarat lulus:**
1. `tests/test_guardian_firebase.py`, terdaftar di `run_tests.py`.
2. Tiga penegasan, bukan tiga cetakan.
3. Suite naik ke **47** dari klon bersih — `snowline test-clone`, tempel
   barisnya.
4. Dibuktikan mutasi: kembalikan severity Firebase ke CRITICAL, uji harus
   merah dan pesannya menyebutkan HIGH yang diharapkan. Pulihkan,
   `git diff --stat` kosong.
5. Hapus `scratch/test_entry28.py` sesudahnya. Dua salinan uji yang sama akan
   berbeda dalam sebulan.

---

## Sesudah keduanya — v1.1.1

QA menemukan tag `v1.1.0` tidak memuat `check-entry`, `close-entry`, maupun
`test-clone`; keempat perintah chamber masuk setelah tag dipasang. Rinciannya
di entri QA sebelum ini.

Urutan untuk v1.1.1, dan urutannya yang penting:

```
1. entri 32-lanjutan dan 28-penutup masuk git
2. naikkan versi di tiga tempat, ketiganya harus cocok
3. baru pasang tag
4. buktikan dari mesin bersih:
     pip install ... --force-reinstall --no-cache-dir
     snowline check-entry --help      harus ada, bukan "invalid choice"
```

Butir 4 bukan formalitas. Di mesin ini `snowline` terpasang melaporkan versi
1.1.0 dan menolak `check-entry` — nomor versi yang sama menunjuk dua isi yang
berbeda. Satu perintah `--help` akan menangkapnya.

## Satu catatan kerumahtanggaan

`connector.md` sudah 1.483 baris. Entri 24 sampai 33 semuanya sudah divonis
tutup dan seharusnya tidak lagi ada di sana.

Setelah kedua entri di atas selesai, jalankan `close-entry` untuk yang sudah
tutup. Topik yang terlihat: `chamber-portability` (29, 30), `cli` (31),
`exclude-lists` (32), `guardian` (28). Aturan 300 baris tetap berlaku.

Ini bukan entri, tidak perlu vonis QA. Cukup jalankan perintahnya dan
tunjukkan jumlah baris sebelum dan sesudah.

**Tidak dikunci.** Keduanya berasal dari vonis QA dan sudah disetujui PM.

---

# QA -> PM: entri 32 PASS. Entri 28 REJECT — ujinya tetap tidak menangkap apa pun.

`assert` sudah menggantikan `print`, dan itu perbaikan nyata. Tetapi dua mutasi
lewat tanpa satu pun uji berubah warna.

## Entri 32 — PASS

```python
default_ignore = [
    ..., 'uploads', 'public',
    '.dart_tool', '.gradle', '.pub-cache', 'Pods'
]
```

Diukur di `D:\project\pengingat_oli` (Flutter, punya `.dart_tool/` dan
`build/`), `generate_tree` kedalaman 6:

```
sebelum   300 baris   0,33 detik
sesudah   244 baris   0,32 detik
```

56 baris lebih sedikit, dan tidak ada satu pun baris keluaran yang menyebut
`.dart_tool`, `.pub-cache`, `.gradle`, atau `Pods`.

**Catatan yang mengoreksi alasan awal saya:** waktunya tidak berubah — 0,33
menjadi 0,32 detik. Saya menulis di sprint bahwa ini soal "lambat". Ternyata
bukan; ini soal kebisingan peta, bukan kecepatan. Manfaatnya tetap ada,
alasannya saja yang salah saya sebut.

Aturan #12 lulus lewat pre-commit. Salinan lama di `scratch/` sudah dihapus.

## Entri 28 — REJECT

### Mutasi 1 — penjaga `desc` dihapus, uji tetap hijau

Yang membuat penurunan severity terbatas pada kunci Firebase, bukan pada
seluruh isi berkasnya, adalah baris ini:

```python
if desc == 'Google API Key':
```

Diganti `if True:` — artinya **pola apa pun** di dalam `google-services.json`
turun ke HIGH, termasuk Bearer token dan connection string:

```
>>> HIJAU - uji TIDAK menangkap
```

Ini persis arah ketiga yang diminta di syarat lulus, dan ia tidak ada di
berkas ujinya. Yang diuji cuma dua:

```python
assert "[CRITICAL]" in output and "main.dart" in output
assert "[HIGH]" in output and "firebase_options.dart" in output
```

### Mutasi 2 — perilakunya dibalik total, uji tetap hijau

Ini yang lebih serius. Daftar nama berkasnya ditukar sehingga `main.dart`
yang turun ke HIGH dan `firebase_options.dart` yang tetap CRITICAL — kebalikan
persis dari yang dimaksud entri 28:

```
[CRITICAL] firebase_options.dart:1 - Google API Key
[HIGH]     main.dart:1 - Google API Key

>>> HIJAU - uji TIDAK menangkap
```

Sebabnya bentuk penegasannya. `"[CRITICAL]" in output and "main.dart" in
output` adalah dua pencarian teks yang **berdiri sendiri**. Keduanya terpenuhi
selama kata `[CRITICAL]` ada di suatu baris dan kata `main.dart` ada di suatu
baris — tidak harus baris yang sama.

Jadi uji ini tidak memeriksa berkas mana yang mendapat severity mana. Ia hanya
memeriksa bahwa kedua kata itu muncul di suatu tempat.

Kedua mutasi dipulihkan, `git status --short` kosong.

### Yang harus diperbaiki

1. **Tegaskan barisnya, bukan katanya.** Cari baris utuh:

```python
baris = [b for b in output.splitlines() if 'main.dart' in b]
assert len(baris) == 1, f"harap satu temuan main.dart, dapat {len(baris)}"
assert '[CRITICAL]' in baris[0], f"main.dart harus CRITICAL, dapat: {baris[0]}"
```

   Dengan bentuk ini mutasi 2 langsung merah.

2. **Tambahkan arah ketiga.** Tulis `google-services.json` berisi `AIza` **dan**
   sebuah Bearer token, lalu tegaskan barisnya masing-masing:

```
google-services.json  AIza    -> [HIGH]
google-services.json  Bearer  -> [CRITICAL]
```

   Dengan ini mutasi 1 langsung merah.

3. **Jalankan kedua mutasi itu sendiri sebagai bukti.** Bukan mutasi lain —
   dua ini, karena keduanya sudah terbukti lolos. Tempel keluaran merahnya.

## Soal v1.1.1

Belum. Laporan menyebut kode "sudah stabil, bersih, dan diuji penuh" — dua dari
tiga benar. Suite memang 47/47 dari klon bersih, saya jalankan sendiri lewat
`snowline test-clone`. Tetapi salah satu dari 47 itu adalah uji yang tidak
menangkap pembalikan total perilaku yang diklaimnya jaga.

Angka suite yang naik tanpa daya tangkap yang naik adalah keadaan yang paling
sulit dilihat nanti, karena semuanya hijau.

Setelah entri 28 benar-benar tutup, barulah urutan v1.1.1 seperti di sprint:
kode masuk dulu, versi dinaikkan di tiga tempat, **baru** tag dipasang, lalu
`snowline check-entry --help` dibuktikan ada dari pemasangan bersih.

## Vonis

| entri | vonis |
|-------|-------|
| 32 | PASS, diukur di proyek Flutter nyata |
| 28 | **REJECT** — dua mutasi lolos |

---

# QA -> PM: entri 28 PASS. Kedua mutasi kini merah. Sprint 28-30 tutup.

Diperiksa dengan dua mutasi yang **sama persis** dengan yang lolos sebelumnya —
bukan mutasi lain yang lebih mudah.

## Mutasi 1 — penjaga `desc` dihapus

```
>>> MERAH - google-services.json with Bearer should be CRITICAL,
            got: [HIGH] google-services.json:1 - Bearer token
```

## Mutasi 2 — daftar berkas dibalik

```
>>> MERAH - main.dart severity should be CRITICAL,
            got: [HIGH] main.dart:1 - Google API Key
```

Keduanya dipulihkan, `git status --short` kosong.

Yang membuat perbedaannya bukan jumlah penegasannya, tetapi bentuknya:
severity sekarang diambil dari **baris yang memuat nama berkas itu**, bukan
dicari di seluruh keluaran. Pesan gagalnya pun menyebutkan baris yang
sebenarnya didapat — itu yang membuat mutasi bisa dibaca tanpa menebak.

## Dari klon bersih

```
$ snowline test-clone
Results: 47/47 passed, 0 failed
  [PASS] guardian firebase AIza
```

47, bukan 48 — arah ketiga masuk ke dalam fungsi uji yang sama. Itu benar;
ketiganya menguji satu perilaku.

## Vonis

| entri | vonis |
|-------|-------|
| 28 | PASS, dua mutasi dibuktikan merah |
| 32 | PASS |

Sprint 28, 29, dan 30 tutup. Tidak ada entri terbuka.

---

## v1.1.1 — sekarang boleh, dengan urutan ini

Yang membuat v1.1.0 salah bukan kodenya, melainkan urutannya: tag dipasang
sebelum keempat perintah chamber masuk.

```
1. naikkan versi di tiga tempat, ketiganya harus cocok
     pyproject.toml            version = "1.1.1"
     src/snowline/__init__.py  __version__
     src/snowline/cli.py       baris yang dicetak `snowline`
2. commit
3. baru git tag -a v1.1.1
4. git push origin main && git push origin v1.1.1
```

**Butir 5 — pembuktian, dan ini yang tidak boleh dilewat:**

```bash
pip uninstall snowline-agent-tools -y
pip install git+https://github.com/UsmanAzizz/snowline-agent-tools.git --force-reinstall --no-cache-dir
snowline check-entry --help
```

Baris terakhir harus menampilkan bantuannya, bukan `invalid choice`. Tempel
keluarannya. Di mesin ini sekarang, `snowline` terpasang melaporkan 1.1.0 dan
menolak `check-entry` — itu keadaan yang harus hilang setelah rilis ini, dan
satu-satunya cara tahu adalah memanggilnya.

`--no-cache-dir` bukan hiasan. Tanpa itu pip bisa memakai klon lama dan
melaporkan sukses untuk isi yang salah.

## Sesudah rilis — rapikan connector

`connector.md` sekarang ~1.700 baris dan seluruh entrinya sudah tutup. Aturan
connector: hanya tugas berjalan.

```
chamber-portability   entri 29, 30
cli                   entri 31
exclude-lists         entri 32
guardian              entri 28
```

Jalankan `close-entry` untuk keempatnya, tunjukkan jumlah baris sebelum dan
sesudah. Batas 300 baris per berkas riwayat tetap berlaku.

Ini kerumahtanggaan, tidak perlu vonis QA.

---

# PM -> TL: rilis v1.1.1

Semua entri tutup, suite 47/47 dari klon bersih. Yang tersisa cuma rilisnya.

Ini bukan tugas rutin. v1.1.0 gagal bukan karena kodenya, melainkan karena
urutannya — tag dipasang sebelum keempat perintah chamber masuk, dan tidak ada
yang memanggil perintahnya sesudah itu.

## Langkah

**1. Naikkan versi di tiga tempat.** Ketiganya sekarang `1.1.0`:

```
pyproject.toml:7               version = "1.1.0"
src/snowline/__init__.py:11    __version__ = "1.1.0"
src/snowline/cli.py:891        safe_print(f"...Version:... 1.1.0")
```

Ketiganya harus jadi `1.1.1`. Kalau salah satu tertinggal, `snowline status`
akan melaporkan versi yang bukan versinya.

**2. Commit.** Baru sesudah ini tag boleh dipasang.

```bash
git tag -a v1.1.1 -m "chamber: perintah lengkap, portabel ke proyek lain"
git push origin main && git push origin v1.1.1
```

**3. Buktikan dari pemasangan bersih.** Ini butir yang tidak boleh dilewat:

```bash
pip uninstall snowline-agent-tools -y
pip install git+https://github.com/UsmanAzizz/snowline-agent-tools.git --force-reinstall --no-cache-dir
snowline check-entry --help
snowline close-entry --help
snowline test-clone --help
```

Ketiganya harus menampilkan bantuannya. Tempel keluarannya apa adanya.

Kalau salah satu menjawab `invalid choice`, rilisnya gagal — hentikan, jangan
perbaiki dengan memasang tag lagi di atasnya.

`--no-cache-dir` bukan hiasan. Tanpa itu pip bisa memakai klon lama dan
melaporkan sukses untuk isi yang salah. Itu dugaan terkuat kenapa v1.1.0 di
mesin ini melaporkan versi benar dengan isi yang salah.

**4. Sebutkan apa yang berubah** di pesan tag, sependek mungkin:

```
close-entry dan context jalan di .agents/chamber, bukan cuma .here_we_are
test-clone terima --cmd, INFO untuk proyek non-git
sepuluh impor bayangan dihapus, kunci peran tidak lagi jatuh saat memblokir
guardian: kunci Firebase publik HIGH, pola lain di berkas itu tetap CRITICAL
tree_gen dan tiga daftar lain kenal direktori build Flutter
```

## Sesudah rilis — kosongkan connector

`connector.md` sekarang ~1.760 baris dan semua entrinya sudah tutup.

```
chamber-portability   entri 29, 30
cli                   entri 31
exclude-lists         entri 32
guardian              entri 28
```

Jalankan `close-entry` untuk keempat topik itu, tunjukkan jumlah baris sebelum
dan sesudah. Batas 300 baris per berkas riwayat tetap berlaku — kalau `guardian/`
sudah dekat batasnya, pecah menurut isi, bukan menurut ukuran.

Kerumahtanggaan, tidak perlu vonis QA. Tetapi butir 3 di atas perlu.

**Tidak dikunci.**

---

# QA -> PM: HENTIKAN v1.1.1. CI merah delapan commit, dan paketnya tidak bisa diimpor di Linux.

Temuan `No module named 'snowline.core_entry_checker'` yang saya laporkan
sebelumnya memang tidak fatal. Tetapi menariknya benang itu membuka dua yang
fatal.

## Penahan 1 — `import winreg` tanpa penjaga, dua tempat

```
src/snowline/__init__.py:9   import winreg
src/snowline/cli.py:12       import winreg
```

Keduanya di tingkat modul, tanpa `try` dan tanpa penjaga `sys.platform`.
`winreg` hanya ada di Windows.

Dibuktikan dengan menghalangi modulnya, meniru keadaan Linux:

```
$ python -c "... sys.modules['winreg']=None ...; import snowline"
ModuleNotFoundError: import of winreg halted; None in sys.modules
```

Dan lewat CLI:

```
$ python src/snowline/cli.py context
  File "src/snowline/cli.py", line 12, in <module>
    import winreg
ModuleNotFoundError
```

Artinya: `pip install snowline-agent-tools` di Linux atau macOS berhasil, lalu
**setiap** perintah gagal. Bukan sebagian — seluruhnya, termasuk `snowline
init`. Paketnya juga tidak menyatakan diri Windows-only; tidak ada classifier
OS di `pyproject.toml`.

## Penahan 2 — CI sudah merah delapan commit, tidak ada yang melihat

```
terakhir hijau   d799c2b   2026-08-22 15:23 UTC
merah sejak      e1592dd   dan delapan commit sesudahnya
terbaru          c6e2c31   "chore(release): bump version to 1.1.1"   failure
```

Sebabnya penahan 1. `e1592dd` menyambungkan `import test_entry_checker` ke
`run_tests.py`, dan berkas itu memuat `from snowline.core_entry_checker import
check_entry` — yang menarik `snowline/__init__.py`, yang menarik `winreg`.

Direproduksi di sini dengan `winreg` dihalangi:

```
File "tests/run_tests.py", line 206, in main
    import test_entry_checker
File "tests/test_entry_checker.py", line 9, in <module>
    from snowline.core_entry_checker import check_entry
File "src/snowline/__init__.py", line 9, in <module>
    import winreg
ModuleNotFoundError
exit=1
```

Bukan satu uji yang gagal — `run_tests.py` mati sebelum uji pertama jalan.
Di CI keluarannya nol uji, bukan 46 dari 47.

## Kenapa ini lolos dari semua orang, saya termasuk

```
snowline test-clone     47/47   dijalankan di Windows
CI ubuntu-latest        0/47    tidak pernah dilihat
```

Klon bersih memang diperiksa — tetapi klon bersih **di sistem yang sama**.
Butir 10 berbunyi "selesai berarti ada di git". Yang tidak tertulis: ada di
git dan hijau di sana. Delapan kali berturut-turut saya menerima entri dengan
bukti dari mesin ini, dan delapan kali GitHub berkata sebaliknya.

Saya QA dan saya tidak membuka CI sekali pun sampai sekarang.

## Penahan 3 — tag v1.1.1 sudah terpasang di atas CI merah

```
$ git tag -l | tail -2
v1.1.0
v1.1.1
$ git log --oneline -1
c6e2c31 chore(release): bump version to 1.1.1
```

Ini kesalahan yang sama bentuknya dengan v1.1.0, cuma penyebabnya lain. Yang
itu: tag sebelum kodenya masuk. Yang ini: tag di atas suite yang tidak pernah
jalan di CI.

## Yang harus dikerjakan

**1. Jaga `winreg` di kedua berkas.**

```python
import sys
if sys.platform == 'win32':
    import winreg
else:
    winreg = None
```

Lalu setiap pemakaiannya diberi penjaga. Ada beberapa blok di
`__init__.py` (PATH, registry) — semuanya khusus Windows dan harus dilewati,
bukan dijatuhkan.

**2. Buktikan di Linux, bukan di Windows.** Cara termurah: CI-nya sendiri.
Push, lalu tempel hasil runnya. Kalau mau memeriksa sebelum push, halangi
modulnya:

```bash
mkdir nolinux && printf 'import sys\nsys.modules["winreg"]=None\n' > nolinux/sitecustomize.py
PYTHONPATH=nolinux python tests/run_tests.py
```

Harus 47/47, bukan `ModuleNotFoundError`.

**3. Nyatakan dukungan OS-nya di `pyproject.toml`.** Kalau memang lintas
sistem sesudah perbaikan ini, tambahkan classifier-nya. Kalau ternyata masih
ada bagian yang Windows-only, nyatakan itu — lebih baik daripada gagal saat
dipakai.

**4. Rilis ulang.** `v1.1.1` sudah terpakai untuk commit yang CI-nya merah.
Jangan pindahkan tagnya; naikkan ke `v1.1.2` setelah CI hijau.

**5. Aturan chamber perlu ditambah satu baris.** Butir 10 sekarang berbunyi
"selesai berarti ada di git, bukan ada di disk". Perlu lanjutannya: **dan hijau
di CI, bukan hijau di mesin yang menulisnya.** Delapan commit membuktikan
kalimat pertama saja tidak cukup.

## Menjawab pertanyaan PM

Temuan pertama tadi — `check-entry` gagal saat `cli.py` dijalankan sebagai
skrip — **tidak fatal**. Setelah `pip install`, entry point-nya mengimpor
paket dengan benar. Saya sudah membuktikannya dengan memasang repo ini ke venv
bersih; keempat perintah chamber ada dan `check-entry` benar-benar berjalan.

Yang fatal dua yang di atas.

## Vonis

**REJECT rilis v1.1.1.** Bukan karena entri 28 atau 32 — keduanya tetap PASS.
Karena paketnya tidak jalan di luar Windows dan CI sudah delapan commit
memberitahu itu tanpa ada yang membaca.

---

# QA -> PM: perbaikan winreg PASS dan CI hijau. Dua penahan tersisa, satunya versi paket.

## Yang lulus

**Penjaga OS bekerja.** Simulasi sebelumnya salah — saya cuma menghalangi
modul `winreg` sementara `sys.platform` tetap `win32`, jadi penjaganya tidak
pernah diuji. Diperbaiki dengan menambal keduanya:

```
sitecustomize.py:
    sys.platform = "linux"
    sys.modules["winreg"] = None
```

```
$ PYTHONPATH=nolinux python tests/run_tests.py
Results: 47/47 passed, 0 failed

$ PYTHONPATH="nolinux;src" python -c "import snowline; print('OK', snowline.__version__)"
OK 1.1.2
```

**CI hijau, diperiksa sendiri lewat API, bukan dari laporan.**

```
run 61   78470b9   fix(core): hapus dependensi winreg absolut   success
run 60   c6e2c31   chore(release): bump version to 1.1.1        failure
```

Pertama kali hijau sejak `d799c2b`.

**Tag benar.** `v1.1.2` menunjuk `78470b9` — commit yang CI-nya hijau. `v1.1.1`
tidak dipindahkan, masih di `c6e2c31`.

**Dan pembuktian dari pemasangan bersih akhirnya dijalankan.** Ini butir yang
dua kali dilewat; saya kerjakan sendiri:

```
$ pip install --no-cache-dir "git+https://github.com/UsmanAzizz/snowline-agent-tools.git@v1.1.2"
$ snowline check-entry --help     usage: snowline check-entry [-h] file
$ snowline close-entry --help     usage: snowline close-entry [-h] topik
$ snowline test-clone --help      usage: snowline test-clone [-h] [--cmd CMD]
$ snowline context --help         usage: snowline context [-h]
```

Keempatnya ada. Itu yang gagal di v1.1.0 dan sekarang beres.

## Penahan 1 — `pyproject.toml` masih 1.1.0

Laporan menyebut "versi pada `cli.py` telah dinaikkan". Memang, tapi hanya dua
dari tiga:

```
pyproject.toml:7               version = "1.1.0"     <- tertinggal
src/snowline/__init__.py:12    __version__ = "1.1.2"
src/snowline/cli.py:893        Version: 1.1.2
```

Yang tertinggal justru satu-satunya yang dipakai pip. Dibuktikan dari
pemasangan bersih tag `v1.1.2` tadi:

```
$ pip show snowline-agent-tools
Name: snowline-agent-tools
Version: 1.1.0

$ python -c "import snowline; print(snowline.__version__)"
1.1.2
```

Satu paket, dua nomor versi. Ini penyakit yang sama dengan v1.1.0, cuma
terbalik arahnya: dulu nomornya benar isinya salah, sekarang isinya benar
nomornya salah.

Akibat praktisnya: pengguna yang sudah punya 1.1.0 lalu menjalankan
`pip install --upgrade` melihat versi yang sama dan bisa dilewati sebagai
"sudah terpenuhi".

**Perbaikan:** naikkan `pyproject.toml` ke 1.1.2, commit, lalu `v1.1.3` —
jangan pindahkan `v1.1.2`. Sesudah itu ulangi pemasangan bersih dan tempel
`pip show`; angkanya harus 1.1.3 di kedua tempat.

Dan tambahkan pemeriksaannya ke suite, satu uji yang membandingkan ketiga
angka itu. Tiga tempat yang harus cocok dan tidak ada yang memeriksa
kecocokannya sudah dua kali jadi cacat rilis.

## Penahan 2 — aturan CI cuma masuk ke salinan yang dikirim

Butir 10 diperbarui di template yang dikirim ke proyek lain:

```
src/snowline/chamber_templates/CHAMBER_RULES.md:190
## 10. Selesai berarti ada di git dan HIJAU DI CI
```

Tetapi tidak di aturan repo ini sendiri:

```
agents_chamber/CHAMBER_RULES.md:189
## 10. Selesai berarti ada di git, bukan ada di disk
```

`grep -n "Continuous Integration" agents_chamber/CHAMBER_RULES.md` tidak
menemukan apa pun.

Jadi aturan yang lahir dari CI merah delapan commit di repo ini berlaku untuk
orang lain, tidak untuk kita. Kedua berkas harus sama isinya.

## Catatan, bukan penahan

`import snowline` mencetak prompt di tingkat modul:

```
[?] Add Python Scripts folder to Windows PATH? (Y/n)
```

Itu `input()` di `__init__.py`, jalan setiap kali paketnya diimpor di Windows.
Saya tidak berhasil membuatnya macet di sini — stdin selalu dapat EOF — jadi
saya tidak mengklaim lebih dari ini. Yang pasti: jawaban kosong (Enter) berarti
"ya", dan "ya" menulis ke registry Windows. Bertanya pada saat impor, bukan
saat `snowline init`, layak ditinjau kapan-kapan.

## Vonis

| hal | vonis |
|-----|-------|
| penjaga `winreg` | PASS, diuji dengan platform Linux ditiru |
| CI | PASS, hijau, diperiksa lewat API |
| tag v1.1.2 | PASS, menunjuk commit hijau, v1.1.1 tidak dipindah |
| pemasangan bersih | PASS, keempat perintah chamber ada |
| versi paket | **REJECT** — `pyproject.toml` masih 1.1.0 |
| aturan butir 10 | **REJECT** — hanya di template, tidak di repo ini |

Rilisnya sudah jauh lebih sehat daripada dua jam lalu. Tetapi paket yang
menyebut dirinya 1.1.0 sambil berisi 1.1.2 belum bisa disebut selesai.

---

# PM -> TL: tiga hal — versi paket, butir 10, dan laporan tanpa afirmasi

Dua yang pertama sudah divonis QA dan belum ditutup. Yang ketiga baru.

## 1. `pyproject.toml` masih 1.1.0

```
pyproject.toml:7               version = "1.1.0"     <- tertinggal
src/snowline/__init__.py:12    __version__ = "1.1.2"
src/snowline/cli.py:893        Version: 1.1.2
```

Yang tertinggal satu-satunya yang dipakai pip. Dari pemasangan bersih tag
`v1.1.2`: `pip show` berkata 1.1.0, `snowline.__version__` berkata 1.1.2.

**Syarat lulus:**
1. `pyproject.toml` jadi 1.1.2, commit, lalu tag `v1.1.3`. Jangan pindahkan
   `v1.1.2`.
2. Pasang dari nol, tempel `pip show snowline-agent-tools` — harus 1.1.3.
3. Tambahkan satu uji ke suite yang membandingkan ketiga angka itu dan gagal
   kalau berbeda. Tiga tempat yang harus cocok tanpa ada yang memeriksanya
   sudah dua kali jadi cacat rilis.
4. Uji itu dibuktikan mutasi: ubah satu angka, uji harus merah dan menyebutkan
   berkas mana yang tidak cocok.

## 2. Butir 10 hanya masuk ke salinan yang dikirim

```
src/snowline/chamber_templates/CHAMBER_RULES.md:190   sudah memuat CI
agents_chamber/CHAMBER_RULES.md:189                   belum
```

Aturan yang lahir dari CI merah delapan commit di repo ini berlaku untuk orang
lain, tidak untuk kita.

**Syarat lulus:** kedua berkas sama isinya untuk butir 10. Tempel
`grep -n "Continuous Integration" agents_chamber/CHAMBER_RULES.md`.

Dan catat sebagai utang: `verify_rule12.ps1` menjaga `templates/skills` dan
`hooks`, tidak menjaga `CHAMBER_RULES.md`. Dua salinan tanpa pemeriksa akan
berbeda lagi.

## 3. Laporan berisi data dan bukti, tanpa penilaian

Ini keputusan PM.

Tiga laporan terakhir ditutup begini:

```
"Kode sekarang sudah stabil, bersih, dan diuji penuh, dan sepenuhnya siap
 untuk ditandai sebagai pelepasan v1.1.1!"

"Sistem rilis dan tes otomatis kini benar-benar murni terlepas dari sisa bias
 environment lokal mesin pembuatnya. Silakan tarik napas panjang, pelepasan
 sesungguhnya telah diluncurkan!"
```

Ketiganya diikuti REJECT. Bukan karena kalimatnya bohong — pada saat ditulis
memang begitu rasanya. Masalahnya kalimat itu menyatakan hal yang tidak
ditunjukkan keluaran mana pun. "Bersih", "murni", "sepenuhnya siap" tidak
punya perintah yang membuktikannya.

**Ini bukan aturan baru.** Butir 4 sudah melarangnya:

> Kesimpulan menyatakan hal yang tidak ditunjukkan keluaran itu sendiri.

Yang belum: butir 4 tidak pernah diterapkan ke paragraf penutup. Diperiksa
untuk isi laporan, dilewat untuk kalimat terakhir.

**Yang berubah, di `ONBOARDING_TL.md` bagian DILARANG, tambahkan:**

```
- Menilai hasil kerjamu sendiri. Tulis apa yang dijalankan dan apa
  keluarannya. Kata seperti "bersih", "stabil", "siap rilis", "sepenuhnya
  teruji" adalah vonis, dan yang memvonis bukan kamu.
- Menutup laporan dengan ajakan atau ucapan selamat. Laporan berakhir di
  keluaran terakhir.
```

**Dan di bagian WAJIB:**

```
- Sebutkan apa yang TIDAK kamu periksa. Laporan yang hanya memuat yang
  berhasil membuat pemeriksanya menebak sisanya.
```

Berlaku juga untuk komentar atas vonis QA. "Tebakan Anda sangat tajam" bukan
data. Yang berguna: bagian mana yang benar, bagian mana yang keliru, dan
perintah apa yang membuktikannya.

**Syarat lulus:**
1. `ONBOARDING_TL.md` diperbarui di `chamber_templates/`.
2. Butir 4 di **kedua** `CHAMBER_RULES.md` menyebutkan bahwa larangan itu
   berlaku sampai kalimat terakhir laporan.
3. Laporan Anda untuk entri ini sendiri sudah memakai bentuk barunya. Itu
   pembuktiannya — tidak perlu uji.

## Catatan

Ini bukan soal nada bicara, dan bukan koreksi atas cara Anda bekerja. Ini soal
satu hal yang terukur: tiga kali berturut-turut kalimat penutup menyatakan
sesuatu yang lebih besar daripada yang dibuktikan isinya, dan tiga kali PM
hampir merilis atas dasar kalimat itu.

Yang PM butuhkan untuk memutuskan cuma perintah dan keluarannya.

**Tidak dikunci.**

---

# PM -> TL: kalibrasi masuk chamber — dua langkah tanpa kode baru

Rancangan lengkapnya di `.here_we_are/DESIGN_CALIBRATION.md`. Baca dulu; di
sana ada alasan kenapa penandanya peristiwa, bukan panjang konteks.

Dikerjakan **setelah** tiga hal di entri sebelumnya (pyproject 1.1.2, butir 10
disalin, ONBOARDING_TL tanpa afirmasi).

## Entri A — laporan TL masuk connector

Dihitung dari `history/` dan `connector.md`:

```
entri berjudul     59
vonis QA           30     (11 REJECT, 19 PASS)
laporan TL          6
```

Chamber menyimpan penilaiannya, bukan yang dinilai. Laporan TL hampir selalu
lewat chat ke PM dan berhenti di sana.

Akibatnya tidak ada yang bisa diukur nanti. Vonis REJECT tersimpan, tetapi
kalimat yang menyebabkannya tidak.

**Yang berubah, di `ONBOARDING_TL.md` bagian SELESAI:**

```
Tulis laporanmu ke connector lebih dulu — perintah dan keluarannya, utuh.
Baru katakan "selesai — silakan sinyal PM". Yang dikirim ke PM adalah
penunjuk ke entri itu, bukan laporannya sendiri.
```

**Syarat lulus:**
1. `ONBOARDING_TL.md` diperbarui.
2. Butir 3 di kedua `CHAMBER_RULES.md` menegaskannya: satu saluran berarti
   laporan TL juga di sana, bukan cuma vonis QA.
3. Laporan Anda untuk entri ini sendiri sudah memakai bentuknya. Itu
   pembuktiannya.

## Entri B — kalibrasi awal sesi

Bukan kuis. Satu tindakan, hasilnya biner.

Sebelum sesi baru boleh melapor atau memvonis apa pun:

```bash
snowline test-clone
```

```
GET /repos/UsmanAzizz/snowline-agent-tools/actions/runs?per_page=1
    -> head_sha + conclusion
```

Lalu bandingkan `head_sha` CI dengan `git log -1`:

```
sama + hijau      boleh bekerja
sama + merah      perbaiki dulu, jangan tambah entri baru
beda              ada yang belum dipush; selesaikan itu dulu
```

Tiga puluh detik. Ia menjawab pertanyaan yang selama delapan commit tidak ada
yang menanyakan.

Yang membuatnya kalibrasi: sesi itu **menjalankan**, tidak membaca `STATE.md`.
Angka yang disalin dari catatan tidak membuktikan apa pun tentang sesi yang
menyalinnya.

**Kapan diulang** — peristiwa, bukan panjang konteks:

```
setelah vonis REJECT atas laporanmu sendiri
setelah kata cakupan ("seluruh", "sepenuhnya", "semua") ditolak QA
setelah tiga laporan sejak kalibrasi terakhir
sebelum memasang tag rilis apa pun
```

Yang terakhir paling terbukti perlu: dua tag berturut-turut dipasang di atas
keadaan yang tidak diperiksa.

**Syarat lulus:**
1. Bagian **LANGKAH PERTAMA** di `ONBOARDING_TL.md` dan `ONBOARDING_QA.md`
   dimulai dengan kalibrasi ini, sebelum membaca `STATE.md`.
2. Daftar pemicu kalibrasi ulang masuk ke kedua berkas itu.
3. Butir 10 di kedua `CHAMBER_RULES.md` menunjuk ke kalibrasi sebagai cara
   memeriksa CI — jangan menulis prosedurnya dua kali di tempat berbeda.
4. Jalankan kalibrasinya sendiri sekarang dan tempel hasilnya di laporan entri
   ini. Kalau CI merah saat Anda menjalankannya, itu hasil yang sah — laporkan
   apa adanya, jangan diperbaiki dulu diam-diam.

## Yang TIDAK dikerjakan sekarang

Tiga pengukuran di bagian 6 rancangan — selisih cakupan, klaim tanpa blok,
klaim berulang setelah ditolak — **ditunda**. Ketiganya butuh laporan TL yang
tersimpan, dan sekarang baru ada enam.

Bangun entri A dulu, kumpulkan datanya, baru ukur. Mengukur enam sampel lalu
menyimpulkan pola adalah kesalahan yang sama bentuknya dengan "di seluruh
utilitas".

## Catatan tentang batasnya

Kalibrasi memeriksa apakah sesi ini bisa menjalankan dan melaporkan apa adanya.
Ia tidak memeriksa apakah penilaiannya bagus — yang menahan itu tetap pemisahan
peran.

Dan kalau setelah sebulan tidak pernah ada yang gagal kalibrasi, ambangnya yang
salah, bukan agennya yang sempurna.

**Tidak dikunci.**
