"""
CONTEXT CURATOR
==================
Filter noise from context.
Keep what's relevant, remove what's not.
"""

import re
from typing import List, Dict

# Noise patterns
NOISE_PATTERNS = [
    r"import\s+os",
    r"import\s+sys",
    r"import\s+json",
    r"import\s+time",
    r"from\s+\w+\s+import",
    r"// ===+",
    r"# ===+",
    r"```[\w]*\n[\s\S]*?```",
    r"<!--[\s\S]*?-->",
    r"\/\*[\s\S]*?\*\/",
]

# Keep patterns (important)
KEEP_PATTERNS = [
    r"function\s+\w+",
    r"def\s+\w+",
    r"class\s+\w+",
    r"const\s+\w+\s*=",
    r"let\s+\w+\s*=",
    r"var\s+\w+\s*=",
    r"interface\s+\w+",
    r"type\s+\w+\s*=",
    r"export\s+",
    r"import\s+\w+",
    r"return\s+",
    r"if\s*\(",
    r"for\s*\(",
    r"while\s*\(",
    r"try\s*{",
    r"try:\s*$",
]

# Relevance patterns
RELEVANT_KEYWORDS = [
    "bug", "error", "fix", "issue", "problem",
    "feature", "refactor", "optimize",
    "auth", "login", "user", "config",
    "api", "route", "endpoint",
    "component", "state", "hook", "effect",
]

# Noise categories
class NoiseType:
    COMMENT = "comment"
    IMPORT = "import"
    WHITESPACE = "whitespace"
    IRRELEVANT = "irrelevant"


class ContextCurator:
    """Filter context to keep what's important."""

    def __init__(self):
        self.stats = {"removed": 0, "kept": 0, "noise_lines": 0}

    def clean(self, text: str) -> str:
        """Remove noise from text."""
        lines = text.split("\n")
        clean_lines = []
        for line in lines:
            if self._is_noise(line):
                self.stats["noise_lines"] += 1
                continue
            clean_lines.append(line)
            self.stats["kept"] += 1
        return "\n".join(clean_lines)

    def _is_noise(self, line: str) -> bool:
        stripped = line.strip()
        if not stripped:
            return True
        if any(re.match(p, stripped) for p in NOISE_PATTERNS):
            return True
        return False

    def score(self, text: str) -> Dict:
        """Score context quality."""
        lines = text.split("\n")
        relevant = sum(1 for l in lines if any(k in l for k in RELEVANT_KEYWORDS))
        return {
            "lines": len(lines),
            "relevant": relevant,
            "quality_pct": int(relevant / len(lines) * 100) if lines else 0,
            "suggestion": "reduce" if relevant < 20 else "ok"
        }


def curate(text: str) -> str:
    curator = ContextCurator()
    return curator.clean(text)


# CLI interface
if __name__ == "__main__":
    import sys
    text = sys.stdin.read()
    if text.strip():
        result = curate(text)
        print(result)
