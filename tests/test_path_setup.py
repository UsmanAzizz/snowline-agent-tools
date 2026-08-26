import os
import sys
import subprocess
from unittest.mock import patch, MagicMock

def test_import_does_not_prompt_or_write():
    env = os.environ.copy()
    env['PYTHONPATH'] = str(os.path.abspath('src'))
    if 'SNOWLINE_NO_PATH_SETUP' in env:
        del env['SNOWLINE_NO_PATH_SETUP']
    result = subprocess.run([sys.executable, "-c", "import snowline"], 
                            capture_output=True, text=True, input="", env=env)
    assert result.returncode == 0, f"Import gagal atau hang: {result.stderr}"
    assert "[?]" not in result.stdout, "Seharusnya tidak ada prompt"

def test_setup_path_opt_out():
    if sys.platform != 'win32':
        import unittest
        raise unittest.SkipTest('Windows only')
    import snowline
    env = os.environ.copy()
    env["SNOWLINE_NO_PATH_SETUP"] = "1"
    
    with patch.dict(os.environ, env):
        with patch('builtins.input') as mock_input, \
             patch('shutil.copy2') as mock_copy, \
             patch('winreg.OpenKey') as mock_open:
            snowline.setup_path()
            mock_input.assert_not_called()
            mock_copy.assert_not_called()
            mock_open.assert_not_called()

def test_setup_path_no_answer():
    if sys.platform != 'win32':
        import unittest
        raise unittest.SkipTest('Windows only')
    import snowline
    env = os.environ.copy()
    if 'SNOWLINE_NO_PATH_SETUP' in env:
        del env['SNOWLINE_NO_PATH_SETUP']
    
    with patch.dict(os.environ, env):
        with patch('builtins.input', return_value=''), \
             patch('shutil.copy2'), \
             patch('winreg.OpenKey') as mock_open_key, \
             patch('winreg.QueryValueEx', return_value=("old_path", 1)), \
             patch('winreg.SetValueEx') as mock_set_value, \
             patch('winreg.CloseKey'), \
             patch('snowline._update_profiles') as mock_update_profiles, \
             patch('ctypes.windll.user32.SendMessageTimeoutW') as mock_send_message:
            snowline.setup_path()
            mock_set_value.assert_not_called()
            mock_update_profiles.assert_not_called()

def test_setup_path_yes_answer():
    if sys.platform != 'win32':
        import unittest
        raise unittest.SkipTest('Windows only')
    import snowline
    env = os.environ.copy()
    if 'SNOWLINE_NO_PATH_SETUP' in env:
        del env['SNOWLINE_NO_PATH_SETUP']
    
    with patch.dict(os.environ, env):
        with patch('builtins.input', return_value='y'), \
             patch('shutil.copy2'), \
             patch('winreg.OpenKey') as mock_open_key, \
             patch('winreg.QueryValueEx', return_value=("old_path", 1)), \
             patch('winreg.SetValueEx') as mock_set_value, \
             patch('winreg.CloseKey'), \
             patch('snowline._update_profiles') as mock_update_profiles, \
             patch('ctypes.windll.user32.SendMessageTimeoutW') as mock_send_message:
            snowline.setup_path()
            mock_set_value.assert_called_once()
            mock_update_profiles.assert_called_once()
def test_setup_path_exception():
    if sys.platform != 'win32':
        import unittest
        raise unittest.SkipTest('Windows only')
    import snowline
    env = os.environ.copy()
    if 'SNOWLINE_NO_PATH_SETUP' in env:
        del env['SNOWLINE_NO_PATH_SETUP']
    
    with patch.dict(os.environ, env):
        with patch('builtins.input', return_value='y'), \
             patch('shutil.copy2'), \
             patch('winreg.OpenKey') as mock_open_key, \
             patch('winreg.QueryValueEx', return_value=("old_path", 1)), \
             patch('winreg.SetValueEx', side_effect=PermissionError("Akses ditolak")), \
             patch('winreg.CloseKey'), \
             patch('sys.stdout', new_callable=__import__('io').StringIO) as mock_stdout:
            snowline.setup_path()
            # Harus mencetak galat, bukan diam
            out = mock_stdout.getvalue()
            assert "[!] Gagal mengatur PATH" in out, "Tidak mencetak galat saat gagal menulis registry"
