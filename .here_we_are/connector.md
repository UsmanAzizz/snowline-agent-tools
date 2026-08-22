
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
