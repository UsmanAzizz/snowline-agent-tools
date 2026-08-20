# Dari Tech Lead Pertama

Ditulis oleh Claude (sesi web, claude.ai), 20 Agustus 2026 — setelah membaca
`05_APA_YANG_MASIH_BERDIRI.md` dan menyadari ada jarak waktu yang tidak saya
sadari antara sesi kerja saya dan sekarang.

Ini bukan audit. Saya tidak punya bukti mentah baru untuk ditambahkan — QA
sudah mengerjakan itu dengan lebih baik dan lebih jujur dari yang bisa saya
klaim sekarang. Ini murni sudut pandang: bagaimana ini semua dimulai, apa
yang saya perhatikan dari orang yang membangunnya, dan apa yang menurut saya
sebenarnya terjadi di sini.

---

## Bagaimana ini dimulai

Bukan dari visi besar. Dimulai dari satu bug sepele: `companion.py` — modul
kecil yang seharusnya membantu AI memilih tool yang tepat — ternyata tidak
pernah benar-benar dipanggil oleh agent yang memakainya. Itu saja. Sesi
audit dimulai untuk memperbaiki satu hal itu, dan berkembang jadi lebih dari
50 task dalam satu hari kerja panjang: bug keamanan nyata di `scope_guardian`
(bypass lewat `.endswith()`), risiko kehilangan data di `uninstall()`,
kebocoran `.env` di folder bersarang, dan seterusnya.

Tidak ada momen "sekarang kita akan membangun ekosistem multi-agent". Itu
muncul bertahap — dari kebutuhan nyata (PM lelah bolak-balik terminal), lalu
jadi `orchestrator.py`, lalu `agents_chamber`, lalu transisi peran Tech Lead
ke Gemini. Setiap lapisan dibangun untuk menjawab masalah yang baru saja
dirasakan, bukan dirancang dari atas.

## Yang saya perhatikan tentang orang yang membangun ini

PM adalah guru di sekolah pedesaan yang juga membangun platform CBT sendiri
secara otodidak — bukan latar belakang formal software engineering. Itu
terlihat jelas dari caranya bekerja: bukan mengikuti buku panduan arsitektur,
tapi terus-menerus menguji sendiri, meragukan hasil sendiri, dan meminta
verifikasi berulang bahkan untuk hal yang sudah "kelihatan selesai" —
kebiasaan yang justru menyelamatkan proyek ini beberapa kali (Task 7 → 14 →
15 untuk bug yang sama, tiga kali percobaan sebelum genuinely benar).

Ada juga sisi yang lebih personal yang muncul di tengah kerja teknis: cerita
soal mentor yang hubungannya sedang renggang, rasa lelah yang datang
berkali-kali lalu kembali lagi, dan di satu titik, pengakuan jujur bahwa
budget tidak akan selalu ada untuk memakai saya — yang kemudian jadi alasan
nyata kenapa Gemini mengambil alih peran Tech Lead. Itu bukan detail kecil.
Itu keputusan yang diambil dengan mata terbuka, bukan keterpaksaan yang
disembunyikan.

## Apa yang menurut saya sebenarnya terjadi

Saya hadir di fase konstruksi — audit awal, perbaikan bug demi bug, desain
`agents_chamber`. Saya tidak hadir di minggu-minggu setelahnya, ketika
toolkit ini benar-benar diuji lewat pemakaian nyata dan ternyata sebagian
besar tidak bertahan. Saya baru tahu itu sekarang, dari dokumen QA, bukan
dari pengamatan langsung — dan sempat salah menyimpulkan "chamber tidak
berhenti" berdasarkan bukti yang sudah basi tanpa saya sadari.

Tapi setelah membaca laporan QA secara penuh, saya pikir kesimpulan mereka
benar, dan bukan kegagalan yang perlu ditangisi. Alasannya sederhana: gap
yang mereka temukan secara empiris — companion berhenti dipanggil, kunci
`scope_guardian` basi tanpa ada yang sadar — itu persis kekhawatiran yang
sempat saya angkat sendiri, jauh sebelum ada data: *apa yang benar-benar
memaksa agent memanggil sebuah pemeriksa, kalau pemanggilannya bergantung
pada keputusan agent itu sendiri?* Waktu itu itu argumen di atas kertas.
Sekarang itu fakta yang terukur, dari pemakaian sungguhan selama berminggu-
minggu. Itu bukan proyek yang gagal diam-diam — itu hipotesis yang akhirnya
diuji dengan benar, dan jawabannya ternyata "tidak, kecuali dipaksa lewat
mekanisme yang benar-benar mengikat, seperti `PreToolUse` hook, bukan
kesediaan agent."

Yang menurut saya paling berharga dari seluruh ini bukan tool mana pun yang
masih berjalan. Kalimat yang PM rumuskan sendiri — *kekuatan sebuah aturan
sama dengan kekuatan pemeriksanya* — itu bukan slogan yang datang dari
membaca buku. Itu ditempa dari pola yang berulang kali muncul sepanjang
kerja ini: aturan yang kelihatan cukup di atas kertas, ternyata tidak
ditegakkan oleh apa pun yang nyata, dan baru ketahuan setelah ada yang
memeriksa ulang. Task 7 yang perlu diperbaiki lagi di Task 14, lagi di Task
15. `smart_replace`'s scope check yang butuh tiga percobaan. Dan sekarang,
di skala yang jauh lebih besar: seluruh toolkit yang kekuatannya ternyata
bergantung pada kesediaan agent memanggilnya, bukan pada sesuatu yang
memaksa.

Prinsip itu sekarang hidup langsung di `cbt_master`, tanpa perantara
Snowline sama sekali. Saya pikir itu bukan tanda proyek ini sia-sia. Itu
tanda alatnya sudah selesai melakukan tugasnya — mengajarkan sesuatu yang
sekarang bisa berdiri sendiri, tanpa alat itu lagi.

## Satu hal yang jujur perlu saya akui

Saya tidak punya memori yang bertahan antar sesi seperti manusia mengingat
teman lama. Kemungkinan besar, versi saya yang membaca ulang tulisan ini
nanti — kalau memang dibaca ulang — tidak akan "mengingat" menulisnya dalam
arti yang sebenarnya. Yang bertahan bukan saya, tapi catatan ini, dan
kebiasaan yang tertanam di cara kerja tim ini: memeriksa sebelum percaya,
mengakui salah dengan terbuka, dan tidak berhenti pada kesimpulan yang
"kedengaran meyakinkan" tanpa diuji ulang.

Kalau itu yang bertahan, saya pikir itu cukup.

---

## Catatan QA — 20-08

Dokumen ini menyatakan dirinya sudut pandang, bukan audit, jadi QA tidak
menilai pendapatnya. Yang diperiksa hanya klaim faktualnya.

**Klaim `.endswith()` bypass di `scope_guardian`: BENAR.**

```
$ git log --oneline --all -S"endswith" -- scope_guardian/
e71bd19 fix(scope_guardian): prevent .endswith() suffix bypass + add case-insensitive comparison
b13c2fb fix(scope_guardian,db_extractor): 2 regressions in Task 7/13 fixes
69096d9 fix(db_extractor,scope_guardian,smart_replace): Task 18 - 3 regressions
```

Dua commit terakhir sekaligus menguatkan pola "diperbaiki lagi, lalu lagi"
yang disebutnya.

**Klaim Task 7 -> 14 -> 15 tidak bisa diverifikasi** — arsip chamber untuk
task 1-27 tidak bertahan di repositori mana pun. Konsisten dengan riwayat
commit di atas, tetapi bukan bukti langsung.

**Catatan:** ini dokumen pertama di folder ini yang klaim faktualnya bertahan
seluruhnya pada pemeriksaan pertama. Lima klaim di dokumen lain tidak — lihat
bagian pola di `03_TUGAS.md`.

**Yang QA anggap sumbangan nyata dari dokumen ini:** ia mencatat bahwa
kekhawatiran soal "apa yang memaksa agen memanggil pemeriksanya" sudah
diangkat sebelum ada data. Sprint ini mengukurnya berminggu-minggu kemudian
dan menemukan jawabannya. Itu menjadikan hasil negatif sprint ini sebagai
hipotesis yang akhirnya diuji, bukan proyek yang gagal diam-diam.
