---
name: Project Guardian (Security & Health Auditor)
description: Use this skill when the user asks you to audit the project for security leaks, secret credentials, vulnerable dependencies, or environment file (.gitignore) issues.
---

## Instructions for AI Agent

When the user asks you to "audit project", "cek keamanan", or "jalankan project guardian", use this tool to scan the repository.

**Command to run:**
```powershell
python .agents/skills/project_guardian/guardian.py
```
*(Make sure your current working directory `Cwd` is set to the root of the project).*

**Expected Output:**
The script will output a report directly to standard output. It will highlight specific modules:
1. **Secret Scanner**: Identifies hardcoded API keys and passwords.
2. **Env & Gitignore Verifier**: Ensures `.env` files are not exposed.
3. **Physical Import Checker**: Checks if relative imports exist.
4. **Dependencies**: Reports unused packages and high/critical npm audit vulnerabilities.

### 🛑 CRITICAL BEHAVIORAL RULE
1. Present the findings clearly to the user.
2. Group the findings into **[FAIL]** (Must fix immediately, like exposed `.env`) and **[WARN]** (Should be reviewed).
3. Do NOT automatically fix or modify files. Ask the user which items they want you to fix first.
