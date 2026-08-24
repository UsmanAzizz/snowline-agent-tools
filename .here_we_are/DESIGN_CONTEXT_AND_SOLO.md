# Rancangan: konteks di snowline, dan agen tunggal berkepribadian dua

Ditulis 22 Agustus 2026 sebagai usulan, bukan keputusan. Belum diuji.

---

# Bagian 1 — Snowline sebagai sumber kebenaran konteks

## Kenapa jendela konteks bukan tempat menyimpan

Empat sifatnya, dan keempatnya merugikan:

```
fana          mati bersama sesi
terkompresi   diringkas saat panjang, dan yang hilang tidak dicatat
tak terperiksa  tidak ada yang bisa memeriksa apa yang "diketahui" agen
tertutup      identitas kedua tidak bisa melihatnya
```

Memindahkannya ke berkas membalik keempatnya. Tetapi versi naifnya gagal:
**membaca berkas juga memakan konteks.** Memindahkan 85 KB dari kepala ke disk
tidak menghemat apa pun kalau 85 KB itu dibaca kembali.

Jadi syarat rancangan ini satu: **terbatas dan bisa dialamati.** Bukan
"semuanya tersimpan", melainkan "yang perlu bisa diambil tanpa membaca sisanya".

## Tiga jenis konteks, dan masing-masing butuh perlakuan berbeda

```
KEADAAN     ditimpa      selalu dibaca      ~100 baris, tetap
RIWAYAT     ditambah     jarang dibaca      tak terbatas, dirotasi
PENGETAHUAN diturunkan   dibaca saat perlu  bisa dibuat ulang, tidak disimpan
```

Snowline sudah punya ketiganya:

```
STATE.md              keadaan
connector.md            riwayat
DEPENDENCY_MAP.md       pengetahuan turunan
selective_reader        pengetahuan turunan, sesuai permintaan
```

**Yang belum ada: irisan tugas.**

## Irisan tugas — bagian yang hilang

Yang benar-benar mati bersama sesi bukan keadaan project, melainkan hal-hal
kecil yang dipelajari agen selama satu tugas:

- berkas mana yang ternyata relevan, di luar yang didaftarkan di awal
- apa yang sudah dicoba dan gagal
- pertanyaan yang belum terjawab

Itu tidak ada di `STATE.md` (terlalu rinci) dan tidak praktis dicari di
`connector.md` (terkubur). Jadi tiap sesi baru menggalinya ulang.

**Usulan: `scope_lock.json` naik pangkat menjadi irisan tugas.** Ia sudah
mendeklarasikan berkas yang boleh disentuh; tambahkan tiga medan:

```json
{
  "task": "...",
  "allowed_files": ["..."],
  "created_at": "...",

  "temuan": [
    "useRunTest membaca kelas dari localStorage, bukan dari testSetting",
    "pita 0 dulu dipakai untuk jawaban pendek — sudah diperbaiki 632e32e"
  ],
  "pertanyaan_terbuka": [
    "apakah VPS sudah menarik main?"
  ],
  "berkas_terkait": ["diturunkan dari DEPENDENCY_MAP, bukan diketik tangan"]
}
```

Aturannya satu, dan harus keras supaya tidak jadi tempat sampah:

> **Satu baris per temuan. Kalau lebih dari sepuluh, yang tertua pindah ke
> connector.** Irisan tugas bukan catatan; ia daftar bawaan.

## Satu perintah untuk memulai sesi

```bash
snowline konteks
```

Mencetak, dalam urutan itu:

```
STATE.md                        ~100 baris
irisan tugas dari scope_lock      ~20 baris
entri connector TERAKHIR saja     ~40 baris
```

Sekitar 160 baris — di bawah 8 KB. Itu bootstrap sesi, menggantikan "baca
85 KB". Berkas lain dibaca hanya saat pertanyaannya muncul.

**Batas keras:** kalau keluaran `snowline konteks` melewati 250 baris, itu
bukan alasan menaikkan batas — itu tanda ada yang harus diringkas atau
dipindah ke riwayat.

## Apa yang TIDAK dilakukan rancangan ini

- Tidak mengganti pembacaan kode. Kode tetap dibaca lewat `selective_reader`
  dan `surgical_splicer` saat perlu.
- Tidak menyimpan transkrip percakapan. Yang disimpan kesimpulannya, bukan
  jalannya.
- Tidak menjanjikan penghematan token. Pengukuran 19-20 Agustus sudah
  menunjukkan klaim semacam itu gampang meleset. Yang dijanjikan: sesi baru
  tidak mulai dari nol, dan yang diketahui bisa diperiksa orang lain.

---

# Bagian 2 — Agen tunggal berkepribadian dua

## Kenapa ganti mode saja tidak cukup

Sudah diuji secara tidak sengaja malam ini. Tiga kegagalan terbesar tertangkap
justru karena pemeriksanya **tidak tahu apa yang dimaksudkan** penulisnya:

```
S1 butir 3-4    perintahnya benar, tetapi tidak menyentuh kode yang diklaim
entri 6         tiga uji lulus tanpa menyentuh gerbang yang mereka klaim uji
entri 10        cache menyajikan hasil lama; penulisnya sendiri tidak melihat
```

Sesi yang sama tidak akan menangkap ketiganya, karena ia tahu maksudnya — dan
pengetahuan itu menutup celah antara maksud dan bukti.

Jadi identitas kedua butuh **batas konteks**, bukan batas nama.

## Bentuk yang bekerja

```
PM      manusia
Agen    satu sesi, dua peran, ditandai berkas
QA      subagent dingin — masukannya HANYA entri connector
```

Yang membuatnya bukan teater, tiga hal, dan semuanya soal konstruksi:

**1. Peran ditandai berkas, bukan niat.**

```json
.agents/chamber/role.json    {"role": "TL"}  |  {"role": "QA"}
```

**2. Mode QA terkunci-tulis.** Ini intinya. Bukan "saya berjanji tidak menulis
sebagai QA" — melainkan `--apply` ditolak selama `peran = QA`. Mekanismenya
sudah ada: `check_task_state` di `replace_text.py:22` sudah menolak `--apply`
berdasarkan isi sebuah berkas. Tinggal ditambah satu syarat.

Kepribadian kedua jadi nyata karena ia **tidak bisa** melakukan apa yang
kepribadian pertama lakukan.

**3. Pemeriksaan dijalankan subagent dingin.** Masukannya persis satu entri
connector, tanpa riwayat induk. Keluarannya ditempel mentah.

Ini yang sudah tertulis di butir 4: *apa yang tidak ada di connector, identitas
kedua tidak tahu.* Bedanya, di sini ia dipakai sebagai mekanisme utama, bukan
pelengkap.

## Alur

```
1  Agen (TL)  kerjakan, tulis entri ke connector: perintah + keluaran mentah
2  Agen       tulis role.json = QA          -> --apply terkunci
3  Agen (QA)  panggil subagent, masukannya HANYA entri itu + jalur repo
4  Subagent   jalankan sendiri, kembalikan keluaran mentah
5  Agen (QA)  tempel apa adanya, beri vonis
6  PM         ratifikasi, buka kunci
```

Langkah 3 yang menentukan. Kalau subagent diberi riwayat induk, seluruh
rancangan ini runtuh jadi ganti topi.

## Apa yang hilang dibanding dua sesi

Satu hal, dan sudah tertulis di butir 7: **premis yang keliru ikut menular.**
Subagent memeriksa di atas premis yang tertulis di entri. Kalau premisnya salah
dan ditulis dengan yakin, ia akan memeriksanya dengan patuh.

Dua sesi terpisah tidak sepenuhnya kebal ini juga — tetapi sesi kedua yang
membaca seluruh connector punya peluang menabrak premis itu dari arah lain.

**Karena itu PM tetap perlu**, sesekali, dengan satu pertanyaan: *perintah mana
yang menunjukkan itu?*

## Yang sudah diuji (Semua lulus di Claude Code)

```
1  apakah subagent Antigravity benar-benar berkonteks bersih (LULUS - Uji X)
2  apakah kunci-tulis berdasarkan role.json benar-benar menahan (LULUS - Uji 0)
3  apakah agen yang sama, dalam mode QA, benar-benar menolak pekerjaannya
   sendiri — atau justru lebih lunak (LULUS - Uji Y)
```

Ketiga uji lulus di Claude Code (entri `052e407`). Mode tunggal terbukti berjalan dengan benar jika prasyarat harness terpenuhi.

---

# Tiga tingkat, supaya tidak ada yang memakai palu untuk paku kecil

```
tanpa chamber   perubahan yang salahnya langsung kelihatan       butir 0
mode tunggal    satu agen + subagent dingin + kunci peran        rancangan ini
mode penuh      TL dan QA sesi terpisah                          yang berlaku
```

Mode tunggal **belum berlaku** sampai ketiga uji di atas dijalankan.

---

# Catatan 22-08: chamber sebagian besar alat bantu ingatan

Temuan dadakan PM, bukan bagian dari rancangan di atas. Ditulis karena berguna
untuk memutuskan ke mana investasi berikutnya.

## Kelemahan jendela konteks yang membuat chamber tumbuh

Kalau jendela konteks tidak terbatas, permanen, bisa dibagi antar agen, dan
bisa diperiksa dari luar — sebagian besar chamber tidak perlu ada:

```
STATE.md          ada karena keadaan mati bersama sesi
connector.md      ada karena dua agen tidak bisa berbagi konteks
bentuk entri      ada karena "saya sudah menjalankannya" tidak bisa diperiksa
klon bersih       ada karena keadaan lokal tidak terlihat dari konteks
kunci peran       ada karena satu agen tidak bisa memegang dua sikap sekaligus
irisan tugas      ada karena temuan kecil hilang saat sesi ditutup
```

Enam mekanisme, semuanya menambal keterbatasan penyimpanan.

## Yang tetap berlaku meski konteksnya sempurna

```
klaim butuh bukti                      soal kejujuran, bukan ingatan
yang menilai bukan yang mengerjakan    soal kepentingan, bukan ingatan
```

Dua ini tidak menambal apa pun. Agen dengan memori tak terbatas tetap bisa
melaporkan sesuatu selesai padahal buktinya tidak menunjukkannya — itu terjadi
tiga kali pada 21-22 Agustus, dan tidak satu pun karena lupa.

## Kenapa pembagian ini berguna

Kira-kira 70% chamber adalah alat bantu ingatan, 30% aturan penilaian.

Yang 70% **akan usang** kalau harness berkembang: konteks makin besar, memori
persisten, subagent yang benar-benar terisolasi. Kalau Antigravity besok punya
memori permanen, `STATE.md` dan `connector.md` jadi pekerjaan yang tidak perlu.

Yang 30% tidak akan usang, karena masalahnya bukan teknis.

**Akibatnya untuk keputusan:** jangan membangun terlalu dalam di bagian
ingatan. Cukup sampai ia bekerja hari ini. Bagian penilaian layak dibangun
sedalam mungkin, karena ia tidak akan dibuat mubazir oleh pembaruan harness.

## Cara memeriksa catatan ini nanti

Kalau suatu hari harness punya memori persisten dan konteks bersama, jalankan
ulang pembagian di atas. Kalau enam mekanisme pertama masih terasa perlu,
catatan ini salah dan sebaiknya dicabut.
