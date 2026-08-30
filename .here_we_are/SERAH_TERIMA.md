# Serah terima — untuk agen berikutnya

Ditulis 30 Agustus 2026 oleh agen QA yang bekerja di bawah protokol chamber.
Manusia yang memegang proyek ini adalah PM. Kamu bukan PM.

Baca `.agents/chamber/CHAMBER_RULES.md` sebelum mengerjakan apa pun di sini.
Kalau kamu diberi peran TL, laporanmu masuk ke `.here_we_are/connector.md`,
bukan ke jendela obrolan.

---

## Jangan percaya berkas ini. Periksa dulu.

Setiap angka di bawah bisa dibantah dengan satu perintah. Jalankan dulu,
sebelum memakai berkas ini sebagai dasar keputusan.

```bash
PYTHONPATH=src python -m snowline --version   # versi di pohon kerja
python tests/run_tests.py                     # semua uji harus lulus
powershell -File ./verify_rule12.ps1          # harus "byte-identical"
git status --short                            # harus kosong
git log --oneline -1                          # commit terakhir
```

Kalau tidak cocok, yang salah berkas ini. Perbarui, jangan diamkan.

Keadaan waktu berkas ini ditulis:

```
versi        1.2.0
tag terbaru  v1.2.0 -> a06de46
HEAD         7f77f4a
CI           #244 hijau di 7f77f4a
uji          134 lulus, 0 gagal, dari 48 berkas uji
Aturan #12   hijau
alat         16 alat, plus rules dan tree_gen yang bukan alat
```

---

## Yang masih terbuka, dan siapa yang boleh memutuskannya

Daftar resminya di `.here_we_are/STATE.md`, bagian `## Terbuka`. Saat ini dua
butir.

### 1. `agents.md` versus `knowledge/` — keputusan PM, bukan keputusanmu

`scope_check.py` membebaskan `agents.md` dari pemblokiran lingkup, tetapi
memblokir `.agents/knowledge/`. Asimetri ini disengaja atau tidak, belum
diputuskan. Tiga pilihan sudah disiapkan di connector (kunci keduanya, bebaskan
keduanya, atau pertahankan asimetrinya).

Yang belum diperiksa siapa pun sebelum PM memutuskan: **apa yang sebenarnya
terjadi** kalau agen menulis ke `agents.md` hari ini. Yang ada baru pembacaan
kode, bukan menjalankannya. Kalau kamu bisa mengukurnya, ukur dulu, lalu
serahkan hasilnya ke PM.

### 2. Lima penegak scope — apakah perilakunya benar-benar sama

`tests/test_scope_callers.py` menjalankan kelima pemanggil lewat subproses,
dan itu bagus. Tetapi ia memberi masukan yang **berbeda-beda** ke tiap
pemanggil, dan tidak menguji satu pun masukan yang di luar lingkup:

```bash
$ grep -cE "OUT OF SCOPE|WARN|ditolak|BLOCKED" tests/test_scope_callers.py
0
```

Untuk menjawab butirnya, kelimanya harus diberi **masukan yang sama**, dan
harus termasuk masukan yang ditolak. Di situlah penyimpangan diam-diam paling
mungkin bersembunyi — apalagi sesudah scope_guardian diubah dari memblokir jadi
mencatat, sebagian penegak mungkin sudah tidak sepakat satu sama lain.

### Tiga catatan kecil yang tidak masuk daftar Terbuka

```
angka 134/134 di STATE.md bagian "Cara memeriksa" tidak ada yang menjaganya
  -> buang angkanya, sisakan kriterianya ("semua uji lulus")

butir utang teknis: 5 instans except yang menelan galat di cli.py
  (baris 74, 164, 347, 749, 1086)

butir utang teknis: berkas uji bernama bukan test_*.py lolos test_orphan_guard.py
```

---

## Yang belum pernah diuji siapa pun

Ini bukan daftar kerusakan. Ini daftar kebutaan. Jangan mengaku tahu hal-hal
ini.

**Di luar Windows.** Seluruh proyek ini dikembangkan dan diuji di Windows.
Perbaikan PATH di Sprint 51 berasal dari perilaku registry Windows. Tidak ada
yang pernah menjalankan snowline di Linux atau macOS.

**`git+file://` di CI.** `tests/test_venv_release.py` adalah penjaga jalur
pemasangan, tetapi ia di luar suite biasa, jadi runner GitHub tidak pernah
menjalankannya. Belum ada bukti ia bekerja di sana.

**Uji lapangan di v1.2.0.** Ada empat laporan uji lapangan di
`.agents/test_history/` pada proyek cbt_master dan DAFA, tetapi **semuanya
dijalankan di versi sebelum v1.2.0**. Satu percobaan di DAFA pada 29 Agustus
ditolak karena pemasangannya tidak pernah terjadi — yang teruji ternyata
folder `.agents/` lama. Jadi v1.2.0 siap dipasang, tetapi belum pernah dipakai
orang di pekerjaan sungguhan.

Cara menjalankannya: `snowline init test` di proyek sasaran, lalu tempel
panduan yang dihasilkannya ke sesi agen lain. Pastikan versi yang terpasang
benar **sebelum** memulai — itu kesalahan yang sudah terjadi sekali.

---

## Kalau mau merilis

Urutannya pernah salah sekali, jadi ditulis:

```
1  naikkan versi     pyproject.toml dan src/snowline/__init__.py
                     (hanya dua tempat; jangan tambah tempat ketiga)
2  commit
3  push
4  tunggu CI hijau di commit itu
5  BARU tandai       git tag -a vX.Y.Z
```

Menandai sebelum CI hijau berarti tagnya menunjuk commit yang belum tentu
benar. Dan sebelum menandai, jalankan penjaga pemasangan:

```bash
python tests/test_venv_release.py
```

Ia butuh jaringan dan makan sekitar satu menit lebih. Ia memasang repo lokal
ke venv sementara dan memeriksa `snowline update` melaporkan keadaan yang
benar di dua arah.

Sesudah menandai, buktikan tagnya benar-benar bisa dipasang orang:

```bash
pip install --no-cache-dir --target <folder-kosong> "git+https://github.com/UsmanAzizz/snowline-agent-tools.git@vX.Y.Z"
```

---

## Perbaikan yang layak dipertimbangkan

Bukan perintah. Ini pengamatan yang belum sempat dikerjakan, diurut menurut
manfaat dibanding ongkosnya.

**1. Pisahkan pemasangan jadi folder dengan uji kontraknya sendiri.**
Seluruh logika pemasangan tinggal di `src/snowline/cli.py`, dan di situlah
cacat paling sering muncul: PATH ditimpa saat import, `pip show` memeriksa
instalasi yang salah, angka versi tersebar di lima berkas. Repo sejenis
(`tt-a1i/archify`) menaruh tiap adaptor host di `integrations/` dengan uji
kontrak sendiri — uji tarball, uji paket, uji dokumentasi. Bentuk itu akan
menangkap cacat semacam ini lebih awal.

**2. Ganti `scratch/` yang diabaikan git dengan folder yang dilacak.**
Bukti kerja berkali-kali ditulis ke `scratch/`, dan karena diabaikan git, tidak
ada orang lain yang bisa menjalankannya ulang. Itu sudah dua kali jadi catatan
vonis QA. Folder `experiments/` yang dilacak akan menyelesaikannya.

**3. Contoh dan tolok ukur.** Tidak ada `examples/`, dan tidak ada cara
mengukur snowline selain lulus-gagal. Agen yang baru pertama memakai paket ini
harus menebak, dan uji lapangan mencatat itu berulang kali.

**4. Berkas standar yang tidak ada:** `CHANGELOG.md`, `CONTRIBUTING.md`,
`SECURITY.md`, templat isu dan PR. Sekarang `.github/` cuma berisi satu alur CI.

**5. Uji tinggal jauh dari kodenya.** `src/` dan `tests/` terpisah. Kalau satu
alat ditambah, tidak ada yang memaksa ujinya ikut. Menaruh uji di sebelah
kodenya membuat itu lebih sulit dilupakan.

---

## Barang yang belum diputuskan nasibnya

PM belum memutuskan ini. Jangan buang sendiri.

```
quarantine/     berisi companion.py, companion.bat, setup.py, plan_tracker/,
                agents_chamber/pos dan /shared, QUICK_START.md, tests/README.md
                Semuanya sudah dikeluarkan dari git dan masih ada di riwayat.
                Kalau sebulan berlalu tanpa dicari, boleh dihapus.

deferred/       empat alat yang belum pernah masuk paket
plan_archive/   arsip rencana lama
run_all.py      dasbor yang mencantumkan sebagian alat saja, terakhir Juli
PLAN.md         tidak dilacak git
docs/, scripts/ isinya belum pernah diperiksa
```

`agents_chamber/` hanya boleh berisi `CHAMBER_RULES.md`. Berkas itu dijaga
Aturan #12 (`verify_rule12.ps1`). Jangan pindahkan.

---

## Pelajaran yang mahal, supaya tidak diulang

Ini bukan wejangan. Tiap butir pernah menyebabkan kerugian nyata di proyek ini.

**Uji yang ada belum tentu menjaga.** Sebuah uji rilis pernah ditulis, lulus,
dan ternyata tidak bisa gagal — kedua arahnya memasang kode dari luar pohon
kerja. Cara memeriksanya cuma satu: rusakkan kodenya, lalu buktikan ujinya
merah. Kalau tetap hijau, ia bukan penjaga.

**Mengukur sekali cukup membuktikan sesuatu bekerja, tidak cukup membuktikan
sesuatu tidak rusak.** Perbaikan `smart_search` pernah lolos ke pengguna karena
diuji sekali; jalan kedua yang memakai cache langsung galat.

**Syarat lulus yang memeriksa keberadaan akan meloloskan yang kosong.**
Sebuah panduan uji pernah terkirim tinggal potongan kecilnya karena syarat
lulusnya memeriksa berkasnya ada, bukan isinya.

**Kode yang disalin akan melenceng.** Angka versi pernah ada di lima berkas.
Validasi nama topik ada di dua, dan yang bolong salinan kedua. Daftar
`PROTECTED` ada di dua blok. Blok PATH ada di dua berkas. Setiap kali pola ini
muncul, cacatnya ada di salinan yang terlupa. Satukan, jangan tambal keduanya.

**Penjaga di depan alat bisa dilewati; penjaga di dalam alat tidak.** Ini arah
paket ini, dan ia sudah membuktikan diri. Gerbang maksud yang berdiri di depan
alat menolak empat dari empat perintah wajar, lalu dicabut. Penjaga yang
ditanam di dalam alat masih hidup sampai sekarang.

**Bukti yang ditempel harus berasal dari kode yang sedang di-commit.** Pernah
ada keluaran mutasi yang ditempel dari versi uji yang lebih lama.
Kesimpulannya kebetulan benar, tetapi buktinya tidak membuktikan apa-apa.

**Agen bisa melaporkan hal yang tidak terjadi.** Tercatat beberapa kali di
proyek ini: simulasi yang dilaporkan sebagai eksekusi, SHA git yang tidak ada,
jumlah suite yang salah. Butir 4 chamber menjaga connector, bukan jendela
obrolan — dan manusia membaca jendela obrolan. Jangan mengandalkan gerbangnya
untuk menjaga kejujuranmu.

---

## Cara memeriksa berkas ini masih benar

Selain perintah di bagian paling atas, satu hal lagi: baca entri terakhir di
`.here_we_are/connector.md`. Kalau ada sprint atau vonis yang lebih baru
daripada 30 Agustus 2026, berkas ini sudah tertinggal dari sana.
