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

TUTUP lewat chamber, arsip per topik:
```
dependency-map       peta arsitektur, daftar yatim          history/dependency-map/
dependency-map-eval  vonis atas context_mapper              history/dependency-map-eval/
ci                   setup alur CI                          history/ci/
guardian             temuan positif palsu dan perbaikan     history/guardian/
guardian-eval        vonis atas perbaikan guardian          history/guardian-eval/
rejection-tests      gerbang tolakan                        history/rejection-tests/
encoding             utf-8 dan baca fungsi tunggal          history/encoding/
selective_reader     pemindai daftar fungsi                 history/selective_reader/
caching              batal saat kode alatnya berubah        history/caching/
clean_sweeper        melapor cakupan hapus sisa             history/clean_sweeper/
context              snowline konteks dan irisan tugas      history/context/
role-lock            kunci-tulis berdasarkan peran          history/role-lock/
solo_mode            pengujian tiga hal mode tunggal        history/solo_mode/
quality_gate         rule12, beda akhir baris               history/quality_gate/
npm_audit            audit project tetangga                 history/npm_audit/
blind_test           pengujian buta 4 mekanisme             history/blind_test/
workflow             arsip connector, rotasi sprint         history/workflow/
```

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
