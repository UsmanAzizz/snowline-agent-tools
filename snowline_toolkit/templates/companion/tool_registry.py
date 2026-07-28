"""
TOOL REGISTRY
==============
Definisi semua tools yang companion bisa sarankan ke agent.

Format:
- name: Tool identifier
- description: Apa tool ini lakukan
- inputs: Parameters yang dibutuhin
- outputs: Apa yang dihasilkan
- safety: Level keamanan (safe, warning, critical)
- use_cases: Kapan tool ini dipakai
"""

TOOL_REGISTRY = {
    # ===========================================
    # SEARCH & MODIFY
    # ===========================================

    "smart_search": {
        "name": "Smart Code Finder",
        "description": "Cari kode dengan 5 baris context. Hemat token karena nggak perlu baca seluruh file.",
        "command": "python .agents/skills/smart_search/code_finder.py <dir> <keyword> [--ext .jsx]",
        "inputs": {
            "required": ["directory", "keyword"],
            "optional": ["extensions"]
        },
        "outputs": {
            "format": "Human-readable blocks dengan line numbers",
            "example": "Found in: src/App.jsx\n>> function handleSubmit() {"
        },
        "safety": "safe",
        "use_cases": [
            "Cari dimana sebuah fungsi dipanggil",
            "Temukan semua penggunaan sebuah variabel",
            "Lacak import statements"
        ],
        "companion_keywords": ["cari", "find", "search", "where is", "locate", "ketemu"]
    },

    "smart_replace": {
        "name": "Safe Find & Replace",
        "description": "Replace text dengan backup otomatis dan dry-run mode. Mencegah code loss.",
        "command": "python .agents/skills/smart_replace/replace_text.py <dir> <search> <replace> [--apply]",
        "inputs": {
            "required": ["directory", "search", "replace"],
            "optional": ["extensions", "--apply", "--backup"]
        },
        "outputs": {
            "format": "Preview perubahan sebelum eksekusi",
            "example": "[WARN] Found 3 matches in src/utils.js"
        },
        "safety": "safe",
        "use_cases": [
            "Rename variabel di seluruh project",
            "Replace import path",
            "Update konfigurasi"
        ],
        "companion_keywords": ["ganti", "replace", "ubah", "rename", "refactor"]
    },

    "import_fixer": {
        "name": "Import Path Fixer",
        "description": "Fix broken relative imports setelah file dipindahkan.",
        "command": "python .agents/skills/import_fixer/fixer.py <file> <broken_import>",
        "inputs": {
            "required": ["file_path", "broken_import_path"]
        },
        "outputs": {
            "format": "Fixed import statement",
            "example": "[FIXED] import { Button } from '../../components/Button'"
        },
        "safety": "moderate",
        "use_cases": [
            "Setelah memindahkan file",
            "Import errors di console",
            "Refactoring structure"
        ],
        "companion_keywords": ["import", "path", "relative", "broken", "fix"]
    },

    # ===========================================
    # AUDIT & ANALYZE
    # ===========================================

    "project_guardian": {
        "name": "Security & Health Auditor",
        "description": "Scan project untuk credential leaks, .gitignore issues, dan security vulnerabilities.",
        "command": "python .agents/skills/project_guardian/guardian.py [--summary|--json]",
        "inputs": {
            "required": [],
            "optional": ["--summary", "--json"]
        },
        "outputs": {
            "format": "Issues grouped by severity",
            "example": "CRITICAL=2 | HIGH=3 | MEDIUM=1 | LOW=5"
        },
        "safety": "safe",
        "use_cases": [
            "Cek keamanan sebelum deployment",
            "Audit project baru",
            "Validasi credential handling"
        ],
        "companion_keywords": ["keamanan", "security", "audit", "vulnerability", "credential", "env", "password"]
    },

    "clean_sweeper": {
        "name": "Tech Debt Scanner",
        "description": "Cari file sampah, TODO/FIXME tags, dan large comment blocks.",
        "command": "python .agents/skills/clean_sweeper/sweeper.py <directory> [--json]",
        "inputs": {
            "required": ["directory"],
            "optional": ["--json"]
        },
        "outputs": {
            "format": "List of residue files dan issues",
            "example": "[FAIL] scratch [Suspected Backup Folder]\n[WARN] Found 12 TODO/FIXME tags"
        },
        "safety": "safe",
        "use_cases": [
            "Cleanup project sebelum commit",
            "Cek tech debt",
            "Identifikasi file yang nggak terpakai"
        ],
        "companion_keywords": ["bersihkan", "cleanup", "residu", "garbage", "tech debt", "unused"]
    },

    "deep_analyzer": {
        "name": "Project Profiler",
        "description": "Deteksi tech stack, dependencies, dan file statistics.",
        "command": "python .agents/skills/deep_analyzer/analyzer.py <directory> [--json]",
        "inputs": {
            "required": ["directory"],
            "optional": ["--json"]
        },
        "outputs": {
            "format": "Tech stack overview",
            "example": "Tech Stack: Node.js, React\nDependencies: 56 runtime, 9 dev"
        },
        "safety": "safe",
        "use_cases": [
            "Understand project structure",
            "Cek tech stack",
            "Validasi dependencies"
        ],
        "companion_keywords": ["struktur", "tech stack", "analisa", "project overview", "dependencies"]
    },

    "selective_reader": {
        "name": "TOC Extractor",
        "description": "Extract Table of Contents dari file besar. Hemat token karena nggak perlu baca seluruh file.",
        "command": "python .agents/skills/selective_reader/reader.py <filepath> [--json]",
        "inputs": {
            "required": ["file_path"],
            "optional": ["--json"]
        },
        "outputs": {
            "format": "List of functions/classes dengan line numbers",
            "example": "Line 45: Function handleSubmit\nLine 78: Arrow Function useEffect"
        },
        "safety": "safe",
        "use_cases": [
            "Baca file besar tanpa scroll semua",
            "Temukan fungsi spesifik",
            "Understand file structure"
        ],
        "companion_keywords": ["baca", "read", "file", "toc", "function", "structure"]
    },

    "context_mapper": {
        "name": "Knowledge Builder",
        "description": "Generate PROJECT_STRUCTURE.md dan COMMON_PATTERNS.md untuk agent understanding.",
        "command": "python .agents/skills/context_mapper/context_mapper.py [--apply]",
        "inputs": {
            "required": [],
            "optional": ["--apply"]
        },
        "outputs": {
            "format": "Markdown files di .agents/knowledge/",
            "example": "Generated: PROJECT_STRUCTURE.md, COMMON_PATTERNS.md"
        },
        "safety": "safe",
        "use_cases": [
            "First time di project baru",
            "Update context setelah major changes",
            "Build knowledge base"
        ],
        "companion_keywords": ["struktur", "map", "context", "knowledge", "architecture"]
    },

    "smart_tree": {
        "name": "Directory Visualizer",
        "description": "Generate visual tree dari directory structure.",
        "command": "python .agents/skills/smart_tree/scripts/tree_viewer.py <dir> [depth] [--simple]",
        "inputs": {
            "required": ["directory"],
            "optional": ["depth", "--simple"]
        },
        "outputs": {
            "format": "Visual tree dengan ├── └── connectors",
            "example": "src/\n├── components/\n│   └── Button.jsx"
        },
        "safety": "safe",
        "use_cases": [
            "Visualize folder structure",
            "Navigate project",
            "Find file location"
        ],
        "companion_keywords": ["struktur", "tree", "directory", "folder", "visualize"]
    },

    "scope_guardian": {
        "name": "Scope Validator",
        "description": "Cek apakah sebuah file di dalam scope task yang sedang berjalan.",
        "command": "python .agents/skills/scope_guardian/scripts/scope_check.py <file_path>",
        "inputs": {
            "required": ["file_path"]
        },
        "outputs": {
            "format": "[ALLOWED] atau [BLOCKED]",
            "example": "[ALLOWED] File is within scope"
        },
        "safety": "safe",
        "use_cases": [
            "Sebelum modify file",
            "Validasi scope expansion",
            "Prevent accidental edits"
        ],
        "companion_keywords": ["scope", "di area", "file ini", "validasi"]
    },

    # ===========================================
    # WORKFLOW HELPERS
    # ===========================================

    "impact_analyzer": {
        "name": "Dependency Tracer",
        "description": "Cek file mana saja yang depend pada sebuah file/function.",
        "command": "python .agents/skills/impact_analyzer/analyzer.py <file> <project_root>",
        "inputs": {
            "required": ["file_path", "project_root"]
        },
        "outputs": {
            "format": "List of dependent files",
            "example": "Level 1: 5 files\nLevel 2: 12 files"
        },
        "safety": "safe",
        "use_cases": [
            "Sebelum delete/modify file penting",
            "Impact analysis",
            "Refactoring planning"
        ],
        "companion_keywords": ["impact", "depend", "usage", "where used", "cascade"]
    },

    "crash_decoder": {
        "name": "Error Parser",
        "description": "Parse crash logs dan ekstrak error yang relevant.",
        "command": "python .agents/skills/crash_decoder/decoder.py <log_file>",
        "inputs": {
            "required": ["log_file_path"]
        },
        "outputs": {
            "format": "Filtered error dengan file:line",
            "example": "Error at src/utils.js:45\nTypeError: Cannot read property"
        },
        "safety": "safe",
        "use_cases": [
            "Debug crash logs",
            "Filter noise dari stack traces",
            "Identify root cause"
        ],
        "companion_keywords": ["error", "crash", "debug", "log", "trace", "bug"]
    },

    "auto_scaffolder": {
        "name": "Boilerplate Generator",
        "description": "Generate boilerplate code untuk components/routes.",
        "command": "python .agents/skills/auto_scaffolder/scaffolder.py <type> <name> [--apply]",
        "inputs": {
            "required": ["type", "name"],
            "optional": ["--apply"]
        },
        "outputs": {
            "format": "Generated code template",
            "example": "Generated: src/components/TestComponent.jsx"
        },
        "safety": "moderate",
        "use_cases": [
            "Buat component baru",
            "Generate API route template",
            "Scaffold project structure"
        ],
        "companion_keywords": ["generate", "create", "boilerplate", "scaffold", "new component"]
    },

    "db_extractor": {
        "name": "Database Schema Extractor",
        "description": "Extract database schema dari .env dan analyze tables.",
        "command": "python .agents/skills/db_extractor/scripts/extractor.py [--env-path .env]",
        "inputs": {
            "required": [],
            "optional": ["--env-path"]
        },
        "outputs": {
            "format": "Table/column schema",
            "example": "Table: users\nColumns: id, name, email, password"
        },
        "safety": "warning",
        "use_cases": [
            "Understand database structure",
            "Map model relationships",
            "Write database queries"
        ],
        "companion_keywords": ["database", "schema", "table", "columns", "db"]
    }
}


def get_tool(name: str) -> dict:
    """Get tool definition by name."""
    return TOOL_REGISTRY.get(name)


def suggest_tools(intent: str) -> List[dict]:
    """Suggest tools based on user intent keywords."""
    intent_lower = intent.lower()
    suggestions = []

    for tool_name, tool_def in TOOL_REGISTRY.items():
        for keyword in tool_def.get("companion_keywords", []):
            if keyword in intent_lower:
                suggestions.append(tool_def)
                break

    return suggestions


def list_all_tools() -> List[dict]:
    """List all available tools."""
    return list(TOOL_REGISTRY.values())


# Quick test
if __name__ == "__main__":
    print("=" * 60)
    print("TOOL REGISTRY - Quick Test")
    print("=" * 60)

    print("\n1. All Tools:")
    for tool in list_all_tools():
        print(f"   - {tool['name']}")

    print("\n2. Suggest for 'cek keamanan':")
    suggestions = suggest_tools("cek keamanan")
    for s in suggestions:
        print(f"   - {s['name']}")

    print("\n3. Tool 'smart_search':")
    tool = get_tool("smart_search")
    print(f"   Command: {tool['command']}")
    print(f"   Safety: {tool['safety']}")

    print("\n" + "=" * 60)
