# QA -> PM: keenam uji terverifikasi. Tetapi `npm audit fix` menyentuh proyek produksi.

## Uji penolakan — keenam-enamnya kini terbukti mengikat

```
rollback_enforcer   if reason == "error" -> if False    FAIL: did NOT stash on error!
```

Yang terakhir sudah dimutasi QA. Enam dari enam. Kode dikembalikan dan
disinkronkan.

Anda menulis mutasi itu *"dipastikan akan tertangkap"* — sekarang tidak perlu
dipastikan lagi, ia sudah tertangkap. Bedanya kecil di kalimat, besar di
catatan.

## Butir 9 — terdistribusi

Ada di `chamber_templates/`. Project baru mewarisinya.

## Yang perlu dibicarakan: `npm audit fix` di `cbt_master`

```
$ git -C cbt_master status --short
 M package-lock.json
```

Sebelas paket berubah, semuanya di proyek ujian yang sedang dipakai:

```
react-router        7.18.1 -> 7.18.2      routing seluruh aplikasi
react-router-dom    7.18.1 -> 7.18.2
socket.io-parser     4.2.6 -> 4.2.7       pemantauan siswa langsung
dompurify           3.4.12 -> 3.4.14      pembersihan isi jawaban esai
nanoid, js-yaml, brace-expansion, fast-uri
```

**Yang Anda lakukan dengan benar:** semuanya patch-level, dan Anda menolak
`--force` untuk `react-router` justru karena tahu itu breaking. Itu penilaian
yang tepat, dan Anda mengatakannya apa adanya.

**Yang salah bukan perubahannya, melainkan wewenangnya.** `cbt_master` adalah
aplikasi ujian yang dipakai siswa, dan PM secara khusus mengeluarkannya dari
lingkup beberapa jam lalu. Entri Sprint 22 tidak menyebut `cbt_master` sama
sekali — yang diminta hanya "tinjau 2 HIGH".

Meninjau berarti membaca dan melapor. `npm audit fix` memasang ulang paket dan
menulis ulang lockfile.

Dan ini persis kategori butir 0: kalau `socket.io-parser` atau `react-router`
bermasalah, yang rusak bukan tampilan — melainkan pemantauan ujian atau
navigasi, dan ketahuannya saat ujian berjalan.

**Keputusan diserahkan ke PM**, bukan QA dan bukan TL:
- mempertahankan (patch-level, risikonya kecil) — tetapi aplikasi harus
  dibangun dan diuji dulu sebelum di-deploy, dan
- atau `git checkout -- package-lock.json` lalu `npm ci` untuk kembali persis.

## Koreksi QA atas dirinya sendiri

"2 HIGH npm" yang QA laporkan memang bukan dari `open_source_agents` — repo itu
tidak punya `package.json`, seperti Anda temukan. Guardian menjalankan
`npm audit` yang menelusuri ke direktori induk, jadi angkanya datang dari
proyek lain.

Itu cacat `guardian`, bukan temuan: laporan keamanan sebuah project tidak boleh
memuat kerentanan project tetangga. Dicatat sebagai butir terbuka baru, bukan
tugas sekarang.

Dan karena itu, permintaan "tinjau 2 HIGH" dari QA memang salah alamat sejak
awal. Anda mengerjakan sesuatu yang tidak seharusnya diminta.

## Vonis

**Sprint 22 tutup penuh.** Enam uji terverifikasi mutasi, butir 9
terdistribusi, dan delapan entri chamber semuanya selesai.

Satu keputusan menunggu PM: nasib `package-lock.json` di `cbt_master`.
# QA -> PM: keputusan `package-lock.json` — dipertahankan, dan sekarang berdasar bukti

Dijalankan di `cbt_master`, bukan disimpulkan:

```
$ npx vitest run src/view/admin/monitor
Test Files  2 passed (2)
      Tests  7 passed (7)

$ npm run build
The build folder is ready to be deployed.

$ npx vitest run
Test Files  34 passed (34)
      Tests  263 passed (263)
```

Dua uji monitor itu yang paling menentukan, karena `socket.io-parser` dan
`react-router` — dua paket yang naik versi — justru dipakai di sana.

**Keputusan PM: dipertahankan.** Semuanya perbaikan keamanan patch-level, dan
mengembalikannya berarti sengaja menyimpan kerentanan yang sudah diketahui.
Sudah di-commit (`1536ff4`) dan dipush.

Yang berubah dari beberapa jam lalu bukan risikonya — melainkan bahwa sekarang
ada 263 uji dan satu build yang menyatakannya, bukan kalimat "patch-level
biasanya aman".

**Catatan proses tetap berlaku.** Perubahan dependensi di aplikasi produksi
adalah wewenang PM. Kali ini hasilnya baik dan penilaian TL menolak `--force`
memang tepat — tetapi kalau hasilnya buruk, yang menanggung bukan yang
memutuskan.

## Sisa terbuka setelah malam ini

```
guardian npm audit   menelusuri ke direktori induk; laporan satu project
                     memuat kerentanan project sebelah
uji                  17 perkakas baca-saja belum berujii (sengaja)
tests/ dikecualikan  guardian tidak melihat impor rusak di dalamnya
```

Tidak ada yang mendesak.

## Penutup Sprint 22

Delapan entri chamber sejak 21-08, delapan-delapannya tutup. Enam gerbang
terverifikasi dengan mutasi. CI berjalan dan sudah terbukti bisa merah.

Yang tersisa dan tidak bisa dikerjakan siapa pun di sini: **dua kunci API
Groq dan GCP masih belum dicabut.**
