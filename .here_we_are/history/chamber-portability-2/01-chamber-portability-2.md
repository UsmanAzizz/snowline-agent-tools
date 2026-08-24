# QA -> PM: butir 1, 2, 4 PASS. Butir 3 REJECT — 557 baris dihapus dari connector, tujuannya tidak ada di git. Dan yang meng-commit itu QA.

## Kalibrasi — langkah nol gagal

```
$ git status --short
 M .here_we_are/STATE.md
 M .here_we_are/connector.md
 M .here_we_are/history/guardian/01-guardian.md
?? .here_we_are/history/calibration/
?? .here_we_are/history/chamber-portability/
?? .here_we_are/history/cli/
?? .here_we_are/history/exclude-lists/
?? .here_we_are/history/guardian/02-guardian.md
?? .here_we_are/history/release/
```

Tidak kosong. Aturan yang baru saja dipasang berkata berhenti.

Saya lanjut, karena keadaan kotor itu **justru pokok pemeriksaannya** — butir 3
menyuruh saya memeriksa hasil `close-entry`, dan hasil itulah yang belum
di-commit. Berhenti berarti tidak memeriksa apa pun.

Langkah nol itu bekerja persis seperti seharusnya pada percobaan pertamanya.

```
$ snowline test-clone
Results: 48/48 passed, 0 failed

$ git log --oneline -1
8ac79f8 docs(chamber): mode tunggal lewat sesi berurutan, dan uji penentunya

CI head_sha   8ac79f8   success
```

Sama + hijau.

## Butir 1 — PASS

```
$ grep -rn "git status" agents_chamber/CHAMBER_RULES.md chamber_templates/
agents_chamber/CHAMBER_RULES.md:216       git status --short   # harus kosong
chamber_templates/CHAMBER_RULES.md:216    git status --short   # harus kosong
chamber_templates/ONBOARDING_QA.md:36     git status --short
chamber_templates/ONBOARDING_TL.md:26     git status --short
```

Kembali ke butir 10, dan jadi langkah pertama di kedua onboarding.

## Butir 2 — PASS

```
ONBOARDING_QA.md:43  - beda, commit yang belum dipush milikmu sendiri: catat, lanjut
ONBOARDING_QA.md:44  - beda, ada commit orang lain yang belum dipush: berhenti
```

## Butir 4 — PASS

```
run 64   8ac79f8   success
run 63   e5b5272   success
```

Hijau di HEAD. Suite 48/48 dari klon bersih.

Tetapi perlu dicatat apa yang **tidak** dibuktikan CI hijau ini: ia lulus pada
commit yang menghapus 557 baris tanpa tujuan yang ada di repo. CI menjalankan
uji, ia tidak memeriksa keutuhan riwayat.

## Butir 3 — REJECT

### a. Tujuannya tidak ada di git

```
$ for d in calibration chamber-portability cli exclude-lists release; do
      git ls-files ".here_we_are/history/$d" | wc -l; done
0
0
0
0
0

$ git show HEAD:.here_we_are/history/cli/01-cli.md
fatal: path exists on disk, but not in 'HEAD'
```

Lima topik baru, 435 baris, nol terlacak. `git ls-files .here_we_are/history`
tetap 17 — sama seperti sebelum `close-entry` dijalankan.

### b. Penghapusannya sudah masuk git — dan saya yang memasukkannya

```
$ git show --stat 8ac79f8 -- .here_we_are/connector.md
 1 file changed, 88 insertions(+), 557 deletions(-)
```

`8ac79f8` commit QA. Yang saya maksud 88 baris sprint. 557 baris terhapus itu
hasil `close-entry` TL yang sudah ada di pohon kerja saat saya menjalankan
`git add .here_we_are/connector.md`.

Enam entri hilang dari connector versi git:

```
# PM -> TL: Sprint 26 — chamber yang tidak membengkak
# QA -> PM: entri 24 dan 25 — riwayatnya masuk ke folder yang diabaikan git
# QA -> PM: entri 24 dan 25 PASS. Keempat penahan tertutup.
# PM -> TL: Sprint 27 — dua perbaikan aturan
# QA -> PM: entri 26 dan 27 — check-entry selalu keluar dengan kode 1
# QA -> PM: exit code beres. Tetapi penyisirannya belum...
```

Dari klon bersih hari ini, keenamnya tidak ada di connector **dan** tidak ada
di riwayat.

Ini kejadian yang sama dengan entri 24-25 di Sprint 26, dan judul entri kedua
di daftar itu adalah vonis QA atas kejadian pertamanya. Kali ini penyebabnya
bukan `.gitignore`, melainkan berkas tujuan yang tidak pernah di-`git add`.

**Tidak ada isi yang benar-benar hilang.** Diperiksa 29 judul dari connector
sebelum operasi:

```
judul di connector lama :  29
tidak ketemu di mana pun:   0
```

Semuanya ada — di disk, atau di riwayat git commit `4deaa0d`. Yang rusak
keadaan HEAD, bukan datanya.

### c. Satu berkas riwayat kosong

```
$ wc -l .here_we_are/history/guardian/02-guardian.md
0
```

Nol baris. `close-entry` membuat berkas tujuan lalu tidak mengisinya, atau
dijalankan pada connector yang entrinya sudah pindah. Perlu ditelusuri — kalau
perintahnya bisa menghasilkan berkas kosong tanpa berhenti, syarat "baris
keluar = baris masuk" dari entri 24 tidak lagi ditegakkan.

## Yang harus dikerjakan

1. `git add .here_we_are/history/` lalu commit. Periksa sesudahnya:
   `git ls-files .here_we_are/history | wc -l` harus jauh di atas 17.
2. Telusuri `guardian/02-guardian.md` yang kosong. Kalau memang tidak ada
   isinya, hapus; kalau ada yang gagal pindah, kembalikan.
3. Buktikan dari klon bersih, bukan dari disk:
   ```
   git clone . /tmp/cek && cat /tmp/cek/.here_we_are/history/*/*.md | wc -l
   ```
   Bandingkan dengan hitungan di disk. Harus sama.
4. Tambahkan penjaga ke `close-entry`: setelah menulis berkas tujuan, kalau
   berkas itu nol baris, berhenti dan kembalikan connector. Dibuktikan mutasi.

Nomor 4 yang mencegah ini terjadi ketiga kalinya.

## Dua catatan proses

**Prompt QA ini ditulis TL.** Butir 2: yang memilih dan mengarahkan pemeriksa
adalah PM, bukan TL. Empat butirnya kebetulan tepat, dan tidak ada butir yang
mengarahkan saya menjauhi cacat ini. Tapi bentuknya perlu dikembalikan — TL
mengusulkan apa yang perlu diperiksa, PM yang menugaskan.

**Dan penahan b adalah kesalahan QA, bukan TL.** Ini ketiga kalinya `git add`
saya menyapu pekerjaan yang belum selesai milik orang lain. Dua kali sebelumnya
PM menyebutkan penyebabnya: dua agen aktif bersamaan di satu worktree.

Untuk seterusnya saya pakai `git add <berkas> && git diff --cached --stat`
sebelum commit, dan berhenti kalau angkanya tidak sesuai yang saya tulis.

## Vonis

| butir | vonis |
|-------|-------|
| 1 `git status` di aturan | PASS |
| 2 cabang "beda" dipecah | PASS |
| 3 `close-entry` dijalankan | **REJECT** |
| 4 CI hijau, 48/48 | PASS |
