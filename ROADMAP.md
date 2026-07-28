# ❄️ Snowline Agent Tools - Roadmap

## 🎯 Mission

> "While others race to burn tokens, we prevent the waste."

**Hunter = Agent** (powerful, free to hunt)
**Chain = Companion** (keeps agent safe, no overflow)

```
Agent is free to hunt...
But companion walks with at every step.
If agent goes too far, chain pulls back.
No restrict, but no overflow.
```

---

## 📦 Current State (v3)

### Tools (14 Core)
| Tool | Purpose |
|------|---------|
| smart_search | Find code with 5-line context |
| smart_replace | Safe find-and-replace with backup |
| selective_reader | TOC extractor for large files |
| project_guardian | Security & health auditor |
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

### Companion Layer (v3)
| Phase | Function | Status |
|-------|---------|--------|
| 1. REASONING | Intent analysis | ✅ |
| 2. THINKING | Tool planning | ✅ |
| 3. PREPARING | Command generation | ✅ |
| 4. EXECUTING | Scope/security validation | ✅ |
| 5. FINISHING | Output validation | ✅ |

**Vocabulary: 170+ keywords** (Indonesian + English)

---

## 📋 Roadmap

### TASK 1: Companion Core Enhancement ⭐ PRIORITY

#### 1.1 Fix Vocabulary Gaps
- [ ] Add "refactor" keyword -> smart_replace
- [ ] Add "export", "excel" keywords
- [ ] Add "PDF", "report" handling
- [ ] Add "import", "module" keywords
- [ ] Test edge cases

#### 1.2 Learning Loop
- [ ] Track usage patterns
- [ ] Store tool selection history
- [ ] Suggest based on past success
- [ ] Build `~/.companion_memory.json`

#### 1.3 Execution Engine
- [ ] Run commands via subprocess
- [ ] Parse JSON output automatically
- [ ] Return structured results to agent
- [ ] Handle errors gracefully

---

### TASK 2: Tool Expansion

#### 2.1 New Tools
- [ ] `token_budget_tracker` - Monitor token usage
- [ ] `context_curator` - Filter noise from context
- [ ] `output_formatter` - Format JSON to readable
- [ ] `decision_validator` - Validate decisions

#### 2.2 Tool Integration
- [ ] Connect new tools to companion
- [ ] Add keywords mapping
- [ ] Document usage patterns

---

### TASK 3: Agent Integration

#### 3.1 Gemini Integration
- [ ] Create companion.py as callable module
- [ ] Test with Gemini CLI
- [ ] Document prompt integration

#### 3.2 Claude Integration
- [ ] Create .claude/skills/ companion
- [ ] Test with Claude Code
- [ ] Document usage

#### 3.3 Universal Adapter
- [ ] Create simple API interface
- [ ] HTTP/JSON endpoint option
- [ ] Documentation for any AI

---

### TASK 4: Documentation & Polish

#### 4.1 User Guide
- [ ] Quick start guide
- [ ] Examples for each tool
- [ ] Troubleshooting FAQ

#### 4.2 Developer Guide
- [ ] How to add new tools
- [ ] How to extend vocabulary
- [ ] Architecture overview

#### 4.3 README Update
- [ ] Vision statement
- [ ] Quick demo
- [ ] Contributing guide

---

### TASK 5: Testing & Validation

#### 5.1 Unit Tests
- [ ] Test vocabulary matching
- [ ] Test tool selection logic
- [ ] Test validation flows
- [ ] Add pytest coverage

#### 5.2 Integration Tests
- [ ] Test with real projects
- [ ] Test agent scenarios
- [ ] Performance benchmarks

#### 5.3 User Testing
- [ ] Get feedback from users
- [ ] Iterate based on feedback
- [ ] Document real-world usage

---

## 📅 Suggested Timeline

```
Week 1: TASK 1 (Companion Enhancement)
├── 1.1 Fix vocabulary (1-2 days)
├── 1.2 Learning Loop (2-3 days)
└── 1.3 Execution Engine (2-3 days)

Week 2: TASK 3 (Agent Integration)
├── 3.1 Gemini (2 days)
├── 3.2 Claude (2 days)
└── 3.3 Universal Adapter (1 day)

Week 3: TASK 2 (Tool Expansion)
├── 2.1 Build 4 new tools (3-4 days)
└── 2.2 Integration (2 days)

Week 4: TASK 4 & 5 (Documentation & Testing)
├── 4.1-4.3 Docs (2 days)
└── 5.1-5.3 Testing (3 days)
```

---

## 🔥 Quick Wins (Next Session)

1. Fix vocabulary gaps (1.1)
2. Test execution with real command
3. Demo full workflow

---

## 📁 Target File Structure

```
snowline-agent-tools/
├── companion/
│   ├── companion.py          # Core
│   ├── vocabulary.py         # 170+ keywords
│   ├── memory.py            # Learning loop
│   ├── executor.py          # Run commands
│   └── README.md
├── tools/
│   └── [14 existing tools]
├── docs/
│   ├── QUICKSTART.md
│   ├── ARCHITECTURE.md
│   └── VOCABULARY.md
└── tests/
    ├── unit/
    └── integration/
```

---

## 🎯 Success Metrics

| Metric | Target |
|--------|--------|
| Token savings per task | 50-80% |
| Tool selection confidence | 95%+ |
| Vocabulary coverage | 200+ keywords |
| Agent integration | 3+ providers |
| User satisfaction | 8+/10 |

---

## 💡 Philosophy

> "We don't build tools. We build partners."
> 
> "Agents that are used to brute-force will feel inferior, because without realizing it, they're training the agentic companion to hunt."

---

*Last Updated: 2026-07-29*
