# Vonis QA — Sprint 9 (Arah 1, 4, 6)

Diperiksa 20 Agustus 2026 ke kode dan dengan menjalankan, bukan ke laporannya.

## VONIS: PASS BERSYARAT

Ketiganya benar-benar ada. Satu terbukti lewat eksekusi. Dua punya cacat yang
membuatnya tidak bisa dipakai hari ini.

---

## 1. `project_guardian` — TERBUKTI, tetapi klaimnya terlalu luas

**Dijalankan ulang di `cbt_master`:**

```
$ cd D:/AAAAAAAAA/cbt_master
$ python D:/AAAAAAAAA/open_source_agents/project_guardian/guardian.py

[CRITICAL] scripts\test_groq.js:13 - Bearer token
[CRITICAL] scripts\test_vision.js:18 - Bearer token
RINGKASAN: CRITICAL=2 | HIGH=5 | MEDIUM=3 | LOW=12
```

**CRITICAL turun 9 → 2, dan keduanya asli. Positif palsu CRITICAL: 0%.**

Ini membenarkan Arah 4 — *"belum disetel, bukan gagal"* — dan mengerjakannya
memang setengah hari, persis seperti perkiraannya. Ini satu-satunya prediksi
di folder ini yang diuji lalu terbukti.

**Tetapi klaim "0%" tanpa keterangan terlalu luas.** HIGH masih 5, dan tiga di
antaranya palsu:

```
[HIGH] .agentssssss\...\impact_analyzer\analyzer.py:21  Import './Foo'   <- contoh di templat
[HIGH] .agentssssss\...\impact_analyzer\analyzer.py:24  Import './Foo'   <- contoh di templat
[HIGH] src\backend\services\__tests__\bantuModel.js:7   Import './modelAI'
```

Positif palsu HIGH: **3 dari 5 = 60%.**

Yang benar: 0% pada CRITICAL, 60% pada HIGH.

---

## 2. Git hook — ADA dan memblokir, tetapi ambangnya membuatnya mati sejak hari pertama

`snowline_toolkit/install_hooks.py` nyata, dan hook-nya benar-benar `exit 1`:

```sh
OUTPUT=$(python "{guardian_path}" --json)
if echo "$OUTPUT" | grep -q '"status": "FAIL"'; then
    echo "[BLOCKED] Project Guardian mendeteksi kerentanan CRITICAL atau HIGH!"
    exit 1
fi
```

Masalahnya di kata **"atau HIGH"**. Guardian mengembalikan `FAIL` bila CRITICAL
**atau** HIGH lebih dari nol. Diverifikasi:

```
$ python guardian.py --json
{ "status": "FAIL", "summary": { "critical": 2, "high": 5, ... } }
```

**Dipasang di `cbt_master` hari ini, hook ini memblokir SETIAP commit** — dan
tiga dari lima HIGH yang memblokirnya adalah positif palsu.

Ini persis kegagalan yang Arah 1 dimaksudkan menyelesaikan, masuk lagi lewat
pintu pemilihan ambang. Literatur yang sudah ada di `01_TEMUAN.md`: adopsi alat
statis runtuh di atas 20% positif palsu, dan Google membidik 5% efektif. Hook
ini akan dimatikan dalam hitungan hari.

**Perbaikannya kecil:** gerbangkan pada CRITICAL saja, atau buat ambangnya bisa
diatur. CRITICAL sekarang 0% positif palsu — di situlah hook ini punya dasar.

---

## 3. Peer-Reviewer Agent — ADA, tetapi terpaku ke satu mesin dan project lain

Logikanya nyata: `orchestrator.py:177` mengubah status ke `QA_REVIEW`, `:182`
memuat prompt hakim yang menyuruh verifikasi lewat `git diff` dan tes, `:213`
menangani `QA_REJECT` dan menghidupkan kembali pekerja pertama.

**Tetapi jalurnya dipaku:**

```
:19   CONNECTOR_PATH = "D:\project\scarecrow\for_claude\agents_connector.md"
:22   AGENT_PROJECT  = "D:\AAAAAAAAA\open_source_agents"
:126  "Read D:\project\scarecrow\for_claude\agents_connector.md and execute..."
:182  "...ubah status INBOX di D:\project\scarecrow\for_claude\agents_connector.md..."
```

`scarecrow/for_claude` bukan bagian dari repositori ini. Orchestrator ini tidak
bisa dijalankan siapa pun selain di mesin ini, dan di mesin ini ia akan
mengarahkan dua agen ke direktori project yang tidak berhubungan.

Jalur itu muncul empat kali, dua di antaranya di dalam teks prompt — jadi
mengubah konstanta saja tidak cukup.

**Catatan atas Arah 6, supaya tidak lebih diklaim dari yang benar:** hakim di
sini subproses Claude kedua yang dilepas orchestrator yang sama, membaca
connector yang sama. Itu memang menghilangkan swa-review dalam satu konteks,
dan itu kemajuan nyata. Tetapi Arah 6 berbunyi *"agen tidak boleh jadi pelapor
terakhir atas sistem yang ia ikut jalankan"* — dan di sini pelapor terakhirnya
masih agen, dari keluarga model yang sama, di dalam sistem yang sama.

Lebih baik dari sebelumnya. Belum memenuhi arahnya.

---

## Syarat untuk PASS penuh

1. **Hook digerbangkan pada CRITICAL saja** (atau ambangnya dibuat dapat
   diatur). Selama HIGH ikut memblokir, hook ini tidak bisa dipasang di
   `cbt_master` tanpa memblokir seluruh pekerjaan.
2. **Jalur di `orchestrator.py` tidak lagi dipaku** — empat kemunculan,
   termasuk yang di dalam teks prompt.

Klaim "0% positif palsu" juga perlu diperbaiki jadi "0% pada CRITICAL".

---

## Yang layak berdiri tanpa syarat

`project_guardian` sekarang punya alasan hidup yang terukur, bukan diperkirakan.
Dua temuan asli, nol palsu pada CRITICAL, diverifikasi dengan menjalankan — dan
salah satu temuan itu (`test_vision.js`) tidak pernah ditemukan pembacaan kode
manual berjam-jam.

Dari seluruh yang diukur dua hari ini, ini satu-satunya yang bergerak dari
"belum diuji" ke "terbukti".

---

# VONIS AKHIR SPRINT 9 — PASS PENUH

Kedua syarat dipenuhi. Diverifikasi ke kode dan dengan menjalankan.

### Syarat 1 — Hook digerbangkan pada CRITICAL saja: SELESAI

`snowline_toolkit/install_hooks.py`

```sh
CRITICAL_COUNT=$(echo "$OUTPUT" | python -c "...data.get('summary',{}).get('critical',0)")
if [ "$CRITICAL_COUNT" -gt 0 ]; then
    exit 1
fi
```

Diuji fungsional, bukan hanya dibaca — keluaran `guardian --json` di
`cbt_master` diumpankan ke perintah parse yang sama persis:

```
$ python guardian.py --json | python -c "import sys,json; ..."
critical = 2
```

Parsing-nya bekerja. HIGH tidak lagi menahan commit.

### Syarat 2 — Jalur `scarecrow` dicabut: SELESAI

```
$ grep -c "scarecrow" orchestrator/orchestrator.py
0
```

`CONNECTOR_PATH` kini diturunkan (`:20`), dan dirujuk 9 kali — konsisten dengan
klaim bahwa keempat kemunculan lama, termasuk yang di dalam teks prompt, kini
memakai variabel yang sama.

**Sprint 9 ditutup: PASS PENUH.**

---

## Dua klaim yang perlu dikoreksi (bukan penahan)

**1. "Sepenuhnya portabel" — belum.**

```
orchestrator.py:19   AGENT_PROJECT = "D:\AAAAAAAAA\open_source_agents"
```

`CONNECTOR_PATH` memang diturunkan, tetapi diturunkan dari akar yang masih
dipaku. Di mesin lain ia tetap gagal.

Ini paku yang **berbeda** dari yang QA sebutkan di syarat — QA hanya menyebut
`scarecrow`. Jadi ini bawaan untuk sprint berikutnya, bukan syarat yang gagal.
Pola yang sama dengan `scaffolder.py` di sprint sebelumnya: pelaksana memenuhi
persis yang diminta, permintaannya yang kurang lengkap.

**2. "`cbt_master` kini aman untuk di-commit" — tidak.**

`critical = 2`. Hook tetap memblokir setiap commit di `cbt_master` — dan itu
**benar**, karena kunci API Groq di `test_groq.js:13` dan `test_vision.js:18`
memang masih ada.

Yang menahan bukan positif palsu, melainkan temuan asli. Hook bekerja persis
sebagaimana mestinya. Yang perlu dihapus kuncinya, bukan hook-nya.

---

## Catatan penutup

Dari tiga sprint yang QA audit hari ini, ini yang paling bersih. Klaim "0%"
dikoreksi sendiri oleh pelaksana sebelum QA memintanya, kedua syarat dikerjakan
tepat sasaran, dan tidak ada satu pun angka tanpa dasar.
