# KEADAAN

**Berkas ini ditimpa, tidak ditambah.** Riwayat ada di `connector.md`.
Siapa pun yang mengubah sesuatu, memperbarui berkas ini di giliran yang sama.

Diperbarui: 22 Agustus 2026 · commit `6cae2d2` · 0 belum commit, 0 belum push

---

## Empat bagian

```
companion       tunggakan terbuka       0          tutup
chamber         kode di pohon git       0 berkas   protokol, bukan program
tools           berujii                 8 / 22     tree_gen, smart_replace,
                                                   scope_guardian, impact_analyzer,
                                                   context_mapper, selective_reader,
                                                   smart_search, surgical_splicer
undang-undang   berlabel                8 / 8      MENGIKAT / SEPARUH / ANJURAN
                mengikat lewat kode     4 gerbang  lihat RULE 0 di agents.md
```

## Empat yang mengikat

| | menolak apa | di mana |
|---|---|---|
| `scope_lock.json` | tulis di luar daftar berkas | `scope_guardian/scripts/scope_check.py` |
| arity check | perintah yang argumennya kurang | `hooks/quality_gate.py` |
| hook | dipanggil harness, bukan diminta | `.agents/hooks.json` |
| gerbang CRITICAL | commit saat ada rahasia terbaca | `install_hooks.py:27` |

## Terbukti dengan perintah, bukan pembacaan

```
uji                24/24 lulus, dan diuji dengan mutasi — kode dirusak,
                   ujinya gagal, kode dikembalikan, ujinya hijau
guardian           CRITICAL 9 -> 2 di proyek nyata, positif palsu 0%
smart_replace      --apply terverifikasi di cbt_master, bukan cuma sandbox
hook               transkrip Antigravity 5330ddf5 menunjukkan penolakan nyata
```

## Terbuka

```
1  uji               14 perkakas baca-saja belum berujii
                     CATATAN: alasan lama "kalau rusak langsung kelihatan"
                     sudah terbantah — impact_analyzer, smart_search, dan
                     selective_reader semuanya baca-saja dan gagal tanpa
                     terlihat. Yang tersisa perlu dipilih menurut bahayanya,
                     bukan menurut baca-saja atau bukan.
2  npm_audit         baris "dilewati" dicetak [HIGH] padahal dihitung nol —
                     pencetak modul memaku labelnya, pola sama dengan :344
3  mode tunggal      rancangan ada di DESIGN_CONTEXT_AND_SOLO.md,
                     tiga hal belum diuji, belum berlaku

TUTUP lewat chamber, lima belas entri:
   1  impact_analyzer   negatif palsu Python, .backup_replace, --depth
   2  npx               suite 2 menit -> 24 detik, probe sekali per proses
   3  context_mapper    DEPENDENCY_MAP; yatim 16 -> 1; pindai 64,8s -> 0,07s
   4  CI                terbukti merah lalu hijau, 14 detik per putaran
   5  guardian          positif palsu HIGH: komentar & scratch/ dikecualikan
   6  uji penolakan     enam gerbang, semuanya terverifikasi mutasi
   7  verify_rule12     beda akhir baris tidak lagi dibaca sebagai beda isi
   8  arsip connector   satu lokasi resmi
   9  encoding          open() tanpa utf-8 menjatuhkan splicer di 39% berkas
  10  selective_reader  impor/useState/useEffect/export masuk TOC
  11  cache             batal sendiri saat kode alatnya berubah
  12  clean_sweeper     melapor cakupan; berhenti menyuruh hapus tanpa syarat
  13  npm audit         berhenti mengambil kerentanan project tetangga
  14  sampah uji        tmp* tidak lagi jatuh di akar repo
  15  tests/            kembali dipindai; string literal dikupas selektif

Di luar chamber:
   smart_replace     --apply pada berkas tunggal tidak pernah berhasil
   :529 relpath      nama berkas tercetak sebagai titik
```

Di luar jangkauan repo: dua kunci Groq dan GCP **belum dicabut**.

## Chamber

Diputuskan 21-08: **protokol birokrasi, bukan program.** PM manusia, TL agen,
QA identitas kedua, pekerja sekali pakai.

Saluran resmi: `.here_we_are/connector.md` — dirotasi 21-08, riwayat lama di
`agents_chamber/shared/archive/connector_2026-08-21.md`. Lima connector di
`agents_chamber/pos/*/` pensiun. `task_board.md` beku di Task 87, dibiarkan
sebagai arsip.

Aturannya ditulis di `agents_chamber/CHAMBER_RULES.md` (21-08). Intinya:
**apa yang tidak ada di connector, identitas kedua tidak tahu** — ditegakkan
dengan memberi subagent hanya entri itu, tanpa riwayat induk. TL tidak boleh
memanggil QA-nya sendiri; PM yang memilih pemeriksa.

Empat `ONBOARDING.md` sudah diarahkan ke saluran resmi. Sesi baru: tempel
dokumen perannya sekali, sesudah itu sinyal cukup `''`.

**Masuk instalasi 21-08** sebagai perintah opsional:
`snowline init_chamber --apply` -> `.agents/chamber/` (7 berkas). Terpisah dari
`init`; diuji di proyek bersih bahwa `init` saja tidak ikut memasangnya.
Templatnya di `src/snowline/chamber_templates/`.

Butir 0 ditambahkan 21-08: penyaring kapan chamber dipakai — *kalau perubahan
ini salah, apakah langsung kelihatan?* Kelihatan seketika, kerjakan biasa; baru
ketahuan nanti, lewat chamber.

Belum diuji: apakah subagent Antigravity benar-benar berkonteks bersih.
**Dipakai: lima belas entri, lima belas-limabelasnya tutup.** Aturannya menahan sesuatu yang
nyata di keduanya — entri 1 menangkap uji yatim yang tidak ikut terjalan, entri
2 menuntut bukti mutasi yang ternyata bekerja.

## Cara memeriksa berkas ini

Jangan percaya angka di atas. Jalankan:

```bash
python tests/run_tests.py                                   # 40/40, ~24 detik
python .agents/skills/project_guardian/guardian.py --summary # CRITICAL=0
git log --oneline -5
```

Kalau tidak cocok, berkas ini basi — perbarui, jangan diamkan.
