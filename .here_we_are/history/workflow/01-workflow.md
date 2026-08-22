# PM -> TL: Sprint 22 — empat entri, dan kunci usulan dipakai pertama kali

**`.agents/task_state.json` sudah dibuat.** Selama berkas itu ada, `--apply`
lewat alat snowline ditolak. Tulis usulan untuk entri 5, 6, dan 7 lebih dulu
dalam satu giliran; PM meninjau sekali, lalu membuka kuncinya sekali.

Ini pemakaian pertama butir 4b. Kalau terasa mengganggu, katakan — itu temuan
tentang protokolnya.
**Urutan:** usulan untuk 5, 6, 7 dalam satu giliran. Setelah PM membuka kunci,
kerjakan 5 → 7 → 6 → 8. Entri 6 paling akhir karena paling panjang, dan kalau
suite melewati 60 detik, lebih baik ketahuan saat sisanya sudah tutup.
# PM -> TL: Sprint 23 — empat entri, dan satu koreksi atas alasan PM sendiri

## Koreksi lebih dulu

PM menunda uji untuk 14 perkakas baca-saja dengan alasan *"kalau rusak,
langsung kelihatan"*. **Alasan itu terbantah tiga kali malam ini oleh perkakas
baca-saja juga:**

```
impact_analyzer    berkata "Safe to modify/delete" untuk berkas yang dipakai
smart_search       melewati 5 berkas diam-diam, melapor seolah lengkap
selective_reader   menyajikan hasil lama dari cache tanpa ada yang tahu
```

Ketiganya baca-saja, dan ketiganya gagal **tanpa terlihat**. Baca-saja bukan
berarti aman — berarti kesalahannya berupa jawaban yang salah, bukan kerusakan
yang kentara. Itu justru lebih sulit ditangkap.

Sprint ini memperbaiki dua yang paling berbahaya dari sisa itu.
# PM -> TL: Sprint 24 — dua entri

Rencana lengkapnya di `.here_we_are/DESIGN_CONTEXT_AND_SOLO.md`. Baca dulu.
