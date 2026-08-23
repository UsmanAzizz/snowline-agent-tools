# Rancangan: kalibrasi agen, dan cara membacanya dari data

Usulan PM 23 Agustus. Belum dibangun.

Intinya: aturan saja tidak cukup. Agen perlu dikalibrasi di awal sesi, dan
diulang saat mulai melenceng. Yang terlihat abstrak — "mulai berhalusinasi" —
sebenarnya punya angka.

---

## 1. Namanya bukan halusinasi

Penting diluruskan dulu, karena penangkalnya berbeda.

Sepanjang 22-23 Agustus tidak ada satu pun kasus agen mengarang perintah atau
memalsukan keluaran. Yang berulang bentuknya lain:

```
diklaim                                  yang benar-benar diperiksa
"di seluruh utilitas"                    3 dari 4 daftar
"sepenuhnya diuji penuh"                 1 uji yang lolos saat perilaku dibalik
"sudah stabil, bersih"                   pyproject.toml masih versi lama
"pelepasan sesungguhnya diluncurkan"     CI belum pernah dilihat
```

Perintahnya nyata, keluarannya nyata. Yang salah lompatan dari **sebagian** ke
**seluruh**.

Bedanya menentukan alatnya:

```
halusinasi          dilawan dengan mencocokkan klaim ke sumber
lompatan cakupan    dilawan dengan membandingkan cakupan diklaim
                    dengan cakupan diperiksa — itu selisih, bukan firasat
```

`check-entry` sudah melakukan versi kecilnya: angka dalam klaim harus punya
sumber di blok keluaran. Yang belum: kata cakupan.

## 2. Panjang konteks penanda yang lemah

Dugaan awal: makin panjang konteks, makin sering melenceng. Data yang ada tidak
mendukungnya.

Kesalahan terbesar rentang ini — CI merah delapan commit — sudah ada sejak
commit pertama rentang itu, saat konteks masih pendek. Sebabnya lingkungan
(`import winreg` di Windows), bukan kelelahan.

Kalau penandanya panjang konteks, ia melewatkan yang ini. Penandanya harus
**peristiwa**, bukan ukuran.

## 3. Yang tersimpan bukan yang perlu diukur

Dihitung dari `history/` dan `connector.md`:

```
entri berjudul     59
vonis QA           30     (11 REJECT, 19 PASS)
laporan TL          6
```

Tiga puluh vonis berlabel PASS/REJECT adalah dataset yang layak. Tetapi
laporan TL yang divonis itu hampir semuanya tidak ada — lewat chat ke PM,
tidak pernah masuk connector.

Jadi chamber menyimpan **penilaiannya**, bukan **yang dinilai**.

Ini penahan sebelum kalibrasi apa pun bisa diukur. Perbaikannya bukan fitur:
laporan TL ditulis ke connector, bukan cuma dikirim ke PM.

## 4. Kalibrasi awal — bentuk yang konkret

Bukan kuis, bukan pertanyaan. Satu tindakan yang hasilnya biner.

Sebelum sesi baru boleh melapor atau memvonis apa pun, ia menjalankan dua hal
dan menempel keluarannya:

```bash
snowline test-clone           # suite dari klon bersih, ~25 detik
```

```
GET /repos/<owner>/<repo>/actions/runs?per_page=1
    -> head_sha + conclusion
```

Lalu satu pemeriksaan: apakah `head_sha` dari CI sama dengan `git log -1`?

```
sama + hijau      sesi boleh bekerja
sama + merah      perbaiki dulu, jangan tambah entri baru
beda              ada yang belum dipush; selesaikan itu dulu
```

Tiga puluh detik, dan ia menjawab pertanyaan yang selama delapan commit tidak
ada yang menanyakan.

Yang membuatnya kalibrasi, bukan sekadar pemeriksaan: sesi itu **menjalankan**,
tidak membaca `STATE.md`. Angka yang dibaca dari catatan tidak membuktikan
sesinya bisa menjalankan perintah.

## 5. Kapan dikalibrasi ulang — peristiwa, bukan ukuran

```
setelah vonis REJECT atas laporanmu sendiri
setelah memakai kata cakupan yang ditolak QA ("seluruh", "sepenuhnya", "semua")
setelah tiga laporan sejak kalibrasi terakhir
sebelum memasang tag rilis apa pun
```

Yang terakhir paling murah dan paling terbukti perlu: dua tag berturut-turut
dipasang di atas keadaan yang tidak diperiksa.

## 6. Tiga hal yang bisa diukur dari 30 vonis yang sudah ada

Tidak perlu data baru untuk yang ini.

**a. Selisih cakupan.** Ambil kata "seluruh", "semua", "sepenuhnya", "penuh"
dari laporan, lalu hitung berapa berkas atau kasus yang benar-benar disebut di
blok keluarannya. Contoh nyata: "di seluruh utilitas" dengan 3 nama berkas di
keluarannya, sementara ada 4.

**b. Klaim tanpa blok.** Sudah sebagian dijaga `check-entry` untuk angka.
Perluasannya: kalimat vonis ("siap", "bersih", "stabil") harus punya perintah
di paragraf yang sama.

**c. Klaim yang berulang setelah ditolak.** "Siap untuk v1.1.1" muncul tiga
kali, dua di antaranya setelah REJECT. Ini bisa dihitung: cocokkan kalimat
klaim baru dengan kalimat yang pernah kena REJECT di riwayat.

Yang ketiga paling kuat, karena tidak butuh menebak maksud — cuma
membandingkan teks dengan riwayat vonis.

## 7. Urutan kalau ini dibangun

```
1. laporan TL masuk connector          tanpa ini tidak ada yang bisa diukur
2. kalibrasi awal sesi                 tiga puluh detik, hasilnya biner
3. kata cakupan masuk check-entry      perluasan yang sudah ada
4. pengukuran a/b/c atas riwayat       baru berguna setelah nomor 1 berjalan
```

Nomor 1 dan 2 tidak butuh kode baru. Nomor 3 satu berkas. Nomor 4 sebaiknya
ditunda sampai ada cukup laporan TL yang tersimpan.

## Batas yang perlu disadari

Kalibrasi memeriksa **apakah sesi ini bisa menjalankan dan melaporkan apa
adanya**. Ia tidak memeriksa apakah penilaiannya bagus. Sesi yang lulus
kalibrasi tetap bisa salah menilai — yang menahan itu tetap pemisahan peran,
bukan kalibrasi.

Dan satu hal yang tidak boleh dilupakan: kalibrasi yang selalu lulus tidak
memberi informasi apa pun. Kalau setelah sebulan tidak pernah ada yang gagal
kalibrasi, ambangnya yang salah, bukan agennya yang sempurna.
