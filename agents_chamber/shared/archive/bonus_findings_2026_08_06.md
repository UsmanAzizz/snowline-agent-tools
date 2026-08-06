# QA Bonus Findings — August 2026
*Diarsipkan oleh `pos/2. QA`, 06 Agustus 2026.*
*Temuan dari eksekusi langsung 3 gap yang PM angkat.*

---

## Finding #1 — Real Usage Accuracy: NOT MEASURABLE

**Status:** Design gap, bukan bug.

memory.json shows `history: []` — tidak ada real usage data tersimpan di companion. Tidak ada file log, tidak ada prompt history.

**Implikasi:** Tidak bisa mengukur akurasi companion terhadap prompt nyata tanpa data. Companion tidak mencatat prompt yang masuk ke log/history.

**Rekomendasi:** Jika akurasi mau diukur, perlu tambahkan logging ke companion (simpan setiap prompt + hasil ke file). Tapi ini perubahan design, bukan bug fix.

---

## Finding #2 — Hardcoded Keywords: 137 Total, 1 Typo Bug

**Total count per tool:**
| Tool | Keywords |
|------|---------|
| clean_sweeper | 20 |
| smart_replace | 15 |
| smart_search | 12 |
| deep_analyzer | 11 |
| project_guardian | 11 |
| selective_reader | 10 |
| impact_analyzer | 10 |
| crash_decoder | 10 |
| smart_tree | 7 |
| scope_guardian | 7 |
| auto_scaffolder | 6 |
| db_extractor | 6 |
| context_mapper | 6 |
| import_fixer | 6 |
| **TOTAL** | **137** |

*Catatan: PM bilang 157. Kemungkinan salah hitung atau termasuk field lain (command_template, dll). 137 adalah angka dari source live.*

**Typo bug found:**
`scope_guardian` keywords: `["scope", "area", "batass", "batasan", "limits", "di area", "seluruh"]`

**"batass" = typo dari "batasan"**

Test:
```
"batass scope"  -> Keywords: ['area']     <- matched by "scope", NOT "batass" ❌
"batass area"   -> Keywords: ['area']     <- matched by "area",  NOT "batass" ❌
"batasan"       -> Keywords: ['batasan']  <- correct ✅
```

"batass" ada di **live AND template** — perlu fix.

**Redundancy note (bukan bug):** Beberapa tools punya banyak keywords (clean_sweeper=20, smart_replace=15) — ini boleh jadi disengaja untuk fleksibilitas bilingual. Tidak ada keyword duplikat antar-tools.

---

## Finding #3 — EXECUTE: Not Dead Code

EXECUTE действительно triggers. Confirmed:

```
"generate component ProductCard" -> Action: EXECUTE ✅
```

EXECUTE butuh: `confidence_level="HIGH"` + `specificity="high"` + `needs_clarification=False`.
Ini narrow path — butuh 1 entity + 1 HIGH-confidence tool match + tidak ada multi-match/clarification trigger.
Bukan dead code. Sudah dipakai.

---

## ACTION ITEMS

| # | Severity | Action |
|---|----------|--------|
| F-B1 | Low (typo) | Fix "batass" → "batasan" di `core_intent.py` (live + template sync) |
| F-B2 | Design gap | Tambahkan usage logging ke companion jika akurasi mau diukur |

F-B1 bisa langsung fix. F-B2 perlu diskusi desain dulu.
