import sys
sys.dont_write_bytecode = True
import os
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
"""
Simple test runner for Snowline Agent Tools
Run with: python tests/run_tests.py
"""
import os
import sys

if '--no-site-packages' in sys.argv:
    sys.path[:] = [p for p in sys.path if 'site-packages' not in p]
    os.environ['SNOWLINE_TEST_NO_SITE_PACKAGES'] = '1'

import unittest
import tempfile
import shutil
from pathlib import Path

# Force UTF-8
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Skill hidup di src/snowline/templates/skills/ sejak paket dipindah dari
# snowline_toolkit ke snowline. Jalur lama membuat runner ini mati diam-diam.
AKAR = Path(__file__).parent.parent
SKILLS = AKAR / "src" / "snowline" / "templates" / "skills"
SRC = AKAR / "src"
sys.path.insert(0, str(AKAR))
sys.path.insert(0, str(SKILLS))
sys.path.insert(0, str(SRC))

from tree_gen.tree_gen import (
    parse_gitignore,
    is_ignored,
    generate_tree,
    generate_simple_tree,
    get_tree_stats
)
from test_smart_replace_apply import DAFTAR as UJI_SMART_REPLACE
import test_scope_guardian
from test_impact_analyzer import test_impact_analysis
import test_context_mapper
import test_rejections
import test_encoding
import test_selective_reader
import test_role_lock
import test_intercept_native
import test_orphan_guard
import test_bom_guard
import test_name_guard
import test_smoke_cli
import test_add_entry
import test_path_setup

class TestRunner:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.results = []

    def run(self, name, test_func):
        try:
            test_func()
            self.passed += 1
            self.results.append(f"  [PASS] {name}")
        except unittest.SkipTest as e:
            self.passed += 1
            self.results.append(f"  [SKIP] {name}: {e}")
        except AssertionError as e:
            self.failed += 1
            self.results.append(f"  [FAIL] {name}: {e}")
            print(f"::error title=FAIL {name}::{e}")
        except Exception as e:
            self.failed += 1
            self.results.append(f"  [ERROR] {name}: {e}")
            print(f"::error title=ERROR {name}::{e}")

    def summary(self):
        total = self.passed + self.failed
        print(f"\n{'='*50}")
        print(f"Results: {self.passed}/{total} passed, {self.failed} failed")
        print(f"{'='*50}")
        for result in self.results:
            print(result)
        return self.failed == 0

# Tree Gen Tests
def test_parse_gitignore_returns_list():
    with tempfile.TemporaryDirectory() as tmpdir:
        result = parse_gitignore(tmpdir)
        assert isinstance(result, list), "Should return list"

def test_parse_gitignore_includes_defaults():
    with tempfile.TemporaryDirectory() as tmpdir:
        result = parse_gitignore(tmpdir)
        assert '.git' in result, "Should include .git"
        assert 'node_modules' in result, "Should include node_modules"

def test_parse_gitignore_parses_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        gitignore = os.path.join(tmpdir, '.gitignore')
        with open(gitignore, 'w') as f:
            f.write('*.log\ntemp/\n')
        result = parse_gitignore(tmpdir)
        assert '*.log' in result, "Should parse *.log pattern"

def test_is_ignored_git():
    patterns = ['.git']
    assert is_ignored('.git', patterns) == True

def test_is_ignored_node_modules():
    patterns = ['node_modules']
    assert is_ignored('node_modules', patterns) == True

def test_is_ignored_respects_patterns():
    patterns = ['*.log']
    assert is_ignored('error.log', patterns) == True
    assert is_ignored('file.txt', patterns) == False

def test_is_ignored_normal_files():
    patterns = ['.git', 'node_modules']
    assert is_ignored('App.jsx', patterns) == False

def test_generate_tree_returns_string():
    with tempfile.TemporaryDirectory() as tmpdir:
        result = generate_tree(tmpdir, max_depth=1)
        assert isinstance(result, str), "Should return string"

def test_generate_tree_includes_entries():
    with tempfile.TemporaryDirectory() as tmpdir:
        open(os.path.join(tmpdir, 'file1.txt'), 'w').close()
        os.makedirs(os.path.join(tmpdir, 'subdir'))
        result = generate_tree(tmpdir, max_depth=1)
        assert 'file1.txt' in result
        assert 'subdir' in result

def test_generate_simple_tree_no_icons():
    with tempfile.TemporaryDirectory() as tmpdir:
        open(os.path.join(tmpdir, 'test.txt'), 'w').close()
        result = generate_simple_tree(tmpdir)
        assert '📄' not in result
        assert '📁' not in result
        assert '📁' not in result

def test_get_tree_stats_returns_dict():
    with tempfile.TemporaryDirectory() as tmpdir:
        result = get_tree_stats(tmpdir)
        assert isinstance(result, dict), "Should return dict"

def test_get_tree_stats_has_keys():
    with tempfile.TemporaryDirectory() as tmpdir:
        result = get_tree_stats(tmpdir)
        assert 'total_files' in result
        assert 'total_dirs' in result
        assert 'file_types' in result

def test_get_tree_stats_counts_files():
    with tempfile.TemporaryDirectory() as tmpdir:
        open(os.path.join(tmpdir, 'file1.txt'), 'w').close()
        open(os.path.join(tmpdir, 'file2.txt'), 'w').close()
        result = get_tree_stats(tmpdir)
        assert result['total_files'] == 2, f"Expected 2 files, got {result['total_files']}"

def test_get_tree_stats_file_types():
    with tempfile.TemporaryDirectory() as tmpdir:
        open(os.path.join(tmpdir, 'file1.js'), 'w').close()
        open(os.path.join(tmpdir, 'file2.jsx'), 'w').close()
        result = get_tree_stats(tmpdir)
        assert result['file_types'].get('.js', 0) == 1
        assert result['file_types'].get('.jsx', 0) == 1

def main():
    print("[TEST] Running Snowline Agent Tools Tests\n")

    runner = TestRunner()

    print("Testing tree_gen module...")
    tests = [
        ("parse_gitignore returns list", test_parse_gitignore_returns_list),
        ("parse_gitignore includes defaults", test_parse_gitignore_includes_defaults),
        ("parse_gitignore parses .gitignore", test_parse_gitignore_parses_file),
        ("is_ignored handles .git", test_is_ignored_git),
        ("is_ignored handles node_modules", test_is_ignored_node_modules),
        ("is_ignored respects patterns", test_is_ignored_respects_patterns),
        ("is_ignored allows normal files", test_is_ignored_normal_files),
        ("generate_tree returns string", test_generate_tree_returns_string),
        ("generate_tree includes entries", test_generate_tree_includes_entries),
        ("generate_simple_tree no icons", test_generate_simple_tree_no_icons),
        ("get_tree_stats returns dict", test_get_tree_stats_returns_dict),
        ("get_tree_stats has required keys", test_get_tree_stats_has_keys),
        ("get_tree_stats counts files", test_get_tree_stats_counts_files),
        ("get_tree_stats tracks file types", test_get_tree_stats_file_types),
    ]

    for name, test in tests:
        runner.run(name, test)

    print("Testing smart_replace --apply...")
    for name, test in UJI_SMART_REPLACE:
        runner.run(name, test)

    import test_write_log
    import test_shell_tracking
    import test_audit_cli
    import test_scope_callers
    import test_init_gitignore
    import test_b1_status
    import test_b2_light_mode_warn
    import test_b3_init_chamber_role
    import test_b4_close_entry_renumber
    import test_b5_install_hooks
    import test_c1_rotate
    import test_c2_state_validation
    print("Testing write_log (Entry A2)...")
    runner.run("write_log directions", test_write_log.test_write_log_directions)
    print("Testing shell tracking (Entry A3)...")
    runner.run("shell_tracking directions", test_shell_tracking.test_shell_tracking_directions)
    print("Testing audit CLI (Entry A4)...")
    runner.run("audit_cli directions", test_audit_cli.test_audit_directions)
    print("Testing unified scope callers (Entry A5)...")
    runner.run("unified_scope_callers", test_scope_callers.test_all_5_callers_after_unification)
    print("Testing init gitignore (Entry A6)...")
    runner.run("init_gitignore directions", test_init_gitignore.test_init_gitignore_and_scope)
    print("Testing B1 status (editable/wheel)...")
    runner.run("b1_status directions", test_b1_status.test_b1_status_directions)
    runner.run("b1_fail_closed", test_b1_status.test_b1_fail_closed_when_scope_guardian_missing)
    print("Testing B2 single light mode warning...")
    runner.run("b2_light_mode_warn", test_b2_light_mode_warn.test_b2_single_warning_when_mode_ringan_corrupt_or_unrecognized)
    print("Testing B3 role.json in init_chamber...")
    runner.run("b3_role_json_installed", test_b3_init_chamber_role.test_b3_role_json_installed_and_ignored)
    print("Testing B4 close-entry renumbering...")
    runner.run("b4_close_entry_renumber", test_b4_close_entry_renumber.test_b4_renumber_terbuka_directions)
    print("Testing B5 install-hooks CLI...")
    runner.run("b5_install_hooks", test_b5_install_hooks.test_b5_install_hooks_directions)
    print("Testing C1 snowline rotate...")
    runner.run("c1_rotate", test_c1_rotate.test_c1_rotate_directions)
    print("Testing C2 STATE.md validation...")
    runner.run("c2_state_validation", test_c2_state_validation.test_c2_state_validation_directions)

    print("Testing scope_guardian...")
    sg = test_scope_guardian.TestScopeCheck()
    runner.run("scope_guardian allowed_exact_match", sg.test_allowed_exact_match)
    runner.run("scope_guardian out_of_scope_warns_and_allows", sg.test_out_of_scope_warns_and_allows)
    runner.run("scope_guardian missing_scope_lock_warns_and_allows", sg.test_missing_scope_lock_warns_and_allows)
    runner.run("scope_guardian outside_project_boundary_blocked", sg.test_outside_project_boundary_blocked)
    runner.run("scope_guardian pattern_matching", sg.test_pattern_matching)
    runner.run("scope_guardian mode_ringan_allowed", sg.test_mode_ringan_allowed)

    print("Testing impact_analyzer...")
    runner.run("impact_analyzer core functions", test_impact_analysis)

    print("Testing context_mapper...")
    runner.run("context_mapper open_source_agents", test_context_mapper.test_context_mapper_open_source_agents)

    print("Testing rejections (Entry 6)...")
    runner.run("rejection project_guardian", test_rejections.test_project_guardian_rejection)
    runner.run("rejection quality_gate", test_rejections.test_quality_gate_rejection)
    runner.run("rejection loop_detector", test_rejections.test_loop_detector_rejection)
    runner.run("rejection rollback_enforcer", test_rejections.test_rollback_enforcer_rejection)
    runner.run("rejection auto_scaffolder", test_rejections.test_auto_scaffolder_rejection)
    runner.run("rejection import_fixer", test_rejections.test_import_fixer_rejection)

    print("Testing encoding bugfixes (Entry 9)...")
    runner.run("encoding code_finder, splicer, loop_detector", test_encoding.test_encoding_tools)
    runner.run("role_lock encoding support", test_role_lock.test_role_lock_encodings)

    print("Testing selective_reader (Entry 10)...")
    import test_selective_reader
    runner.run("selective_reader extracted_items", test_selective_reader.test_selective_reader_extracted_items)
    import test_entry_checker
    import test_close_entry
    print("Testing entry checker (Entry 27 & 32)...")
    runner.run("entry checker exceptions", test_entry_checker.test_exemption_line_numbers)
    runner.run("entry checker claim rejected", test_entry_checker.test_quantitative_claim_rejected)
    runner.run("entry checker claim accepted", test_entry_checker.test_quantitative_claim_accepted)
    runner.run("entry checker history validation", test_entry_checker.test_real_qa_entries)
    runner.run("entry checker cli exit code", test_entry_checker.test_cli_exit_code)
    runner.run("tl verdict rejected", test_entry_checker.test_tl_verdict_rejected)
    runner.run("tl verdict accepted", test_entry_checker.test_tl_verdict_accepted)
    runner.run("tl_qa verdict rejected", test_entry_checker.test_tl_qa_verdict_rejected)
    runner.run("tl_qa verdict accepted", test_entry_checker.test_tl_qa_verdict_accepted)
    runner.run("close entry success & table inject", test_close_entry.test_close_entry_success)
    runner.run("close entry rejections (space/prefix)", test_close_entry.test_close_entry_rejections)
    
    import test_chamber_integration
    print("Testing chamber integration (Entry 29)...")
    runner.run("chamber full lifecycle", test_chamber_integration.test_chamber_integration)

    import test_guardian_firebase
    print("Testing Guardian Firebase rules (Entry 28)...")
    runner.run("guardian firebase AIza", test_guardian_firebase.test_guardian_firebase)

    import test_version_sync
    print("Testing version sync...")
    runner.run("version sync across files", test_version_sync.test_version_sync)
    
    import test_native_checker_gen
    print("Testing native_checker_gen...")
    runner.run("native checker gen --apply", test_native_checker_gen.test_native_checker_gen_apply)

    import test_clean_sweeper
    print("Testing clean_sweeper...")
    runner.run("clean_sweeper clean_project", test_clean_sweeper.test_sweeper_clean_project)
    runner.run("clean_sweeper needs_cleanup", test_clean_sweeper.test_sweeper_needs_cleanup)
    
    import test_crash_decoder
    print("Testing crash_decoder...")
    # Manual runner mock for capsys
    class DummyCapsys:
        def readouterr(self):
            import sys
            class OutErr: pass
            ret = OutErr()
            ret.out = sys.stdout.getvalue() if hasattr(sys.stdout, "getvalue") else ""
            ret.err = ""
            return ret
    # We need to capture stdout for crash decoder
    def wrapper_valid():
        import io, sys
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        try:
            test_crash_decoder.test_crash_decoder_valid_log(DummyCapsys())
        finally:
            sys.stdout = old_stdout
    def wrapper_empty():
        import io, sys
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        try:
            test_crash_decoder.test_crash_decoder_empty_log(DummyCapsys())
        finally:
            sys.stdout = old_stdout
    runner.run("crash_decoder valid_log", wrapper_valid)
    runner.run("crash_decoder empty_log", wrapper_empty)

    runner.run("path_setup import", test_path_setup.test_import_does_not_prompt_or_write)
    runner.run("path_setup opt_out", test_path_setup.test_setup_path_opt_out)
    runner.run("path_setup no_answer", test_path_setup.test_setup_path_no_answer)
    runner.run("path_setup yes_answer", test_path_setup.test_setup_path_yes_answer)
    runner.run("path_setup exception", test_path_setup.test_setup_path_exception)
    runner.run("bom_guard test_no_bom_in_src", test_bom_guard.test_no_bom_in_src)
    runner.run("name_guard no_undefined", test_name_guard.test_no_undefined_names)
    runner.run("smoke_cli init test (help)", test_smoke_cli.test_smoke_init_test_help)
    runner.run("smoke_cli init (full)", test_smoke_cli.test_smoke_init_full)
    runner.run("smoke_cli update (full)", test_smoke_cli.test_smoke_update_full)
    runner.run("smoke_cli uninstall (help)", test_smoke_cli.test_smoke_uninstall_help)
    runner.run("smoke_cli reinstall (full)", test_smoke_cli.test_smoke_reinstall_full)
    runner.run("smoke_cli init_chamber (help)", test_smoke_cli.test_smoke_init_chamber_help)
    runner.run("smoke_cli context (full)", test_smoke_cli.test_smoke_context_full)
    runner.run("smoke_cli check-entry (help)", test_smoke_cli.test_smoke_check_entry_help)
    runner.run("smoke_cli add-entry (help)", test_smoke_cli.test_smoke_add_entry_help)
    runner.run("add_entry BOM removal", test_add_entry.test_add_entry_bom)
    runner.run("add_entry UTF-16 conversion", test_add_entry.test_add_entry_utf16)
    runner.run("add_entry invalid header rejection", test_add_entry.test_add_entry_invalid_header)
    runner.run("add_entry valid header", test_add_entry.test_add_entry_valid)
    
    runner.run("smoke_cli close-entry (help)", test_smoke_cli.test_smoke_close_entry_help)
    runner.run("smoke_cli rotate (help)", test_smoke_cli.test_smoke_rotate_help)
    runner.run("smoke_cli test-clone (help)", test_smoke_cli.test_smoke_test_clone_help)
    runner.run("smoke_cli setup-path (help)", test_smoke_cli.test_smoke_setup_path_help)
    runner.run("smoke_cli path (full)", test_smoke_cli.test_smoke_path_full)
    runner.run("smoke_cli status (full)", test_smoke_cli.test_smoke_status_full)
    runner.run("smoke_cli audit (help)", test_smoke_cli.test_smoke_audit_help)
    runner.run("smoke_cli install-hooks (help)", test_smoke_cli.test_smoke_install_hooks_help)

    runner.run("orphan_guard test_yatim", test_orphan_guard.test_tidak_ada_berkas_uji_yatim)
    runner.run("intercept_native bom_empty_payload", test_intercept_native.test_bom_empty_payload)
    runner.run("intercept_native missing_fields", test_intercept_native.test_missing_fields)
    runner.run("intercept_native malformed_json", test_intercept_native.test_malformed_json)
    runner.run("intercept_native missing_scope_lock", test_intercept_native.test_missing_scope_lock)
    runner.run("intercept_native in_and_out_of_scope", test_intercept_native.test_in_and_out_of_scope)

    import test_skills_structure
    runner.run("skills_structure test_skills_folder_rules", test_skills_structure.test_skills_folder_rules)


    import test_init_test
    runner.run("init_test creates_files", test_init_test.test_init_test_creates_files)
    runner.run("init_test rejects_overwrite", test_init_test.test_init_test_rejects_overwrite)
    runner.run("init_test force_overwrite", test_init_test.test_init_test_force_overwrite)

    success = runner.summary()

    if success:
        print("\nAll tests passed!")
        return 0
    else:
        print("\nSome tests failed.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
