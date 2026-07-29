# Snowline Agent Tools - Roadmap

## Mission

> "Prevent token waste in AI agent workflows."

Focus: Portable efficiency across AI platforms (Gemini, Claude, etc.), not vendor-specific optimization. Pure Python, minimal external dependencies.

---

## Current State (v4.4)

### Core Tools (14)
| Tool | Purpose |
|------|---------|
| smart_search | Find code with context |
| smart_replace | Find-and-replace with backup |
| selective_reader | TOC extractor for large files |
| project_guardian | Security auditor |
| clean_sweeper | Tech debt scanner |
| deep_analyzer | Project profiler |
| smart_tree | Directory visualizer |
| context_mapper | Knowledge builder |
| scope_guardian | Scope validator |
| impact_analyzer | Dependency tracer |
| crash_decoder | Error parser |
| auto_scaffolder | Boilerplate generator |
| import_fixer | Import path fixer |
| db_extractor | Database schema extractor |

### Context Management Tools (4)
| Tool | Purpose |
|------|---------|
| token_budget | Token usage monitor |
| context_curator | Context noise filter |
| output_formatter | JSON formatter |
| decision_validator | Risk assessor |

### Companion Layer (v4.4)
| Phase | Function | Status |
|-------|---------|--------|
| 1. REASONING | Intent analysis | done |
| 2. THINKING | Tool planning | done |
| 3. PREPARING | Command generation | done |
| 4. EXECUTING | Tool execution | done |
| 5. VALIDATING | Output validation | done |

### Safety
| Feature | Status |
|---------|--------|
| Approval required for file-modifying tools | done |
| Preview command without --apply | done |
| Project-scoped memory | done |

---

## Roadmap

### TASK 1: Companion Core Enhancement - COMPLETED

#### 1.1 Vocabulary Gaps - DONE
- [x] Add "refactor" keyword
- [x] Add "export", "excel" handling (clarification)
- [x] Add "PDF", "report" handling (clarification)
- [x] Multi-word keyword support
- [x] Blocking logic for clarification

#### 1.2 Learning Loop - DONE
- [x] Track usage patterns
- [x] Store history in .agents/memory.json
- [x] Suggest based on past success

#### 1.3 Execution Engine - DONE
- [x] Run commands via subprocess
- [x] Return structured results
- [x] Handle errors gracefully

---

### TASK 2: Tool Expansion - COMPLETED

#### 2.1 New Tools
- [x] token_budget - Token usage tracker
- [x] context_curator - Context noise filter
- [x] output_formatter - JSON formatter
- [x] decision_validator - Risk assessor

#### 2.2 Tool Integration
- [x] Connect to companion
- [x] Add keywords mapping
- [x] Test integration

---

### TASK 3: Agent Integration - IN PROGRESS

#### 3.1 Gemini Integration
- [ ] Create callable module for Gemini CLI
- [ ] Test with Gemini
- [ ] Document prompt integration

#### 3.2 Claude Integration - DONE
- [x] Create .claude/skills/ companion
- [x] SKILL.md created

#### 3.3 Universal Adapter - DONE
- [x] HTTP/JSON API (api.py)
- [x] CLI interface (cli.py)
- [x] Python module (__init__.py)

---

### TASK 4: Documentation - PENDING

#### 4.1 User Guide
- [ ] Quick start guide
- [ ] Examples for each tool
- [ ] Troubleshooting FAQ

#### 4.2 Developer Guide
- [ ] How to add new tools
- [ ] How to extend vocabulary
- [ ] Architecture overview

#### 4.3 README Update
- [ ] Quick demo
- [ ] Contributing guide

---

### TASK 5: Testing & Validation - PENDING

#### 5.1 Unit Tests
- [ ] Test vocabulary matching
- [ ] Test tool selection logic
- [ ] Test validation flows

#### 5.2 Integration Tests
- [ ] Test with real projects
- [ ] Test agent scenarios

#### 5.3 User Testing
- [ ] Get feedback
- [ ] Document real-world usage

---

## Timeline

```
Week 1-2: TASK 3.1 (Gemini Integration)
Week 3: TASK 4 (Documentation)
Week 4: TASK 5 (Testing)
```

---

## File Structure

```
snowline-agent-tools/
├── companion/                    # Companion Layer v4.4
│   ├── companion_core.py        # Intent analysis, planning
│   ├── memory.py               # Learning loop
│   ├── executor.py             # Command execution
│   ├── tool_registry.py        # Tool definitions
│   ├── api.py                  # HTTP/JSON API
│   ├── cli.py                  # CLI interface
│   └── __init__.py             # Python module
├── .claude/skills/             # Claude Code integration
│   └── companion/
│       └── SKILL.md
├── .agents/                    # Project-scoped data
│   └── memory.json             # Learning history
├── tools/                       # 18 tools
└── tests/
```

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Token savings per task | 50-80% |
| Tool selection confidence | 95%+ |
| Vocabulary coverage | 200+ keywords |
| Agent integration | 3+ providers |

---

*Last Updated: 2026-07-29*
