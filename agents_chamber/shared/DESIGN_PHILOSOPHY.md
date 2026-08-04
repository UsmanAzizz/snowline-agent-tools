# DESIGN PHILOSOPHY

This file stores the theoretical, academic, and philosophical justifications for architectural decisions in the Chamber ecosystem.
By keeping philosophy here, we keep `project_context.md` strictly focused on factual history and hard rules (Zero-Bloat).

## 1. Role Specialization Validation (The MetaGPT Principle)
Our separation of roles (PM, Tech Lead, QA, Executor) is validated by principles found in MetaGPT and similar frameworks:
- **Product Manager (PM)**: Operates at the human level, defining requirements and making high-level compromises.
- **Tech Lead (TL)**: Acts as the architectural gatekeeper, orchestrating tasks and enforcing constraints (The Ledger). Never writes code directly.
- **QA / Reviewer**: Provides adversarial review. Their independence ensures that the TL's decisions and the Executor's output are stress-tested before merging.
- **Executor**: The coding engine. Focuses strictly on implementation and proving correctness through raw terminal output.

By keeping these separate, we prevent the "echo chamber" effect where a single LLM context becomes a yes-man to its own flawed ideas.
