# Snowline Portable Agentic OS - Technical Specification

**Version:** 1.0 (Production Ready)  
**Status:** Blueprint → Phase 1 Development  
**Date:** July 2025  
**Philosophy:** Like snowflakes gently flowing into a child's hands — never forcing, always guiding.

---

## 📋 Executive Summary

**Snowline** adalah **Portable Agentic Operating System** yang berfungsi sebagai **lapis pengaman & asisten** (companion layer) untuk AI agents. Snowline bukan framework baru, tetapi **middleware yang dapat dipasang di mana saja** — bekerja dengan Claude, GPT-4, Gemini, atau LLM apapun.

**Tujuan Utama:**
- ✅ Agents bekerja lebih aman (guardrails)
- ✅ Agents berpikir lebih baik (guidance)
- ✅ Agents menghemat tokens (efficiency)
- ✅ Agents punya partner yang dapat dipercaya (companionship)

---

## 🎯 Positioning: Companion Layer, Bukan Framework

Landscape Before Snowline:
```
┌─────────────────────┐
│ LangChain           │ ← Framework untuk orchestration
│ AutoGen             │ ← Framework untuk multi-agent
│ Semantic Kernel     │ ← Framework untuk skill management
└─────────────────────┘
```

Landscape With Snowline:
```
┌─────────────────────┐
│ Any LLM Agent       │
├─────────────────────┤
│ SNOWLINE LAYER ⭐   │ ← Companion, Safety, Guidance
├─────────────────────┤
│ LangChain / AutoGen │
├─────────────────────┤
│ LLM Provider        │
└─────────────────────┘
```

**Keuntungan positioning ini:**
- Tidak ada lock-in: bisa pasang di framework apa saja
- Komplementer: tidak bersaing, melengkapi
- Portable: copy-paste ke proyek manapun
- Independent: bisa run standalone atau integrated

---

## 🏗️ Arsitektur: 4 Core Domain (MVP Focus)

**Workflows dipindahkan ke Phase 3+ (tidak di MVP)**

Agent Request (OpenAI Function Call Protocol)
↓
```
┌─────────────────────────────────────────┐
│ SNOWLINE COMPANION OS (Phase 1-2)       │
├─────────────────────────────────────────┤
│                                         │
│ DOMAIN 1: SYSTEM                        │
│ ├─ Tool Registry & Discovery            │
│ ├─ Configuration Management             │
│ ├─ Environment Validation               │
│ └─ State Manager (SQLite)               │
│                                         │
│ DOMAIN 2: ACTIONS                       │
│ ├─ Smart Replace (atomic, safe)         │
│ ├─ Deep Analyzer (read-only)            │
│ ├─ Impact Analyzer (prediction)         │
│ └─ Tool Execution Engine                │
│                                         │
│ DOMAIN 3: CHECKS                        │
│ ├─ Safety Validator                     │
│ ├─ Risk Assessor                        │
│ ├─ Compliance Checker                   │
│ └─ Guidance Generator                   │
│                                         │
│ DOMAIN 4: CONTEXT (Phase 2)             │
│ ├─ Agent Memory (episodic, semantic)    │
│ ├─ Project Context Cache                │
│ └─ Knowledge Base                       │
│                                         │
└─────────────────────────────────────────┘
```
↓ Structured Response + Guidance
↓ Agent Decision (Claude/GPT harus respect guidance)

---

## 🛠️ Domain 1: SYSTEM (Foundation)

**Tanggung Jawab:** Registry, konfigurasi, state management

### Tool Registry

```python
class ToolRegistry:
    """Semua tools terdaftar di sini"""
    
    def register(self, tool_def: ToolDefinition):
        """Daftarkan tool dengan JSON schema"""
        pass
    
    def discover(self, category: str = None) -> List[Tool]:
        """Temukan tools berdasarkan kategori"""
        pass
    
    def get_schema(self, tool_name: str) -> dict:
        """Ambil JSON schema untuk agent"""
        pass
```

### State Manager (Game Changer)

```python
import sqlite3
import json
import uuid
from datetime import datetime

class StateManager:
    """
    Pengelola state persistent untuk Snowline.
    Ini yang membuat Snowline menjadi "OS" bukan hanya script.
    """
    
    def __init__(self, db_path: str = "./.snowline/state.db"):
        self.db_path = db_path
        self.db = sqlite3.connect(db_path)
        self.current_execution_id = None
        self._init_schema()
    
    def _init_schema(self):
        """Setup database schema"""
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS executions (
                id TEXT PRIMARY KEY,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                status TEXT,
                tool_name TEXT,
                agent_id TEXT,
                request_params JSON
            );
            
            CREATE TABLE IF NOT EXISTS artifacts (
                id TEXT PRIMARY KEY,
                execution_id TEXT,
                artifact_type TEXT,
                data JSON,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(execution_id) REFERENCES executions(id)
            );
            
            CREATE TABLE IF NOT EXISTS agent_memory (
                id TEXT PRIMARY KEY,
                agent_id TEXT,
                memory_type TEXT,
                content JSON,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                ttl_seconds INTEGER
            );
        """)
        self.db.commit()
    
    def start_execution(self, exec_id: str, tool_name: str, agent_id: str = None):
        """Tandai eksekusi dimulai"""
        self.current_execution_id = exec_id
        self.db.execute(
            """INSERT INTO executions (id, status, tool_name, agent_id, request_params)
               VALUES (?, ?, ?, ?, ?)""",
            (exec_id, "started", tool_name, agent_id, "{}")
        )
        self.db.commit()
    
    def save_artifact(self, artifact_type: str, data: dict) -> str:
        """
        Simpan hasil eksekusi (backup, preview, dll).
        Ini yang memungkinkan rollback bekerja.
        """
        artifact_id = str(uuid.uuid4())
        self.db.execute(
            """INSERT INTO artifacts (id, execution_id, artifact_type, data)
               VALUES (?, ?, ?, ?)""",
            (artifact_id, self.current_execution_id, artifact_type, json.dumps(data))
        )
        self.db.commit()
        return artifact_id
    
    def get_artifact(self, artifact_id: str) -> dict:
        """Ambil artifact dari eksekusi sebelumnya"""
        result = self.db.execute(
            "SELECT data FROM artifacts WHERE id = ?",
            (artifact_id,)
        ).fetchone()
        return json.loads(result[0]) if result else None
    
    def memorize(self, agent_id: str, memory_type: str, content: dict, ttl_seconds: int = 3600):
        """Simpan ke agent memory (dengan auto-expire)"""
        memory_id = str(uuid.uuid4())
        self.db.execute(
            """INSERT INTO agent_memory (id, agent_id, memory_type, content, ttl_seconds)
               VALUES (?, ?, ?, ?, ?)""",
            (memory_id, agent_id, memory_type, json.dumps(content), ttl_seconds)
        )
        self.db.commit()
    
    def recall(self, agent_id: str, memory_type: str, limit: int = 5) -> list:
        """Ambil memory dari history"""
        results = self.db.execute(
            """SELECT content FROM agent_memory 
               WHERE agent_id = ? AND memory_type = ?
               ORDER BY created_at DESC LIMIT ?""",
            (agent_id, memory_type, limit)
        ).fetchall()
        return [json.loads(r[0]) for r in results]
```

---

## 🎯 Domain 2: ACTIONS (Tool Execution)
**Tanggung Jawab:** Eksekusi tool dengan aman

### 5 Core Tools (MVP)

**Tool 1: Smart Replace**
```json
{
  "tool_id": "smart_replace",
  "name": "Smart Replace",
  "category": "execution",
  "token_cost": 200,
  "safety_level": "guarded",
  "features": [
    "Dry-run preview",
    "Automatic backup",
    "Rollback plan",
    "Git integration"
  ]
}
```

**Tool 2: Deep Analyzer**
```json
{
  "tool_id": "deep_analyzer",
  "name": "Deep Analyzer",
  "category": "analysis",
  "token_cost": 300,
  "safety_level": "safe",
  "features": [
    "Code flow analysis",
    "Dependency mapping",
    "Complexity measurement",
    "Anti-pattern detection"
  ]
}
```

**Tool 3: Impact Analyzer**
```json
{
  "tool_id": "impact_analyzer",
  "name": "Impact Analyzer",
  "category": "analysis",
  "token_cost": 250,
  "safety_level": "safe",
  "features": [
    "Change impact prediction",
    "Risk assessment",
    "Affected systems mapping",
    "Rollback planning"
  ]
}
```

**Tool 4: Project Guardian**
```json
{
  "tool_id": "project_guardian",
  "name": "Project Guardian",
  "category": "validation",
  "token_cost": 150,
  "safety_level": "guarded",
  "features": [
    "Pattern enforcement",
    "Standard validation",
    "Consistency checking"
  ]
}
```

**Tool 5: Scope Guardian**
```json
{
  "tool_id": "scope_guardian",
  "name": "Scope Guardian",
  "category": "validation",
  "token_cost": 120,
  "safety_level": "guarded",
  "features": [
    "Scope boundary checking",
    "Out-of-scope detection",
    "Scope recommendations"
  ]
}
```

---

## 🛡️ Domain 3: CHECKS (Safety & Guidance)
**Tanggung Jawab:** Validasi, risk assessment, guidance generation

### Safety Validator
```python
class SafetyValidator:
    """Pastikan aksi tidak berbahaya"""
    
    def validate(self, action: Action) -> SafetyResult:
        checks = [
            self.check_destructive(),
            self.check_boundaries(),
            self.check_permissions(),
            self.check_backup_exists(),
        ]
        
        # Combine results
        return SafetyResult(
            safe=all(c.passed for c in checks),
            risks=[c.message for c in checks if not c.passed]
        )
```

### Risk Assessor
```python
class RiskAssessor:
    """Hitung risk score (0-100)"""
    
    def score(self, action: Action) -> RiskScore:
        factors = {
            "scope_size": self.count_affected_items(action),
            "rollback_ability": self.check_rollback_plan(action),
            "test_coverage": self.check_tests(action),
            "impact_radius": self.estimate_impact(action)
        }
        
        score = self.calculate_weighted_score(factors)
        return RiskScore(
            score=score,
            level="low" if score < 30 else "medium" if score < 70 else "high"
        )
```

### Guidance Generator
```python
class GuidanceGenerator:
    """Generate structured guidance untuk agent"""
    
    def generate(self, validation: SafetyResult, risk: RiskScore) -> Guidance:
        if not validation.safe or risk.level == "high":
            return Guidance(
                action="abort",
                reason=f"Risk score {risk.score}, tidak aman",
                suggestions=["Kurangi scope", "Tambah test coverage"]
            )
        
        elif risk.level == "medium":
            return Guidance(
                action="review",
                reason="Perlu review manual sebelum lanjut"
            )
        
        else:
            return Guidance(
                action="proceed",
                reason="Aman untuk dijalankan"
            )
```

---

## 📤 Response Protocol (Critical)
Ini format yang **WAJIB** diikuti agent:

```json
{
  "snowline_response": {
    "status": "success|warning|blocked",
    "tool": "smart_replace",
    "timestamp": "2025-07-25T10:30:00Z",
    
    "verdict": {
      "safe": true,
      "confidence": 95,
      "reasoning": "Perubahan terbatas, ada backup, rollback tersedia"
    },
    
    "guidance": {
      "action": "proceed",
      "message": "Aman untuk dijalankan",
      "suggestions": ["Lakukan dry-run dulu", "Monitor hasil"],
      "alternatives": ["Gunakan regex lebih ketat", "Lakukan per-file"]
    },
    
    "metadata": {
      "risks": ["Bisa affect 3 files", "Membutuhkan restart"],
      "impacts": {
        "areas": ["api", "tests"],
        "severity": "medium"
      },
      "token_estimate": 200,
      "performance_impact": "Tidak ada"
    },
    
    "dry_run": {
      "enabled": true,
      "preview": "47 occurrences akan di-replace di 5 files",
      "reversal_plan": "Backup di .snowline/backup_uuid tersimpan"
    }
  }
}
```

---

## 🔐 Domain 4: CONTEXT (Phase 2)
**Tanggung Jawab:** Memory, awareness, context compression

Akan diimplementasikan di Phase 2. Foundation sudah ada di StateManager.

---

## 📦 Implementation Roadmap

### Phase 1 Implementation Plan (Minggu 1-2)
**Deliverables:**
- **System Domain**
  - ToolRegistry
  - StateManager dengan SQLite
  - Environment validator
- **Actions Domain**
  - Base Tool class
  - Smart Replace implementation
  - Deep Analyzer implementation
- **Checks Domain**
  - SafetyValidator
  - RiskAssessor
  - GuidanceGenerator
- **Integration**
  - OpenAI function calling adapter
  - `run_all.py` orchestrator
  - Configuration system
- **Documentation**
  - System Prompt template (`AGENTS_TEMPLATE.md`)
  - Tool API reference
  - Usage examples

### Phase 2 Implementation Plan (Minggu 3-4)
- Context Domain (Memory management)
- Runs Domain (Lifecycle, retry, timeout)
- Remaining 3 tools (Deep Analyzer, Impact Analyzer, full Project Guardian)
- Integration tests dengan LangChain & AutoGen
- Performance benchmarking

### Phase 3+ (Scaling)
Workflows, advanced tools, ecosystem:
- Parallel/conditional execution (kalau MVP sudah solid)
- 8+ tools tambahan
- Community plugin system
- Web dashboard
- Cloud deployment helpers

---

## 🎓 Filosofi Tertanam dalam Design
Setiap keputusan architecture mencerminkan filosofi:

- **Companion, Bukan Boss**
  - Guidance > Commands
  - Suggest > Force
  - Partner > Master
- **Transparency**
  - Semua keputusan dijelaskan
  - Preview sebelum aksi
  - Audit trail lengkap
- **Reversibility**
  - Setiap aksi bisa dibatalkan
  - Backup automatic
  - Rollback plan included
- **Efficiency**
  - Token tracking
  - Context compression (Phase 2)
  - Smart caching
- **Portability**
  - Bekerja dengan any LLM
  - Independent dari framework
  - Copy-paste friendly
