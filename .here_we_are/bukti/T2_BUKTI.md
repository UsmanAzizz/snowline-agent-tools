# Bukti T2 - Analisis Cache Prompt

## Sumber Data

File: `C:\Users\LENOVO\.claude\projects\D--AAAAAAAAA-cbt-master\abbd62e6-656c-4061-9d29-da2d728599bc.jsonl`
- Total baris: 15.747
- Baris dengan usage: 5.893

## Tarif API

Sumber: https://platform.claude.com/docs/en/docs/build-with-claude/prompt-caching

Model: `claude-opus-5` (dikonfirmasi dari session trace)

| Jenis Token | Harga ($/juta) | Kelipatan |
|-------------|----------------|-----------|
| Input (base) | $5.00 | 1x |
| Cache Read | $0.50 | 0.1x |
| Cache Write 5m | $6.25 | 1.25x |
| Cache Write 1h | $10.00 | 2x |
| Output | $25.00 | - |

## Perintah Reproduksi

```bash
# Jalankan analisis lengkap
cd D:\AAAAAAAAA\cbt_master
python t2_complete_analysis.py

# Atau analisis individual
python analyze_t2.py
python analyze_t2_spikes.py
```

## Data Token yang Dihasilkan

```
cache_read_input_tokens:      3.006.412.128 (3006,41 juta)
cache_creation_input_tokens:    59.117.589 (59,12 juta)
  - 1h TTL:                     59.049.867 (99,9%)
  - 5m TTL:                         67.722 (0,1%)
output_tokens:                    6.285.003 (6,29 juta)
input_tokens:                        48.800 (0,05 juta)
```

## Perbandingan Biaya

| Kondisi | Biaya (USD) |
|---------|-------------|
| Dengan Cache | $2.251,25 |
| Tanpa Cache | $15.485,02 |
| **Penghematan** | **$13.233,76 (85,5%)** |

## Breakdown Biaya dengan Cache

| Komponen | Biaya | % |
|----------|-------|---|
| Cache Read | $1.503,21 | 66,8% |
| Cache Write 1h | $590,50 | 26,2% |
| Cache Write 5m | $0,42 | 0,0% |
| Output | $157,13 | 7,0% |

## Lonjakan Cache Creation

Klasifikasi:
- Very High (>100k): 95 events
- High (20k-100k): 24 events
- Moderate (5k-20k): 190 events
- Total spikes: 309 events

Top 5 lonjakan terbesar:
1. Line 14415: 952.139 tokens (prompt: "apakah ada yang belum kita kerjakan")
2. Line 14416: 952.139 tokens
3. Line 14417: 952.139 tokens (dengan tool Read)
4. Line 14403: 948.279 tokens (prompt: "itu memang nilai lama...")
5. Line 14404: 948.279 tokens (dengan tool Write)

Pola yang teridentifikasi:
- Lonjakan >900k terjadi saat pergantian task/session
- Lonjakan ~25k saat membaca banyak file dokumentasi
- Lonjakan ~21k saat menganalisis error logs

## Dampak Prospektif Ablasi

Data baseline (dari T6 korpus cbt_master):
- Total karakter populasi: 3.392.349
- Penghematan kotor ablasi: 1.275.069 karakter (37,6%)

Jika ablasi diterapkan secara prospektif:
- Karakter yang berubah: ~1.275.523 (37,6%)
- Cache read terpengaruh: 1.130.410.960 token (37,6% dari cache read)
- Biaya tambahan prospektif: $10.738,90

Analisis:
- Biaya cache read yang dihemat: $565,21
- Biaya cache write baru: $11.304,11
- NET CHANGE: +$10.738,90 (PENAMBAHAN biaya)

## Struktur cache_creation Object

Sample dari baris 9:
```json
{
  "input_tokens": 10719,
  "cache_creation_input_tokens": 10719,
  "cache_read_input_tokens": 0,
  "output_tokens": 512,
  "server_tool_use": {...},
  "service_tier": "pro",
  "cache_creation": {
    "ephemeral_1h_input_tokens": 10719,
    "ephemeral_5m_input_tokens": 0
  },
  "inference_geo": "id",
  "iterations": 1,
  "speed": "high"
}
```

## Kesimpulan

1. Cache memberikan penghematan 85,5% ($13.233 dari $15.485)
2. 98%+ token input adalah cache read (murah)
3. Ablasi karakter akan MENAMBAH biaya $10.738,90 (tidak sebanding dengan manfaat)
4. Semua cache creation menggunakan TTL 1-jam (99,9%)
5. Rasio biaya: cache write 1h = 20x biaya cache read
