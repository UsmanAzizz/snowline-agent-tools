## Entri 22 — uji buta, dan ini yang menentukan

PM sudah menyiapkan bahannya di `.here_we_are/bahan_uji_solo/`.

Isinya empat entri di `ENTRI_UNTUK_DIPERIKSA.md`, masing-masing dengan
berkasnya di `kasus_A` sampai `kasus_D`. **Berapa yang benar tidak
diberitahukan.**

Cacat yang dipakai bukan kesalahan buku teks. Ketiganya dipilih dari yang
benar-benar lolos malam ini dan tidak terlihat dari membaca.

**Caranya:**
1. Pasang `role.json` = QA (entri 19 harus sudah jadi).
2. Periksa keempat entri satu per satu. Jalankan perintahnya sendiri.
3. Untuk tiap entri beri vonis PASS / REJECT / TIDAK BISA DIUJI + alasannya.
4. Tempel keluaran mentah tiap perintah yang Anda jalankan.

**Jangan menebak dari nama kasus.** Kalau Anda meloloskan yang cacat, katakan
apa adanya — itu hasil yang paling berguna dari seluruh sprint ini.

**Cara membacanya nanti:** kalau ketiga cacat tertangkap dan yang bersih tidak
ditolak, mode tunggal layak dilanjutkan. Kalau ada yang lolos, kita tahu persis
jenis cacat mana yang butuh sesi kedua — dan itu jawaban yang jauh lebih
berguna daripada "bisa" atau "tidak bisa".
**Urutan:** 19, 20, 21, lalu 22. Entri 22 tidak boleh dikerjakan sebelum 19
selesai.
# QA -> PM: Sprint 25 — uji buta 4/4. Tiga mekanisme bekerja. Satu cacat gagal-terbuka.

## Uji buta — 4/4, dan alasannya tepat semua

PM yang menanam cacatnya, jadi jawabannya bisa dicocokkan langsung:

```
A  ditanam: uji mengumpan "belum_siap" yang kena cabang penolakan LAIN
   dijawab: benar, disebut cabang "modul belum siap"                    tepat

B  ditanam: templates/alat.py 2.0, terpasang/alat.py masih 1.0
   dijawab: benar, disebut pengguna tidak akan dapat pembaruan          tepat

C  ditanam: cache.json masih "LAPORAN v1"
   dijawab: benar, disebut perubahan tidak muncul sebelum cache dihapus tepat

D  bersih
   dijawab: PASS, tidak ada positif palsu                               tepat
```

Empat dari empat, termasuk yang bersih. Ini hasil yang berarti, dan berbeda
dari uji 3 sebelumnya — cacatnya bukan kesalahan buku teks, melainkan tiga
jenis yang benar-benar lolos pada 21-22 Agustus.

**Batas yang jujur:** bahan ujinya kecil, empat kasus dengan berkas pendek.
Versi nyatanya tersembunyi di ribuan baris. Jadi hasil ini menunjukkan mode
tunggal bisa menemukan **jenis** cacat itu, belum menunjukkan ia menemukannya
di dalam repo sebesar `cbt_master`.

## Entri 19, 20, 21 — ketiganya bekerja

```
19  peran QA -> [BLOCKED] Akses tulis (--apply) ditolak untuk peran QA
    peran TL -> [SUCCESS]
    berlaku juga di auto_scaffolder (diuji), import_fixer, context_mapper

20  entri tanpa keluaran -> [REJECTED] mengklaim selesai tetapi tidak
                            memiliki blok perintah dan keluaran
    entri lengkap        -> [PASS]
    tiga entri QA nyata yang sudah PASS -> ketiganya lolos, tidak terlalu ketat

21  test-clone jalan, klonnya dibersihkan sendiri
    perubahan tanpa commit TIDAK muncul di hasil (diuji dengan penanda)
```

Syarat 2 entri 21 QA buktikan sendiri: penanda ditambahkan ke `run_tests.py`
tanpa commit, hasil klon tidak memuatnya sama sekali.

## Cacat: kunci peran gagal-terbuka kalau berkasnya UTF-16

`.here_we_are/role.json` di repo ini tersimpan UTF-16 — kemungkinan ditulis
lewat `>` di PowerShell, yang defaultnya memang begitu:

```
$ python -c "print(open('.here_we_are/role.json','rb').read()[:20])"
b'\xff\xfe{\x00"\x00p\x00e\x00r\x00a\x00n\x00"\x00:\x00'
```

Isinya `{"role": "QA"}`. Tetapi:

```
$ replace_text.py a.js "const" "let" --apply
[SUCCESS] Berhasil memodifikasi 1 file.
```

**Kuncinya tidak menahan apa pun.** Sebabnya `check_task_state` membaca dengan
`encoding='utf-8'`, gagal, lalu jatuh ke `except Exception: pass`.

Itu gagal-terbuka. Berkas kunci yang tidak terbaca seharusnya menolak, bukan
mengizinkan — pola yang sama dengan `scope_lock.json` yang hilang, dan itu
sudah gagal-tertutup sejak awal.

**Syarat perbaikan:**
1. `role.json` yang ada tetapi tidak terbaca -> tolak `--apply`, sebutkan
   alasannya. Jangan diam.
2. Terima UTF-8 dengan atau tanpa BOM, dan UTF-16. Ini Windows; berkas ditulis
   PowerShell adalah kejadian normal, bukan kasus aneh.
3. Uji dua arah, dibuktikan mutasi.

## Sisa kecil

`temp_clone/` 27 MB masih ada di akar — bukan dari `core_test_clone.py`, yang
sudah benar memakai `tempfile.mkdtemp` dan membersihkan diri. Itu sisa percobaan
manual. QA hapus.

`.here_we_are/role.json` sebaiknya tidak ikut git sama sekali — ia keadaan
lokal, seperti `scope_lock.json`.

## Vonis

Entri 19, 20, 21, 22 **PASS**. Satu cacat baru (gagal-terbuka UTF-16) dicatat
sebagai entri 23, bukan penahan.

**Mode tunggal layak dilanjutkan** — dengan catatan bahwa buktinya masih dari
bahan uji kecil.
# PM -> TL: kunci dibuka, usulan Sprint 28 disetujui

```
$ cat .here_we_are/role.json
{"role": "TL"}

$ ls .agents/task_state.json
tidak ada
```

Diuji di sandbox: `--apply` kini `[SUCCESS]`, tidak lagi diblokir.

Kerjakan dengan empat penajaman dari vonis QA di atas. Dua yang paling mudah
terlewat:

- **Entri 30:** sepuluh impor bayangan, bukan hanya `sys` dan `os`. Lima
  lainnya `shutil`, `json` (dua tempat), `ast`, `subprocess`, `tempfile`.
- **Entri 32:** enam daftar pengecualian terpisah, bukan satu. Semua harus
  ditambah, dan penyatuannya dicatat sebagai tunggakan.

Urutan bebas, tetapi entri 28 duluan — itu satu-satunya yang membuat snowline
tidak bisa dipakai sama sekali di sebuah ekosistem.

Butir 10 tetap berlaku: `git status --short` kosong sebelum melapor.
