import os
import sys
import subprocess
import tempfile
import time
from pathlib import Path

def test_context_mapper_open_source_agents():
    # Run context mapper on the current repository (open_source_agents)
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cm_script = os.path.join(repo_root, "src", "snowline", "templates", "skills", "context_mapper", "context_mapper.py")
    
    result = subprocess.run([sys.executable, cm_script], cwd=repo_root, capture_output=True, text=True, encoding='utf-8')
    
    assert result.returncode == 99, f"Context mapper failed with error: {result.stderr}"
    
    output = result.stdout
    # Orphans should be small, specifically loop_detector and companions should not be marked as orphans
    orphans_section = output.split("Orphans (Kandidat Kode Mati)")[1] if "Orphans (Kandidat Kode Mati)" in output else ""
    
    assert "scope_check.py" not in orphans_section, "scope_check.py should NOT be in orphans"
    
    # Extract list of orphans
    orphan_lines = [line for line in orphans_section.split('\n') if line.strip().startswith('- `')]
    assert len(orphan_lines) <= 5, f"Orphans count should be small, but got {len(orphan_lines)}: {orphan_lines}"
