import os
import sys
import tempfile
import subprocess
from pathlib import Path

def test_chamber_integration():
    src_path = Path(__file__).parent.parent / 'src'
    cli_path = src_path / 'snowline' / 'cli.py'
    
    env = os.environ.copy()
    env['PYTHONPATH'] = str(src_path) + os.pathsep + env.get('PYTHONPATH', '')
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Run init
        subprocess.run([sys.executable, str(cli_path), "init", "--apply"], cwd=temp_dir, env=env, check=True)
        # Run init_chamber
        subprocess.run([sys.executable, str(cli_path), "init_chamber", "--apply"], cwd=temp_dir, env=env, check=True)
        
        # Verify it created .agents/chamber
        chamber_dir = Path(temp_dir) / ".agents" / "chamber"
        assert chamber_dir.exists(), ".agents/chamber was not created"
        assert (chamber_dir / "connector.md").exists(), "connector.md was not created"
        
        # Add an entry to connector
        connector_path = chamber_dir / "connector.md"
        with open(connector_path, 'a', encoding='utf-8') as f:
            f.write("\n# Test Entry\nSelesai!\n```\n$ echo ok\nok\n```\n")
            
        # Run check-entry
        result_check = subprocess.run([sys.executable, str(cli_path), "check-entry", str(connector_path)], cwd=temp_dir, env=env, capture_output=True, text=True)
        assert result_check.returncode == 0, f"check-entry failed: {result_check.stderr}"
        
        # Run context
        result_ctx = subprocess.run([sys.executable, str(cli_path), "context"], cwd=temp_dir, env=env, capture_output=True, text=True)
        assert result_ctx.returncode == 0, f"context failed: {result_ctx.stderr}"
        
        # Run close-entry
        result_close = subprocess.run([sys.executable, str(cli_path), "close-entry", "test_topic"], cwd=temp_dir, env=env, capture_output=True, text=True)
        assert result_close.returncode == 0, f"close-entry failed: {result_close.stderr} {result_close.stdout}"
        
        # Verify history
        history_file = chamber_dir / "history" / "test_topic" / "01-test_topic.md"
        assert history_file.exists(), "History file not created"
