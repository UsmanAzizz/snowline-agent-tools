"""
Simple test runner for Snowline Agent Tools
Run with: python tests/run_tests.py
"""
import os
import sys
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
sys.path.insert(0, str(AKAR))
sys.path.insert(0, str(SKILLS))

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
        except AssertionError as e:
            self.failed += 1
            self.results.append(f"  [FAIL] {name}: {e}")
        except Exception as e:
            self.failed += 1
            self.results.append(f"  [ERROR] {name}: {e}")

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
        assert 'test.txt' in result
        assert '📄' not in result
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

    print("Testing scope_guardian...")
    sg = test_scope_guardian.TestScopeCheck()
    runner.run("scope_guardian allowed_exact_match", sg.test_allowed_exact_match)
    runner.run("scope_guardian blocked_out_of_scope", sg.test_blocked_out_of_scope)
    runner.run("scope_guardian missing_scope_lock", sg.test_missing_scope_lock)
    runner.run("scope_guardian pattern_matching", sg.test_pattern_matching)

    print("Testing impact_analyzer...")
    runner.run("impact_analyzer core functions", test_impact_analysis)

    print("Testing context_mapper...")
    runner.run("context_mapper open_source_agents", test_context_mapper.test_context_mapper_open_source_agents)

    success = runner.summary()

    if success:
        print("\nAll tests passed!")
        return 0
    else:
        print("\nSome tests failed.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
