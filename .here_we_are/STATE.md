# STATE

**Berkas ini ditimpa, tidak ditambah.** Riwayat ada di `connector.md`.
Siapa pun yang mengubah sesuatu, memperbarui berkas ini di giliran yang sama.

Diperbarui: 30 Agustus 2026 — commit `0d96ace` — 0 belum commit, 0 belum push

---

## Empat bagian

```
companion       tunggakan terbuka       0          tutup
chamber         kode di pohon git       5 berkas   528 baris + init_chamber di
                                                   cli.py:738 — bukan lagi
                                                   protokol murni
tools           beruji                  16 / 16    semua 16 perkakas aktif beruji
                                                   (beruji = ada uji yang menjalankan alatnya dan menegaskan keluarannya)
                                                   (alat = folder di skills/ yang punya SKILL.md)
undang-undang   berlabel                8 / 8      MENGIKAT / SEPARUH / ANJURAN
                mengikat lewat kode     4 gerbang  lihat RULE 0 di AGENTS.md
```

## Garis rilis

Daftar Terbuka tidak akan pernah kosong. Rilis terjadi waktu tidak ada lagi
yang di atas garis — bukan waktu daftarnya habis.

**Menahan rilis:**

```
1  suite merah, atau CI merah di commit terakhir
2  Aturan #12 merah
3  perintah yang tidak jalan sama sekali        (contoh: rotate tanpa dispatch)
4  perintah yang melapor berhasil padahal tidak (contoh: nol kecocokan -> SUCCESS)
5  penjaga yang menolak pekerjaan wajar         (contoh: gerbang intent menolak
                                                 4 dari 4 perintah tulis)
6  kehilangan atau menimpa pekerjaan pengguna
```

**Tidak menahan rilis:**

```
pesan yang salah label atau kosong sesudah titik dua
keluaran yang berisik tetapi benar
berkas nyasar di pohon kerja
alat yang belum pernah dipakai siapa pun di lapangan
temuan uji lapangan yang tidak masuk keenam di atas
```

Uji lapangan akan selalu menemukan sesuatu. Itu tanda ujinya bekerja, bukan
tanda proyeknya belum siap. Yang perlu diperiksa cuma: apakah temuannya masuk
daftar pertama.

## Empat yang mengikat

| | menolak apa | di mana | uji |
|---|---|---|---|
| `scope_lock.json` | tulis di luar daftar berkas | `scope_check.py:143` (terpusat) | ada |
| arity check | perintah yang argumennya kurang | `src/snowline/templates/hooks/quality_gate.py` (templat) | ada, **dua arah** |
| `--apply` | tulis apa pun tanpa flag | 4 alat tulis, **bukan semua** | ada |
| risiko Medium/High | apply tanpa `--apply-validated` | `replace_text.py:512` | ada, **dua arah** |

Diperiksa 30-08 dengan menjalankan, bukan membaca — keluarannya di connector.
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
uji         134/134 lulus, ~24 detik, diuji dengan mutasi — kode dirusak,
            ujinya gagal, kode dikembalikan, ujinya hijau
CI          head_sha e163031, conclusion success (Sprint 53).
guardian    repo ini CRITICAL=0 HIGH=0 MEDIUM=0 LOW=0
```

Tidak diperiksa ulang di sesi ini, dibiarkan sebagai klaim historis: guardian
9 -> 2 dan `--apply` di cbt_master, transkrip Antigravity 5330ddf5.

## Terbuka

```
1  agents.md vs knowledge/  agents.md sengaja tidak dilindungi scope, sedangkan
                            folder knowledge/ diblokir. Menunggu keputusan arsitektur PM:
                            (A) Lindungi agents.md dan knowledge/ dengan scope_lock
                            (B) Bebaskan keduanya dari pemblokiran otomatis
                            (C) Pertahankan asimetri saat ini (agents.md bebas, knowledge/ diblokir).
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
python tests/run_tests.py                                   # semua uji lulus (Results: 134/134 passed, 0 failed)
python .agents/skills/project_guardian/guardian.py --summary # CRITICAL=0
git status --short                                          # bersih (0 berkas termodifikasi/tak terlacak di pohon kerja)
```

Kalau tidak cocok, berkas ini basi — perbarui, jangan diamkan.

## Utang Teknis (Technical Debt)
1. 5 instans `except ...: pass` di `src/snowline/cli.py` (baris 74, 164, 347, 749, 1086) yang menelan galat tanpa penanganan spesifik.
2. Berkas uji liar di `tests/` yang namanya tidak diawali `test_*.py` dapat lolos dari pengawasan `test_orphan_guard.py`.
