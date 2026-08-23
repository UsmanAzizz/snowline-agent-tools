import os
import sys
from pathlib import Path
import tempfile
import subprocess

def test_guardian_firebase():
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create normal file with AIza
        normal_file = os.path.join(temp_dir, 'main.dart')
        with open(normal_file, 'w', encoding='utf-8') as f:
            f.write('String key = "AIzaSyD_SOME_FAKE_KEY_12345678901234567";')
            
        # Create firebase file with AIza
        firebase_file = os.path.join(temp_dir, 'firebase_options.dart')
        with open(firebase_file, 'w', encoding='utf-8') as f:
            f.write('String key = "AIzaSyD_SOME_FAKE_KEY_12345678901234567";')
            
        # Run guardian
        guardian_script = Path(__file__).parent.parent / 'src' / 'snowline' / 'templates' / 'skills' / 'project_guardian' / 'guardian.py'
        
        env = os.environ.copy()
        env['PYTHONPATH'] = str(Path(__file__).parent.parent / 'src') + os.pathsep + env.get('PYTHONPATH', '')
        
        result = subprocess.run(
            [sys.executable, str(guardian_script)],
            capture_output=True,
            text=True,
            cwd=temp_dir,
            env=env
        )
        
        output = result.stdout + result.stderr
        print("GUARDIAN OUTPUT:\n", output)
        
        assert "[CRITICAL]" in output and "main.dart" in output, "main.dart not detected as CRITICAL"
        assert "[HIGH]" in output and "firebase_options.dart" in output, "firebase_options.dart not detected as HIGH"

if __name__ == '__main__':
    test_guardian_firebase()
