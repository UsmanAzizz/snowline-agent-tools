# T5 Extension: Deduplikasi Analisis

## Sumber Data

File: `C:\Users\LENOVO\.claude\projects\D--AAAAAAAAA-cbt-master\abbd62e6-656c-4061-9d29-da2d728599bc.jsonl`
- Total baris di JSONL: 15,747

## Statistik Peristiwa

| Kategori | Jumlah |
|----------|--------|
| Queue Operations | 1,366 |
| User Messages | 3,612 |
| Assistant Messages | 5,912 |
| Attachment Events | 806 |
| - deferred_tools_delta | 19 |
| - agent_listing_delta | 6 |
| - mcp_instructions_delta | 6 |
| - skill_listing | 6 |
| Other Events | 4,051 |

## Payload Statistics (Semua ≥50 Karakter)

| Kategori | Peristiwa | Total Karakter |
|----------|-----------|----------------|
| Semua payload | 402 | 1,346,138 |
| Harness (attachment) | 116k events | 116,983 |
| User messages | ~ | 1,229,155 |

### Distribusi Ukuran (Semua Payload)

| Ukuran | Jumlah |
|--------|--------|
| >5,000 chars | 43 |
| 1,001-5,000 chars | 40 |
| 501-1,000 chars | 14 |
| 101-500 chars | 187 |
| 50-100 chars | 118 |

## Deduplikasi: Payload Identik ≥50 Karakter

### Ringkasan

| Metrik | Nilai |
|--------|-------|
| Unique payloads (duplikat ≥2x) | 7 |
| Total peristiwa dengan duplikat | 28 |
| Total karakter (termasuk duplikat) | 107,457 |
| **Penghematan potensial** | **79,748 karakter** |

### Breakdown: Harness vs LLM

| Sumber | Peristiwa | Penghematan Karakter |
|--------|-----------|---------------------|
| Harness (sinkronisasi) | 28 | 79,748 |
| LLM (injeksi konten) | 0 | 0 |

### Aturan Deduplikasi NON-DESTRUKTIF

**PRINSIP**: Cache yang sudah ada TIDAK diubah. Yang dicegah adalah penyuntikan ULANG teks identik.

```
Implementasi:

1. Maintain LRU cache of seen payloads:
   seen_payloads: Map[hash, dict]  # hash -> content, first_seen_line

2. Pada setiap peristiwa attachment baru:
   IF payload_hash IN seen_payloads:
       # Ganti dengan hash reference
       INJECT: {"type": "dedup_ref", "hash": payload_hash}
   ELSE:
       # Payload baru, simpan dan inject normal
       seen_payloads[payload_hash] = {"content": payload, "line": line_num}
       INJECT: payload

3. Hash reference format (32 chars SHA-256):
   {"type":"dedup_ref","hash":"a1b2c3d4e5f6..."}

4. Rekonstruksi di sisi consumer:
   IF event.type == "dedup_ref":
       content = cache_lookup(hash)  # lookup dari cache lokal
```

### Perbandingan dengan T2 (Ablasi)

| Aspek | T2 Ablasi | T5 Deduplikasi |
|-------|-----------|----------------|
| Efek pada cache | MERUSAK cache existing | NON-DESTRUKTIF |
| Risiko cache miss | TINGGI | TIDAK ADA |
| Karakter dihapus | 1,275,069 | 79,748 |
| Dampak biaya | +$10,738,90 | ~0 (cache stays intact) |

## Detail Payload Duplikat

### Top 20 Payload Identik Terbesar

| # | Hash | Count | Avg Chars | Total Chars | Avg Line | Type | Source |
|---|------|-------|-----------|-------------|----------|------|--------|
| 1 | `7838d7937ab3750c` | 5 | 10,855 | 54,275 | 7219 | skill_listing | Harness |
| 2 | `730ada2cf1578a17` | 3 | 6,714 | 20,142 | 8785 | deferred_tools_delta | Harness |
| 3 | `5dee5103d00a7f63` | 6 | 2,372 | 14,232 | 7326 | agent_listing_delta | Harness |
| 4 | `12fea8009f58b65d` | 2 | 5,714 | 11,428 | 1548 | deferred_tools_delta | Harness |
| 5 | `b9ae2bcaf6ee9ef6` | 6 | 1,078 | 6,468 | 7327 | mcp_instructions_delta | Harness |
| 6 | `ef7b39cb89574165` | 3 | 194 | 582 | 9793 | deferred_tools_delta | Harness |
| 7 | `4e7733f67bdadc94` | 3 | 110 | 330 | 13882 | deferred_tools_delta | Harness |

### Distribusi Duplikasi

```
Ukuran Payload (rerata):
  >5,000: 3 payloads
  1,001-5,000: 2 payloads
  501-1,000: 0 payloads
  101-500: 2 payloads
  50-100: 0 payloads

Count distribution:
  >10x: 0 payloads
  6-10x: 2 payloads
  3-5x: 4 payloads
  2x: 1 payloads

```

## Analisis Peristiwa TIDAK Bisa Di-Deduplikasi

### Mengapa LLM Injection Tidak Bisa Di-Deduplikasi?

1. **Variabilitas tinggi**: Konten dari LLM unik per situasi
2. **Konteks-dependent**: Même payload "mirip" bisa punya makna berbeda
3. **Risiko kehilangan informasi**: Deduplikasi kasar bisa menghilangkan nuansa

### Statistik LLM Injection

| Metrik | Nilai |
|--------|-------|
| Total peristiwa LLM | 369 |
| Karakter | 1,229,155 |

## Rekomendasi Implementasi

### Fase 1: Harness Deduplication (Aman)
- Target: `deferred_tools_delta`, `agent_listing_delta`, `skill_listing`
- Risiko: SATU
- Penghematan: ~79,748 karakter

### Fase 2: MCP Instructions Deduplication
- Target: `mcp_instructions_delta`
- Catatan: Beberapa MCP instructions mungkin genuinely unik
- Verifikasi: Cek cosine similarity >0.95 sebelum deduplicate

### Fase 3: Evaluasi
- Ukur cache hit rate
- Validasi tidak ada informasi yang hilang
- Benchmark latency

## Kesimpulan

1. **7 payload identik** ditemukan di 15,747 peristiwa
2. **Penghematan potensial: 79,748 karakter** dengan deduplikasi
3. **Harness menyumbang 100.0%** dari penghematan jika diterapkan
4. **T5 TIDAK merusak cache** (berbeda dengan T2 ablasi)
5. Implementasi aman dimulai dari harness sync payloads

## Perintah Reproduksi

```bash
cd D:\AAAAAAAAA\cbt_master
python t5_extension.py
```

Atau langsung lihat bukti:
```bash
cat D:\AAAAAAAAA\open_source_agents\.here_we_are\bukti\T5_BUKTI.md
```
