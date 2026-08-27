"""
Unit tests for scope_guardian module
"""
import os
import sys
import tempfile
import json
from pathlib import Path

# Add skills directory to path
skills_path = Path(__file__).parent.parent / "src" / "snowline" / "templates" / "skills"
sys.path.insert(0, str(skills_path))
from scope_guardian.scripts.scope_check import check_scope, is_light_mode

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
                    check_scope(os.path.relpath(target_file, tmpdir))
                    assert True  # If no exception, check passed
                except SystemExit as e:
                    if e.code == 0:
                        assert True
                    else:
                        assert False, f"Expected exit code 0, got {e.code}"
            finally:
                os.chdir(original_cwd)

    def test_out_of_scope_warns_and_allows(self):
        """(A1.a) Should warn but allow files out of scope"""
        with tempfile.TemporaryDirectory() as tmpdir:
            agents_dir = os.path.join(tmpdir, '.agents')
            os.makedirs(agents_dir)

            scope_lock = {
                "task": "Update Button component",
                "allowed_files": ["src/components/Button.jsx"],
                "allowed_patterns": []
            }

            with open(os.path.join(agents_dir, 'scope_lock.json'), 'w') as f:
                json.dump(scope_lock, f)

            os.makedirs(os.path.join(tmpdir, 'src', 'other'))
            target_file = os.path.join(tmpdir, 'src', 'other', 'Other.jsx')
            with open(target_file, 'w') as f:
                f.write('// Other component')

            original_cwd = os.getcwd()
            os.chdir(tmpdir)

            try:
                res = check_scope(os.path.relpath(target_file, tmpdir))
                # res is (allowed, in_scope, task) -> allowed is True, in_scope is False
                assert res[0] is True and res[1] is False
            finally:
                os.chdir(original_cwd)

    def test_missing_scope_lock_warns_and_allows(self):
        """(A1.f) Should warn but allow when scope_lock.json is missing"""
        with tempfile.TemporaryDirectory() as tmpdir:
            target_file = os.path.join(tmpdir, 'test.js')
            with open(target_file, 'w') as f:
                f.write('// test')

            original_cwd = os.getcwd()
            os.chdir(tmpdir)

            try:
                res = check_scope(os.path.relpath(target_file, tmpdir))
                assert res[0] is True
            finally:
                os.chdir(original_cwd)

    def test_outside_project_boundary_blocked(self):
        """(A1.e) Should block files outside project root"""
        with tempfile.TemporaryDirectory() as tmpdir:
            agents_dir = os.path.join(tmpdir, '.agents')
            os.makedirs(agents_dir)
            with open(os.path.join(agents_dir, 'scope_lock.json'), 'w') as f:
                json.dump({"task": "test", "allowed_files": []}, f)

            outside_file = os.path.abspath(os.path.join(tmpdir, "..", "outside.txt"))
            original_cwd = os.getcwd()
            os.chdir(tmpdir)
            try:
                try:
                    check_scope(outside_file)
                    assert False, "Expected SystemExit for outside project boundary"
                except SystemExit as e:
                    assert e.code == 1
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
                    check_scope(os.path.relpath(target_file, tmpdir))
                    assert True
                except SystemExit as e:
                    if e.code == 0:
                        assert True  # Pattern matched
                    else:
                        assert False
            finally:
                os.chdir(original_cwd)

    def test_mode_ringan_allowed(self):
        """(a) mode_ringan.json with {"mode_ringan": true} enables light mode.
        (b) missing marker -> mode ringan OFF.
        (c) mode_ringan.json with unrecognized content -> mode ringan OFF with warning.
        (d) old marker name -> mode ringan OFF."""
        # Arah a: mode_ringan.json valid -> lolos tanpa scope_lock.json
        with tempfile.TemporaryDirectory() as tmpdir:
            agents_dir = os.path.join(tmpdir, '.agents')
            os.makedirs(agents_dir)
            with open(os.path.join(agents_dir, 'mode_ringan.json'), 'w', encoding='utf-8') as f:
                json.dump({"mode_ringan": True}, f)

            target_file = os.path.join(tmpdir, 'src', 'components', 'Button.jsx')
            os.makedirs(os.path.dirname(target_file), exist_ok=True)
            with open(target_file, 'w') as f:
                f.write('// Button')

            original_cwd = os.getcwd()
            os.chdir(tmpdir)
            try:
                assert is_light_mode(tmpdir) is True
                assert check_scope(os.path.relpath(target_file, tmpdir))[0] is True
            finally:
                os.chdir(original_cwd)

        # Arah b: berkas tidak ada -> MATI (check_scope False)
        with tempfile.TemporaryDirectory() as tmpdir:
            agents_dir = os.path.join(tmpdir, '.agents')
            os.makedirs(agents_dir)
            assert is_light_mode(tmpdir) is False

        # Arah c: berkas ada tetapi format salah -> MATI
        with tempfile.TemporaryDirectory() as tmpdir:
            agents_dir = os.path.join(tmpdir, '.agents')
            os.makedirs(agents_dir)
            with open(os.path.join(agents_dir, 'mode_ringan.json'), 'w', encoding='utf-8') as f:
                json.dump({"mode": "blah"}, f)
            assert is_light_mode(tmpdir) is False

        # Arah d: nama lama -> MATI
        with tempfile.TemporaryDirectory() as tmpdir:
            agents_dir = os.path.join(tmpdir, '.agents')
            os.makedirs(agents_dir)
            with open(os.path.join(agents_dir, 'light_mode'), 'w', encoding='utf-8') as f:
                f.write('')
            assert is_light_mode(tmpdir) is False
