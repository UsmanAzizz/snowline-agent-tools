# Penilaian QA atas v2_prototypes

Diperiksa 20 Agustus 2026. Pertanyaannya satu: **apakah prototipe ini
bergantung pada hipotesis penghematan token yang sudah gugur?**

Latar: T2r mengukur pemangkasan konteks menghemat 3,1% — jauh di bawah ambang
15%. Hipotesis mati. Pertanyaannya lalu, berapa banyak dari prototipe ini yang
ikut runtuh bersamanya.

**Jawabannya: sebagian besar tidak. Dua di antaranya justru mengasumsikan
kebalikannya.**

Dugaan awal QA sendiri keliru dan dicatat di sini apa adanya.

| berkas | bergantung hipotesis mati? | catatan |
|---|---|---|
| `golden_payload_poc.py` | **Tidak — kebalikannya** | Menyusun konteks stabil jadi satu blok sistem. Ramah cache, bukan memangkas. Sejalan dengan temuan T2 bahwa cache menghemat 85,5% |
| `agnostic_adapter_poc.py` | **Tidak — kebalikannya** | Menyuntikkan `cache_control` ke blok sistem terakhir. Eksplisit sadar cache |
| `silent_parser_poc.py` | Tidak | Mengurai JSON dari keluaran model. Tak berhubungan dengan konteks |
| `knip_wrapper_poc.py` | Tidak | Membungkus knip untuk dependensi tak terpakai |
| `semgrep_wrapper_poc.py` | Tidak | Membungkus semgrep |
| `run_v2_simulation.py` | Tidak | "Mencegah infinite loop LLM" — benang aturan berhenti, bukan hemat token |
| `snowline_core_v2.py` | Tidak | Perakit komponen |
| `delta_firewall_poc.py` | **Mungkin — dan kini terjawab** | Lihat di bawah |

## `delta_firewall_poc.py` — terjawab, dan tidak berguna

Membuang muatan berulang lewat hashing setelah menanggalkan timestamp dan UUID.
Itu memang pengurangan konteks, tetapi jenisnya beda dari yang dibunuh T2: ia
membuang duplikat yang datang **belakangan**, bukan mengubah bagian **awal**
konteks. Awalan utuh, jadi cache-nya selamat.

Aman — tetapi tidak ada bahannya. T5r mengukur seluruh korpus:

```
salinan berlebih  :     2      (papan sebelumnya menulis 32)
karakter berlebih : 6.195      (papan sebelumnya menulis 132.261)
                  = 0,00005% dari cache read sesi
```

Aman terhadap cache, dan menghemat seperseratus ribu. Tidak ada yang menentang
keberadaannya; juga tidak ada alasan menjalankannya.

## Dua yang layak diperhatikan sesi berikutnya

`golden_payload_poc.py` dan `agnostic_adapter_poc.py` adalah satu-satunya kode
di seluruh folder ini yang bergerak **searah** dengan angka terbesar yang
diukur sprint ini — cache menghemat 85,5% biaya sesi.

Keduanya belum dievaluasi. QA tidak mengevaluasinya karena itu perumusan arah,
bukan pemeriksaan.

Satu keberatan yang harus dijawab lebih dulu oleh siapa pun yang melanjutkannya:
T7 menemukan pembatalan cache disebabkan harness membongkar-pasang tool-nya
sendiri, dan menyimpulkan skrip di luar tidak bisa mencegahnya. Kalau prototipe
ini menyusun payload untuk API secara langsung — bukan lewat Claude Code —
keberatan itu tidak berlaku, karena payload-nya milik sendiri. **Perbedaan itu
menentukan, dan belum diperiksa.**

## Catatan lingkup

`README.md` folder induk menyatakan `.here_we_are` adalah catatan pengukuran,
bukan tempat merancang fitur. Prototipe ini melanggar lingkup itu.

QA mencatat, tidak menghapus. Keputusan ada di PM.
