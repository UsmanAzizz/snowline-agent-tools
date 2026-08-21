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
    
    assert result.returncode == 0, f"Context mapper failed with error: {result.stderr}"
    
    output = result.stdout
    assert "scope_check.py" not in output.split("Orphans")[1] if "Orphans" in output else "scope_check.py" not in output, "scope_check.py should NOT be in orphans"
    
def test_context_mapper_performance_4311():
    # Simulate a project with 4311 files
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create some files
        num_files = 4311
        for i in range(num_files):
            filepath = os.path.join(tmpdir, f"file{i}.js")
            with open(filepath, 'w') as f:
                # Add a few imports
                if i > 0:
                    f.write(f"import {{ something }} from './file{i-1}';\n")
        
        # Run context mapper
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cm_script = os.path.join(repo_root, "src", "snowline", "templates", "skills", "context_mapper", "context_mapper.py")
        
        start_time = time.time()
        result = subprocess.run([sys.executable, cm_script], cwd=tmpdir, capture_output=True, text=True, encoding='utf-8')
        end_time = time.time()
        
        assert result.returncode == 0
        elapsed = end_time - start_time
        # Make sure it runs under 120 seconds (Windows filesystem overhead)
        assert elapsed < 120.0, f"Performance test failed, took {elapsed:.2f}s"
        
        # We can extract the reported time from the script
        print(f"  [INFO] 4311 files simulation took: {elapsed:.2f}s")
