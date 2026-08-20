# Vonis QA — Sprint 12 (Pivot: musnahkan orchestrator, jiwanya jadi SOP)

Tinjauan konseptual. Tidak ada kode untuk diperiksa.

## VONIS: PREMIS BENAR, KESIMPULAN SALAH

**Yang benar:** `orchestrator.py` memang tidak bisa mengendalikan *native agent*.
Ia hanya mengikat CLI yang ia sendiri jalankan lewat `subprocess`. Agen yang
tidak Anda spawn tidak bisa Anda bungkus. Menghapusnya masuk akal.

**Yang salah:** memindahkan pengamanan ke SOP bukan memindahkan penegakan.
Ia mengubah jaminan jadi imbauan.

## Bukti yang sudah ada di folder ini

```
companion         aturan "WAJIB PANGGIL DULU" di agents.md
                  -> 18 panggilan, berhenti 7 Agustus
scope_guardian    akan memblokir seluruh epik panduanKoreksi.js bila dipanggil
                  -> tidak pernah dipanggil, kunci basi sejak 6 Agustus
QA sesi ini       aturan terpasang di .agents/ cbt_master
                  -> diabaikan 6 hari berturut, lalu melenceng 3x dalam 1 malam
literatur         pelanggaran batasan 38,33% - kategori kegagalan terbesar,
                  dan porsinya MEMBESAR seiring model membaik
```

Ketiga "jiwa" yang diusulkan adalah aturan swa-awas: *"Jika Anda mendeteksi
diri Anda gagal 3 kali, Anda WAJIB berhenti."* Kamoi dkk. (TACL 2024): tidak ada
karya yang menunjukkan koreksi-diri berhasil dari umpan balik yang dibangkitkan
agen sendiri. BAGEN: agen tetap optimistis setelah membakar 60% anggaran.

## Yang mengikat pada native agent

Bukan SOP, dan bukan skrip pembungkus. **Hook.** `PreToolUse` keluar kode 2
memblokir panggilan — agen tidak punya pilihan melewatinya. Itu Arah 1, dan
`install_hooks.py` dari Sprint 9 sudah membuktikannya bekerja.

Pivot ini menukar mekanisme yang mengikat-tapi-tidak-muat dengan yang
muat-tapi-tidak-mengikat. Pilihan ketiga muat dan mengikat.

## Syarat

Hapus `orchestrator.py` silakan. Tetapi ketiga jiwa itu ditulis sebagai hook,
bukan sebagai kalimat SOP. Loop detector dan rollback keduanya bisa jadi
`PreToolUse`/`Stop` hook; QA handoff tidak, dan itu memang harus diakui sebagai
imbauan.

Kalau tetap jadi SOP, catat di dokumennya bahwa ini imbauan, bukan jaminan.
