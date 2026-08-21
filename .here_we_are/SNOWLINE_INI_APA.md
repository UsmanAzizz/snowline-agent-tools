# Snowline ini apa, dan sedang di mana

Satu halaman. Ditulis 21 Agustus 2026, untuk siapa pun — termasuk yang
menulisnya — yang lupa sedang berdiri di mana.

Berkas lain di folder ini menganggap pembacanya sudah tahu konteksnya. Berkas
ini tidak.

---

## Ini apa

Perangkat yang membuat agen AI **tidak bisa diam-diam merusak proyek nyata.**

Proyek nyatanya konkret: aplikasi CBT yang dipakai untuk ujian di sekolah.
Ribuan jawaban siswa, dinilai sebagian oleh model. Kalau agen salah mengubah
sesuatu di sana, yang rugi bukan pengembangnya.

Bukan agar agen lebih pintar. Agar yang salah tertahan **sebelum** jadi.

## Yang berubah dari niat awal

Snowline lahir dengan misi menghemat token — itu masih tertulis di `README.md`
repo utama.

Misi itu diukur dan mati. Penghematannya **3,1%**, jauh di bawah ambang 15%
yang ditetapkan sebelum pengukuran, karena teks yang disuntik perkakas cuma
8,7% dari prefix. Rinciannya di `01_TEMUAN.md`.

Yang tumbuh menggantikannya bukan penghematan, melainkan **penolakan yang bisa
diperiksa.** Itu isi snowline sekarang.

## Empat yang benar-benar mengikat

Cuma empat hal yang menolak lewat kode. Sisanya tata tertib yang bisa diabaikan
agen mana pun — dan Gemini mengakui itu sendiri saat ditanya (21-08, `connector.md`).

| yang mengikat | menolak apa | di mana |
|---|---|---|
| `scope_lock.json` | tulis di luar daftar berkas | `scope_guardian/scripts/scope_check.py` |
| arity check | perintah yang argumennya kurang | `hooks/quality_gate.py` |
| hook | dipanggil harness, bukan diminta baik-baik | `.agents/hooks.json` |
| gerbang CRITICAL | commit saat ada rahasia terbaca | `install_hooks.py:27` |

Kalau suatu hari ada yang mengusulkan fitur baru, pertanyaan pertamanya:
**apakah ia menolak, atau cuma menganjurkan?**

## Enam arah, dan status akhirnya

Enam arah lahir dari sprint penelitian 19–20 Agustus. Semuanya sudah tutup.

```
1  hook bisa mengikat                terbukti — transkrip Antigravity 5330ddf5
2  ditutup                           milik harness, bukan milik kita
3  ditutup                           pivot Sprint 12
4  guardian bisa disetel             terbukti — CRITICAL 9 -> 2, palsu 0%
5  selesai-sebatas-kerangka          aturan domain tetap ditulis manusia
6  selesai-sebatas-jeda-paksa        penilaian akhir tetap milik manusia
```

Dua terbukti lewat eksekusi. Dua ditutup karena bukan wilayah kita. Dua ditutup
sejujurnya — sampai sebatas itu, dan tidak lebih.

## Posisi hari ini

```
24 Juli -> 21 Agustus     29 hari, 338 commit, satu orang
22 perkakas               terpasang lewat pip, hooks terikat harness
uji                       24/24 lulus, diuji dengan mutasi bukan cuma dijalankan
terverifikasi             di proyek nyata (cbt_master), bukan cuma sandbox
```

## Yang tersisa

Satu yang bukan kosmetik: **`impact_analyzer` berkata "Safe to modify/delete"
untuk berkas Python yang jelas dipakai.** Polanya menuntut jalur dalam tanda
kutip — sintaks JavaScript — sementara Python menulis `from a.b.c import x`
tanpa kutip. Alat yang dipanggil justru sebelum mengubah sesuatu, dan salahnya
ke arah yang menenangkan.

Sisanya bisa menunggu berminggu-minggu tanpa ada yang rusak: ongkos `npx` 24
detik per `--apply`, `context_mapper` yang menghasilkan pohon direktori alih-alih
peta arsitektur, dan 21 perkakas yang belum punya satu uji pun.

## Jangan percaya halaman ini

Halaman ini ditulis seseorang yang bisa salah, dan akan basi. Kalau ragu,
jalankan:

```bash
python tests/run_tests.py                                  # 24/24?
python .agents/skills/project_guardian/guardian.py          # ada rahasia?
git -C . log --oneline -10                                  # apa yang terakhir terjadi
```

Aturan yang berlaku di seluruh folder ini, dan yang paling mahal dipelajari:
**laporan yang meyakinkan bukan laporan yang bisa diperiksa.** Dua kali dalam
dua hari, sesuatu dilaporkan selesai dengan bukti yang tidak menunjukkannya —
sekali oleh Tech Lead, sekali oleh QA yang meluluskan kode dengan membacanya
saja. Keduanya tercatat di `connector.md`, sengaja tidak dihapus.

Kalau kamu agen yang baru masuk: jangan menilai apa pun sebelum menjalankannya.
