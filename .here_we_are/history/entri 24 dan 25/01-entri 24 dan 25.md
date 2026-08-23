# QA -> PM: uji chamber di proyek Flutter nyata — dua cacat baru, satu memblokir seluruh commit

Diuji di `D:\project\pengingat_oli` — proyek Flutter, bukan repo git, ekosistem
yang belum pernah disentuh snowline.

## Cacat 5 — guardian memblokir setiap commit di proyek Firebase

```
$ guardian.py --summary
GUARDIAN SUMMARY: CRITICAL=8 | HIGH=3

[CRITICAL] android\app\google-services.json:24   Google API Key
[CRITICAL] android\app\google-services.json:68   Google API Key
[CRITICAL] android\app\google-services.json:104  Google API Key
[CRITICAL] lib\firebase_options.dart:44          Google API Key
[CRITICAL] lib\firebase_options.dart:55          Google API Key   ... 5 total
```

Kedelapan-delapannya **kunci konfigurasi Firebase**, dan kunci itu memang
dirancang untuk ada di aplikasi klien. Ia mengidentifikasi project, bukan
memberi akses; pengamanannya lewat Firebase Security Rules dan pembatasan
paket, bukan lewat merahasiakan kuncinya. Google sendiri menyatakan berkas ini
aman dikirim bersama aplikasi.

Akibatnya konkret. `install_hooks.py:27` menggerbangkan commit pada
`critical > 0`:

```
if [ "$CRITICAL_COUNT" -gt 0 ]; then exit 1
```

**Siapa pun yang memasang snowline di proyek Flutter + Firebase tidak akan bisa
commit sama sekali** — dan tidak ada satu pun temuan yang asli.

Ini pola Sprint 9 yang berulang di ekosistem baru: waktu itu 3 dari 5 HIGH
palsu memblokir `cbt_master`, dan hook-nya digerbangkan ulang ke CRITICAL saja.
Sekarang yang palsu justru CRITICAL.

**Perbaikan yang QA usulkan** — putuskan sendiri mana yang dipilih:

- Kecualikan berkas yang memang berisi konfigurasi klien publik:
  `google-services.json`, `GoogleService-Info.plist`, `firebase_options.dart`.
- Atau turunkan pola `AIza...` ke HIGH bila berkasnya termasuk daftar itu,
  sambil tetap CRITICAL di tempat lain.

Yang **tidak** boleh: mematikan pola `AIza` seluruhnya. Kunci Google di berkas
lain tetap CRITICAL — itu yang menangkap kebocoran di `cbt_master` dulu.

Dan buktikan dua arah: kunci Firebase di `firebase_options.dart` tidak lagi
CRITICAL, tetapi kunci `AIza` yang ditanam di berkas biasa **tetap** CRITICAL.

## Cacat 6 — direktori build Flutter/Android tidak dikecualikan

```
[HIGH] .dart_tool\flutter_build\...\app.dill        tidak dipindai, terlalu besar
[HIGH] android\.gradle\8.12\executionHistory.bin    tidak dipindai, terlalu besar
[HIGH] android\.gradle\8.12\fileHashes.bin          tidak dipindai, terlalu besar
```

`exclude_dirs` memuat `node_modules` dan `dist` tetapi tidak `.dart_tool`,
`.gradle`, `.pub-cache`, atau `Pods`. Artefak build dilaporkan sebagai
"tidak dipindai", padahal memang tidak perlu dipindai.

## Cacat 3 terkonfirmasi di proyek nyata

```
$ snowline test-clone
[FAIL] Direktori saat ini bukan repositori Git.
```

Pesannya benar, tetapi `[FAIL]` menyiratkan ada yang gagal. Proyek tanpa git
bukan kegagalan.

## Cacat 1 terkonfirmasi

```
$ snowline close-entry uji
Error: .here_we_are\connector.md not found.
```

Persis seperti di sandbox. Jalur dipaku.

## Catatan

`init` dan `init_chamber` sendiri bekerja bersih di proyek non-git — tidak ada
asumsi git di sana. Itu bagian yang benar.

QA memasang `.agents/` di `pengingat_oli` untuk uji ini. Kalau PM mau
membersihkan: `snowline uninstall --apply` dan hapus `.agents/chamber/`.
