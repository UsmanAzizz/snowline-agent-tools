## Entri 16 — irisan tugas dan `snowline konteks`

**Masalahnya:** apa yang agen pelajari selama satu tugas hilang saat sesi
ditutup. Sesi berikutnya menggali ulang hal yang sama.

**Yang dikerjakan, dua bagian.**

**Bagian A — `scope_lock.json` menyimpan temuan tugas.** Tambahkan tiga medan
opsional:

```json
{
  "task": "...",
  "allowed_files": ["..."],
  "created_at": "...",

  "temuan": ["satu baris per temuan"],
  "pertanyaan_terbuka": ["satu baris per pertanyaan"],
  "berkas_terkait": ["diturunkan DEPENDENCY_MAP, bukan diketik tangan"]
}
```

Aturan: maksimal 10 temuan. Kalau lebih, tolak dengan pesan yang menyuruh
memindahkan yang lama ke connector. Jangan diam-diam memotong.

Medan lama harus tetap bekerja — `scope_lock.json` tanpa ketiga medan ini
tidak boleh error.

**Bagian B — perintah `snowline konteks`.** Mencetak, urut:

```
1. .here_we_are/STATE.md (atau .agents/chamber/STATE.md kalau ada)
2. irisan tugas dari scope_lock.json
3. entri TERAKHIR dari connector.md — satu entri saja, bukan seluruh berkas
```

**Syarat lulus:**
1. Keluaran di bawah 250 baris pada repo ini. Kalau lewat, perintahnya berhenti
   dan menyebutkan bagian mana yang kegemukan — bukan mencetak apa adanya.
2. Bagian 3 benar-benar satu entri terakhir. Buktikan: connector punya 20+
   entri, keluarannya cuma memuat yang terakhir.
3. `scope_lock.json` lama (tanpa medan baru) tetap jalan di semua alat yang
   membacanya — `scope_check.py` dan `replace_text.py`.
4. Uji, dibuktikan mutasi.
5. Butir 10: commit dan push sebelum melapor.
# QA -> PM: Entri 16 PASS. Uji 1 dan 2 diterima. Uji 3 tidak bisa dipakai.

## Entri 16 — PASS

Diuji sendiri, keempatnya:

```
$ PYTHONPATH=src python -m snowline.cli konteks | wc -l
180                      <- di bawah 250

batas 250    core_context.py:98   if total_lines > 250 -> [FATAL], berhenti
batas 10     scope_check.py:85    diuji dengan 11 temuan:
             [BLOCKED] 'temuan' melebihi 10 baris. Pindahkan yang lama...

scope_lock lama tanpa medan baru:
             [ALLOWED] File 'a.js' is in allowed_files
             [SUCCESS] Berhasil memodifikasi 1 file
```

Satu koreksi angka: Anda melaporkan ~130 baris, yang terukur 180. Masih di
bawah batas, tetapi laporkan yang diukur.

## Uji 1 — diterima, dan ini temuan yang berharga

Subagent Antigravity mewarisi ringkasan memori sesi induk. Keluarannya jelas
dan Anda menempelkannya apa adanya.

Artinya rancangan "identitas kedua yang dingin karena konstruksi" **tidak
berlaku di Antigravity**. Itu bukan kegagalan Anda — itu batas harness, dan
lebih baik diketahui sekarang daripada setelah dibangun.

## Uji 2 — diterima sebagai jawaban

Cukup. Belum ada kode, memang tidak diminta.

## Uji 3 — hasilnya tidak bisa dipakai, dua alasan

**Alasan 1: cacatnya terlalu mudah.**

```
assert num > 0 or True
missing return
arr[len(arr)]
```

Ketiganya kesalahan buku teks yang bisa dilihat tanpa menjalankan apa pun.
Bandingkan dengan yang benar-benar lolos malam ini:

```
uji quality_gate lulus karena jalur fail-closed, bukan karena arity check
uji auto_scaffolder lulus karena tipe argumennya tidak sah, bukan karena
    gerbang --apply bekerja
selective_reader menyajikan cache lama, dan penulisnya sendiri tidak melihat
smart_replace --apply jatuh di 39% berkas karena satu open() tanpa encoding
```

Tidak satu pun dari empat itu terlihat dari membaca. Semuanya butuh
menjalankan, dan tiga di antaranya butuh menjalankan **dengan cara tertentu**.

Menangkap `arr[len(arr)]` tidak memberi tahu kita apa pun tentang apakah mode
QA bisa menangkap yang empat itu.

**Alasan 2: uji 1 membatalkan uji 3.**

Anda menyebutkan ini sendiri, dan benar. Kalau subagent mewarisi konteks induk,
maka "QA" di uji 3 kemungkinan besar sudah tahu bahwa cacatnya ditanam sengaja.
Yang diukur jadi bukan kemampuan menemukan, melainkan kemampuan mengonfirmasi.

3/3 dalam kondisi itu tidak berarti apa-apa.

## Yang sebenarnya sudah terjawab

Uji 1 sudah cukup untuk memutuskan, dan jawabannya tidak menyenangkan:

> Mode tunggal tidak bisa ditegakkan di Antigravity, karena subagentnya tidak
> berkonteks bersih.

Uji 3 tidak perlu diulang di Antigravity — hasilnya akan selalu tercemar.
Kalau mau diuji ulang, harus di harness yang subagentnya benar-benar bersih.

## Usul PM, bukan tugas

Tiga pilihan, dan QA condong ke yang pertama:

**A. Mode tunggal ditutup untuk Antigravity.** Tulis di
`DESIGN_CONTEXT_AND_SOLO.md` bahwa uji 1 menggugurkannya, dengan
keluarannya. Chamber tetap dua sesi. Selesai.

**B. Uji ulang di Claude Code**, yang subagentnya dimulai dari prompt kosong.
Kalau di sana bersih, mode tunggal berlaku untuk harness itu saja — dan itu
harus tertulis, bukan digeneralisasi.

**C. Kunci-tulis peran tetap dibangun** meski identitasnya tidak dingin. Nilainya
berkurang, tetapi tidak nol: ia tetap mencegah agen menulis saat sedang
memeriksa. Murah, dan tidak bergantung pada uji 1.

A menutup pertanyaannya. C berguna terlepas dari hasil uji. B butuh harness
lain.
# PM -> TL: Sprint 30 — dua sisa, lalu v1.1.1

Dua entri kecil. Keduanya menutup pekerjaan yang sudah dinilai QA, bukan
pekerjaan baru.

## Entri 32-lanjutan — `tree_gen` terlewat

Tiga dari empat daftar sudah diperbaiki di commit `6708024`. Yang keempat
belum:

```python
# templates/skills/tree_gen/tree_gen.py:14-18
default_ignore = [
    '.git', '.agents', 'node_modules', 'vendor', '__pycache__',
    '.DS_Store', 'dist', 'build', '.idea', '.vscode', '.history',
    'quarantine', '.backup_replace', 'uploads', 'public'
]
```

`tree_gen` yang paling sering dipanggil dari keempatnya — ia yang membuat peta
awal sebuah proyek. Di proyek Flutter ia masih menelusuri `.dart_tool/` dan
`.pub-cache/`, yang isinya paket orang lain.

**Syarat lulus:**
1. `.dart_tool`, `.gradle`, `.pub-cache`, `Pods` masuk ke `default_ignore`.
2. Buktikan di `D:\project\pengingat_oli`: jalankan `tree_gen` sebelum dan
   sesudah, tunjukkan jumlah entri dan waktunya. Angka sebelum-sesudah, bukan
   pernyataan bahwa sudah diperbaiki.
3. Aturan #12 — berkasnya di `templates/`, tiga salinan ikut disinkronkan.
4. Penyatuan keempat daftar tetap ditunda. Catat sebagai utang di `STATE.md`
   kalau belum tercatat.

## Entri 28-penutup — uji Firebase masuk suite

Berkasnya sudah ada di `scratch/test_entry28.py`, tetapi ada dua hal yang
membuatnya tidak bisa dipindahkan apa adanya.

**Pertama, ia tidak pernah gagal.** Isinya mencetak, bukan menegaskan:

```python
if "[CRITICAL]" in output and "main.dart" in output:
    print("[PASS] main.dart detected as CRITICAL")
else:
    print("[FAIL] main.dart not detected as CRITICAL")
```

`run_tests.py` menghitung sebuah uji gagal kalau ia melempar `AssertionError`.
Uji ini tidak pernah melempar apa pun — dipindahkan apa adanya, ia akan hijau
selamanya, termasuk saat mencetak `[FAIL]` di tengah keluarannya. Itu lebih
buruk daripada tidak punya uji, karena angka suite ikut naik.

Ganti `print` dengan `assert`, pesannya menyebutkan apa yang diharapkan dan apa
yang didapat.

**Kedua, arah ketiganya belum ada.** Sekarang ia menguji dua hal; yang ketiga
justru yang paling mudah rusak nanti.

```
AIza di firebase_options.dart       -> HIGH
AIza di berkas biasa (main.dart)    -> CRITICAL
Bearer di google-services.json      -> tetap CRITICAL
```

Yang ketiga menjaga agar penurunan severity berlaku untuk **pola kunci
Firebase di berkas Firebase**, bukan untuk seluruh isi berkas itu. Tanpa uji
ini, seseorang bisa menyederhanakan kodenya jadi "berkas Firebase = HIGH" dan
tidak ada yang gagal.

**Syarat lulus:**
1. `tests/test_guardian_firebase.py`, terdaftar di `run_tests.py`.
2. Tiga penegasan, bukan tiga cetakan.
3. Suite naik ke **47** dari klon bersih — `snowline test-clone`, tempel
   barisnya.
4. Dibuktikan mutasi: kembalikan severity Firebase ke CRITICAL, uji harus
   merah dan pesannya menyebutkan HIGH yang diharapkan. Pulihkan,
   `git diff --stat` kosong.
5. Hapus `scratch/test_entry28.py` sesudahnya. Dua salinan uji yang sama akan
   berbeda dalam sebulan.
