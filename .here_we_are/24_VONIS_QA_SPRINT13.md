# Vonis QA — Sprint 13 (Native Hooks)

## VONIS: REJECT — hook-nya tidak terpasang, dan satu di antaranya berbahaya

## 1. Tidak terpasang

Kedua skrip nyata dan logikanya benar: `loop_detector.py` menghitung SHA-256
payload, `MAX_REPEATS = 3`, mengeluarkan `{"decision":"deny"}` saat tiga
eksekusi identik beruntun. `rollback_enforcer.py` menjalankan `git clean -fd`.

Tetapi konfigurasinya ditaruh di `.agents/hooks.json`. **Claude Code tidak
pernah membaca berkas itu.** Hook dibaca dari `settings.json` di bawah kunci
`hooks`:

```
$ python -c "...json.load(open('.claude/settings.local.json'))"
kunci  : ['permissions']
hooks  : TIDAK ADA
```

Bentuknya juga berbeda dari yang dipakai harness: `.agents/hooks.json` menaruh
**nama hook** di tingkat teratas (`c4-loop-detector`) lalu nama event di
dalamnya. Formatnya kebalikan — event di teratas. Dan entri `Stop` melewatkan
susunan `matcher`/`hooks` yang dipakai entri `PreToolUse`-nya sendiri.

Jadi ini dua skrip di folder yang menunggu dipanggil — pola yang sama persis
dengan companion dan `scope_guardian`, dan justru pola itu yang Sprint 13
dimaksudkan untuk mengakhiri.

**Belum diverifikasi:** apakah `{"decision":"deny"}` lewat stdout memang
memblokir, atau yang mengikat hanya *exit code* 2. Dokumentasi menyebut exit 2
sebagai satu-satunya yang memblokir lewat kode saja. Perlu dipastikan sebelum
dipasang.

## 2. `rollback_enforcer` berbahaya bila dipasang hari ini

Ia menjalankan `git reset --hard` dan `git clean -fd` secara diam-diam di
*event* `Stop`. Repositori ini punya **116 berkas belum ter-commit**, termasuk
sisa Sprint 9.

Kalau hook itu terpasang lalu menyala sekali, seluruhnya hilang — tanpa
konfirmasi, tanpa jejak.

## Syarat

1. Pindahkan konfigurasi ke `settings.json` dengan bentuk yang benar, lalu
   buktikan ia menyala — jalankan tool yang sama tiga kali dan tunjukkan
   penolakannya.
2. `rollback_enforcer` jangan dipasang sebelum 116 berkas itu di-commit.
   Pertimbangkan `git stash` alih-alih `reset --hard`.

## Yang benar dari sprint ini

Arahnya tepat, dan pengakuan bahwa QA Handoff tetap imbauan itu jujur —
persis seperti yang diminta vonis 23.
