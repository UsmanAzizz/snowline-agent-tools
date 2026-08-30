# Snowline Agent Tools — Roadmap

## Arah

> Taruh penjaganya di dalam alat, bukan di depan alat.

Penjaga yang berdiri di depan alat bisa dilewati. Penjaga yang ada di dalam
alat tidak bisa. Itu yang membedakan snowline dari kumpulan skrip biasa, dan
itu yang menentukan mana ide yang diterima ke dalam paket ini.

Sasarannya proyek kecil dan menengah. Python murni, tanpa dependensi.

---

## Keadaan sekarang — v1.2.0

Dirilis, tagnya menunjuk commit yang CI-nya hijau, dan paketnya sudah diuji
bisa dipasang dari tag itu.

```
v1.2.0 -> a06de46
128 uji lulus
Aturan #12 hijau
```

### 16 alat

```
smart_search        cari kode beserta konteks di sekitarnya
smart_replace       ganti teks dengan cadangan dan pratinjau
selective_reader    baca berkas besar tanpa memuat semuanya
smart_tree          peta direktori yang ringkas
context_mapper      peta ketergantungan antar berkas
deep_analyzer       profil proyek
impact_analyzer     lacak siapa memakai apa
crash_decoder       urai pesan galat
project_guardian    audit keamanan
clean_sweeper       cari sisa dan utang teknis
scope_guardian      catat dan batasi tulis di luar lingkup tugas
auto_scaffolder     bikin kerangka berkas
import_fixer        betulkan jalur impor
db_extractor        tarik skema basis data
surgical_splicer    ambil satu fungsi atau kelas saja, tanpa konteks sekitarnya
native_checker_gen  bikin uji unit atau skrip pemeriksa yang berdiri sendiri
```

`tree_gen` juga ikut terpasang, tetapi ia modul bersama, bukan alat yang
dipanggil pengguna (`tests/test_skills_structure.py:17`).

### Chamber

Protokol empat peran: PM (manusia), TL (agen), QA (agen kedua), dan subagen
sekali pakai. Opsional — dipasang terpisah lewat `snowline init_chamber`.

Aturannya di `src/snowline/chamber_templates/CHAMBER_RULES.md`. Yang paling
sering menggigit: butir 4, entri yang mengaku selesai tanpa blok perintah dan
keluaran mentah ditolak sebelum dibaca.

### Yang sudah diarsipkan

`companion` — penganalisis maksud. Diuji di tiga proyek, dan di ketiganya agen
memanggilnya lalu mengabaikan sarannya. Ia menjawab pertanyaan yang tidak
sedang ditanyakan siapa pun. Kodenya disimpan di `archive/companion/`, bukan
dibuang, kalau-kalau idenya muncul lagi dalam bentuk lain.

---

## Yang menentukan rilis berikutnya

Daftar Terbuka tidak akan pernah kosong, dan itu bukan alasan menahan rilis.
Yang menahan cuma butir di atas garis.

**Garis rilisnya ada di `.here_we_are/STATE.md`, bagian "Garis rilis".**
Jangan menyalinnya ke sini — satu daftar yang hidup di dua tempat akan
melenceng, dan kita sudah tiga kali kena pola itu (angka versi di lima berkas,
validasi topik di dua berkas, `PROTECTED` di dua blok).

---

## Terbuka

Butir yang sudah punya nama tetapi belum dikerjakan. Yang lengkap ada di
`STATE.md`; ini yang menyentuh arah paket.

```
dua literal versi di cli.py    nilai cadangan "1.2.0" di get_snowline_version(),
                               tidak dijaga uji mana pun (dibuktikan dengan
                               mutasi: diubah ke "0.0.0", suite tetap hijau)
label [Companion Gate]         tersisa di quality_gate.py, 3 tempat, padahal
                               companion sudah diarsipkan
clean_sweeper berisik          mencetak daftar panjang seperti smart_search dulu
pesan gagal uji kosong         tercatat empat kali, belum diperbaiki
```

---

## Ditangguhkan

Empat berkas di `deferred/`, belum pernah masuk paket:

```
token_budget         pemantau pemakaian token
context_curator      penyaring kebisingan konteks
output_formatter     perapi keluaran JSON
decision_validator   penilai risiko
```

Semuanya ditangguhkan karena alasan yang sama: belum jelas penjaganya bisa
ditaruh di dalam alat, atau cuma akan jadi lapisan di depannya.

---

## Struktur berkas

```
snowline-agent-tools/
├── src/snowline/
│   ├── templates/          alat yang disalin ke .agents/ proyek pengguna
│   ├── chamber_templates/  protokol chamber
│   └── test_templates/     panduan uji lapangan (snowline init test)
├── tests/                  43 berkas uji, 128 uji
├── archive/                yang dipensiunkan tetapi disimpan
├── deferred/               yang belum pernah masuk
├── quarantine/             kandidat buang, tidak dilacak git
├── .agents/                pemasangan snowline ke dirinya sendiri
├── .here_we_are/           chamber repo ini (connector, STATE)
└── agents_chamber/         hanya CHAMBER_RULES.md, dijaga Aturan #12
```

---

## Cara memeriksa berkas ini masih benar

Setiap angka di atas bisa dibantah dengan satu perintah:

```
jumlah alat      ls src/snowline/templates/skills   (18 entri: 16 alat,
                                                     plus rules dan tree_gen)
jumlah uji       python tests/run_tests.py
versi            PYTHONPATH=src python -m snowline --version
Aturan #12       powershell -File ./verify_rule12.ps1
```

Kalau angkanya berbeda, yang salah berkas ini, bukan perintahnya.

Perhatikan `PYTHONPATH=src` pada perintah versi. Tanpa itu, yang terukur
adalah snowline yang **terpasang di mesin**, bukan yang ada di repo ini —
dan keduanya sering berbeda. Perintah tanpa `PYTHONPATH` bahkan bisa gagal
sama sekali kalau paket terpasangnya lebih tua daripada `__main__.py`.

*Terakhir diperbarui: 2026-08-30, sesudah Sprint 50.*
