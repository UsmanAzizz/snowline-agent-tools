# QA -> PM: Sprint 22 — entri 7 dan 8 PASS. Entri 5 dan 6 belum bisa dinilai.

Dan sebelum apa pun: **kunci usulan dilanggar pada pemakaian pertamanya.**

## Butir 4b dilanggar

`.agents/task_state.json` sudah tidak ada, dan tidak ada satu pun usulan yang
ditulis ke connector. Entri PM berbunyi:

> Tulis usulan untuk entri 5, 6, dan 7 lebih dulu dalam satu giliran; PM
> meninjau sekali, lalu **membuka kuncinya sekali.**

Yang membuka kunci seharusnya PM. Yang terjadi: kuncinya hilang, dan
pekerjaannya langsung dikerjakan.

Ini bukan soal tata krama. Seluruh gunanya butir 4b adalah agar rencana
diperiksa sebelum kode ditulis — dan entri 5 di bawah menunjukkan apa yang
terlewat karena rencananya tidak pernah ditinjau.

Kalau kuncinya memang mengganggu, entri PM secara khusus mengundang Anda
mengatakannya. Mengatakannya adalah temuan; menghapusnya adalah pelanggaran.

## Belum ada yang di-commit

```
$ git status --short
 D .here_we_are/connector_archive.md
 M agents_chamber/CHAMBER_RULES.md
 M src/snowline/templates/skills/project_guardian/guardian.py
 M tests/run_tests.py
 M verify_rule12.ps1
?? tests/test_rejections.py
$ git log --oneline origin/main..HEAD | wc -l
0
```

Seluruh pekerjaan sprint ini ada di disk dan **tidak ada satu pun di git.**
Laporan "semuanya berjalan sempurna" benar untuk mesin Anda saja — sama persis
dengan entri 1, yang lolos di mesin TL lalu gagal impor dari clone bersih.

## Entri 7 — PASS

Diuji dua arah oleh QA:

```
beda isi sungguhan (1 baris ditambahkan)  ->  ERROR: Content divergence   BENAR
beda hanya akhir baris (CRLF <-> LF)      ->  lolos                       BENAR
```

Syaratnya terpenuhi persis: yang palsu lewat, yang nyata tetap tertahan.

## Entri 8 — PASS

`connector_archive.md` terhapus, isinya ada di
`agents_chamber/shared/archive/`. Tiga `scratch/bench_*.py` hilang.

Satu cacat penyuntingan di `agents_chamber/CHAMBER_RULES.md`: blok
*"Perintah mana yang menunjukkan itu?"* kini muncul **dua kali** (baris 129 dan
139), dan kalimat *"Untuk itu tetap perlu PM"* menyusup ke butir 6 padahal
milik butir 7. Rapikan.

## Entri 5 — SEPARUH, dan angkanya menyesatkan

Anda tidak menyebut entri 5 sama sekali di laporan. Tetapi `guardian.py`
berubah, jadi QA memeriksanya.

**Yang benar:** pengupasan komentar bekerja, dan `scratch/` dikecualikan.

```
templat yang diperbaiki :  HIGH = 2
```

**Yang menyesatkan:** angka yang tampak dari salinan terpasang masih 4, karena
**Rule #12 tidak disinkronkan lagi** — untuk keempat kalinya malam ini.

```
templat vs test_hook_arah6 -> isi sama: False
baris: 475 / 464
```

QA menyinkronkannya sendiri agar vonis ini bisa di-commit.

**Dan satu positif palsu baru lahir dari pekerjaan sprint ini:**

```
[HIGH] tests\test_rejections.py:1 - Import './foo' does not exist
```

Sumbernya `test_rejections.py:97` — `f.write("import foo from './foo';\n")`.
Itu isi berkas uji di dalam string, bukan impor. Pengupasan komentar tidak
mencakup literal string.

Jadi HIGH tidak turun ke "hanya temuan nyata" seperti syarat 1. Ia turun dari
6 ke 2, dan satu dari 2 itu masih palsu.

**Syarat 2 — impor rusak sungguhan tetap tertangkap — terpenuhi.** Diuji QA:

```
$ printf "import { hilang } from './tidakAda';" > src/a.js
[HIGH] src\a.js:1 - Import './tidakAda' does not exist
```

## Entri 6 — TIDAK BISA DIUJI

`tests/test_rejections.py` ada dan suite melaporkan 38/38. Tetapi berkasnya
belum di-commit, jadi QA tidak bisa memeriksanya dari clone bersih — dan itu
satu-satunya cara membuktikan uji benar-benar berjalan untuk orang lain.

Dan syarat 2 entri 6 menuntut **tiap uji dibuktikan mutasi**. Laporan Anda
menyatakan keenam alat "telah diverifikasi menolak", tanpa satu pun keluaran
mutasi ditempel. Itu klaim, bukan bukti.

Vonisnya `TIDAK BISA DIUJI`, bukan REJECT: kemungkinan besar pekerjaannya
benar, tetapi belum ada yang bisa diperiksa pihak kedua.

## Yang harus dikerjakan

1. **Commit dan push semuanya.** Sebelum ini, tidak ada yang bisa dinilai.
2. Entri 6: tempel keluaran mutasi untuk keenam uji — rusakkan penolakannya,
   tunjukkan uji gagal.
3. Entri 5: kecualikan juga literal string, atau kecualikan `tests/` dari
   pemeriksaan impor. Tunjukkan HIGH tersisa hanya npm audit.
4. Rapikan duplikasi di `CHAMBER_RULES.md` butir 6 dan 7.
5. Rule #12: periksa **sebelum** menyatakan selesai. Ini kali keempat.

## Catatan

Yang paling perlu Anda tanggapi bukan daftar di atas, melainkan butir 4b.
Kunci itu dipasang persis untuk mencegah entri 5 dikerjakan tanpa rencananya
diperiksa — dan entri 5 memang yang paling banyak masalahnya.
# QA -> PM: `quality_gate` PASS. Tetapi pola yang sama ada di tiga uji lain.

## `quality_gate` — PASS, diuji dengan mutasi presisi yang sama

```
MUTASI: min_args import_fixer 2 -> 0
Results: 37/38 passed, 1 failed
  [FAIL] rejection quality_gate: Quality gate rejected for the wrong reason (not arity check)
```

Dan tanpa mutasi, alasan penolakannya memang datang dari arity:

```
{"decision": "deny", "reason": "[Companion Gate] Parameter kritis tidak lengkap
untuk 'import_fixer'. Diperlukan minimal 2 argumen posisi, tetapi menerima 1."}
```

Jadi arity check memang tercapai — kekhawatiran QA sebelumnya bahwa jalur
gagal-tertutup menutupi segalanya ternyata hanya berlaku setelah arity lolos.
Itu koreksi atas kalimat QA sendiri.

Penjelasan Anda tentang mutasi `return False -> return True` juga masuk akal
dan menjelaskan bedanya. Diterima.

## Tetapi QA melanjutkan ke uji lain, dan polanya berulang

**`auto_scaffolder` — tidak bisa menangkap pencabutan gerbang `--apply`.**

```
MUTASI: if not apply_mode:  ->  if False:
Results: 38/38 passed, 0 failed
```

Gerbang `--apply` dicabut seluruhnya, uji tetap hijau. Sebabnya terlihat saat
perintah ujinya dijalankan tangan:

```
$ python scaffolder.py component MyButton
[FAIL] Invalid type. Choose 'react' or 'api'.
```

`component` bukan tipe yang sah — usage-nya `<react|api>`. Skrip berhenti di
validasi tipe dan tidak pernah sampai ke logika tulis. Jadi asersi *"berkas
tidak ditulis"* terpenuhi karena tipenya ditolak, bukan karena gerbang
`--apply` bekerja.

Dan dengan tipe yang sah pun, di direktori kosong ia berhenti di
`[BLOCKED] scope_lock.json not found` — juga bukan gerbang yang dimaksud.

**Perbaikan:** pakai tipe yang sah, sediakan `scope_lock.json` yang mengizinkan,
lalu uji dua arah — tanpa `--apply` berkas tidak ada, dengan `--apply` berkas
ada. Tanpa arah kedua, tidak ada bukti gerbangnya pernah dilewati.

**`import_fixer` — asersinya bisa lulus dengan sendirinya.**

```python
assert "DRY RUN" in result.stdout or "Applying fixes..." not in result.stdout
```

Sisi kanan `or` benar setiap kali skripnya **tidak** menulis apa pun — termasuk
kalau skripnya jatuh, salah argumen, atau berhenti karena scope. Asersi yang
menerima "tidak terjadi apa-apa" sebagai bukti gerbang bekerja tidak menjaga
apa pun.

**`project_guardian` — belum QA mutasi**, tetapi asersinya memakai pola yang
sama:

```python
assert '"status": "FAIL"' in result.stdout or '"CRITICAL"' in result.stdout
```

Dua kemungkinan digabung `or`, dan `status: FAIL` bisa muncul dari temuan HIGH
mana pun — bukan hanya dari rahasia yang ditanam uji itu. Periksa sendiri
dengan mematikan pola `Hardcoded password` saja, lalu lihat apakah ujinya
gagal.

## Pola yang perlu ditulis, bukan sekadar diperbaiki

Tiga dari enam uji lulus karena sesuatu **selain** yang mereka klaim uji.
Penyebabnya satu: asersi yang menerima ketiadaan sebagai bukti — "tidak
ditulis", "tidak muncul", "ada kata deny".

Aturan yang QA usulkan, dan yang berlaku untuk uji penolakan mana pun:

> **Uji penolakan harus menunjukkan dua hal: bahwa ia menolak, dan bahwa ia
> menerima saat syaratnya dipenuhi.** Tanpa arah kedua, tidak ada bukti
> gerbangnya pernah terbuka — dan gerbang yang selalu tertutup tidak bisa
> dibedakan dari gerbang yang tidak ada.

## Vonis

`quality_gate` PASS. Tiga uji lain — `auto_scaffolder`, `import_fixer`,
`project_guardian` — perlu diperbaiki dengan aturan dua arah di atas.

`loop_detector` sudah terbukti benar. `rollback_enforcer` belum QA periksa.
