import unittest
import os
import shutil
import tempfile
import subprocess
import json

class TestImpactAnalyzer(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.target_py = os.path.join(self.test_dir, 'target.py')
        with open(self.target_py, 'w') as f:
            f.write("def foo(): pass\n")

        # Create a Python file importing the target
        self.dependant_py = os.path.join(self.test_dir, 'dependant.py')
        with open(self.dependant_py, 'w') as f:
            f.write("from a.b.c import target\n")
            
        # Create a Python file indirectly importing the target (Level 2)
        self.indirect_py = os.path.join(self.test_dir, 'indirect.py')
        with open(self.indirect_py, 'w') as f:
            f.write("import dependant\n")

        # Create a backup file importing the target
        backup_dir = os.path.join(self.test_dir, '.backup_replace')
        os.makedirs(backup_dir)
        self.backup_py = os.path.join(backup_dir, 'dependant.py')
        with open(self.backup_py, 'w') as f:
            f.write("from a.b.c import target\n")
            
        self.analyzer_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'snowline', 'templates', 'skills', 'impact_analyzer', 'analyzer.py'))

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_impact_analysis(self):
        cmd = ["python", self.analyzer_path, self.target_py, self.test_dir, "--json", "--depth", "2"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, f"Analyzer failed: {result.stderr}")
        
        output = json.loads(result.stdout)
        
        # Test Cacat 1: Ensure dependant.py is found (unquoted python import)
        level_1 = [os.path.basename(f) for f in output['levels'][0]]
        self.assertIn('dependant.py', level_1)
        
        # Test Cacat 2: Ensure backup file is ignored
        for level in output['levels']:
            for f in level:
                self.assertNotIn('.backup_replace', f)
                
        # Test Cacat 3: Ensure depth works (Level 2 should find indirect.py)
        level_2 = [os.path.basename(f) for f in output['levels'][1]]
        self.assertIn('indirect.py', level_2)

if __name__ == '__main__':
    unittest.main()
