# PM -> TL: Sprint 27 — dua perbaikan aturan

Keduanya kecil dan tidak bergantung satu sama lain.
## Enam cacat, urut dari yang paling merusak

### Entri 28 — guardian memblokir seluruh commit di proyek Firebase

Bukti lengkap ada di vonis tepat di atas. Ringkasnya: 8 CRITICAL di
`pengingat_oli`, kedelapannya kunci konfigurasi Firebase yang memang publik,
dan hook menggerbangkan commit pada `critical > 0`.

**Syarat lulus:**
1. Di `pengingat_oli`, CRITICAL dari berkas konfigurasi Firebase hilang.
2. Kunci `AIza` yang ditanam di berkas biasa **tetap** CRITICAL. Buktikan
   dua arah — ini yang paling penting.
3. Uji, dibuktikan mutasi.

Jangan mematikan pola `AIza` seluruhnya.

### Entri 29 — `close-entry` memaku `.here_we_are`

```
core_close_entry.py:7-11    Path(".here_we_are")
```

Tidak jalan di proyek yang memasang chamber ke `.agents/chamber/`.
`core_context.py:8-9` sudah benar memeriksa dua lokasi. Tiru itu.

**Syarat lulus:** jalankan di `pengingat_oli` dan tempel keluarannya.

### Entri 30 — impor bayangan, sepuluh titik

Empat di dalam fungsi gerbang, dan satu sudah aktif merusak:

```
$ replace_text.py ... --apply     # role.json = QA
UnboundLocalError: cannot access local variable 'sys'
[BLOCKED] Akses tulis (--apply) ditolak untuk role QA.
```

**Syarat lulus:**
1. Kesepuluh dicabut.
2. Keluaran kunci peran bersih — satu baris `[BLOCKED]`, tanpa traceback.
3. Uji `role_lock` diperluas: keluaran tidak boleh memuat `Traceback` atau
   `UnboundLocalError`.

### Entri 31 — `test-clone` mengandaikan tata letak snowline

```
proyek tanpa tests/run_tests.py  ->  [FAIL] Skrip tes tidak ditemukan
proyek non-git                   ->  [FAIL] bukan repositori Git
```

Keduanya bukan kegagalan; keduanya keadaan wajar di proyek orang.

**Syarat lulus:** terima `--cmd "npm test"`, atau deteksi otomatis. Proyek yang
tidak punya uji dilaporkan sebagai `[INFO] tidak ada uji terdeteksi`, bukan
`[FAIL]`.

### Entri 32 — `.dart_tool`, `.gradle`, `.pub-cache`, `Pods` belum dikecualikan

Artefak build dilaporkan "tidak dipindai, terlalu besar".

### Entri 33 — `STATE.md` yang dikirim masih berjudul `# KEADAAN`

Sekalian sisir templat chamber lain untuk sisa rename yang sama.
# PM -> TL: kalibrasi masuk chamber — dua langkah tanpa kode baru

Rancangan lengkapnya di `.here_we_are/DESIGN_CALIBRATION.md`. Baca dulu; di
sana ada alasan kenapa penandanya peristiwa, bukan panjang konteks.

Dikerjakan **setelah** tiga hal di entri sebelumnya (pyproject 1.1.2, butir 10
disalin, ONBOARDING_TL tanpa afirmasi).

## Entri A — laporan TL masuk connector

Dihitung dari `history/` dan `connector.md`:

```
entri berjudul     59
vonis QA           30     (11 REJECT, 19 PASS)
laporan TL          6
```

Chamber menyimpan penilaiannya, bukan yang dinilai. Laporan TL hampir selalu
lewat chat ke PM dan berhenti di sana.

Akibatnya tidak ada yang bisa diukur nanti. Vonis REJECT tersimpan, tetapi
kalimat yang menyebabkannya tidak.

**Yang berubah, di `ONBOARDING_TL.md` bagian SELESAI:**

```
Tulis laporanmu ke connector lebih dulu — perintah dan keluarannya, utuh.
Baru katakan "selesai — silakan sinyal PM". Yang dikirim ke PM adalah
penunjuk ke entri itu, bukan laporannya sendiri.
```

**Syarat lulus:**
1. `ONBOARDING_TL.md` diperbarui.
2. Butir 3 di kedua `CHAMBER_RULES.md` menegaskannya: satu saluran berarti
   laporan TL juga di sana, bukan cuma vonis QA.
3. Laporan Anda untuk entri ini sendiri sudah memakai bentuknya. Itu
   pembuktiannya.

## Entri B — kalibrasi awal sesi

Bukan kuis. Satu tindakan, hasilnya biner.

Sebelum sesi baru boleh melapor atau memvonis apa pun:

```bash
snowline test-clone
```

```
GET /repos/UsmanAzizz/snowline-agent-tools/actions/runs?per_page=1
    -> head_sha + conclusion
```

Lalu bandingkan `head_sha` CI dengan `git log -1`:

```
sama + hijau      boleh bekerja
sama + merah      perbaiki dulu, jangan tambah entri baru
beda              ada yang belum dipush; selesaikan itu dulu
```

Tiga puluh detik. Ia menjawab pertanyaan yang selama delapan commit tidak ada
yang menanyakan.

Yang membuatnya kalibrasi: sesi itu **menjalankan**, tidak membaca `STATE.md`.
Angka yang disalin dari catatan tidak membuktikan apa pun tentang sesi yang
menyalinnya.

**Kapan diulang** — peristiwa, bukan panjang konteks:

```
setelah vonis REJECT atas laporanmu sendiri
setelah kata cakupan ("seluruh", "sepenuhnya", "semua") ditolak QA
setelah tiga laporan sejak kalibrasi terakhir
sebelum memasang tag rilis apa pun
```

Yang terakhir paling terbukti perlu: dua tag berturut-turut dipasang di atas
keadaan yang tidak diperiksa.

**Syarat lulus:**
1. Bagian **LANGKAH PERTAMA** di `ONBOARDING_TL.md` dan `ONBOARDING_QA.md`
   dimulai dengan kalibrasi ini, sebelum membaca `STATE.md`.
2. Daftar pemicu kalibrasi ulang masuk ke kedua berkas itu.
3. Butir 10 di kedua `CHAMBER_RULES.md` menunjuk ke kalibrasi sebagai cara
   memeriksa CI — jangan menulis prosedurnya dua kali di tempat berbeda.
4. Jalankan kalibrasinya sendiri sekarang dan tempel hasilnya di laporan entri
   ini. Kalau CI merah saat Anda menjalankannya, itu hasil yang sah — laporkan
   apa adanya, jangan diperbaiki dulu diam-diam.

## Yang TIDAK dikerjakan sekarang

Tiga pengukuran di bagian 6 rancangan — selisih cakupan, klaim tanpa blok,
klaim berulang setelah ditolak — **ditunda**. Ketiganya butuh laporan TL yang
tersimpan, dan sekarang baru ada enam.

Bangun entri A dulu, kumpulkan datanya, baru ukur. Mengukur enam sampel lalu
menyimpulkan pola adalah kesalahan yang sama bentuknya dengan "di seluruh
utilitas".

## Catatan tentang batasnya

Kalibrasi memeriksa apakah sesi ini bisa menjalankan dan melaporkan apa adanya.
Ia tidak memeriksa apakah penilaiannya bagus — yang menahan itu tetap pemisahan
peran.

Dan kalau setelah sebulan tidak pernah ada yang gagal kalibrasi, ambangnya yang
salah, bukan agennya yang sempurna.

**Tidak dikunci.**
