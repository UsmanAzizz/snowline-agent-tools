# Snowline Agent Tools - Roadmap

## Mission

> "Prevent token waste in AI agent workflows."

Focus: Low-mid tier projects, portable efficiency across AI platforms. Pure Python, minimal dependencies.

---

## Current State (v4.5 MVP)

### Core Tools (10)
| Tool | Purpose |
|------|---------|
| smart_search | Find code with context |
| smart_replace | Find-and-replace with backup |
| selective_reader | Extract TOC from large files |
| smart_tree | Compact directory visualizer |
| scope_guardian | File scope validator |
| project_guardian | Security auditor |
| clean_sweeper | Tech debt scanner |
| deep_analyzer | Project profiler |
| impact_analyzer | Dependency tracer |
| crash_decoder | Error parser |
| auto_scaffolder | Boilerplate generator |
| import_fixer | Import path fixer |
| db_extractor | Database schema extractor |

### Deferred Tools (4) - Future
| Tool | Purpose |
|------|---------|
| token_budget | Token usage monitor |
| context_curator | Context noise filter |
| output_formatter | JSON formatter |
| decision_validator | Risk assessor |

### Companion Layer (v4.1)
| Feature | Status |
|---------|--------|
| Intent analysis | ✅ |
| Tool routing | ✅ |
| Command generation | ✅ |

### Safety
| Feature | Status |
|---------|--------|
| Approval for file-modifying tools | ✅ |
| Preview without --apply | ✅ |
| Bootstrapping rules | ✅ |

---

## Roadmap

### ✅ DONE - MVP Core
- [x] 10 core tools
- [x] Companion v4.1 (simplified)
- [x] Installer (`snowline_toolkit`)
- [x] Bootstrapping safety rules
- [x] README updated

### ⏳ IN PROGRESS - Gemini Integration

#### 3.1 Gemini Integration
- [ ] Test with Gemini
- [ ] Document prompt integration

### 📋 TODO - Next Phase

#### Documentation
- [ ] Quick start guide
- [ ] Examples for each tool
- [ ] Troubleshooting FAQ

#### Testing
- [ ] User feedback
- [ ] Real-world testing

#### Advanced (Deferred)
- [ ] Re-integrate context management tools
- [ ] Learning loop
- [ ] Unit tests

---

## File Structure

```
snowline-agent-tools/
├── companion/               # Companion v4.1 (simplified)
├── deferred/               # Future tools
├── snowline_toolkit/        # Installer package
├── .agents/                # User workspace (from install)
└── .claude/               # Claude Code skills
```

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Token savings | 30-50% |
| Tool routing accuracy | 90%+ |
| Setup time | <5 min |

---

*Last Updated: 2026-07-29*
