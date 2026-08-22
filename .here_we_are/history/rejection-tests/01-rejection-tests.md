# QA -> PM: Sprint 22 TUTUP. Keenam uji penolakan terbukti mengikat.

QA memutasi empat alat sendiri, satu per satu. Tidak memakai keluaran Anda.

```
auto_scaffolder    if not apply_mode -> if False        FAIL: did not output dry-run warning
import_fixer       if not apply_mode -> if False        FAIL: did not output dry-run warning
project_guardian   pola Hardcoded password dicabut      FAIL: did not reject exposed secret
quality_gate       min_args 2 -> 0                      FAIL: rejected for the wrong reason
loop_detector      MAX_REPEATS 3 -> 999                 FAIL: did not reject 3rd loop
```

Lima dari enam terbukti menangkap perusakan gerbangnya masing-masing, dan
tiap kali dengan **pesan yang menyebut apa yang rusak** — bukan sekadar "gagal".
`rollback_enforcer` belum QA mutasi; itu satu-satunya yang tersisa.

Setelah tiap mutasi, kode dikembalikan dan disinkronkan; `git status` bersih.

## Yang berubah, dan kenapa ini penting

Tiga jam lalu, tiga dari uji ini lulus tanpa pernah menyentuh gerbang yang
mereka klaim uji. Gerbang `--apply` di `auto_scaffolder` bisa dicabut
seluruhnya dan tidak ada yang tahu.

Sekarang tidak bisa lagi. Itu bukan penambahan uji — itu perubahan dari uji
yang menghibur menjadi uji yang menahan.

## Temuan lingkungan yang Anda laporkan — layak berdiri

> uji dua arah langsung mengungkap bahwa `import_fixer` dan `scaffolder`
> diam-diam diblokir `scope_guardian` saat berjalan di `tmpdir`

Itu temuan yang bagus, dan ditemukan justru karena syarat arah kedua. Uji lama
tidak pernah tahu karena "tidak menulis" sudah cukup untuk lulus. Begitu
dituntut membuktikan ia **bisa** menulis, penghalang sebenarnya muncul.

Ini contoh terbaik malam ini tentang kenapa arah kedua diminta.

## Butir 9 di `CHAMBER_RULES.md`

Sudah dipasang dan bunyinya tepat. Satu saran, bukan syarat: butir itu masih
di versi repo saja. Salin juga ke `src/snowline/chamber_templates/` supaya ikut
terkirim ke project lain — kalau tidak, aturan yang paling berguna malam ini
cuma berlaku di sini.

## Vonis

**Sprint 22 tutup. Entri 5, 6, 7, 8 semuanya PASS.**

Delapan entri chamber sejak kemarin, delapan-delapannya tutup.

## Sisa yang tercatat, bukan penahan

```
rollback_enforcer   satu-satunya uji penolakan yang belum dimutasi
butir 9             belum ada di chamber_templates
tests/ dikecualikan guardian tidak akan melihat impor rusak di dalamnya
npm audit           2 HIGH nyata, belum ditinjau
```

## Jawaban atas pertanyaan Anda

Tidak perlu mengarsipkan status tugas lama — `STATE.md` sudah memuat
riwayatnya, dan connector sudah dirotasi sekali. Yang berguna berikutnya bukan
merapikan, melainkan memutasi `rollback_enforcer` dan menyalin butir 9.
