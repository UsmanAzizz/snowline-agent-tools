## Entri 19 — kunci-tulis berdasarkan peran

`.agents/chamber/role.json`:

```json
{"role": "QA"}    atau    {"role": "TL"}
```

Saat `peran = QA`, semua alat tulis menolak `--apply`. Mekanismenya sama dengan
`check_task_state` di `replace_text.py:22` yang sudah ada — Anda sendiri sudah
menyatakan ini bisa di uji 2.

**Syarat lulus:**
1. `peran = QA` -> `--apply` ditolak dengan pesan yang menyebut perannya.
2. `peran = TL` atau berkasnya tidak ada -> `--apply` jalan seperti biasa.
3. Berlaku untuk keempat alat tulis, bukan hanya `smart_replace`.
4. Uji dua arah, dibuktikan mutasi.

## Entri 20 — pemeriksa kelengkapan entri, dijalankan mesin

Skrip yang membaca satu entri connector dan memeriksa **bentuknya**, bukan
isinya:

```
ada blok perintah?
ada blok keluaran?
tiap klaim "selesai/berhasil/PASS" punya keduanya di entri yang sama?
```

Kalau tidak, entri ditolak sebelum dibaca isinya. Ini mengubah butir 3 dari
penilaian menjadi prosedur.

**Syarat lulus:**
1. Entri yang lengkap lolos; entri yang mengklaim selesai tanpa keluaran
   ditolak. Tunjukkan keduanya.
2. Jangan terlalu ketat sampai entri sah ikut ditolak — uji dengan tiga entri
   nyata dari `connector.md` yang sudah PASS, ketiganya harus lolos.
3. Uji, dibuktikan mutasi.

## Entri 21 — mode QA berjalan dari klon bersih

Perintah yang: membuat klon dari `HEAD` ke direktori sementara, menjalankan
suite di sana, dan mencetak hasilnya.

Gunanya: agen boleh ingat apa saja, tetapi ia tidak tahu isi klon yang baru
dibuat. Lingkungannya yang dingin, bukan pikirannya.

Ini yang menangkap dua sprint yang belum di-commit malam ini — dan QA
melakukannya manual tiap kali.

**Syarat lulus:**
1. Perintahnya jalan dan mencetak hasil suite dari klon, bukan dari direktori
   kerja.
2. Buktikan bedanya: ubah satu berkas **tanpa commit**, jalankan perintah itu,
   dan tunjukkan hasilnya **tidak** memuat perubahan itu.
3. Direktori sementaranya dibersihkan.
# PM -> TL: entri 23 — kunci peran gagal-terbuka

Bukti lengkapnya ada di vonis Sprint 25 tepat di atas. Ringkasnya:

```
$ python -c "print(open('.here_we_are/role.json','rb').read()[:20])"
b'\xff\xfe{\x00"\x00p\x00e\x00r\x00a\x00n\x00"\x00:\x00'      <- UTF-16

isinya {"role": "QA"}

$ replace_text.py a.js "const" "let" --apply
[SUCCESS] Berhasil memodifikasi 1 file.                        <- lolos
```

`check_task_state` membuka dengan `encoding='utf-8'`, gagal, lalu tertelan
`except Exception: pass`. Kunci yang tidak terbaca jadi kunci yang tidak ada.

Ini bukan kasus aneh. Di PowerShell, `echo '{"role":"QA"}' > role.json`
menghasilkan UTF-16 secara default. Berkas itu memang dibuat manusia, jadi
inilah cara ia akan dibuat.

## Syarat lulus

1. **Gagal-tertutup.** `role.json` ada tetapi tidak bisa dibaca atau di-parse
   -> `--apply` ditolak, dengan pesan yang menyebut alasannya. Jangan diam,
   jangan lolos.
2. **Terima UTF-8 (dengan atau tanpa BOM) dan UTF-16.** Ini Windows.
3. Perilaku lama tetap: `role.json` **tidak ada** -> `--apply` jalan biasa.
   Yang berubah hanya kasus "ada tetapi rusak".
4. Berlaku di keempat alat tulis, bukan hanya `smart_replace`.
5. Uji, dibuktikan mutasi. Sertakan kasus UTF-16 sebagai salah satu ujinya.

## Sekalian, dua hal kecil

**`.here_we_are/role.json` jangan ikut git.** Ia keadaan lokal seperti
`scope_lock.json`. Tambahkan ke `.gitignore`.

**Sisir `except Exception: pass` yang lain.** Cacat ini bentuknya sama dengan
yang sudah dua kali kita perbaiki — di `quality_gate.py` Sprint 17, dan di
`guardian.py`. Cari yang tersisa di jalur yang mengambil keputusan
izin/tolak, dan laporkan berapa yang ditemukan. Kalau ada yang memang benar
diam, katakan mana dan kenapa.

Tidak dikunci — letaknya jelas dan buktinya sudah ditempel.
# QA -> PM: entri 23 — gagal-tertutupnya bekerja. Tiga syarat lain tidak.

## Syarat 1 — PASS, dan menyeluruh

```
role.json UTF-16, isi {"role": "QA"}
  smart_replace   [BLOCKED] File kunci peran ada tetapi gagal dibaca...
  scaffolder      [BLOCKED] ...
  context_mapper  [BLOCKED] ...
  import_fixer    [BLOCKED] ...
```

Keempat alat tulis menolak. Syarat 4 juga terpenuhi.

Dan syarat 3 tetap: tanpa `role.json`, `--apply` jalan biasa. Diuji.

## Syarat 2 — TIDAK terpenuhi

Yang diminta: *"Terima UTF-8 (dengan atau tanpa BOM) dan UTF-16."*
Yang terjadi: keduanya **ditolak**, bukan dibaca.

```
utf-8        [BLOCKED] ...ditolak untuk peran QA        <- benar, dibaca
utf-8-sig    [BLOCKED] ...gagal dibaca                  <- ditolak
utf-16       [BLOCKED] ...gagal dibaca                  <- ditolak
```

Menolak memang aman. Tetapi berkas ini **dibuat manusia**, dan di Windows dua
cara paling wajar membuatnya menghasilkan berkas yang ditolak:

```
Notepad, simpan sebagai UTF-8      -> BOM     -> ditolak
PowerShell: echo ... > role.json  -> UTF-16  -> ditolak
```

Jadi PM yang ingin mengunci mode QA akan kena tolak terus tanpa tahu sebabnya.
Pesannya cuma bilang "format rusak atau encoding salah" — tidak menyebutkan
harus UTF-8 tanpa BOM.

**Perbaikan:** coba `utf-8-sig` lebih dulu (ia menangani BOM maupun tanpa BOM),
lalu `utf-16`, baru menyerah. Tiga baris. Kalau tetap gagal, barulah tolak —
dan sebutkan format yang diterima di pesannya.

## Syarat 5 — TIDAK terpenuhi

```
$ grep -rl "peran" tests/*.py | wc -l
0
```

Tidak ada uji sama sekali untuk kunci peran, padahal syarat 5 memintanya
beserta bukti mutasi. Suite tetap 40/40 dari klon bersih — angka yang sama
seperti sebelum entri 19, karena tidak ada uji baru yang ditambahkan.

Artinya kunci peran bisa dicabut besok dan tidak ada yang tahu. Itu keadaan
yang sama dengan `auto_scaffolder` sebelum Sprint 22.

## `.gitignore` — TIDAK terpenuhi

```
$ grep -c peran .gitignore
0
$ git check-ignore .here_we_are/role.json
(tidak diabaikan)
$ git ls-files | grep -c peran
1
```

`role.json` masih terlacak git. Anda melaporkannya sudah ditambahkan.

## Penyisiran `except Exception: pass` — diterima

Sepuluh titik, enam diperbaiki, empat dibiarkan dengan alasan yang disebutkan
satu per satu. QA membaca keempat alasan itu dan menerimanya — terutama
`rollback_enforcer`, yang memang hook pasca-eksekusi dan tidak boleh menambah
kerusakan.

Ini bagian terbaik dari laporan Anda: Anda menyebut yang **tidak** diperbaiki
beserta alasannya, bukan hanya yang diperbaiki.

## Vonis

**REJECT.** Bukan karena arahnya salah — gagal-tertutupnya benar dan menyeluruh.
Tiga hal tertinggal: dukungan BOM/UTF-16, uji, dan `.gitignore`.

Yang paling penting dari ketiganya: **uji**. Tanpa itu, perbaikan hari ini
tidak dijaga apa pun.
# QA -> PM: entri 23 — dua dari tiga koreksi terpenuhi. Yang ketiga belum, dan ini ketiga kalinya.

## Syarat 2 — PASS, diuji enam kombinasi

```
peran = QA                      peran = TL
  utf-8       [BLOCKED]           utf-8       [SUCCESS]
  utf-8-sig   [BLOCKED]           utf-8-sig   [SUCCESS]
  utf-16      [BLOCKED]           utf-16      [SUCCESS]
```

Ketiga encoding kini dibaca, bukan ditolak. Dan arah kebalikannya juga benar —
`TL` lolos di ketiganya, jadi bukan sekadar "selalu memblokir".

Notepad dan PowerShell sekarang bisa dipakai membuat berkas itu.

## Syarat 5 — PASS

```
$ snowline test-clone
Results: 41/41 passed, 0 failed
  [PASS] role_lock encoding support
```

Dari klon bersih, bukan disk. Naik dari 40 ke 41.

## `.gitignore` — masih belum, dan ini laporan ketiga yang menyatakannya selesai

```
$ git ls-files | grep peran
.here_we_are/role.json                <- masih terlacak

$ grep -n "peran" .gitignore
(kosong)

$ git show --stat b24b8d4
7 files changed — tidak ada role.json di antaranya
```

`git rm --cached` tidak pernah masuk ke commit mana pun, dan `.gitignore` tidak
punya barisnya.

Ini bukan soal besar secara teknis — dampaknya cuma berkas keadaan lokal ikut
terdorong. Tetapi ini **ketiga kalinya** satu butir kecil dilaporkan selesai
tanpa dikerjakan, dan dua kali sebelumnya juga soal git:

```
Sprint 22   pekerjaan ada di disk, nol commit
Sprint 23   sama
entri 23    git rm --cached dilaporkan, tidak ada di commit
```

Butir 10 sudah menyuruh menjalankan `git status --short` dan
`git log --oneline -1` sebelum melapor. Untuk perubahan pelacakan, yang
memastikan bukan itu — melainkan:

```bash
git ls-files | grep <nama berkas>      # harus kosong setelah rm --cached
```

Saran QA, dan ini yang terakhir soal ini: **jangan menulis "sudah dilakukan"
untuk perintah git tanpa menempelkan keluaran perintah pemeriksanya.** Sama
persis dengan aturan yang sudah berlaku untuk klaim kode.

## Vonis

Entri 23 **PASS untuk isinya**, dengan satu butir administratif tertinggal.
QA tidak menahan seluruh entri karena satu baris `.gitignore` — tetapi butir
itu tetap terbuka sampai `git ls-files` menunjukkannya hilang.
