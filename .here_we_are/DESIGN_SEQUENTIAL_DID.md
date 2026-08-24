# Rancangan: agen tunggal berurutan — DID tanpa subagent

23 Agustus 2026. Menggantikan mekanisme di Bagian 2
`DESIGN_CONTEXT_AND_SOLO.md`, bukan gagasannya.

---

## Yang menghambat selama ini

Mode tunggal digantungkan pada subagent dingin. Uji 1 menggugurkannya:

> Mode tunggal tidak bisa ditegakkan di Antigravity, karena subagentnya tidak
> berkonteks bersih.

Sejak itu chamber kembali ke dua sesi, dan sepuluh sprint terakhir habis untuk
menambal protokol dua sesi — connector, kalibrasi, butir 10, aturan laporan.
Semuanya ada karena dua agen tidak bisa berbagi konteks.

Kesalahannya bukan pada uji itu. Pada asumsi yang tidak pernah diperiksa:

> identitas dingin harus datang dari proses lain yang hidup bersamaan.

Tidak harus.

## Pembalikan: berurutan, bukan bersamaan

Dua sesi dibutuhkan hanya kalau TL dan QA harus hidup pada saat yang sama.
Tidak ada alasan begitu. Chamber tidak pernah butuh keduanya bicara serentak —
alurnya selalu bergiliran.

```
sekarang            TL hidup  ||  QA hidup       PM mengoper di antaranya
usulan ini          TL hidup  ->  TL mati  ->  QA hidup
```

Satu sesi pada satu waktu. Sesi berikutnya adalah **sesi baru dari agen yang
sama**, dan sesi baru tidak punya ingatan apa pun tentang sesi sebelumnya.

Dingin, dijamin oleh konstruksi harness, bukan oleh perilaku subagent.

Jendela konteks yang mati itu bukan keterbatasan yang ditambal — itu
mekanismenya.

## Kenapa ini benar-benar DID, bukan ganti topi

Tiga syarat kepribadian terpisah, dan ketiganya terpenuhi tanpa janji:

```
tidak berbagi ingatan     sesi baru mulai dari nol — sifat harness
tidak bisa saling lihat   yang lalu sudah tidak ada, bukan disembunyikan
punya catatan bersama     chamber, satu-satunya yang menyeberang
```

Bandingkan dengan ganti `role.json` di tengah sesi: agen tetap ingat maksudnya
sendiri. Itu topi. Yang ini bukan.

## Syarat tunggal, dan ini yang menentukan segalanya

> **Chamber harus memegang 100% kesinambungan.**

Kalau ada satu hal yang hanya hidup di percakapan, sesi berikutnya kehilangan
itu, dan seluruh rancangan gagal.

Inilah kenapa "memindahkan jendela konteks ke dalam chamber" bukan pekerjaan
sampingan — ia gerbangnya. Selama masih ada yang tinggal di kepala, mode
tunggal tidak bisa jalan. Begitu tidak ada lagi, mode tunggal jalan dengan
sendirinya.

Dan syarat ini **bisa diukur**, tidak perlu diperdebatkan.

## Uji yang menentukan (SUDAH DIJALANKAN — Entri `052e407`)

Cukup satu, murah, dan hasilnya biner.

```
1  Ambil satu entri terbuka di connector.
2  Buka sesi yang benar-benar baru dari agen yang sama.
3  Beri ia HANYA: keluaran `snowline context` + entri itu + jalur repo.
   Tidak ada penjelasan, tidak ada riwayat percakapan, tidak ada niat.
4  Minta vonis QA.
5  Bandingkan dengan vonis sesi yang punya konteks penuh.
```

```
vonis sama                     chamber cukup. Mode tunggal berlaku.
vonis beda / tidak bisa mulai  chamber kurang — dan yang kurang terlihat
```

Bagian terakhir yang membuat uji ini berguna. Kegagalan tidak berhenti sebagai
"tidak bisa"; ia menghasilkan **daftar apa yang dicari sesi dingin dan tidak
ketemu.** Daftar itu adalah spesifikasi persis dari apa yang harus dipindahkan
ke chamber.

Ulangi sampai daftar itu kosong.

Catatan jujur: hari ini uji ini kemungkinan besar gagal. Sepanjang 22-23
Agustus, sesi QA membawa sangat banyak yang tidak pernah masuk connector —
alasan di balik vonis, pola yang dikenali dari sprint lama, kecurigaan yang
belum terbukti. Itu bukan alasan menunda ujinya. Itu justru isinya.

## Pengukuran dan penilaian — dan kenapa subagent tercemar tetap berguna

Tambahan 23 Agustus, dari pengamatan PM: agen induk **menunggu** subagent, dan
tidak tahu apa yang dikerjakannya. Batasnya nyata, tetapi arahnya satu:

```
induk -> subagent    konteks bisa bocor turun   (ini yang diuji dan gagal)
subagent -> induk    induk cuma dapat laporan   (ini yang tetap berlaku)
```

Arah kedua tidak menambal arah pertama. Tetapi menelusurinya membuka sesuatu
yang membuat arah pertama jauh kurang penting daripada yang diasumsikan
rancangan lama.

**Perlindungan chamber tidak pernah "pemeriksanya tidak tahu".** Perlindungannya
"klaim harus membawa perintah dan keluarannya". Subagent yang tercemar tetap
harus menjalankan perintahnya. Mutasi tetap merah atau hijau. Pencemaran
membuatnya lunak dalam **menilai**, tidak membuatnya bisa mengarang
**keluaran**.

Jadi kerja QA terbelah dua, dan hanya separuhnya butuh identitas dingin:

```
PENGUKURAN   jalankan mutasi, hitung AST, ambil status CI, diff dua berkas,
             pasang di venv bersih, jalankan suite dari klon
             -> tidak peduli siapa yang bertanya
             -> subagent tercemar sekalipun sah
             -> BERLAKU: untuk harness yang subagentnya bisa menjalankan perintah tanpa persetujuan manusia per perintah (di Antigravity terhalang prompt izin)
             -> subagent tidak bisa mengukur tanpa interaksi manusia

PENILAIAN    apakah ujinya menguji yang benar
             apakah klaim cakupannya jujur
             apakah kesimpulan melebihi keluarannya
             -> di sini pencemaran menggigit
             -> butuh sesi dingin berurutan
```

Sepanjang 22-23 Agustus, sebagian besar kerja QA ada di kolom kiri. Mutasi dua
arah, `TOTAL 0`, `pip show`, `head_sha` CI, `git ls-files ... | wc -l` —
semuanya keluaran, bukan pendapat.

Akibatnya untuk rancangan ini: **kolom kiri tidak perlu menunggu apa pun.**
Ia bisa diserahkan ke subagent sekarang, dan itu memperkecil kolom kanan sampai
tinggal bagian yang benar-benar butuh sesi dingin.

Batasnya harus disadari: subagent yang tercemar akan cenderung memilih
pengukuran yang **membenarkan** entri. Karena itu perintah yang dijalankan
harus ditulis di entrinya, bukan dipilih subagent. Ia menjalankan daftar, bukan
menyusunnya.

## Mekanismenya

### 1. Peralihan peran adalah tindakan terakhir sesi yang mati

```
TL bekerja
TL menulis laporan ke connector
TL menulis role.json = QA
sesi berakhir
```

Ini yang membuat peralihan tidak bisa disalahgunakan: **tidak ada waktu
tersisa untuk menyalahgunakannya.** Agen yang menulis "sekarang aku QA" langsung
mati sesudahnya. Yang bangun sebagai QA adalah sesi yang tidak tahu apa-apa.

Bandingkan dengan peralihan di tengah sesi, yang selalu bisa dibalas
"tapi aku tahu maksudku tadi".

### 2. `snowline handoff` — sesi tidak boleh mati diam-diam

Perintah yang menutup sesi, dan menolak kalau kesinambungannya bolong:

```
tolak kalau  git status --short tidak kosong
tolak kalau  connector tidak memuat entri untuk pekerjaan sesi ini
tolak kalau  irisan tugas (scope_lock) kosong padahal ada berkas disentuh
tulis        role.json berikutnya
cetak        apa yang akan dibaca sesi berikutnya, supaya bisa dilihat
             sekarang apakah itu cukup
```

Baris terakhir yang paling berguna: TL melihat, sebelum mati, persis sebanyak
apa yang akan diketahui QA. Kalau kelihatan kurang, ia masih sempat menulisnya.

### 3. Himpunan baca ditentukan peran, ditegakkan alat

```
TL     STATE.md, connector penuh, kode, irisan tugas
QA     STATE.md, entri terakhir saja, kode, dan TIDAK ada catatan kerja TL
```

Bukan imbauan. `chamber/work/` dibaca TL, ditolak untuk QA — mekanismenya sama
dengan kunci tulis yang sudah ada di `check_task_state`.

### 4. Kunci tulis tetap seperti sekarang

`role.json = QA` menolak `--apply`. Sudah ada, sudah diuji.

## Yang hilang, dan harus disadari

**Tidak ada lagi pihak yang bisa ditanya seketika.** Kalau QA butuh penjelasan,
tidak ada TL yang hidup untuk menjawab. Ia harus memutuskan dari yang tertulis,
atau memvonis `TIDAK BISA DIUJI`.

Itu terasa seperti kerugian. Sebenarnya penegakan: pertanyaan yang harus
dijawab lisan adalah bukti entrinya kurang lengkap.

**Premis keliru tetap menular** — sudah tertulis di butir 7 dan tidak berubah.
QA memeriksa di atas premis entrinya. PM tetap perlu, sesekali, dengan satu
pertanyaan: *perintah mana yang menunjukkan itu?*

**Untuk PM lebih repot di awal:** harus membuka sesi baru tiap peralihan, bukan
mengoper pesan antar dua jendela yang sudah terbuka. Sesudah `handoff` ada,
bedanya tinggal satu perintah.

## Yang didapat

```
tidak ada lagi dua agen bersamaan     tidak ada masalah sinyal darurat
satu jendela hidup pada satu waktu    ongkos separuh
sesi mulai kecil                      hanya himpunan baca perannya
dingin dijamin harness                tidak bergantung perilaku subagent
batasan harness untuk perintah        Antigravity memblokir subagent (timeout izin)
```

Yang terakhir penting untuk snowline sebagai paket yang dikirim: mode tunggal
berbasis subagent hanya jalan di harness tertentu, dan itu harus ditulis
sebagai syarat. Mode berurutan tidak punya syarat itu.

## Urutan membangun

```
1  jalankan uji penentu di atas, apa adanya, dan catat daftar yang hilang
2  pindahkan yang ada di daftar itu ke chamber
3  ulangi 1 sampai daftarnya kosong
4  baru bangun `snowline handoff`
5  himpunan baca per peran
```

Nomor 1 tidak butuh kode. Nomor 4 dan 5 tidak layak dibangun sebelum 1 sampai
3 selesai — membangun perkakas untuk alur yang belum terbukti bisa berjalan
adalah cara paling mahal untuk mengetahui bahwa ia tidak bisa.

## Apa yang akan membatalkan rancangan ini

Ditulis di depan supaya tidak dicari-cari alasannya nanti:

- Kalau setelah tiga putaran uji, daftar yang hilang tidak mengecil — berarti
  ada yang memang tidak bisa dituliskan, dan mode dua sesi tetap berlaku untuk
  pekerjaan yang lolos butir 0.
- Kalau sesi dingin secara sistematis **lebih lunak** — meluluskan yang
  ditolak sesi berkonteks — berarti masalahnya bukan ingatan melainkan
  kedalaman, dan rancangan ini tidak menjawabnya.

Keduanya terukur dari uji yang sama. Tidak perlu perdebatan.
