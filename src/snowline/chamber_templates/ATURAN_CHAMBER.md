# Aturan Chamber

Chamber adalah **protokol**, bukan program. Tidak ada daemon, tidak ada skrip
yang memanggil agen. Semua sinyal dijalankan manusia.

Dipasang lewat `snowline init_chamber --apply`.

---

## 0. Kapan chamber dipakai — dan kapan tidak

Chamber punya ongkos: PM jadi jembatan manual, dan tiap iterasi butuh entri
tertulis. Memakainya untuk segalanya akan membuatnya dilanggar diam-diam, dan
protokol yang dilanggar diam-diam tidak melindungi apa pun.

Penyaringnya satu pertanyaan:

> **Kalau perubahan ini salah, apakah langsung kelihatan?**

```
kelihatan seketika     warna, teks, tata letak, salin-tempel  ->  kerjakan biasa
baru ketahuan nanti    skema data, alur penyimpanan, penilaian,
                       keamanan, migrasi, apa pun yang menyentuh
                       data orang lain                        ->  lewat chamber
```

Bukan "berisiko tinggi" — itu tidak bisa diperiksa dan tiap orang menilainya
berbeda. Yang bisa diperiksa: seberapa lama kesalahan sempat hidup sebelum ada
yang menyadarinya.

Tombol salah warna ketahuan dalam sedetik. Jawaban yang tersimpan ke paket yang
salah baru ketahuan setelah ujian selesai — dan saat itu tidak bisa diulang.

Kalau ragu, pakai chamber. Ongkos memakainya untuk hal kecil cuma waktu;
ongkos tidak memakainya untuk hal besar dibayar orang lain.

## 1. Empat peran, dan siapa boleh memanggil siapa

```
PM        manusia            memvonis terakhir, menjembatani semua sinyal
TL        agen               memutuskan, mendelegasikan, melaporkan
QA        agen kedua         memeriksa dengan menjalankan, bukan membaca
Pekerja   subagent           sekali pakai, mati setelah tugasnya selesai
```

**TL tidak boleh memanggil QA-nya sendiri.** Yang memilih pemeriksa adalah PM.
Alasannya bukan formalitas: agen yang memilih hakimnya sendiri sedang
memberkati pekerjaannya sendiri.

```
PM  <-> TL       dua arah
PM  <-> QA       dua arah
TL   -> pekerja  subagent sekali pakai, hasilnya ditempel mentah
QA   -> pekerja  subagent sekali pakai, hasilnya ditempel mentah
TL   -X- QA      tidak ada jalur langsung
```

Subagent boleh dipanggil siapa saja, karena ia **tidak pernah memvonis**. Ia
menyediakan bukti; yang menyimpulkan tetap peran di atasnya.

## 2. Satu saluran

`.agents/chamber/connector.md`. Semua peran menulis dan membaca di situ.

Bukan satu berkas per peran. Itu sudah dicoba dan mati: PM tidak mau memikirkan
"ini masuk kotak yang mana", dan pertukaran QA↔TL sifatnya percakapan, bukan
surat-menyurat.

## 3. Syarat entri — ditolak sebelum isinya dibaca

- Menyatakan sesuatu selesai tanpa memuat **perintah dan keluarannya**.
- Keluaran diringkas atau dirapikan, bukan ditempel apa adanya.
- Kesimpulan menyatakan hal yang tidak ditunjukkan keluaran itu sendiri —
  termasuk bila perintahnya benar tetapi tidak menyentuh kode yang diklaim.

Kalau tidak ada keluaran untuk ditempel, vonisnya **`TIDAK BISA DIUJI`**. Itu
sah, dan lebih berguna daripada tebakan.

## 4. Connector adalah satu-satunya lebar pita

**Apa yang tidak ada di connector, identitas kedua tidak tahu.**

Ini bukan aturan kehormatan. Ditegakkan dengan memberi subagent **hanya entri
itu** — tanpa riwayat induk, tanpa alasan, tanpa niat. Ia dingin karena
konstruksinya, bukan karena berjanji lupa.

Akibat sampingnya yang paling berharga: laporan yang malas langsung terasa.
Kalau entrinya tidak lengkap, pemeriksanya tidak bisa bekerja, dan itu ketahuan
seketika.

## 5. Siapa yang menutup

QA memvonis PASS / REJECT / TIDAK BISA DIUJI. TL tidak bisa menutup tugas tanpa
vonis itu.

Tetapi **wewenang terakhir tetap pada PM**, dan PM boleh bertanya kapan saja:

> *Perintah mana yang menunjukkan itu?*

Satu pertanyaan itu menangkap sebagian besar klaim yang tidak berdasar, tanpa PM
perlu membaca satu baris kode pun.

## 6. KEADAAN.md — keadaan, bukan riwayat

```
KEADAAN.md      ditimpa, tidak ditambah      dibaca dalam beberapa detik
connector.md    ditambah, tidak ditimpa      riwayat, untuk menelusuri
```

Siapa pun yang mengubah sesuatu memperbarui `KEADAAN.md` di giliran yang sama.
Kalau aturan ini dilanggar dua-tiga kali, berkas itu jadi bohong dan lebih baik
dihapus daripada dipercaya.

Rotasi: kalau `connector.md` lewat ~100 KB, arsipkan ke
`.agents/chamber/archive/connector_<tanggal>.md` dan mulai berkas baru dengan
kepala yang sama.

## 7. Batas yang perlu diketahui sejak awal

Identitas kedua menangkap klaim yang tidak didukung buktinya. Ia **tidak**
menangkap kesalahan yang lahir dari premis keliru yang ikut tertulis di entri.
Kalau premis salah ditulis dengan yakin, pemeriksa dingin akan memeriksanya di
atas premis yang sama.

Untuk itu tetap perlu PM, sesekali, dengan pertanyaan di butir 5.

## 8. Kalau chamber terasa terlalu berat

Kurangi, jangan tinggalkan diam-diam. Protokol yang lebih berat daripada beban
kerjanya akan mati, dan matinya tidak terlihat sampai ada yang memeriksa.

Urutan yang boleh dilepas lebih dulu: peran Executor terpisah, lalu subagent
dingin. Yang **terakhir** dilepas: syarat entri di butir 3. Itu yang menahan
laporan tanpa bukti, dan itu inti seluruh protokol ini.
