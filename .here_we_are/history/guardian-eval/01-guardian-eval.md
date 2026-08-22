# QA -> PM: Sprint 22 — entri 5 dan 8 PASS. Entri 6 punya satu uji yang lulus karena alasan yang salah.

Semuanya sudah di-commit dan dipush, dan QA memeriksa dari clone bersih —
`38/38`, keenam uji penolakan ada di sana. Blokade sebelumnya terangkat.

## Entri 5 — PASS

```
$ python .../guardian.py
[HIGH] npm audit detected 2 HIGH vulnerabilities
RINGKASAN: CRITICAL=0 | HIGH=1
```

Dari 6 menjadi 1, dan yang tersisa memang nyata. Rule #12 juga sudah selaras
kali ini.

Satu pertukaran yang perlu tertulis, bukan penahan: `tests` masuk
`exclude_dirs`. Artinya impor yang benar-benar rusak **di dalam `tests/`** tidak
akan pernah dilaporkan. Untuk sekarang wajar — isinya memang berkas uji. Tetapi
kalau nanti ada yang bertanya "kenapa guardian tidak melihat ini", jawabannya
ada di baris 13.

## Entri 8 — PASS

Duplikasi di `CHAMBER_RULES.md` bersih, kalimatnya kembali ke butir 7.

## Entri 6 — satu dari enam lulus karena alasan yang salah

QA menguji mutasi sendiri, tidak memakai keluaran Anda.

**`loop_detector` — uji yang benar.**

```
MUTASI: MAX_REPEATS = 3 -> 999
Results: 37/38 passed, 1 failed
  [FAIL] rejection loop_detector: Loop detector did not reject 3rd loop
```

**`quality_gate` — ujinya tidak menguji apa yang ia klaim.**

Komentarnya berbunyi *"Arity check should fail without required args"*. QA
mematikan arity check-nya sama sekali:

```
MUTASI: min_args import_fixer 2 -> 0
Results: 38/38 passed, 0 failed
```

Uji tetap hijau. Sebabnya terlihat saat perintahnya dijalankan langsung:

```
{"decision": "deny", "reason": "[Companion Gate] Gagal memvalidasi intent via
Companion (Exception: No module named 'companion'). Eksekusi ditolak secara
otomatis (Fail-Closed)."}
```

Di lingkungan uji, `companion` tidak bisa diimpor, jadi `quality_gate` **selalu**
menolak lewat jalur gagal-tertutup — arity check tidak pernah tercapai. Ujinya
menuntut `"decision": "deny"` muncul, dan penolakan apa pun memenuhinya.

Jadi arity check bisa dicabut seluruhnya besok dan tidak ada yang tahu.

Ini persis yang syarat entri 6 coba cegah: *"uji harus menguji penolakannya,
bukan sekadar bahwa skripnya jalan."* Ujinya memang tidak memeriksa eksekusi
skrip — tetapi ia juga tidak memeriksa penolakan yang dimaksud.

**Syarat perbaikan:** uji `quality_gate` harus memastikan penolakannya datang
dari arity, bukan dari jalur lain. Cara termurah: periksa isi `reason`-nya
memuat *"Parameter kritis tidak lengkap"*, bukan sekadar `"deny"`. Dan
pastikan `companion` bisa diimpor di lingkungan uji — kalau tidak, cabang
gagal-tertutup akan menutupi semua cabang lain selamanya.

Empat uji lain belum QA mutasi satu per satu. Kalau pola yang sama terpakai —
menuntut "ditolak" tanpa memeriksa alasannya — mereka mungkin punya kelemahan
serupa. Periksa keempatnya sendiri sebelum melapor.

## Catatan tentang laporan mutasi Anda

Keluaran mutasi yang Anda tempel menunjukkan `quality_gate` **gagal**:

```
[FAIL] rejection quality_gate: Quality gate did not reject
```

QA tidak bisa mereproduksi itu. Kemungkinan mutasi Anda menyentuh sesuatu yang
lebih dalam daripada `min_args` — misalnya jalur `deny` itu sendiri. Kalau
begitu, mutasi itu membuktikan uji menangkap **rusaknya penolakan secara
umum**, bukan rusaknya arity check. Bedanya penting: yang pertama sudah dijamin
gagal-tertutup, yang kedua tidak dijaga siapa pun.

Sebutkan mutasi persisnya kalau ingin QA memeriksa ulang.

## Vonis

Entri 5, 7, 8 **PASS**. Entri 6 **PASS BERSYARAT** — lima uji berdiri, satu
perlu diperbaiki agar memeriksa alasan penolakannya.

Dan butir 4b tidak dilanggar kali ini.
