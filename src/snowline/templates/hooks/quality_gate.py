import sys
import json
import subprocess
import os
import shlex
import platform

# ---------------------------------------------------------------------------
# SAFE / READ-ONLY TOOLS FAST-PATH (Instant allow, zero latency)
# ---------------------------------------------------------------------------
SAFE_TOOLS = {
    "smart_search": "code_finder.py",
    "selective_reader": "reader.py",
    "smart_tree": "tree_viewer.py",
    "deep_analyzer": "analyzer.py",
    "crash_decoder": "decoder.py",
    "clean_sweeper": "sweeper.py",
    "impact_analyzer": "analyzer.py",
    "db_extractor": "extractor.py",
    "scope_guardian": "scope_check.py"
}

# Tools requiring approval (High Risk)
APPROVAL_REQUIRED_TOOLS = {
    "replace_text.py": {
        "tool_name": "smart_replace",
        "min_args": 3,  # <target_dir> <search_string> <replace_string>
        "usage": "python .agents/skills/smart_replace/replace_text.py <dir> <old_text> <new_text> [--apply]"
    },
    "scaffolder.py": {
        "tool_name": "auto_scaffolder",
        "min_args": 2,  # <react|api> <ComponentName>
        "usage": "python .agents/skills/auto_scaffolder/scaffolder.py <react|api> <ComponentName> [target_dir] [--apply]"
    },
    "fixer.py": {
        "tool_name": "import_fixer",
        "min_args": 2,  # <source_file> <broken_import>
        "usage": "python .agents/skills/import_fixer/fixer.py <source_file> <broken_import_string> [--apply]"
    },
    "context_mapper.py": {
        "tool_name": "context_mapper",
        "min_args": 0,
        "usage": "python .agents/skills/context_mapper/context_mapper.py [--apply]"
    }
}


def clean_target_cwd(workspace_paths):
    """Normalize workspace path cross-platform."""
    if not workspace_paths:
        return os.getcwd()
    target_cwd = workspace_paths[0]
    if target_cwd.startswith("file:///"):
        target_cwd = target_cwd[8:]
        if platform.system() != "Windows":
            target_cwd = "/" + target_cwd
        else:
            target_cwd = target_cwd.replace("%3A", ":").replace("/", "\\")
    return target_cwd


def validate_companion_intent(script_name: str, config: dict, args_list: list, cmd_str: str, target_cwd: str):
    """
    Transparently run Companion intent analysis and argument checks.
    Returns (is_valid: bool, error_reason: str).
    """
    tool_name = config["tool_name"]
    
    # Filter out flags like --apply, --regex, --whole-word to count positional args
    positional_args = [a for a in args_list if not a.startswith("--")]
    has_apply = "--apply" in args_list or "--apply" in cmd_str

    # 1. Parameter Completeness Check
    if len(positional_args) < config["min_args"]:
        return False, (
            f"[Companion Gate] Parameter kritis tidak lengkap untuk '{tool_name}'. "
            f"Diperlukan minimal {config['min_args']} argumen posisi, tetapi menerima {len(positional_args)}.\n"
            f"Format yang benar: {config['usage']}"
        )

    # Specific parameter checks
    if tool_name == "auto_scaffolder":
        scaffold_type = positional_args[0].lower() if positional_args else ""
        if scaffold_type not in ("react", "api"):
            return False, (
                f"[Companion Gate] Tipe scaffold '{scaffold_type}' tidak valid. "
                f"Pilihan yang didukung: 'react' atau 'api'.\n"
                f"Contoh: python .agents/skills/auto_scaffolder/scaffolder.py react UserProfile"
            )

    if tool_name == "smart_replace":
        if len(positional_args) >= 3:
            old_str = positional_args[1]
            if len(old_str.strip()) == 0:
                return False, "[Companion Gate] Target string pencarian (old_text) tidak boleh kosong."

    # 2. Dynamic Companion Intent Validation
    companion_dir = os.path.join(target_cwd, ".agents", "skills", "companion")
    skills_dir = os.path.join(target_cwd, ".agents", "skills")
    
    if os.path.exists(companion_dir) and skills_dir not in sys.path:
        sys.path.insert(0, skills_dir)

    try:
        from companion.core_intent import analyze_intent
        
        # Analyze the arguments / command context
        analysis = analyze_intent(" ".join(positional_args))
        
        # If intent indicates high ambiguity or mismatch during destructive apply
        if has_apply and analysis.needs_clarification and analysis.confidence_level in ("LOW", "NONE"):
            return False, (
                f"[Companion Gate] Intent terdeteksi ambigu ({analysis.clarification_note}). "
                f"Gunakan mode dry-run (tanpa flag --apply) terlebih dahulu untuk preview perubahan."
            )
    except Exception:
        # Non-draconian fallback: if companion module is not importable, do not block valid syntax
        pass

    return True, ""


def check_arah6_guardian(target_cwd: str):
    """ARAH 6 Quality Gate: Validate git commits against Project Guardian."""
    guardian_script = os.path.join(target_cwd, ".agents", "skills", "project_guardian", "guardian.py")
    if not os.path.exists(guardian_script):
        return False, "[JEDA PAKSA - ARAH 6] project_guardian/guardian.py tidak ditemukan di workspace ini. Eksekusi ditolak karena audit tidak bisa dilakukan."

    try:
        result = subprocess.run(
            ["python", guardian_script, "--json"],
            cwd=target_cwd,
            capture_output=True,
            text=True
        )
        if result.stdout:
            try:
                guardian_out = json.loads(result.stdout)
                critical_count = guardian_out.get("summary", {}).get("critical", 0)
                if critical_count > 0:
                    return False, (
                        f"[JEDA PAKSA - ARAH 6] project_guardian menemukan {critical_count} isu CRITICAL! "
                        f"Anda dilarang melakukan commit sebelum memperbaikinya atau menyertakan penanda abaikan (// guardian-ignore)."
                    )
            except json.JSONDecodeError:
                return False, "[JEDA PAKSA - ARAH 6] Output guardian tidak valid (JSON error)."
        else:
            return False, f"[JEDA PAKSA - ARAH 6] project_guardian tidak menghasilkan output (returncode={result.returncode}, stderr={result.stderr})."
    except Exception as e:
        return False, f"[JEDA PAKSA - ARAH 6] Gagal memvalidasi repositori dengan project_guardian (Exception: {str(e)}). Eksekusi ditolak untuk mencegah commit tanpa audit."

    return True, ""


def main():
    try:
        input_data = json.load(sys.stdin)
    except Exception:
        print(json.dumps({"decision": "allow"}))
        return

    tool_name = input_data.get("toolName", "")
    tool_call = input_data.get("toolCall", {})
    workspace_paths = input_data.get("workspacePaths", [])
    
    # Deteksi eksekusi shell command
    if tool_name == "run_command" or "CommandLine" in tool_call:
        cmd = tool_call.get("CommandLine", "").strip()
        
        # 1. Check ARAH 6 for git commit
        if "git commit" in cmd:
            if not workspace_paths:
                print(json.dumps({
                    "decision": "deny",
                    "reason": "[JEDA PAKSA - ARAH 6] Parameter workspacePaths tidak ditemukan dalam konteks hook. Eksekusi ditolak karena lingkungan gagal diverifikasi."
                }))
                return
                
            target_cwd = clean_target_cwd(workspace_paths)
            ok, reason = check_arah6_guardian(target_cwd)
            if not ok:
                print(json.dumps({"decision": "deny", "reason": reason}))
                return
            print(json.dumps({"decision": "allow"}))
            return

        # 2. Check Approval-Required Skills
        for script_name, config in APPROVAL_REQUIRED_TOOLS.items():
            if script_name in cmd:
                target_cwd = clean_target_cwd(workspace_paths) if workspace_paths else os.getcwd()
                try:
                    tokens = shlex.split(cmd, posix=(platform.system() != "Windows"))
                except Exception:
                    tokens = cmd.split()

                script_idx = -1
                for idx, tok in enumerate(tokens):
                    if script_name in tok:
                        script_idx = idx
                        break

                tool_args = tokens[script_idx + 1:] if script_idx != -1 else []
                is_valid, err_reason = validate_companion_intent(script_name, config, tool_args, cmd, target_cwd)
                
                if not is_valid:
                    print(json.dumps({"decision": "deny", "reason": err_reason}))
                    return
                # If valid, allow it
                print(json.dumps({"decision": "allow"}))
                return

        # 3. Fast-Path: Allow safe/read tools instantly
        for safe_tool, safe_script in SAFE_TOOLS.items():
            if safe_script in cmd:
                print(json.dumps({"decision": "allow"}))
                return

    # Jika aman atau bukan shell command berisiko, izinkan eksekusi
    print(json.dumps({"decision": "allow"}))

if __name__ == "__main__":
    main()
