"""
Unit tests for tree_gen module
"""
import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from tree_gen.tree_gen import (
    parse_gitignore,
    is_ignored,
    generate_tree,
    generate_simple_tree,
    get_tree_stats
)

class TestParseGitignore:
    """Tests for parse_gitignore function"""

    def test_returns_list(self):
        """Should return a list of patterns"""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = parse_gitignore(tmpdir)
            assert isinstance(result, list)
            assert len(result) > 0

    def test_includes_defaults(self):
        """Should include default patterns"""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = parse_gitignore(tmpdir)
            assert '.git' in result
            assert 'node_modules' in result

    def test_parses_gitignore(self):
        """Should parse .gitignore file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            gitignore = os.path.join(tmpdir, '.gitignore')
            with open(gitignore, 'w') as f:
                f.write('# Comment\n')
                f.write('*.log\n')
                f.write('temp/\n')

            result = parse_gitignore(tmpdir)
            assert '*.log' in result
            assert 'temp' in result


class TestIsIgnored:
    """Tests for is_ignored function"""

    def test_ignores_git(self):
        """Should ignore .git directory"""
        patterns = ['.git']
        assert is_ignored('.git', patterns) == True

    def test_ignores_node_modules(self):
        """Should ignore node_modules"""
        patterns = ['node_modules']
        assert is_ignored('node_modules', patterns) == True

    def test_respects_patterns(self):
        """Should respect glob patterns"""
        patterns = ['*.log']
        assert is_ignored('error.log', patterns) == True
        assert is_ignored('file.txt', patterns) == False

    def test_does_not_ignore_normal_files(self):
        """Should not ignore normal files"""
        patterns = ['.git', 'node_modules']
        assert is_ignored('App.jsx', patterns) == False
        assert is_ignored('utils.py', patterns) == False


class TestGenerateTree:
    """Tests for generate_tree function"""

    def test_returns_string(self):
        """Should return a string"""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = generate_tree(tmpdir, max_depth=1)
            assert isinstance(result, str)

    def test_includes_entries(self):
        """Should include directory entries"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files
            open(os.path.join(tmpdir, 'file1.txt'), 'w').close()
            os.makedirs(os.path.join(tmpdir, 'subdir'))

            result = generate_tree(tmpdir, max_depth=1)
            assert 'file1.txt' in result
            assert 'subdir' in result

    def test_respects_max_depth(self):
        """Should respect max_depth parameter"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create nested structure
            level1 = os.path.join(tmpdir, 'level1')
            level2 = os.path.join(level1, 'level2')
            os.makedirs(level2)
            open(os.path.join(level2, 'deep.txt'), 'w').close()

            # With max_depth=1, should show level1 but not level2
            result = generate_tree(tmpdir, max_depth=1)
            assert 'level1' in result
            assert 'max depth reached' in result


class TestGenerateSimpleTree:
    """Tests for generate_simple_tree function"""

    def test_returns_string(self):
        """Should return a string"""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = generate_simple_tree(tmpdir)
            assert isinstance(result, str)

    def test_no_icons(self):
        """Should not include folder/file icons"""
        with tempfile.TemporaryDirectory() as tmpdir:
            open(os.path.join(tmpdir, 'test.txt'), 'w').close()

            result = generate_simple_tree(tmpdir)
            assert 'test.txt' in result
            assert '📄' not in result
            assert '📁' not in result


class TestGetTreeStats:
    """Tests for get_tree_stats function"""

    def test_returns_dict(self):
        """Should return a dictionary"""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = get_tree_stats(tmpdir)
            assert isinstance(result, dict)

    def test_has_required_keys(self):
        """Should have required keys"""
        with tempfile.TemporaryDirectory() as tmpdir:
            open(os.path.join(tmpdir, 'file1.txt'), 'w').close()
            open(os.path.join(tmpdir, 'file2.js'), 'w').close()
            os.makedirs(os.path.join(tmpdir, 'subdir'))

            result = get_tree_stats(tmpdir)
            assert 'total_files' in result
            assert 'total_dirs' in result
            assert 'file_types' in result

    def test_counts_files(self):
        """Should count files correctly"""
        with tempfile.TemporaryDirectory() as tmpdir:
            open(os.path.join(tmpdir, 'file1.txt'), 'w').close()
            open(os.path.join(tmpdir, 'file2.txt'), 'w').close()

            result = get_tree_stats(tmpdir)
            assert result['total_files'] == 2

    def test_file_types(self):
        """Should track file types"""
        with tempfile.TemporaryDirectory() as tmpdir:
            open(os.path.join(tmpdir, 'file1.js'), 'w').close()
            open(os.path.join(tmpdir, 'file2.jsx'), 'w').close()
            open(os.path.join(tmpdir, 'file3.py'), 'w').close()

            result = get_tree_stats(tmpdir)
            assert result['file_types'].get('.js', 0) == 1
            assert result['file_types'].get('.jsx', 0) == 1
            assert result['file_types'].get('.py', 0) == 1
