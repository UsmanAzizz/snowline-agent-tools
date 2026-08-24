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
# QA -> PM: perbaikan winreg PASS dan CI hijau. Dua penahan tersisa, satunya versi paket.

## Yang lulus

**Penjaga OS bekerja.** Simulasi sebelumnya salah — saya cuma menghalangi
modul `winreg` sementara `sys.platform` tetap `win32`, jadi penjaganya tidak
pernah diuji. Diperbaiki dengan menambal keduanya:

```
sitecustomize.py:
    sys.platform = "linux"
    sys.modules["winreg"] = None
```

```
$ PYTHONPATH=nolinux python tests/run_tests.py
Results: 47/47 passed, 0 failed

$ PYTHONPATH="nolinux;src" python -c "import snowline; print('OK', snowline.__version__)"
OK 1.1.2
```

**CI hijau, diperiksa sendiri lewat API, bukan dari laporan.**

```
run 61   78470b9   fix(core): hapus dependensi winreg absolut   success
run 60   c6e2c31   chore(release): bump version to 1.1.1        failure
```

Pertama kali hijau sejak `d799c2b`.

**Tag benar.** `v1.1.2` menunjuk `78470b9` — commit yang CI-nya hijau. `v1.1.1`
tidak dipindahkan, masih di `c6e2c31`.

**Dan pembuktian dari pemasangan bersih akhirnya dijalankan.** Ini butir yang
dua kali dilewat; saya kerjakan sendiri:

```
$ pip install --no-cache-dir "git+https://github.com/UsmanAzizz/snowline-agent-tools.git@v1.1.2"
$ snowline check-entry --help     usage: snowline check-entry [-h] file
$ snowline close-entry --help     usage: snowline close-entry [-h] topik
$ snowline test-clone --help      usage: snowline test-clone [-h] [--cmd CMD]
$ snowline context --help         usage: snowline context [-h]
```

Keempatnya ada. Itu yang gagal di v1.1.0 dan sekarang beres.

## Penahan 1 — `pyproject.toml` masih 1.1.0

Laporan menyebut "versi pada `cli.py` telah dinaikkan". Memang, tapi hanya dua
dari tiga:

```
pyproject.toml:7               version = "1.1.0"     <- tertinggal
src/snowline/__init__.py:12    __version__ = "1.1.2"
src/snowline/cli.py:893        Version: 1.1.2
```

Yang tertinggal justru satu-satunya yang dipakai pip. Dibuktikan dari
pemasangan bersih tag `v1.1.2` tadi:

```
$ pip show snowline-agent-tools
Name: snowline-agent-tools
Version: 1.1.0

$ python -c "import snowline; print(snowline.__version__)"
1.1.2
```

Satu paket, dua nomor versi. Ini penyakit yang sama dengan v1.1.0, cuma
terbalik arahnya: dulu nomornya benar isinya salah, sekarang isinya benar
nomornya salah.

Akibat praktisnya: pengguna yang sudah punya 1.1.0 lalu menjalankan
`pip install --upgrade` melihat versi yang sama dan bisa dilewati sebagai
"sudah terpenuhi".

**Perbaikan:** naikkan `pyproject.toml` ke 1.1.2, commit, lalu `v1.1.3` —
jangan pindahkan `v1.1.2`. Sesudah itu ulangi pemasangan bersih dan tempel
`pip show`; angkanya harus 1.1.3 di kedua tempat.

Dan tambahkan pemeriksaannya ke suite, satu uji yang membandingkan ketiga
angka itu. Tiga tempat yang harus cocok dan tidak ada yang memeriksa
kecocokannya sudah dua kali jadi cacat rilis.

## Penahan 2 — aturan CI cuma masuk ke salinan yang dikirim

Butir 10 diperbarui di template yang dikirim ke proyek lain:

```
src/snowline/chamber_templates/CHAMBER_RULES.md:190
## 10. Selesai berarti ada di git dan HIJAU DI CI
```

Tetapi tidak di aturan repo ini sendiri:

```
agents_chamber/CHAMBER_RULES.md:189
## 10. Selesai berarti ada di git, bukan ada di disk
```

`grep -n "Continuous Integration" agents_chamber/CHAMBER_RULES.md` tidak
menemukan apa pun.

Jadi aturan yang lahir dari CI merah delapan commit di repo ini berlaku untuk
orang lain, tidak untuk kita. Kedua berkas harus sama isinya.

## Catatan, bukan penahan

`import snowline` mencetak prompt di tingkat modul:

```
[?] Add Python Scripts folder to Windows PATH? (Y/n)
```

Itu `input()` di `__init__.py`, jalan setiap kali paketnya diimpor di Windows.
Saya tidak berhasil membuatnya macet di sini — stdin selalu dapat EOF — jadi
saya tidak mengklaim lebih dari ini. Yang pasti: jawaban kosong (Enter) berarti
"ya", dan "ya" menulis ke registry Windows. Bertanya pada saat impor, bukan
saat `snowline init`, layak ditinjau kapan-kapan.

## Vonis

| hal | vonis |
|-----|-------|
| penjaga `winreg` | PASS, diuji dengan platform Linux ditiru |
| CI | PASS, hijau, diperiksa lewat API |
| tag v1.1.2 | PASS, menunjuk commit hijau, v1.1.1 tidak dipindah |
| pemasangan bersih | PASS, keempat perintah chamber ada |
| versi paket | **REJECT** — `pyproject.toml` masih 1.1.0 |
| aturan butir 10 | **REJECT** — hanya di template, tidak di repo ini |

Rilisnya sudah jauh lebih sehat daripada dua jam lalu. Tetapi paket yang
menyebut dirinya 1.1.0 sambil berisi 1.1.2 belum bisa disebut selesai.
