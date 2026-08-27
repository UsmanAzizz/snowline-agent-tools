# STATE

**Berkas ini ditimpa, tidak ditambah.** Riwayat ada di `connector.md`.
Siapa pun yang mengubah sesuatu, memperbarui berkas ini di giliran yang sama.

Diperbarui: 24 Agustus 2026 · commit `c08767f` · 2 belum commit, 2 belum push

> Dua yang belum commit adalah `STATE.md` dan `connector.md` sendiri. Entri PM
> yang sedang dikerjakan melarang `git commit`/`git push`, jadi giliran ini
> berhenti di disk. Butir 10 `CHAMBER_RULES.md` belum terpenuhi untuk giliran
> ini, dan itu disengaja PM, bukan terlewat.

---

## Empat bagian

```
companion       tunggakan terbuka       0          tutup
chamber         kode di pohon git       5 berkas   528 baris + init_chamber di
                                                   cli.py:738 — bukan lagi
                                                   protokol murni
tools           beruji                  13 / 17    4 belum, didaftar di Terbuka 2
                                                   (beruji = ada uji yang menjalankan alatnya dan menegaskan keluarannya)
                                                   (alat = folder di skills/ yang punya SKILL.md)
undang-undang   berlabel                8 / 8      MENGIKAT / SEPARUH / ANJURAN
                mengikat lewat kode     4 gerbang  lihat RULE 0 di AGENTS.md
```

## Empat yang mengikat

| | menolak apa | di mana | uji |
|---|---|---|---|
| `scope_lock.json` | tulis di luar daftar berkas | `scope_check.py:143` (terpusat) | ada |
| arity check | perintah yang argumennya kurang | `src/snowline/templates/hooks/quality_gate.py` (templat) | ada, **dua arah** |
| `--apply` | tulis apa pun tanpa flag | 4 alat tulis, **bukan semua** | ada |
| risiko Medium/High | apply tanpa `--apply-validated` | `replace_text.py:512` | ada, **dua arah** |

Diperiksa 24-08 dengan menjalankan, bukan membaca — keluarannya di connector.
Tiga catatan yang tidak muat di tabel:

```
baris 1  ada dua titik penegakan, bukan satu. scope_check.py dipanggil manual;
         yang menahan tulisan smart_replace adalah check_scope() internalnya.
         Keduanya sekarang dirancang sejalan dan dibuktikan pengujian.
baris 2  gerbangnya menolak DAN menerima (dibuktikan dua arah). Ujinya kini
         memvalidasi penolakan dan eksekusi lolos, mencakup salinan aktif
         hook yang terpasang, bukan hanya templat.
baris 3  "tiap alat tulis" salah dan sudah dikoreksi. Yang bergerbang --apply
         ada 4: smart_replace, auto_scaffolder, context_mapper, import_fixer.
         native_checker_gen/generator.py menulis ke disk dan kata "apply"
         muncul 0 kali di dalamnya — tidak ada flag yang bisa menahannya.
```


## Terbukti dengan perintah, bukan pembacaan

```
uji         50/50 lulus, 22,8 detik, diuji dengan mutasi — kode dirusak,
            ujinya gagal, kode dikembalikan, ujinya hijau
CI          head_sha c0158ca, conclusion success (24-08). Itu origin/main,
            tertinggal 2 commit dari HEAD lokal c08767f — keduanya milik
            sendiri dan belum dipush, jadi CI belum melihatnya.
guardian    repo ini CRITICAL=0 HIGH=0 MEDIUM=0 LOW=0
```

Tidak diperiksa ulang di sesi ini, dibiarkan sebagai klaim historis: guardian
9 -> 2 dan `--apply` di cbt_master, transkrip Antigravity 5330ddf5.

## Terbuka

```
1  rotasi otomatis   rotasi manual menjatuhkan 227 baris (entri QA dan Uji B).
                     Rotasi harus dibuatkan perintah CLI snowline rotate
                     yang memvalidasi baris masuk = baris keluar.
2  uji               4 perkakas belum beruji: companion, db_extractor,
                     deep_analyzer, smart_tree.
                     Alasan lama "kalau rusak langsung kelihatan" sudah
                     terbantah — impact_analyzer, smart_search, dan
                     selective_reader baca-saja dan gagal tanpa terlihat.
                     Pilih menurut bahayanya, bukan baca-saja atau bukan.
3  rotasi connector  connector.md saat ini berukuran 16.347 byte, sudah rotasi (terselesaikan, namun close-entry tidak mengecek nomor tabel ganda).
4  gerbang CRITICAL  install_hook belum punya pemanggil. Masih 0 pemanggil.
5  header STATE.md   diperbarui tangan dan akan basi lagi (jangan bangun
                     otomatisasinya sekarang). STATE.md disunting per bagian.
                     Jangan menulis ulang seluruh berkas dari draf — draf yang
                     disiapkan lebih awal akan menimpa perubahan yang terjadi
                     di antaranya.
6  close-entry       (Utang baru) close-entry saat menyisipkan topik ke tabel
                     TUTUP tidak mengecek penomoran Terbuka, sehingga
                     sempat terjadi nomor ganda pada daftar ini.
7  role.json absen   role.json tidak dipasang oleh init_chamber, sehingga kunci
                     peran tidak ada di proyek baru.
8  .gitignore        .gitignore tidak diputuskan, .agents/ jadi untracked di
                     proyek baru.
9  STATE.md tanda-   STATE.md dikirim berisi tanda hubung, sehingga sesi baru
                     tidak dapat apa-apa.
10 scope penegak     penyatuan lima salinan penegak scope (belum diketahui apakah
                     perilakunya sama persis untuk masukan yang sama, atau ada
                     penyimpangan diam-diam).
11 agents.md         agents.md sengaja tidak dilindungi scope, sedangkan folder
                     knowledge/ diblokir. Putuskan sekaligus bersama penyelesaian
                     penyatuan scope (a/b/c).
```

TUTUP lewat chamber, arsip per topik:
```
blind_test           pengujian buta 4 mekanisme             history/blind_test/
caching              batal saat kode alatnya berubah        history/caching/
calibration          kalibrasi versi masuk chamber          history/calibration/
chamber-history      riwayat chamber, dua entri             history/chamber-history/
chamber-portability  chamber ikut ke proyek lain            history/chamber-portability/
ci                   setup alur CI                          history/ci/
clean_sweeper        melapor cakupan hapus sisa             history/clean_sweeper/
cli                  perilaku antarmuka baris perintah      history/cli/
context              snowline konteks dan irisan tugas      history/context/
dependency-map       peta arsitektur, daftar yatim          history/dependency-map/
dependency-map-eval  vonis atas context_mapper              history/dependency-map-eval/
encoding             utf-8 dan baca fungsi tunggal          history/encoding/
entry-checker        pemeriksa syarat entri connector       history/entry-checker/
exclude-lists        daftar kecualian pemindai              history/exclude-lists/
guardian             temuan positif palsu dan perbaikan     history/guardian/
guardian-eval        vonis atas perbaikan guardian          history/guardian-eval/
npm_audit            audit project tetangga                 history/npm_audit/
quality_gate         rule12, beda akhir baris               history/quality_gate/
rejection-tests      gerbang tolakan                        history/rejection-tests/
release              penandaan rilis                        history/release/
role-lock            kunci-tulis berdasarkan peran          history/role-lock/
selective_reader     pemindai daftar fungsi                 history/selective_reader/
solo_mode            pengujian tiga hal mode tunggal        history/solo_mode/
workflow             arsip connector, rotasi sprint         history/workflow/
single-agent         (entri baru)                           history/single-agent/
chamber-rules        (entri baru)                           history/chamber-rules/
chamber-portability-2 (entri baru)                           history/chamber-portability-2/
dependency-map-eval-2 (entri baru)                           history/dependency-map-eval-2/
quality_gate-2       (entri baru)                           history/quality_gate-2/
role-lock-2          (entri baru)                           history/role-lock-2/
selective_reader-2   (entri baru)                           history/selective_reader-2/
```

24 topik, 25 entri, semuanya tutup.

Dua butir yang dulu berdiri di luar chamber sekarang tutup, keduanya dijaga
`tests/test_smart_replace_apply.py:210`: `--apply` pada berkas tunggal
berhasil, dan nama berkasnya tidak lagi tercetak sebagai titik (:529 -> :535).

Di luar jangkauan repo: dua kunci Groq dan GCP **belum dicabut** — tidak bisa
diperiksa dari sini.

## Chamber

Diputuskan 21-08: protokol birokrasi. Sebagian kini **sudah jadi program** —
`core_close_entry.py` (159 baris), `core_entry_checker.py` (84), `init_chamber`
di `cli.py:738`, dijaga tiga uji (285 baris). PM manusia, TL agen, QA identitas
kedua, pekerja sekali pakai.

Saluran resmi: `.here_we_are/connector.md` — dirotasi 21-08, riwayat lama di
`agents_chamber/shared/archive/connector_2026-08-21.md`. Tujuh connector di
`agents_chamber/pos/*/` pensiun. `task_board.md` beku di Task 87, arsip.

Aturan di `agents_chamber/CHAMBER_RULES.md`, isinya identik dengan
`src/snowline/chamber_templates/CHAMBER_RULES.md` (md5 sama). Intinya: **apa
yang tidak ada di connector, identitas kedua tidak tahu.** TL tidak boleh
memanggil QA-nya sendiri; PM yang memilih pemeriksa.

Empat `ONBOARDING.md` di `agents_chamber/pos/` diarahkan ke saluran resmi.
Sesi baru: tempel dokumen perannya sekali, sesudah itu sinyal cukup `''`.

**Masuk instalasi 21-08** sebagai perintah opsional: `snowline init_chamber
--apply` -> `.agents/chamber/` (**8 berkas** dari sumber repo). Terpisah dari
`init`; diuji di proyek bersih bahwa `init` saja tidak ikut memasangnya.

Butir 0 ditambahkan 21-08: penyaring kapan chamber dipakai — *kalau perubahan
ini salah, apakah langsung kelihatan?* Kelihatan seketika, kerjakan biasa; baru
ketahuan nanti, lewat chamber.

**Sudah diuji, jawabannya negatif:** subagent Antigravity **tidak** berkonteks
bersih (Uji 1, entri 17). Rancangan mode tunggal digeser: pemeriksa tidak perlu
*tidak tahu*, ia perlu *tidak bisa memakai apa yang ia tahu*. Kunci-tulis
berdasarkan peran sudah terpasang — `replace_text.py:26` membaca
`.here_we_are/role.json` lalu `.agents/chamber/role.json`, dijaga
`tests/test_role_lock.py`.

Aturannya menahan sesuatu yang nyata: entri 1 menangkap uji yatim yang tidak
ikut terjalan, entri 2 menuntut bukti mutasi, Sprint 32 menangkap penegasan
"ada di suatu tempat" yang lolos saat perilakunya dibalik.

## Cara memeriksa berkas ini

Jangan percaya angka di atas. Jalankan:

```bash
python tests/run_tests.py                                   # 50/50, ~23 detik
python .agents/skills/project_guardian/guardian.py --summary # CRITICAL=0
git status --short                                          # 2 (STATE.md, connector.md)
git log --oneline -1                                        # c08767f
git log origin/main..main --oneline | wc -l                 # 2
```

Kalau tidak cocok, berkas ini basi — perbarui, jangan diamkan.

## Utang Teknis (Technical Debt)
- Ada 5 instans except Exception: pass lain di src/snowline/cli.py yang menelan galat dan belum diperbaiki di sprint ini.
6. Berkas uji liar di `tests/` lolos penjaga yatim karena namanya bukan `test_*.py`.
