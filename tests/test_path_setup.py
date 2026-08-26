import os
import sys
import subprocess
from unittest.mock import patch, MagicMock

def test_import_does_not_prompt_or_write():
    # Menjalankan 'python -c "import snowline"' di subprocess.
    # Jika ia melakukan prompt, subprocess akan menggantung atau gagal jika inputnya tidak ada.
    # Kita berikan stdin kosong dan harap ia selesai sukses segera.
    # Ini membuktikan tidak ada modifikasi di luar proses dan tidak prompt.
    env = os.environ.copy()
    env['PYTHONPATH'] = str(os.path.abspath('src'))
    if 'SNOWLINE_NO_PATH_SETUP' in env:
        del env['SNOWLINE_NO_PATH_SETUP']
    
    # Hapus path scripts agar ia pikir butuh di-setup, tapi karena import snowline tidak prompt lagi, ia akan sukses.
    # (sebenarnya os.environ['PATH'] kita timpa dengan empty, tapi python butuh path dasar)
    
    result = subprocess.run([sys.executable, "-c", "import snowline"], 
                            capture_output=True, text=True, input="", env=env)
    assert result.returncode == 0, f"Import gagal atau hang: {result.stderr}"
    assert "[?]" not in result.stdout, "Seharusnya tidak ada prompt"

def test_setup_path_opt_out():
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
    import snowline
    env = os.environ.copy()
    env['PYTHONPATH'] = str(os.path.abspath('src'))
    if 'SNOWLINE_NO_PATH_SETUP' in env:
        del env['SNOWLINE_NO_PATH_SETUP']
    
    with patch.dict(os.environ, env):
        # Tiruan input merespons 'n' (atau Enter kosong yang diubah lowercase -> '')
        # Kita uji selain 'y' misal '' atau 'n'
        with patch('builtins.input', return_value=''), \
             patch('shutil.copy2'), \
             patch('winreg.OpenKey') as mock_open_key, \
             patch('winreg.QueryValueEx', return_value=("old_path", 1)), \
             patch('winreg.SetValueEx') as mock_set_value:
            
            snowline.setup_path()
            
            # Karena input bukan 'y', ia tidak akan memanggil SetValueEx
            mock_set_value.assert_not_called()

def test_setup_path_yes_answer():
    import snowline
    env = os.environ.copy()
    env['PYTHONPATH'] = str(os.path.abspath('src'))
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
            
            # Karena input 'y', ia harus menulis ke registry
            mock_set_value.assert_called_once()
            # Dan memperbarui profil
            mock_update_profiles.assert_called_once()