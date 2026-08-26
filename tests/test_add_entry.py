import tempfile
import os
import sys
import subprocess
from pathlib import Path


def run_cli(args, cwd=None, env=None):
    exe = sys.executable
    cmd = [exe, '-m', 'snowline.cli'] + args
    res = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True)
    if res.returncode != 0:
        raise AssertionError(f"Command {' '.join(args)} failed with output:\n{res.stderr}\n{res.stdout}")
    return res

def run_cli_expect_fail(args, cwd=None, env=None):
    exe = sys.executable
    cmd = [exe, '-m', 'snowline.cli'] + args
    res = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True)
    if res.returncode == 0:
        raise AssertionError(f"Command {' '.join(args)} should have failed but succeeded!")
    return res

def test_add_entry_bom():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        os.makedirs(tmp_path / ".agents" / "chamber")
        connector_path = tmp_path / ".agents" / "chamber" / "connector.md"
        connector_path.write_text("INIT", encoding="utf-8")
        
        test_file = tmp_path / "test_input.md"
        content = "\ufeff# PM -> TL: Title\nContent"
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        env = os.environ.copy()
        env['PYTHONPATH'] = str(Path('.').resolve() / 'src') + os.pathsep + env.get('PYTHONPATH', '')
        
        run_cli(['add-entry', '--from-file', str(test_file)], cwd=tmpdir, env=env)
        
        with open(connector_path, "r", encoding="utf-8") as f:
            final_content = f.read()
            assert "\ufeff" not in final_content[4:] # past INIT

def test_add_entry_utf16():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        os.makedirs(tmp_path / ".agents" / "chamber")
        connector_path = tmp_path / ".agents" / "chamber" / "connector.md"
        connector_path.write_text("INIT", encoding="utf-8")
        
        test_file = tmp_path / "test_input.md"
        test_file.write_text("# PM -> TL: Title\nContent", encoding="utf-16")
        
        env = os.environ.copy()
        env['PYTHONPATH'] = str(Path('.').resolve() / 'src') + os.pathsep + env.get('PYTHONPATH', '')
        
        run_cli(['add-entry', '--from-file', str(test_file)], cwd=tmpdir, env=env)
        
        with open(connector_path, "rb") as f:
            final_bytes = f.read()
            assert b'\x00' not in final_bytes # No null bytes from utf-16

def test_add_entry_invalid_header():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        os.makedirs(tmp_path / ".agents" / "chamber")
        connector_path = tmp_path / ".agents" / "chamber" / "connector.md"
        connector_path.write_text("INIT", encoding="utf-8")
        
        orig_size = os.path.getsize(connector_path)
        
        test_file = tmp_path / "test_input.md"
        test_file.write_text("Wrong Header\nContent", encoding="utf-8")
        
        env = os.environ.copy()
        env['PYTHONPATH'] = str(Path('.').resolve() / 'src') + os.pathsep + env.get('PYTHONPATH', '')
        
        run_cli_expect_fail(['add-entry', '--from-file', str(test_file)], cwd=tmpdir, env=env)
        
        new_size = os.path.getsize(connector_path)
        assert orig_size == new_size

def test_add_entry_valid():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        os.makedirs(tmp_path / ".agents" / "chamber")
        connector_path = tmp_path / ".agents" / "chamber" / "connector.md"
        connector_path.write_text("INIT", encoding="utf-8")
        
        test_file = tmp_path / "test_input.md"
        test_file.write_text("# PM -> TL: Valid Title\nContent", encoding="utf-8")
        
        env = os.environ.copy()
        env['PYTHONPATH'] = str(Path('.').resolve() / 'src') + os.pathsep + env.get('PYTHONPATH', '')
        
        run_cli(['add-entry', '--from-file', str(test_file)], cwd=tmpdir, env=env)
        
        with open(connector_path, "r", encoding="utf-8") as f:
            final_content = f.read()
            assert "Valid Title" in final_content