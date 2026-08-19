# Apa yang masih berdiri

Disusun QA, 20 Agustus 2026, setelah delapan tugas selesai.

Halaman ini menyatukan temuan lintas tugas. Bukan rencana — tidak ada rencana
di folder ini, karena tidak ada yang selamat dari pengukuran. Bacalah sebagai
laporan lahan: apa yang sudah dibersihkan, dan apa yang masih tegak.

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

**1. `project_guardian` — pemindaian aktif.** Satu-satunya perkakas yang
terbukti menemukan sesuatu yang terlewat manusia: kunci API ter-commit,
ditemukan dalam 30 detik setelah pembacaan kode 12 jam melewatkannya. Ini
kebalikan dari seluruh arah lain — bukan menghemat, melainkan menemukan.
**Belum pernah diukur dengan benar.**

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
