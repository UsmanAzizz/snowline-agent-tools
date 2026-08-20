# Apa yang masih berdiri

Disusun QA, 20 Agustus 2026, setelah delapan tugas selesai.

Halaman ini menyatukan temuan lintas tugas. Bukan rencana — tidak ada rencana
di folder ini, karena tidak ada yang selamat dari pengukuran. Bacalah sebagai
laporan lahan: apa yang sudah dibersihkan, dan apa yang masih tegak.

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

## Bentuk seluruh sprint

Delapan tugas dijalankan. **Tujuh bertanya "apakah X layak dibunuh", dan
semuanya dijawab ya.** Satu-satunya tugas afirmatif — T7 — menemukan sesuatu
yang nyata dan masif, lalu menyimpulkan itu bukan milik kita.

Itu bukan kegagalan sprint. Itu hasilnya.

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
sumbangan snowline atas 20 bug terakhir   0 dari 20
perkakas tanpa bukti pernah dijalankan    11 dari 23
```

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
