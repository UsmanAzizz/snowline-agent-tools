# Metode — ablasi retrospektif

Dipakai supaya korpus berbeda bisa dibandingkan. Parameter tidak boleh diubah
di tengah jalan; kalau diubah, catat dan ukur ulang seluruhnya.

## Kenapa metode ini

Datanya sudah ada di disk. Mengukurnya tidak butuh panggilan model — penting,
karena yang diuji justru soal biaya.

**Yang TIDAK dipakai:** memutar ulang tugas dengan dan tanpa perkakas. Model
tidak deterministik, sampelnya kecil, biayanya besar, hasilnya tidak
terpisahkan dari derau.

## Urutan langkah

### 1. Kecukupan DULU

Dijalankan sebelum menghitung total penghematan, supaya penilaian tidak
condong oleh angka yang menggiurkan.

Ambil sampel acak >=20 peristiwa **dari peristiwa yang benar-benar membuang
sesuatu** (bukan dari seluruh populasi — tingkat kegagalan harus dikondisikan
pada pembuangan yang betul-betul terjadi).

Untuk tiap sampel: baca apa yang agen lakukan 5 giliran berikutnya. Apakah
bagian yang dibuang memuat baris, nilai, atau pengenal yang kemudian dikutip,
disunting, atau ditindaklanjuti?

Catat: ukuran sampel, jumlah gagal, 3 contoh konkret dikutip.

#### Kriteria kecukupan bersama — WAJIB, jangan ditafsir ulang

Ditetapkan 19-08 setelah dua pihak berselisih tiga kali lipat semata karena
kriterianya berbeda. Ini aturan eksekusi, bukan gambaran umum.

Sebuah peristiwa dinyatakan **GAGAL** bila memenuhi salah satu dari tiga
pendeteksi ini. Kalau tidak satu pun terpenuhi, peristiwa itu LOLOS.

**D1 — Pemakaian ulang harfiah.** Ada satu baris utuh (setelah dipangkas spasi
tepi, panjang >= 20 karakter) yang ada di bagian DIBUANG, tidak ada di bagian
DISIMPAN, dan muncul persis di teks 5 giliran berikutnya.

**D2 — Sasaran suntingan.** Sebuah operasi Edit dalam 5 giliran berikutnya
memakai `old_string` yang tumpang tindih dengan bagian DIBUANG sepanjang
>= 20 karakter berurutan.

**D3 — Pengenal khas.** Sebuah token yang cocok dengan `[A-Za-z_][A-Za-z0-9_]{5,}`
atau berbentuk pengenal berstruktur (ID arXiv, jalur berkas, nama fungsi,
alamat URL) ada di bagian DIBUANG, TIDAK ada di bagian DISIMPAN, dan dipakai
di 5 giliran berikutnya sebagai argumen perintah, sasaran suntingan, atau
kutipan langsung.

**Yang TIDAK dihitung gagal, apa pun keadaannya:**
- Kata tunggal yang kebetulan muncul lagi tanpa dipakai sebagai argumen,
  sasaran, atau kutipan. Ini yang membuat angka 88% kemarin.
- Frasa yang juga ada di bagian DISIMPAN — agen tidak kehilangan apa pun.
- Kata umum bahasa Indonesia atau Inggris, sepanjang apa pun kecocokannya
  (`berikutnya`, `complete`, `if no user in`). Kecocokan n-gram saja tidak
  cukup; harus lolos D1, D2, atau D3.
- Kemunculan di keluaran tool, bukan di tindakan agen.

**Jendela:** 5 giliran asisten berikutnya. Tetap, jangan diubah.

**Sampel:** minimal 25, diambil acak dari peristiwa yang benar-benar membuang
karakter (bukan dari seluruh populasi), dengan benih tetap yang dilaporkan.

**Pelaporan:** untuk tiap kegagalan, sebutkan pendeteksi mana yang memicunya
(D1/D2/D3), teks yang dibuang, dan persisnya apa yang dipakai sesudahnya.
Kegagalan tanpa keterangan pendeteksi dianggap tidak sah.

### 2. Populasi

Setiap peristiwa yang memasukkan teks ke konteks. Golongkan: baca berkas /
hasil pencarian / keluaran perintah / lain-lain. Ukur karakter sebenarnya.

### 3. Tandingan

| aturan | parameter yang dipakai 19-08-2026 |
|---|---|
| a. baca berkas | ambang 2.000 karakter; di atasnya simpan hanya baris tanda tangan (import, `function`/`class`/`def`, deklarasi bertipe, `const X = (…)=>`, `interface`/`type`/`enum`/`struct`, `module.exports`, registrasi route, DDL SQL, judul markdown), nomor baris dipertahankan |
| b. hasil pencarian | buang baris duplikat; 2 baris konteks per temuan; 20 temuan per hasil |
| c. keluaran perintah | buang baris `node_modules`; buang bingkai tumpukan tanpa nama project; buang bilah kemajuan (`\r` di TENGAH baris, bukan di ujung); rangkum peringatan identik berulang jadi satu |

### 4. Bersih

`bersih = kotor x (1 - tingkat kegagalan kecukupan)`

Laporkan juga varian per-kategori sebagai sensitivitas, jangan menggantikan
angka utama dengan yang lebih enak.

## Jebakan yang sudah kena sekali

**CRLF.** Memperlakukan `\r` di ujung baris sebagai bilah kemajuan membuat
penghematan keluaran perintah tampak 20x lebih besar. Normalkan akhir baris
dulu; bilah kemajuan menuntut `\r` di tengah baris.

## Batas yang WAJIB ditulis di tiap laporan

- Mengukur pengurangan masukan, bukan keterjagaan hasil.
- Satu pengguna, satu basis kode, satu model. Tidak digeneralisasi.
- Karakter sebagai proksi token — sebutkan konversinya. Persentase karakter
  tidak sama dengan persentase token: kerangka membuang badan kode yang
  indentasinya padat, jadi persentase token sebenarnya kemungkinan lebih kecil.
- Bias penyintas: sebagian bacaan yang tampak mubazir justru yang membuat kita
  tahu ia mubazir.
- Uji kecukupan oleh agen yang sama yang menyusun aturan tidak buta. Katakan.

## Yang harus ditambahkan di sprint berikutnya

Metode ini mengukur karakter. Pertanyaan sebenarnya adalah biaya tertagih.
Perlu cara mengukur interaksi dengan cache prompt sebelum angka mana pun
berarti — lihat `arXiv:2607.12161` di `01_TEMUAN.md`.
