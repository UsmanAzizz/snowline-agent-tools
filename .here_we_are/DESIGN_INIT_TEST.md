# Rancangan: `snowline init test`

26 Agustus 2026. Belum dibangun.

Membuat perintah dari sesuatu yang sudah terbukti nilainya: uji oleh agen yang
belum pernah melihat snowline, di proyek yang bukan repo ini.

Dua kali dijalankan tangan, dua kali menghasilkan temuan yang tidak pernah
muncul dari dalam:

```
pengingat_oli       6 cacat, 3 membuat perintah tidak bisa dipakai orang lain
persuratan_desa     4 temuan, termasuk tidak ada perintah menulis entri
```

---

## Bukan rahasia — tetap

PM menyebutnya "prompt rahasia". Ia dikirim di dalam paket; siapa pun bisa
`cat` isinya. Yang dibutuhkan bukan kerahasiaan melainkan **ketetapan**: teks
yang sama persis tiap kali, supaya hasil dua proyek bisa dibandingkan.

Menyebutnya rahasia justru merugikan — ia rahasia yang bisa dibuka satu
perintah, dan itu merusak kepercayaan pada hal lain yang kita klaim.

## Bentuknya

```
snowline init test
  -> SNOWLINE_TEST.md    prompt tetap, tidak untuk disunting
  -> TEST_REPORT.md      kerangka kosong, diisi agen
```

PM menempelkan isi `SNOWLINE_TEST.md` ke sesi agen. Agen mengisi
`TEST_REPORT.md`.

## Empat aturan di dalam promptnya

Keempatnya dari kegagalan nyata, bukan kehati-hatian.

**1. Jangan sebutkan apa yang harus dicari.** Begitu disebut, yang diuji jadi
kemampuan mengkonfirmasi, bukan menemukan.

**2. Wajib mencatat apa yang harus ditebak.** Ini yang menghasilkan temuan
terbaik dua kali. Bukan "ini rusak", tetapi "aku mencari X dan tidak ketemu".

**3. Larangan memperbaiki.** Tanpa itu agennya menambal sambil jalan dan
datanya hilang.

**4. Wajib mencatat lingkungan.** OS, versi Python, terpasang atau dari sumber.
Cacat terbesar sepanjang 24-26 Agustus semuanya terikat lingkungan — `winreg`,
`pytest`, site-packages. Tanpa kolom ini, laporan dari dua mesin tidak bisa
dibandingkan.

## Kerangka `TEST_REPORT.md`

```
1  Lingkungan          OS, Python, snowline terpasang/sumber, versi
2  Perintah dan keluaran   mentah, termasuk yang gagal
3  Yang tidak jalan    satu baris per hal, dengan perintah dan galatnya
4  Yang harus ditebak  satu baris per hal
5  Ongkos masuk        detik dari perintah pertama sampai mulai bekerja
6  Keputusan tanpa cara memeriksa    <- lihat bagian berikut
7  Catatan bebas       apa pun yang tidak muat di atas
```

Bagian 7 sengaja ada. Temuan yang tidak terduga selalu datang dari tempat yang
tidak disediakan.

## Bagian 6 — mengukur apakah council perlu, tanpa menyebut council

Usul PM: sekalian tanyakan ke agen yang menjalankan uji, apakah chamber butuh
council untuk perencanaan.

**Jangan ditanyakan begitu.** Agen cenderung mengiyakan fitur yang ditawarkan
kepadanya, dan jawabannya akan bilang "ya" tanpa memberi tahu apa-apa.

Yang ditanyakan pertanyaan yang jawabannya **menyiratkan** kebutuhannya:

```
6. Keputusan yang tidak bisa kamu periksa

   Selama tugas ini, adakah keputusan yang kamu ambil tanpa cara memastikan
   keputusan itu benar? Bukan yang salah — yang tidak bisa diperiksa.

   Satu baris per keputusan, dan sebutkan apa yang akan membuktikannya salah
   seandainya ada.

   Kalau tidak ada, tulis: tidak ada.
```

Cara membacanya, dan ini harus tertulis supaya tidak ditafsir bebas nanti:

```
daftarnya kosong atau sepele        council tidak perlu
daftarnya panjang dan berakibat     council punya alasan
```

Satu laporan tidak cukup memutuskan. Yang menentukan pola dari beberapa proyek
— karena pendapat agen yang baru bertemu snowline setengah jam adalah bukti
lemah sendirian, dan jadi bukti hanya kalau beberapa sepakat.

Karena itu bentuk bagian 6 harus tetap sama di tiap laporan, supaya bisa
ditumpuk.

## Yang perintah ini TIDAK lakukan

Tidak menjalankan ujinya. Ia menyiapkan bahan; agen dan PM yang menjalankan.
Perintah yang mencoba mengorkestrasi sesi agen akan terikat pada satu harness,
dan seluruh nilai uji ini justru datang dari dijalankan di harness yang berbeda.

## Syarat lulus kalau dibangun

1. `SNOWLINE_TEST.md` **tidak memuat satu pun** nama cacat yang sudah diketahui.
   Diperiksa dengan membacanya, dan itu bagian tersulitnya.
2. Dua berkasnya UTF-8 tanpa BOM. Sudah lima kali kena.
3. `init test` menolak menimpa `TEST_REPORT.md` yang sudah terisi, kecuali
   `--force`. Laporan lama adalah data.
4. Terdaftar di uji asap.
5. Dijalankan sungguhan sekali di proyek yang bukan repo ini, dan hasilnya
   ditempel — termasuk bagian 6.

## Catatan

Perintah ini menghasilkan pekerjaan, bukan menyelesaikannya. Dua kali
dijalankan tangan menghasilkan sepuluh temuan. Jangan dijalankan di tengah
sprint lain.
