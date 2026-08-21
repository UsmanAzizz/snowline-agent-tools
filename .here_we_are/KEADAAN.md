# KEADAAN

**Berkas ini ditimpa, tidak ditambah.** Riwayat ada di `connector.md`.
Siapa pun yang mengubah sesuatu, memperbarui berkas ini di giliran yang sama.

Diperbarui: 21 Agustus 2026 · commit `2c24e07` · 0 belum commit, 0 belum push

---

## Empat bagian

```
companion       tunggakan terbuka       0          tutup
chamber         kode di pohon git       0 berkas   protokol, bukan program
tools           berujii                 2 / 22     tree_gen, smart_replace
undang-undang   mengikat lewat kode     4 / 14     sisanya tulisan
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
1  impact_analyzer   "Safe to modify/delete" untuk berkas Python yang dipakai
                     pola menuntut kutip (sintaks JS); Python tanpa kutip
                     -> satu-satunya yang bukan kosmetik
2  npx               24 detik per --apply; biner lokal 5 detik
3  connector.md      112 KB, lewat ambang rotasi 100 KB
4  uji               20 perkakas belum punya satu uji pun
5  context_mapper    menghasilkan pohon direktori, bukan peta arsitektur
6  :529 relpath      nama berkas tercetak "." pada target berkas-tunggal
7  verify_rule12     CRLF vs LF terbaca sebagai pelanggaran isi
8  CI                belum ada
```

Di luar jangkauan repo: dua kunci Groq dan GCP **belum dicabut**.

## Chamber

Diputuskan 21-08: **protokol birokrasi, bukan program.** PM manusia, TL agen,
QA identitas kedua, pekerja sekali pakai.

Saluran resmi: `.here_we_are/connector.md`. Lima connector di
`agents_chamber/pos/*/` pensiun. `task_board.md` beku di Task 87, dibiarkan
sebagai arsip.

Aturan yang sedang dirumuskan: **apa yang tidak ada di connector, identitas
kedua tidak tahu** — ditegakkan dengan memberi subagent hanya entri itu, tanpa
riwayat induk.

## Cara memeriksa berkas ini

Jangan percaya angka di atas. Jalankan:

```bash
python tests/run_tests.py
python .agents/skills/project_guardian/guardian.py --summary
git log --oneline -5
```

Kalau tidak cocok, berkas ini basi — perbarui, jangan diamkan.
