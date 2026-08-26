import subprocess
import sys

def run_cli(args):
    result = subprocess.run([sys.executable, 'src/snowline/cli.py'] + args, capture_output=True, text=True, input="N\n")
    if result.returncode != 0:
        assert False, f"Command {' '.join(args)} failed with output:\n{result.stderr}\n{result.stdout}"

def test_smoke_init_full(): run_cli(['init'])
def test_smoke_update_full(): run_cli(['update'])
def test_smoke_uninstall_help(): run_cli(['uninstall', '--help'])
def test_smoke_reinstall_full(): run_cli(['reinstall'])
def test_smoke_init_chamber_help(): run_cli(['init_chamber', '--help'])
def test_smoke_context_full(): run_cli(['context'])
def test_smoke_check_entry_help(): run_cli(['check-entry', '--help'])
def test_smoke_close_entry_help(): run_cli(['close-entry', '--help'])
def test_smoke_test_clone_help(): run_cli(['test-clone', '--help'])
def test_smoke_setup_path_help(): run_cli(['setup-path', '--help'])
def test_smoke_path_full(): run_cli(['path'])
def test_smoke_status_full(): run_cli(['status'])