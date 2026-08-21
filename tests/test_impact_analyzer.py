import os
import shutil
import tempfile
import subprocess
import json

def test_impact_analysis():
    test_dir = tempfile.mkdtemp()
    try:
        target_py = os.path.join(test_dir, 'target.py')
        with open(target_py, 'w') as f:
            f.write("def foo(): pass\n")

        # Create a Python file importing the target
        dependant_py = os.path.join(test_dir, 'dependant.py')
        with open(dependant_py, 'w') as f:
            f.write("from a.b.c import target\n")
            
        # Create a Python file indirectly importing the target (Level 2)
        indirect_py = os.path.join(test_dir, 'indirect.py')
        with open(indirect_py, 'w') as f:
            f.write("import dependant\n")

        # Create a backup file importing the target
        backup_dir = os.path.join(test_dir, '.backup_replace')
        os.makedirs(backup_dir)
        backup_py = os.path.join(backup_dir, 'dependant.py')
        with open(backup_py, 'w') as f:
            f.write("from a.b.c import target\n")
            
        analyzer_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'snowline', 'templates', 'skills', 'impact_analyzer', 'analyzer.py'))

        cmd = ["python", analyzer_path, target_py, test_dir, "--json", "--depth", "2"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        assert result.returncode == 0, f"Analyzer failed: {result.stderr}"
        
        output = json.loads(result.stdout)
        
        # Test Cacat 1: Ensure dependant.py is found (unquoted python import)
        level_1 = [os.path.basename(f) for f in output['levels'][0]]
        assert 'dependant.py' in level_1, "dependant.py not found in level 1"
        
        # Test Cacat 2: Ensure backup file is ignored
        for level in output['levels']:
            for f in level:
                assert '.backup_replace' not in f, f"Backup file found in usages: {f}"
                
        # Test Cacat 3: Ensure depth works (Level 2 should find indirect.py)
        level_2 = [os.path.basename(f) for f in output['levels'][1]]
        assert 'indirect.py' in level_2, "indirect.py not found in level 2"
    finally:
        shutil.rmtree(test_dir)
