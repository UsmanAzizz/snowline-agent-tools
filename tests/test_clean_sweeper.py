import os
import sys
import tempfile
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/snowline/templates/skills/clean_sweeper')))
import sweeper

def test_sweeper_clean_project():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Buat project bersih
        os.makedirs(os.path.join(tmpdir, 'src'))
        with open(os.path.join(tmpdir, 'src', 'main.py'), 'w') as f:
            f.write("print('hello')\n")
        
        residue, todo, comments, scanned, skipped = sweeper.sweep(tmpdir)
        assert len(residue) == 0, "Project bersih seharusnya tidak ada file residu"
        assert todo == 0, "Project bersih seharusnya tidak ada TODO"
        assert len(comments) == 0, "Project bersih seharusnya tidak ada komentar besar"

def test_sweeper_needs_cleanup():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Buat residu
        os.makedirs(os.path.join(tmpdir, 'backup'))
        with open(os.path.join(tmpdir, 'database.db'), 'w') as f:
            f.write("sqlite data")
        with open(os.path.join(tmpdir, 'main.py'), 'w') as f:
            f.write("# TODO: fix this\n")
            f.write("# comment 1\n# comment 2\n# comment 3\n# comment 4\n# comment 5\n# comment 6\n# comment 7\n# comment 8\n")
        
        residue, todo, comments, scanned, skipped = sweeper.sweep(tmpdir)
        
        assert todo == 1, "Gagal mendeteksi TODO"
        assert len(comments) == 1, "Gagal mendeteksi blok komentar besar"
        
        db_found = any(r['type'] == 'local_sqlite' for r in residue)
        backup_found = any(r['type'] == 'backup_folder' for r in residue)
        
        assert db_found, "Gagal mendeteksi database lokal"
        assert backup_found, "Gagal mendeteksi backup folder"
