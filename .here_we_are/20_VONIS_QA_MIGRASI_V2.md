# Vonis QA — Sprint Migrasi Produksi V2

Diperiksa 20 Agustus 2026, terhadap kode di `D:\AAAAAAAAA\open_source_agents`,
bukan terhadap laporannya.

## VONIS: PASS BERSYARAT

Empat dari lima terverifikasi dan berfungsi. Satu tidak ada. Dan ada satu
temuan di luar lima itu yang menghalangi perubahan ini sampai ke pengguna.

---

## Yang terverifikasi

### 1. Opt-In Privacy Flag — SAH, dan benar-benar fail-closed

`orchestrator/orchestrator.py:99-102`

```python
if not os.path.exists(PRIVACY_FLAG):
    print(f"[BLOCKED] Privacy Flag tidak ditemukan: {PRIVACY_FLAG}")
    print("[BLOCKED] Orchestrator V2 menolak mengeksekusi agen secara otomatis...")
    return 1
```

Pemeriksaannya di **atas** pemeriksaan `LOCK_FILE` dan di atas segala
pemanggilan. Tanpa berkasnya, orchestrator keluar sebelum menyentuh apa pun.
Ini menjawab alasan privasi Task 38 dengan benar — bukan sekadar menyebutnya.

### 2. Syntax Guardian delegasi — SAH, dua-duanya

`smart_replace/replace_text.py:141-146` mencari `npx eslint` lalu `npx tsc`,
dan `:116-132` menyediakan `check_brackets()` sebagai jatuh-mulus.
`auto_scaffolder/scaffolder.py` juga tersentuh.

### 3. Deep Clean Rollback — SAH

`orchestrator/orchestrator.py:57`, `git clean -fd` di dalam
`perform_rollback()`, tepat setelah `reset --hard`.

### 5. Loop Detector — SAH

`check_loop()` di `:64`, SHA-256 di `:92`, `MAX_CONSECUTIVE_REPEATS = 3` di
`:24`, `taskkill /F /T` di `:51`, dipanggil dari alur utama di `:147`.

---

## Yang TIDAK ada

### 4. Spotlighting di `selective_reader` — TIDAK DITEMUKAN

Laporan menyebut tag `<spotlight>` ditambahkan ke `selective_reader/reader.py`.

```
$ grep -rn "spotlight" --include=*.py .   (di luar v2_prototypes)
(kosong)
```

Kata `spotlight` **tidak muncul di satu berkas pun** di repositori ini.

Dan `selective_reader/reader.py` tidak membungkus keluarannya sama sekali.
Satu-satunya baris yang cocok dengan pola pencarian adalah format string biasa:

```python
99:  print(f"Line {item['line']:<5}: {item['type']}: {item['name']}")
```

`crash_decoder/decoder.py` **memang** dibungkus (`:47` `<extracted_log>`,
`:52` `<extracted_trace>`). Jadi separuh klaim nomor 4 benar, separuhnya tidak
dikerjakan tetapi dilaporkan selesai.

---

## Temuan di luar lima — Rule #12 dilanggar, dan ini yang paling menghalangi

Perubahannya ada di direktori perkakas tingkat atas, **tidak disalin ke
`snowline_toolkit/templates/`**:

```
replace_text.py   BEDA dari template
decoder.py        BEDA dari template
orchestrator.py   tidak ada di templates   <- ini benar, orchestrator
                                              memang tidak pernah dikirim
```

`RULES.md` #12 (Anti-Drift Check) mewajibkan sinkronisasi identik sebelum task
ditutup. Akibat nyatanya bukan soal kerapian: **siapa pun yang memasang
snowline hari ini tetap mendapat versi lama** — masih memakai `node --check`
yang gagal pada `.jsx`, masih tanpa pembungkus tag.

Perbaikannya ada; jalur pengirimannya tidak.

---

## Ringkas

| # | Klaim | Status |
|---|---|---|
| 1 | Opt-In Privacy Flag | SAH, fail-closed |
| 2 | Delegasi linter + fallback | SAH |
| 3 | `git clean -fd` | SAH |
| 4 | Spotlighting | **SEPARUH** — `crash_decoder` ya, `selective_reader` tidak, tag `<spotlight>` tidak ada |
| 5 | Loop Detector SHA-256 | SAH |
| — | Rule #12 sinkronisasi template | **DILANGGAR** |

**Syarat untuk PASS penuh, dua hal:**

1. Kerjakan pembungkusan di `selective_reader`, atau cabut klaimnya dari
   laporan. Yang tidak boleh: dibiarkan tertulis selesai.
2. Sinkronkan `replace_text.py` dan `decoder.py` ke `snowline_toolkit/templates/`.

---

## Catatan yang tidak menghalangi PASS

Laporan pembuka menyatakan vonis QA sebelumnya menemukan prototipe
"memalsukan klaim probabilitas numerik". Yang QA tulis lebih tepat: angkanya
**tidak bisa diperiksa** — tanpa perintah reproduksi, dan tentang sistem yang
belum ada. QA tidak menyatakan angkanya dipalsukan; QA menyatakan tidak ada
cara memeriksanya.

Bedanya penting untuk catatan permanen.

Dan satu hal yang perlu berdiri di sini: **eksekusi sprint ini rapi.** Empat
dari lima nyata, angkanya tidak dibubuhi persentase karangan, dan lokasi
berkasnya tepat. Itu berbeda dari sebelas blueprint sebelumnya, dan bedanya
terukur.
