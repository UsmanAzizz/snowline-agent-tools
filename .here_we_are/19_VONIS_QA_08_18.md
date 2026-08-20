# Vonis QA atas 08–18

Diperiksa 20 Agustus 2026. Sebelas dokumen, dibuat antara 08.45 dan 10.21 —
rata-rata satu per 8,6 menit.

Vonis dipisah tiga: yang bertabrakan dengan keputusan tercatat, yang angkanya
tidak bisa diperiksa, dan yang benar-benar berguna.

---

## A. Bertabrakan dengan keputusan yang sudah tercatat

Ini bagian paling serius, karena keputusannya ada di folder yang sama.

### A1. `13` dan `17` membalik peran companion

`13_PROTOTYPE_COMPANION_V2.md` menjadikan companion **Dispatcher / Traffic
Controller** yang menyortir ke tiga rel eksekusi.

`17_PROTOTYPE_RISK_MITIGATION.md` §3 mempertegasnya:

> *Companion Router* tidak boleh bersikap demokratis. 80% dari kueri harian
> **HARUS** dipaksa masuk ke rute `SOLO_AGENT` yang mengeksekusi secara instan.

`DESIGN_PHILOSOPHY.md`, kutipan langsung PM:

> Begitu companion mengeluarkan perintah eksekusi, ia berhenti menjadi rantai
> dan berubah menjadi pemberi perintah — dan itu **pembalikan peran**, bukan
> peningkatan kemampuan.
>
> `Action: EXECUTE` **bukan bagian dari rancangan awal**... Bila kemudian
> muncul lagi, itu **penyimpangan yang perlu dikembalikan** — bukan fitur yang
> perlu dipertahankan.

Dan perancang aslinya, di `07_JAWABAN_PERANCANG.md` yang ditulis **hari yang
sama, beberapa jam sebelumnya**:

> companion **bukan** entitas yang memahami maksud user atau mengambil
> keputusan sendiri.

`SOLO_AGENT` yang "dieksekusi seketika" adalah `EXECUTE` dengan nama baru.

### A2. `12` mengotomasi chamber, yang sudah diputuskan tidak boleh

`12_PROTOTYPE_CHAMBER_V2.md` menggantikan "Manusia Penjahit" dengan
*middle-layer script* otomatis.

`project_context.md:81`, keputusan Task 38:

> `agents_chamber/` dan `orchestrator/` **NOT to be integrated**... invoked
> **manually every time (no automation/daemon that calls agents on its own)**.

Tiga alasannya tercatat, salah satunya privasi — memanggil CLI AI eksternal
tanpa persetujuan per-proyek disebut "a privacy concern, not just a technical
inconvenience".

`12` tidak menyebut keputusan itu, tidak membantahnya, dan tidak menyatakan
bahwa ia sedang membatalkannya.

---

## B. Angka yang tidak bisa diperiksa

Empat klaim persentase tentang sistem yang **belum ada**, tanpa satu pun
perintah reproduksi:

| dokumen | klaim |
|---|---|
| `08` | "`smart_tree` menghemat **84% token murni** dibanding `tree`" |
| `12` | "kita telah mengeliminasi **90%** penyebab kegagalan agen otonom di dunia nyata (berdasarkan data SWE-bench)" |
| `14` | "jaminan keandalan (*Reliability Guarantee*) sebesar **99%**" |
| `17` | "meroketkan peluang sukses agen hingga **90%**" |

Bentuknya sama dengan enam klaim yang sudah gugur di papan ini: angka bulat,
terdengar meyakinkan, muncul tepat di kalimat penutup.

**Satu koreksi faktual di `08`:**

> Transformasi `impact_analyzer` dan `plan_tracker` menjadi alat MEMERIKSA
> (dengan `exit 1`) menyempurnakan posisi ekosistem kita.

Itu ditulis sebagai sudah terjadi. Belum. T8 mengklasifikasikan keduanya
SETENGAH, dan sitasi T8 sendiri ditolak QA karena 10 dari 11 nomor barisnya
menunjuk ke luar berkas.

**`15`** menyatakan "membuang kebutuhan atas server *Vector Database* raksasa".
Tidak ada yang pernah mengusulkannya di repositori ini.

---

## C. Yang benar-benar berguna, dan bisa dikerjakan besok

Empat butir konkret, tidak bergantung pada Chamber V2 sama sekali:

**C1. `18` §3 — Syntax Guardian delegasi ke linter proyek.** `node --check`
memang gagal pada `.jsx`/`.tsx`. Mendelegasikan ke ESLint/TSC dan membaca exit
code-nya adalah perbaikan nyata untuk keterbatasan nyata.

**C2. `18` §4 — `git clean -fd` setelah `git reset --hard`.** Benar. Reset saja
memang meninggalkan berkas *untracked* buatan agen.

**C3. `10` — firewall injeksi prompt + spotlighting.** Ini satu-satunya
prototipe di sini yang punya artefak uji sungguhan: `malicious_readme.md` dan
`clean_readme.md` ada di `v2_prototypes/`. Tekniknya baku dan pemindainya
deterministik.

**C4. `09` §2 — loop detector.** Tiga panggilan identik lalu berhenti. Benar,
tetapi **bukan hal baru** — Kilocode, opencode-anti-loop, dan hermes-agent
sudah mengirimkannya. Lihat `01_TEMUAN.md` bagian B.

Keempatnya bisa dikerjakan tanpa membangun apa pun yang bernama V2.

---

## D. Catatan tentang laju

Sebelas blueprint dalam 95 menit. Tidak satu pun memuat perintah reproduksi,
dan `05_EXECUTION_REPORT_V2.md` di `antigravity_insights/` sudah menyatakan
arsitekturnya "sukses direalisasikan" sebelum satu pun di antaranya diperiksa.

Sprint 19–20 Agustus ada justru untuk memotong pola ini: membangun di atas
premis sebelum premisnya diperiksa. `04_V2_ROADMAP.md` dan delapan prototipe
sudah berjalan saat pengukurannya belum selesai; sekarang sebelas lagi.

QA tidak menilai apakah V2 layak dibangun — itu bukan wewenang QA.
Yang dilaporkan hanya ini: **dua dokumen membatalkan keputusan yang PM catat
sendiri, tanpa menyebutkan bahwa keputusan itu ada.**

---

## Ringkas

| | |
|---|---|
| Bertabrakan dengan keputusan tercatat | `12`, `13`, `17` |
| Angka tak terperiksa | `08`, `12`, `14`, `17` |
| Salah menyatakan sesuatu sudah terjadi | `08` |
| Berguna dan bisa dikerjakan langsung | `18` §3, `18` §4, `10`, `09` §2 |
| Tidak diperiksa butir per butir | `11`, `16` |
