# KEADAAN

**Berkas ini ditimpa, tidak ditambah.** Riwayat ada di `connector.md`.
Siapa pun yang mengubah sesuatu, memperbarui berkas ini di giliran yang sama.

Diperbarui: 21 Agustus 2026 · commit `2b49585` · 0 belum commit, 0 belum push

---

## Empat bagian

```
companion       tunggakan terbuka       0          tutup
chamber         kode di pohon git       0 berkas   protokol, bukan program
tools           berujii                 4 / 22     tree_gen, smart_replace,
                                                   scope_guardian, impact_analyzer
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
1  uji               18 perkakas belum punya satu uji pun
2  context_mapper    menghasilkan pohon direktori, bukan peta arsitektur
3  :529 relpath      nama berkas tercetak "." pada target berkas-tunggal
4  verify_rule12     CRLF vs LF terbaca sebagai pelanggaran isi
5  CI                belum ada

TUTUP 21-08 lewat chamber:
   impact_analyzer   entri 1 - negatif palsu Python, .backup_replace, --depth
   npx               entri 2 - suite 2 menit -> 12,2 detik
```

Di luar jangkauan repo: dua kunci Groq dan GCP **belum dicabut**.

## Chamber

Diputuskan 21-08: **protokol birokrasi, bukan program.** PM manusia, TL agen,
QA identitas kedua, pekerja sekali pakai.

Saluran resmi: `.here_we_are/connector.md` — dirotasi 21-08, riwayat lama di
`agents_chamber/shared/archive/connector_2026-08-21.md`. Lima connector di
`agents_chamber/pos/*/` pensiun. `task_board.md` beku di Task 87, dibiarkan
sebagai arsip.

Aturannya ditulis di `agents_chamber/ATURAN_CHAMBER.md` (21-08). Intinya:
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
**Dipakai 21-08: dua entri, dua-duanya tutup.** Aturannya menahan sesuatu yang
nyata di keduanya — entri 1 menangkap uji yatim yang tidak ikut terjalan, entri
2 menuntut bukti mutasi yang ternyata bekerja.

## Cara memeriksa berkas ini

Jangan percaya angka di atas. Jalankan:

```bash
python tests/run_tests.py
python .agents/skills/project_guardian/guardian.py --summary
git log --oneline -5
```

Kalau tidak cocok, berkas ini basi — perbarui, jangan diamkan.
