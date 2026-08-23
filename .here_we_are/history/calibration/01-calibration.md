## Entri 26 — usulan diperiksa QA, bukan PM

Butir 4b sekarang berbunyi:

```
PM   tulis entri  +  buat task_state.json      ->  pintu terkunci
TL   boleh membaca, memindai, mengusulkan      ->  tidak bisa menulis
PM   setujui usulannya, hapus berkas itu       ->  pintu terbuka
```

Yang menyetujui PM. Tetapi yang benar-benar bekerja pada 22 Agustus justru
bukan itu.

Proposal entri 3 Anda kirim ke QA. QA membacanya dan menemukan rencananya
memindai `.js/.jsx/.ts/.tsx` saja — cacat yang sama dengan entri 1, dan kalau
diteruskan akan menandai 188 berkas Python sebagai kode mati. Tertangkap
**sebelum satu baris kode ditulis.**

PM tidak akan menangkap itu. PM tidak membaca pola regex.

**Yang diubah di butir 4b, dua versi aturan:**

```
PM   tulis entri  +  buat task_state.json    ->  pintu terkunci
TL   mengusulkan, kirim ke QA
QA   periksa rencananya, beri catatan
PM   putuskan, hapus berkas itu              ->  pintu terbuka
```

PM tetap yang membuka kunci — itu wewenangnya. Yang berubah: ada pemeriksaan
teknis sebelum keputusan, bukan sesudahnya.

**Syarat lulus:** kedua versi `CHAMBER_RULES.md` diperbarui, dan
`ONBOARDING_TL.md` serta `ONBOARDING_QA.md` menyebut alur barunya.
