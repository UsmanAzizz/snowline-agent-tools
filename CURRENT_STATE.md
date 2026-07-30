# CURRENT STATE - Phase 3

**Last Updated:** 2026-07-30  
**Scope:** Companion Layer ONLY  
**Principle:** Agent = Decision Maker, Companion = Data Processor

---

## Prinsip Dasar

```
ALUR YANG DIHARAPKAN:

User Input
    ↓
Companion.analyze_intent() → {data terstruktur}
    ↓
Agent MEMBACA data, agent YANG MEMUTUSKAN
    ↓
Tools dieksekusi oleh Agent
```

**Companion = OCR** — transformasi data, bukan pengambilan keputusan.

---

## Phase 3 Goal

**Refactor companion menjadi pure data processor**

---

## Data Structure Target

```python
@dataclass
class AnalyzeResult:
    input: str                       # original input
    keywords: List[str]              # keyword yang terdeteksi
    entities: List[str]              # entitas (filename, function, dll)
    specificity: str                 # "high" | "medium" | "low"
    confidence_level: str            # "HIGH" | "MEDIUM" | "LOW" | "NONE"
    
    # Tool signals (bukan keputusan)
    single_tool: ToolMatch | None
    sequential_steps: List[ToolMatch] | None
    
    # Clarification
    needs_clarification: bool
    clarification_note: str | None

@dataclass
class ToolMatch:
    name: str                       # tool identifier
    confidence: str                 # "high" | "medium" | "low"
    reason: str                     # kenapa cocok
    command_template: str           # command preview
    safety: str                     # "safe" | "moderate"
```

---

## Agent Decision Matrix

| Confidence | Specificity | Agent Action |
|------------|-------------|-------------|
| HIGH | high | **Execute** (WAJIB ikut rekomendasi) |
| MEDIUM | any | **Konfirmasi** ke user |
| LOW | any | **Clarify** - tanya maksud spesifik |
| NONE | low | **Abort** - cannot proceed |

---

## Tool Categories

### Write Tools (Needs Approval)
- smart_replace
- auto_scaffolder
- context_mapper
- import_fixer

### Read Tools (Safe - No Approval)
- smart_search
- selective_reader
- project_guardian
- clean_sweeper
- deep_analyzer
- crash_decoder
- impact_analyzer
- scope_guardian
- smart_tree
- token_budget
- context_curator
- output_formatter
- decision_validator

---

## Scope Lock

**SCOPE: companion/ folder ONLY**

```
Dilarang mengubah:
- .agents/skills/ (tools apapun)
- Other project files
- Architecture lain di luar companion

Boleh berubah:
- companion/companion_core.py
- companion/__init__.py
- companion/api.py
- companion/cli.py
- companion/memory.py
- companion/tool_registry.py
```

---

## Checklist Selesai (Phase 3)

- [ ] Revise analyze_intent() → return structured data dengan confidence
- [ ] Update plan_steps() atau integrate ke analyze_intent
- [ ] Update tool_registry.py dengan confidence scoring
- [ ] Update semua caller (cli.py, api.py, __init__.py)
- [ ] Update tests/test_approval.py
- [ ] Live-test: 10 scenario
- [ ] Bukti akurasi routing meningkat

---

## Celah Ditemukan (Catat, Jangan Kerjakan Sekarang)

- [ ] companion.py vs companion_core.py duplication
- [ ] executor.py ada tapi tidak digunakan secara optimal
- [ ] Memory learning loop belum teruji

---

## Constraints yang Dijaga

1. **NO autonomous execution** — TASK 7 principle preserved
2. **Companion tidak pernah execute** — hanya return data
3. **Agent yang decision maker** — companion cuma processor
4. **Backward compatibility** — existing tools tetap jalan

---

## Finish Line

Phase 3 SELESAI kalau:
1. analyze_intent() return structured data (keywords, entities, confidence, tools)
2. 10 scenario tested dengan bukti akurasi meningkat
3. Agent decision matrix working correctly
4. TASK 7 principle preserved (no autonomous execution)

**Tidak perlu sempurna — 10 scenario bukti improvement就够了.**

---

*Generated: 2026-07-30*
