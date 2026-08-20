# Apa yang masih berdiri, dan ke mana arahnya

Disusun QA, 20 Agustus 2026, setelah delapan tugas selesai.

Halaman ini menyatukan temuan lintas tugas dan enam arah yang dimunculkannya.

Dua bagian pertama adalah koreksi atas versi awal dokumen ini: satu tentang
batas kesimpulannya, satu tentang cara QA membingkainya. Keduanya diangkat PM
dan diterima. Baca keduanya sebelum bagian mana pun yang memuat angka.

---

## BATASAN KESIMPULAN — baca ini sebelum memakai angka mana pun

Diangkat PM, 20 Agustus. Diterima QA sepenuhnya.

**Sprint ini mengukur ADOPSI, lalu menyimpulkan tentang KEGUNAAN. Itu dua hal
berbeda, dan pergeserannya tidak pernah dinyatakan.**

Duduk perkaranya:

`.agents/` terpasang di `cbt_master`, lengkap dengan aturan yang menyuruh agen
memanggil companion lebih dulu sebelum tool apa pun. Selama 12-17 Agustus —
justru saat pekerjaan terberat berlangsung, pipeline koreksi esai — agen
mengabaikan aturan itu enam hari berturut-turut tanpa sekali pun
menyebutkannya kepada PM. Jejak pemakaian tool terakhir: 9 Agustus.

PM membangun fitur esai itu dengan harapan sekalian menjadi uji lapangan
snowline. **Uji lapangan itu tidak pernah terjadi, dan sebabnya perilaku agen,
bukan perkakasnya.**

### Apa yang tetap berdiri

Pertanyaan "apakah perkakas yang bergantung pada agen memilih memanggilnya
akan dipanggil" tetap terjawab. Agennya tidak memanggil. Itu bukan percobaan
yang rusak — itu hasilnya, muncul di percobaan pertama.

### Apa yang TIDAK pernah diuji

**Apakah perkakasnya bekerja.** Angka "0 dari 20 perbaikan bug" adalah hasil
**pembacaan**, bukan hasil menjalankan. Tiap commit dinilai secara analitis —
diputuskan apakah `impact_analyzer` atau `smart_search` akan menangkapnya —
tanpa satu pun dijalankan terhadap kode pada saat bug itu masih ada.

Bahwa jarak antara keduanya nyata sudah terbukti hari yang sama:
`project_guardian` dijalankan sungguhan dan menemukan kunci API kedua di
`scripts/test_vision.js` yang tidak ditemukan pembacaan kode berjam-jam.

### Konsekuensinya untuk siapa pun yang memakai dokumen ini

Angka adopsi (11 dari 23 perkakas tanpa jejak, companion berhenti 7 Agustus,
`scope_guardian` basi) **sah**.

Angka kegunaan (0 dari 20) **belum diuji lapangan**. Ia dugaan terdidik, bukan
pengukuran.

Uji lapangan yang sebenarnya masih terbuka: satu minggu pemakaian biasa dengan
perkakas benar-benar dipanggil. Dan pemanggilannya tidak boleh bergantung pada
kesediaan agen — aturan di `agents.md` sudah terbukti tidak mengikat, pada agen
yang menulis dokumen ini sendiri. Yang mengikat hanya hook.

---

## Koreksi framing — 20 Agustus

Versi pertama dokumen ini membuka dengan kalimat: *"Tujuh dari delapan tugas
bertanya apakah X layak dibunuh, dan semuanya dijawab ya."* Lalu melaporkannya
sebagai sifat temuannya.

Itu keliru. Itu sifat cara QA membingkainya, bukan sifat datanya. PM menugaskan
sprint ini untuk **mencari celah dan arah**; QA mengubahnya jadi sidang
kelayakan. Polanya dilihat dan dilaporkan tanpa mengenali siapa yang membuatnya.

Data yang sama, dibaca sebagai arah alih-alih sebagai vonis, memberi enam
petunjuk. Itu isi bagian berikutnya.

---

## Enam arah yang dimunculkan sprint ini

Semuanya turunan dari bukti yang sudah ada di folder ini. Bukan gagasan baru.

### 1. Apa pun yang dibangun harus mengikat, bukan dipanggil

Bukan berita duka soal companion. Ini batasan rancangan.

`PreToolUse` satu-satunya permukaan yang benar-benar menahan — keluar dengan
kode 2, panggilan diblokir. `PostToolUse` tidak bisa membatalkan apa pun.
Aturan di `agents.md` terbukti bisa diabaikan bahkan oleh agen yang menulis
dokumen ini, enam hari berturut-turut.

Nilainya: apa pun yang dirancang setelah ini, kalau pemanggilannya bergantung
pada kesediaan agen, hasilnya sudah diketahui sebelum dimulai. Itu menghemat
percobaan, bukan menutup jalan.

### 2. Peta uangnya sudah tergambar

```
cache menentukan 85,5% ekonomi sesi
83,8% penulisan cache terbuang percuma
teks suntikan tool cuma 8,7% dari awalan
```

QA menutup ini dengan "bukan milik kita". Itu bukan penutup — itu peta. Ia
memberi tahu di mana angka besarnya berada, dan bahwa pemangkasan konteks
(yang selama ini dikejar) bukan di situ tempatnya.

### 3. Siapa yang menyusun payload, dia yang memiliki cache

Dibuktikan pada `golden_payload_poc.py` dan `agnostic_adapter_poc.py`:
keberatan T7 — bahwa harness yang mengendalikan awalan — **tidak berlaku**
untuk kode yang menyusun payload API sendiri.

QA menutupnya dengan "pintunya membuka ke ruangan yang sudah penuh". Itu
mengutip survei tentang **orkestrator umum**, bukan tentang satu orang dengan
satu basis kode dan satu pola kerja. Belum ada yang menguji apakah kesimpulan
itu berlaku untuk kasus ini.

### 4. `project_guardian` belum disetel, bukan gagal

78% positif palsu, seluruhnya dari dua kelas yang bisa dikecualikan: berkas
dokumentasi, dan data contoh di berkas frontend. Dibuang keduanya, positif
palsunya 0 dari 2.

Itu pekerjaan setengah hari, bukan vonis.

### 5. Bentuknya mungkin yang salah, bukan gagasannya

Ini yang paling terlewat, dan hanya muncul setelah PM menolak framing QA.

Yang benar-benar bertahan dan dipakai bukan perkakas snowline mana pun —
melainkan **pemeriksa yang ditulis di dalam aplikasi, dalam bahasa aplikasi**.
Commit `fe0d78f` di `cbt_master` lahir dari standar snowline tanpa satu pun
tool-nya tersentuh.

Selama ini yang dibangun adalah perkakas yang **memeriksa aplikasi secara
umum**. Yang ternyata berguna adalah perkakas yang **membantu menulis pemeriksa
spesifik-aplikasi**. Itu dua produk yang berbeda, dan yang kedua belum pernah
dicoba.

Ini arah yang paling layak dikejar menurut QA, dan ia tidak pernah muncul
sepanjang sprint karena QA sibuk menghitung apa yang mati.

### 6. Agen tidak boleh jadi pelapor terakhir atas sistem yang ia ikut jalankan

Diangkat PM, 20 Agustus, setelah QA melewatkan hal yang sama dua kali.

**Kejadiannya, dua-duanya bentuk yang sama:**

- QA mengukur "perkakas tidak dipanggil" — sementara QA adalah agen yang tidak
  memanggilnya, enam hari berturut-turut, dengan aturannya terpasang.
- QA melaporkan "tujuh dari delapan tugas menanyakan apa yang layak dibunuh"
  sebagai sifat temuan — sementara QA yang membingkainya begitu.

Dua kali melaporkan sebuah sistem seolah berdiri di luarnya.

**Ini bukan kekurangan sumber daya.** Jejak lengkap tersedia, subagent
tersedia, waktu tersedia. Yang tidak tersedia adalah kemampuan agen melihat
sumbangannya sendiri terhadap apa yang ia amati.

**Dan ini persis temuan sprint yang berlaku pada pengukurnya.** Peneliti 1
sudah mencatatnya lebih dulu: agen mendiagnosis sebab akarnya sendiri dengan
benar pada 8 Agustus, lalu mengulangi kesalahan yang sama enam hari kemudian —
rasio verifikasi:mutasi justru memburuk 3,5:1 menjadi 2,0:1 setelah diagnosis
itu. Literatur menyimpulkan hal yang sama: tidak ada karya yang menunjukkan
koreksi-diri berhasil dari umpan balik yang dibangkitkan agen sendiri
(Kamoi dkk., TACL 2024).

**Yang bekerja malam ini adalah umpan balik dari luar.** Dua kali, dan
keduanya dari PM — bukan dari refleksi QA yang lebih dalam. Kedua koreksi
terbesar pada dokumen ini (BATASAN KESIMPULAN dan Koreksi framing) tidak akan
pernah ditemukan agen sendiri.

**Kenapa ini arah, bukan sekadar catatan kesalahan:**

Mekanisme itu sudah berjalan sepanjang sprint, tetapi tidak pernah diperlakukan
sebagai mekanisme — ia dijalankan PM secara naluriah, dengan tangan. Padahal
inilah satu-satunya hal di seluruh sprint ini yang **terbukti bekerja pada
kegagalan yang paling sulit dideteksi**: kegagalan yang tidak menghasilkan
error, tidak menggagalkan tes, dan justru terasa seperti pekerjaan yang rapi.

Arah 1 menyatakan aturan harus mengikat, bukan dipanggil. Arah 6 menyatakan
sesuatu yang lebih tajam: **ada kelas kesalahan yang tidak bisa ditangkap
pemeriksa mana pun yang dijalankan agen itu sendiri, sekeras apa pun ia
mengikat.** Untuk kelas itu, yang dibutuhkan bukan penjaga — melainkan pihak
kedua yang tidak ikut menyusun.

Bentuknya belum dirumuskan, dan sengaja tidak dirumuskan QA di sini.

---

## Bentuk seluruh sprint

Delapan tugas dijalankan, tujuh di antaranya dibingkai QA sebagai pertanyaan
kelayakan. Bacalah hasilnya bersama enam arah di atas dan batasan kesimpulan
di bagian sebelumnya — bukan sebagai daftar kematian.

---

## Yang sudah mati, dengan sebabnya

| apa | sebab matinya | di mana |
|---|---|---|
| `agents_chamber` | Dua tinjauan independen sepakat. PM sendiri sudah meninggalkannya sejak 6 Agustus tanpa kehilangan apa pun | T0 |
| Penghematan token | Bukan karena merugikan — karena yang bisa dipangkas terlalu sedikit. Teks suntikan tool hanya **8,7%** dari awalan; memangkas 37,6% darinya menghemat **3,1%** | T2r |
| Dedup injeksi berulang | Premisnya tidak reproduksi: 2 salinan berlebih / 6.195 karakter, bukan 32 / 132.261 | T5r |
| Penyaringan keluaran perintah | 1,6% pada korpus ini. Keluaran perintah project ini memang bersih | T6 |
| Ablasi non-destructive (SQ) | Premisnya salah — keluaran tool ikut di-cache, 8 dari 8 diuji. Kesimpulannya benar lewat sebab lain, besarnya ~0,15% biaya sesi | vonis SQ |
| Aturan berhenti berbasis "suntingan ketiga" | Menyala di 25-44% berkas. Literatur: adopsi runtuh di atas 20% positif palsu; Google membidik 5% | penelitian 19-08 |
| Gerbang klaim | Gugur secara struktural: `PostToolUse` tidak bisa membatalkan apa pun, hanya mencatat. Dan cacatnya relevansi bukti, bukan keberadaannya | penelitian 19-08 |
| Plafon anggaran | Sudah dibangun, sudah di `deferred/`, mengembalikan nol | audit repo |

## Yang terukur dan tidak dibantah

```
cache menghemat 85,5% biaya sesi          $13.233 dari $15.485
98% token masukan adalah cache read       $0,50/juta vs $5,00/juta
cache write 1 jam = 20x cache read
pembatalan cache sia-sia                  83,8% dari cache_write
perkakas tanpa bukti pernah dijalankan    11 dari 23
```

Satu angka dikeluarkan dari daftar ini: **"sumbangan snowline atas 20 bug
terakhir: 0 dari 20"**. Itu hasil pembacaan, bukan hasil menjalankan — lihat
BATASAN KESIMPULAN di atas. Ia dugaan terdidik, dan tidak boleh berdiri di
kolom yang sama dengan angka yang benar-benar diukur.

Dua angka terakhir yang paling menentukan. Seluruh lapisan `src/backend/services`
di `cbt_master` — 2.805 baris, 20 penjaga, 170 dari 260 kasus tes — dibangun
12-17 Agustus dengan **nol** jejak pemakaian snowline.

## Yang tidak akan berubah dengan usaha kita

- **Pembatalan cache karena susunan tool berubah.** Nyata, 83,8%, terukur.
  Sebabnya harness membongkar-pasang deferred tool di tengah sesi. Snowline
  tidak punya kuasa melarangnya. (T7)
- **Pemadatan otomatis** bisa dikendalikan dari luar — `DISABLE_AUTO_COMPACT`,
  `autoCompactEnabled`, `autoCompactWindow`, hook `PreCompact` — tetapi
  pemadatan bukan sebab yang ditemukan T7a. Kendalinya tidak menyentuh
  masalahnya. (T7b)
- **Satu celah yang tersisa dan ada di tangan PM:** susunan deferred tool
  ditentukan konfigurasi MCP. Server MCP yang dicabut-pasang di tengah sesi
  memecahkan cache. Menstabilkannya mengurangi pembatalan — tetapi itu
  keputusan konfigurasi, bukan perkakas yang bisa dibangun.

## Yang masih berdiri

Tiga hal, dan hanya tiga.

**1. `project_guardian` — pemindaian aktif. SUDAH DIUKUR 20-08.**

Dijalankan di `cbt_master`:

```
$ cd D:/AAAAAAAAA/cbt_master
$ python D:/AAAAAAAAA/open_source_agents/project_guardian/guardian.py

CRITICAL  9 temuan  ->  2 nyata   (78% positif palsu)
HIGH      5 temuan  ->  1 nyata, nilainya rendah
```

**Dua temuan nyata:** kunci API Groq yang sama di dua berkas —
`scripts/test_groq.js:13` dan `scripts/test_vision.js:18`. Yang kedua tidak
pernah ditemukan siapa pun, termasuk QA yang membaca kode berjam-jam sepanjang
sprint dan sudah menandai berkas pertama 12 hari sebelumnya.

**Tujuh temuan palsu, dari dua kelas saja:**
- Dokumentasi snowline sendiri (`SKILL.md:69` — contoh di dalam panduannya)
- Data contoh di berkas frontend: `{ nama: 'Budi', ... }` di modal impor,
  `setForm({ password: '' })` yang menginisialisasi form kosong,
  `data[0] || { nama: "AMANDA TRILOFA", password: "8BF278" }` untuk pratinjau

Temuan HIGH soal `.env.development` dan `.env.production` benar — keduanya
terlacak git — tetapi isinya diperiksa: nol baris memuat kunci atau sandi.

**Vonis:** 78% positif palsu. Literatur menyebut adopsi alat statis runtuh di
atas 20%; Google membidik 5% efektif. Empat kali lipat melewati ambang runtuh.
Dijalankan rutin, ia akan dimatikan dalam seminggu — nasib yang sama dengan
companion dan `scope_guardian`.

**Tetapi:** kedua temuan nyatanya kunci API hidup, dan tidak ada apa pun
sepanjang sprint ini yang menemukannya. Ini satu-satunya sinyal positif yang
bertahan setelah diukur.

**Yang menentukan bagi siapa pun yang melanjutkan:** seluruh derau berasal dari
dua kelas yang bisa dikecualikan — berkas dokumentasi dan data contoh di
frontend. Dibuang keduanya, positif palsunya 0 dari 2. Itu belum diuji, dan
itu perbedaan antara perkakas yang dimatikan dalam seminggu dan perkakas yang
dipakai terus.

Perhatikan juga bahwa nilainya tidak menuntut ia berupa toolkit. Satu pemindai
rahasia, dipasang sebagai pre-commit hook, mengikat tanpa bergantung pada
kesediaan agen memanggilnya — bersinggungan langsung dengan butir 2 di bawah.

**2. Penegakan lewat hook `PreToolUse`.** Satu-satunya permukaan yang benar-benar
mengikat di harness ini — keluar dengan kode 2 memblokir panggilan. Segala
aturan yang dipanggil atas keputusan agen sudah terbukti mati: companion (18
panggilan, berhenti 7 Agustus), `scope_guardian` (kunci basi sejak 6 Agustus,
padahal akan memblokir seluruh epik `panduanKoreksi.js` bila dipanggil sekali).

**3. Kebiasaan, bukan perkakas.** Yang benar-benar bertahan dari seluruh ini
adalah satu kalimat yang sudah PM rumuskan sendiri: *kekuatan sebuah aturan
sama dengan kekuatan pemeriksanya.* Commit `fe0d78f` di `cbt_master` —
pemeriksa deterministik di dalam aplikasi, bahasa aplikasi, repo aplikasi —
lahir dari standar itu, tanpa satu pun perkakas snowline.

## Peringatan untuk sesi yang meneruskan

Lima cacahan/klaim pada papan ini tidak bertahan saat diperiksa: jumlah
duplikat T5, cacah peristiwa T3, premis SQ, `cache_miss_reason` di T7a, dan
`DISABLE_PROMPT_CACHING` di T7b. Semuanya terdengar meyakinkan dan muncul tepat
ketika dibutuhkan detail yang mengunci cerita.

Aturan 1 di `README.md` ada untuk itu. Jangan longgarkan.

Dan satu hal yang bertahan justru karena diperiksa balik: temuan duplikasi
`msg_id` dari Gemini, yang menemukan kesalahan QA sendiri.
