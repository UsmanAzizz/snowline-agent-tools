# Snowline: Portable Agentic OS

Your AI agent's thinking partner.

## What is Snowline?

Snowline is not a framework. It's a **companion layer** that sits between your agent and execution, providing:
- 🛡️ **Safety**: Every action validated, backed up, reversible
- 💡 **Guidance**: Agent gets structured advice before acting
- 📊 **Efficiency**: Token-conscious, context-aware
- 🤝 **Partnership**: Agent + Snowline = stronger together

## Quick Start

```bash
pip install snowline-agents
```

```python
from snowline import SnowlineCompanion
from snowline.adapters import OpenAIAdapter

# Initialize
companion = SnowlineCompanion()
adapter = OpenAIAdapter(companion)

# Use with your LLM
system_prompt = adapter.build_system_prompt()
tools_schema = adapter.tools_schema
```

## Features (v0.1-alpha)
- ✅ **SmartReplace** - Safe code replacement with backup
- ✅ **DeepAnalyzer** - Code structure and complexity analysis
- ✅ **Safety validation** - Risk scoring & guidance
- ✅ **OpenAI adapter** - Function calling protocol
- ✅ **State management** - SQLite for persistence
- ✅ **Rollback capability** - Restore from backups

## Documentation
- [Integration Guide](docs/INTEGRATION_GUIDE.md)
- [API Reference](docs/API_REFERENCE.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Changelog](CHANGELOG.md)

## Example
See `example_mock_integration.py` for a complete end-to-end example simulating agent compliance and safety validation.

## Philosophy
Like snowflakes gently flowing into a child's hands — never forcing, always guiding.

## License
MIT
