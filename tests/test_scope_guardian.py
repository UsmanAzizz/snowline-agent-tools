"""
Unit tests for scope_guardian module
"""
import os
import sys
import tempfile
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from scope_guardian.scripts.scope_check import check_scope

class TestScopeCheck:
    """Tests for scope_check function"""

    def test_allowed_exact_match(self):
        """Should allow exact file match"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create .agents directory and scope_lock.json
            agents_dir = os.path.join(tmpdir, '.agents')
            os.makedirs(agents_dir)

            scope_lock = {
                "task": "Update Button component",
                "allowed_files": ["src/components/Button.jsx"],
                "allowed_patterns": []
            }

            with open(os.path.join(agents_dir, 'scope_lock.json'), 'w') as f:
                json.dump(scope_lock, f)

            # Create the target file
            os.makedirs(os.path.join(tmpdir, 'src', 'components'))
            target_file = os.path.join(tmpdir, 'src', 'components', 'Button.jsx')
            with open(target_file, 'w') as f:
                f.write('// Button component')

            # Change to temp directory
            original_cwd = os.getcwd()
            os.chdir(tmpdir)

            try:
                # Should exit with code 0 (ALLOWED)
                try:
                    check_scope(target_file)
                    assert True  # If no exception, check passed
                except SystemExit as e:
                    if e.code == 0:
                        assert True
                    else:
                        assert False, f"Expected exit code 0, got {e.code}"
            finally:
                os.chdir(original_cwd)

    def test_blocked_out_of_scope(self):
        """Should block files not in scope"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create .agents directory and scope_lock.json
            agents_dir = os.path.join(tmpdir, '.agents')
            os.makedirs(agents_dir)

            scope_lock = {
                "task": "Update Button component",
                "allowed_files": ["src/components/Button.jsx"],
                "allowed_patterns": []
            }

            with open(os.path.join(agents_dir, 'scope_lock.json'), 'w') as f:
                json.dump(scope_lock, f)

            # Create a file OUT of scope
            os.makedirs(os.path.join(tmpdir, 'src', 'other'))
            target_file = os.path.join(tmpdir, 'src', 'other', 'Other.jsx')
            with open(target_file, 'w') as f:
                f.write('// Other component')

            # Change to temp directory
            original_cwd = os.getcwd()
            os.chdir(tmpdir)

            try:
                # Should exit with code 1 (BLOCKED)
                try:
                    check_scope(target_file)
                    assert False, "Expected SystemExit"
                except SystemExit as e:
                    if e.code == 1:
                        assert True  # Blocked as expected
                    else:
                        assert False, f"Expected exit code 1, got {e.code}"
            finally:
                os.chdir(original_cwd)

    def test_missing_scope_lock(self):
        """Should block if scope_lock.json is missing"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # No .agents directory
            target_file = os.path.join(tmpdir, 'test.js')

            original_cwd = os.getcwd()
            os.chdir(tmpdir)

            try:
                try:
                    check_scope(target_file)
                    assert False, "Expected SystemExit"
                except SystemExit as e:
                    if e.code == 1:
                        assert True  # Blocked as expected
            finally:
                os.chdir(original_cwd)

    def test_pattern_matching(self):
        """Should match patterns in allowed_patterns"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create .agents directory and scope_lock.json
            agents_dir = os.path.join(tmpdir, '.agents')
            os.makedirs(agents_dir)

            scope_lock = {
                "task": "Update all components",
                "allowed_files": [],
                "allowed_patterns": ["src/components/*.jsx"]
            }

            with open(os.path.join(agents_dir, 'scope_lock.json'), 'w') as f:
                json.dump(scope_lock, f)

            # Create target file matching pattern
            os.makedirs(os.path.join(tmpdir, 'src', 'components'))
            target_file = os.path.join(tmpdir, 'src', 'components', 'Button.jsx')
            with open(target_file, 'w') as f:
                f.write('// Button')

            original_cwd = os.getcwd()
            os.chdir(tmpdir)

            try:
                try:
                    check_scope(target_file)
                    assert True
                except SystemExit as e:
                    if e.code == 0:
                        assert True  # Pattern matched
                    else:
                        assert False
            finally:
                os.chdir(original_cwd)
