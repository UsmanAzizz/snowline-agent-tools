## Guardrail Compliance â€” Non-Negotiable

Any new tool or modification to an existing tool MUST preserve the following guardrail principles, without exception:
1. Any action that writes, modifies, moves, or deletes files MUST have a dry-run/preview mode as the default.
2. Actual execution (write/modify/delete) may ONLY occur with an explicit flag like `--apply`, never automatically.
3. Any claim that guardrails are "already implemented" MUST be accompanied by live-test proof (actual output of running the tool without the apply flag, proving no changes occurred) â€” not just a statement in README or SKILL.md.
4. If there is a code change that potentially removes existing guardrails (intentionally or unintentionally), you MUST explicitly report this to the user before proceeding â€” do not let guardrail regressions happen silently.
5. Documentation (README, SKILL.md) MUST always reflect the actual guardrail behavior in the code. If there is a discrepancy between what is documented and what actually happens in the code, it is considered a bug and must be fixed consistently on both sides (code and documentation).


