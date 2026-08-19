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
keberatan itu tidak berlaku, karena payload-nya milik sendiri.

## Pemeriksaan lanjutan — 20-08, atas permintaan PM

**Keberatan T7 memang TIDAK berlaku untuk keduanya.** Keduanya menyusun payload
API secara langsung. Siapa yang menyusun payload, dia yang memiliki awalan.
Harness tidak ikut campur. Pintu itu nyata.

Tetapi tiga hal ditemukan saat diperiksa.

### 1. Keduanya tidak nyambung

```
$ python -c "... GoldenPayloadBuilder -> AnthropicAdapter ..."
kunci keluaran golden_payload : ['system_context', 'tools', 'user_message']
setelah lewat AnthropicAdapter: ['system_context', 'tools', 'user_message']
cache_control tersuntik?      : False
```

Adapter memeriksa `if "system" in payload`. Builder mengeluarkan
`system_context`, bukan `system`. Syaratnya tidak pernah terpenuhi, adapter
tidak melakukan apa-apa. **`cache_control` tidak pernah tersuntik.**

Dua prototipe yang dimaksudkan berpasangan, tidak berpasangan.

### 2. Pembuktian `golden_payload` melingkar

`__main__`-nya membangun dua payload dari builder yang SAMA dengan
`raw_code` dan `tools_dict` yang sama, lalu membuktikan bagian bersamanya
identik. Itu `json.dumps(x) == json.dumps(x)`.

Ia tidak menguji apa pun tentang kestabilan awalan. Untuk menguji itu,
payload kedua harus dibangun dari masukan yang **berbeda urutannya** —
misalnya `tools_dict` dengan urutan kunci teracak — lalu dibuktikan hasil
serialisasinya tetap identik.

Dan pengurutan yang menentukan justru terjadi di `json.dumps(..., sort_keys=True)`
milik berkas ujinya, bukan di builder.

Gagasannya benar — urutan stabil menghasilkan awalan stabil, dan itu memang
penyakit yang T7 temukan. Kodenya belum membuktikannya.

### 3. TTL-nya keliru untuk sesi panjang

```python
payload["system"][-1]["cache_control"] = {"type": "ephemeral"}
```

Nama dan bentuk fieldnya benar — ini memang mekanisme API yang sesungguhnya.
Tetapi `ephemeral` tanpa keterangan berarti TTL 5 menit. T2 mengukur Claude
Code memakai TTL 1 jam untuk **99,9%** cache creation-nya. Untuk sesi kerja
panjang, 5 menit adalah setelan yang salah; perlu `"ttl": "1h"` eksplisit.

## Yang menentukan, dan bukan urusan QA

Untuk memakai keduanya, snowline harus memanggil API sendiri — artinya
menjadi gelung agennya sendiri, bukan perkakas yang membantu Claude Code.

Itu wilayah orkestrator, dan proyek ini sudah pernah menolaknya sebagai
scope inflation. Survei lanskap 19-08 juga menyimpulkan ruang itu tertutup.

**Pintunya nyata dan tidak terhalang keberatan T7. Tetapi ia terbuka ke
ruangan yang sudah disurvei dan dinyatakan penuh.**

Keputusan apakah tetap masuk ke situ ada di PM, bukan QA.

## Catatan lingkup

`README.md` folder induk menyatakan `.here_we_are` adalah catatan pengukuran,
bukan tempat merancang fitur. Prototipe ini melanggar lingkup itu.

QA mencatat, tidak menghapus. Keputusan ada di PM.
