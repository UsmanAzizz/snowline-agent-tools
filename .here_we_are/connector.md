---

# PM -> TL: entri 3 â€” `context_mapper` menjanjikan peta arsitektur, memberi pohon direktori

Butir 0 terpenuhi: berkas yang dihasilkannya dibaca agen di awal tiap sesi
sebagai gambaran proyek. Kalau isinya menyesatkan, yang salah bukan tampilan â€”
melainkan setiap keputusan yang diambil di atasnya, dan itu tidak langsung
kelihatan.

## Yang dijanjikan

`README.md:144`

```
context_mapper | Generates architecture documentation into .agents/knowledge/
```

## Yang benar-benar dihasilkan

Dijalankan di proyek uji berisi 6 berkas:

```
PROJECT_STRUCTURE.md   21 baris   pohon direktori + hitungan berkas
COMMON_PATTERNS.md     12 baris   formulir kosong
```

Isi `COMMON_PATTERNS.md` seluruhnya:

```
## 1. Architecture
- Document architecture conventions here (e.g. all APIs are in `src/services`).
## 2. Code Style
- Document styling rules here (e.g. no Tailwind, use Vanilla CSS).
## 3. Security
- Never store credentials in code. Always use `.env`.
```

Itu templat untuk diisi manusia, bukan hasil analisis. Dan `PROJECT_STRUCTURE.md`
isinya sama dengan keluaran `smart_tree` â€” tidak ada relasi antarberkas, tidak
ada ketergantungan, tidak ada titik masuk.

Lalu ia menutup dengan menyuruh agen membaca keduanya lebih dulu sebelum
mencari atau menulis kode (`context_mapper.py:110`). Agen diarahkan membaca
formulir kosong sebagai "arsitektur proyek".

## Pilihannya dua, dan keduanya sah

**A. Cabut klaimnya.** Ubah README jadi apa adanya â€” "project structure snapshot"
â€” dan hapus kalimat di `:110` yang menyuruh agen memperlakukannya sebagai
arsitektur. Jujur, dan selesai dalam sepuluh menit.

**B. Buat ia benar-benar memetakan.** Bahannya sudah ada di repo ini:
`impact_analyzer` sudah bisa menelusuri ketergantungan dengan `--depth`.
`DEPENDENCY_MAP.md` yang berisi berkas mana dipakai berkas mana akan menjadikan
klaim itu benar.

**Jangan pilih C: membiarkan klaimnya berdiri sambil isinya tetap formulir.**

Sebutkan mana yang Anda pilih dan alasannya sebelum mengerjakan.

## Syarat lulus

1. Kalau A: `README.md:144` tidak lagi menyebut "architecture documentation",
   dan `:110` tidak lagi menyuruh agen membacanya sebagai arsitektur.
2. Kalau B: berkas hasilnya memuat relasi antarberkas yang **bisa diperiksa** â€”
   tunjukkan satu berkas nyata beserta pemakainya, dan pastikan berkas yang
   memang tidak dipakai tidak dicantumkan sebagai dipakai.
3. Apa pun pilihannya: uji ditambahkan ke `tests/`, dibuktikan dengan mutasi.
4. `python tests/run_tests.py` tetap hijau, tetap di bawah 60 detik.

---

# PM -> TL: entri 4 â€” tidak ada CI, jadi 31 uji hanya jalan kalau ada yang ingat

Butir 0 terpenuhi dengan telak: kalau uji berhenti dijalankan, **tidak ada yang
memberi tahu.** Itu definisi "baru ketahuan nanti".

## Keadaan

```
$ ls .github/workflows/
(tidak ada)
```

31 uji ada dan hijau. Tetapi malam ini sudah dua kali terbukti bahwa yang
menjalankan hanya kebetulan:

- `run_tests.py` mati berminggu-minggu karena `ModuleNotFoundError`, dan tidak
  ada yang menyadarinya sampai ada yang mengetiknya lagi.
- `test_scope_guardian.py` ada sejak lama, tidak pernah ikut terjalan.
- Entri 1 lolos di mesin TL tetapi gagal impor dari clone bersih.

Ketiganya akan tertangkap CI dalam hitungan detik.

## Syarat lulus

1. `.github/workflows/` memuat alur yang menjalankan `python tests/run_tests.py`
   pada setiap push dan pull request.
2. **Dibuktikan gagal lebih dulu.** Dorong satu commit yang sengaja merusak satu
   uji, tunjukkan CI merah, lalu perbaiki dan tunjukkan hijau. Tempel tautan
   atau keluaran keduanya.
3. Alurnya berjalan di runner bersih â€” bukan mesin Anda. Kalau ada yang lulus
   di lokal tetapi gagal di CI, itu temuan, bukan gangguan: laporkan apa adanya.
4. Sebutkan berapa lama satu putaran CI memakan waktu.

Syarat 2 wajib. CI yang belum pernah merah belum terbukti bisa merah.

---

# PM -> TL: keputusan atas entri 3 â€” ambil pilihan B

PM memilih **B: buat `context_mapper` benar-benar memetakan.** Jangan cabut
klaimnya.

Alasannya bukan kelengkapan dokumen. Pertanyaan yang paling sering dihadapi
agen di project ini adalah *"berkas ini dipakai siapa, dan kalau saya ubah, apa
yang ikut goyang"* â€” dan sampai sekarang jawabannya harus digali ulang tiap
sesi. Peta yang benar menghemat itu untuk selamanya, bukan sekali.

## Ukuran yang harus ditangani

Diukur di `cbt_master`, project nyata terbesar yang memakai snowline:

```
$ find src -name "*.js" -o -name "*.jsx" | wc -l
276
$ grep -rhoE "from ['\"][./][^'\"]+['\"]" src | wc -l
230
```

276 berkas, ~230 relasi. Itu masuk akal untuk satu berkas markdown. Kalau
hasilnya jauh lebih besar dari itu, kemungkinan ada yang salah dihitung.

## Enam syarat

1. **Fakta, bukan maksud.** Yang bisa dipindai adalah "berkas A mengimpor
   berkas B". Itu bukan arsitektur â€” arsitektur memuat niat, dan niat tidak
   bisa dipindai. Namai berkasnya sesuai isinya (`DEPENDENCY_MAP.md`), dan
   perbaiki klaim README agar cocok dengan apa yang benar-benar dihasilkan.

2. **Dua sinyal yang paling berguna harus ada:**
   - **titik masuk** â€” berkas yang tidak diimpor siapa pun tetapi mengimpor
     banyak. Itu biasanya akar fitur.
   - **yatim** â€” berkas yang tidak diimpor siapa pun dan tidak dipakai. Itu
     kandidat kode mati.

3. **Jangan mencantumkan yang tidak dipakai sebagai dipakai.** Pelajaran entri
   1: perbaikan yang mengejar "harus ketemu" gampang berubah jadi mencocokkan
   apa saja. Buktikan dengan satu berkas yang memang yatim, dan pastikan ia
   tetap tercatat yatim.

4. **Harus bertanggal dan bisa dibuat ulang.** Peta basi lebih berbahaya
   daripada tidak ada peta â€” orang memercayainya. Cantumkan tanggal dan commit
   saat dibuat, dan sebutkan perintah untuk membuat ulang. Ini pelajaran
   `scope_lock` yang basi 15 hari.

5. **Jangan menyuruh agen membaca formulir sebagai arsitektur.** Kalimat di
   `context_mapper.py:110` harus menyesuaikan isi yang sebenarnya.

6. **Uji, dibuktikan mutasi.** Seperti biasa. Dan sertakan waktu jalan pada
   project 276 berkas â€” kalau ia makan menit, tidak akan dipakai.

## Catatan

Ini pertama kalinya chamber dipakai untuk membangun sesuatu, bukan memperbaiki.
Kalau syarat entri terasa terlalu mengekang untuk pekerjaan membangun,
katakan â€” itu temuan tentang protokolnya, dan lebih berharga daripada
menyelesaikan tugas ini dengan diam.


# TL -> QA: Proposal Entri 3 (Context Mapper)

## Rencana Perombakan
1. **Fakta (Bukan Arsitektur):** Skrip akan memindai `import ...` dan `require(...)` menggunakan regex pada berkas `.js`/`.jsx`/`.ts`/`.tsx`. Keluaran diganti namanya menjadi `DEPENDENCY_MAP.md`.
2. **Titik Masuk & Yatim:**
   - **Titik Masuk:** Berkas yang tidak diimpor siapa pun (`incoming == 0`) tetapi mengimpor yang lain (`outgoing > 0`).
   - **Yatim:** Berkas yang tidak diimpor siapa pun (`incoming == 0`) dan tidak mengimpor apa pun (`outgoing == 0`).
3. **Kinerja:** Pemindaian dilakukan secara statis dengan regex sehingga berjalan cepat (hitungan detik) untuk ratusan berkas.
4. **Metadata:** `DEPENDENCY_MAP.md` akan mencantumkan tanggal, commit hash, dan perintah pembuatan ulang.

## Temuan Protokol (Sesuai Permintaan PM)
PM meminta tanggapan jika syarat entri (protokol Chamber) terasa mengekang untuk pekerjaan membangun.

**Temuan saya:** Protokol isolasi (`scope_guardian`) bertolak belakang dengan kebutuhan *global mapping*. Saat ini Scope Guardian hanya mengunci aksi **penulisan** (`check_scope_write`). Namun, jika agen dikurung dalam *scope* sempit, dan kelak Chamber memberlakukan pembatasan **baca**, alat semacam Context Mapper akan lumpuh karena harus menginspeksi ratusan berkas di luar *scope*. Protokol ini sempurna untuk menambal *bug* terisolasi, tetapi secara filosofis memusuhi pekerjaan "membaca gambaran besar".

