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
            
        # Create another firebase file with Bearer token (should NOT be downgraded)
        json_file = os.path.join(temp_dir, 'google-services.json')
        with open(json_file, 'w', encoding='utf-8') as f:
            f.write('{"token": "Bearer y2.SOME_FAKE_BEARER_TOKEN"}')
            
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
        
        lines = output.splitlines()
        
        main_lines = [b for b in lines if 'main.dart' in b]
        assert main_lines, "main.dart not found in output"
        assert "[CRITICAL]" in main_lines[0], f"main.dart severity should be CRITICAL, got: {main_lines[0]}"
        
        firebase_lines = [b for b in lines if 'firebase_options.dart' in b]
        assert firebase_lines, "firebase_options.dart not found in output"
        assert "[HIGH]" in firebase_lines[0], f"firebase_options.dart severity should be HIGH, got: {firebase_lines[0]}"
        
        json_lines = [b for b in lines if 'google-services.json' in b]
        assert json_lines, "google-services.json not found in output"
        assert "[CRITICAL]" in json_lines[0], f"google-services.json with Bearer should be CRITICAL, got: {json_lines[0]}"

if __name__ == '__main__':
    test_guardian_firebase()
