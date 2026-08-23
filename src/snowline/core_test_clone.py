import os
import sys
import tempfile
import shutil
import subprocess

def run_test_clone(cmd=None):
    project_root = os.getcwd()
    
    # Ensure it's a git repository
    if not os.path.exists(os.path.join(project_root, '.git')):
        print("[INFO] Direktori saat ini bukan repositori Git. Kloning dilewati.")
        return
        
    print(f"Creating a clean clone of the repository from {project_root}...")
    temp_dir = tempfile.mkdtemp(prefix="snowline_clone_")
    
    try:
        # Clone HEAD
        # We use git clone to clone the local repository to temp_dir
        # This will only clone committed changes
        res = subprocess.run(["git", "clone", project_root, temp_dir], capture_output=True, text=True)
        if res.returncode != 0:
            print(f"[FAIL] Gagal membuat klon bersih:\n{res.stderr}")
            sys.exit(1)
            
        print(f"Clone created at {temp_dir}.")
        print("Running tests in the clean clone...")
        
        test_command = None
        if cmd:
            import shlex
            test_command = shlex.split(cmd)
        else:
            test_script = os.path.join(temp_dir, "tests", "run_tests.py")
            if os.path.exists(test_script):
                test_command = ["python", "tests/run_tests.py"]
                
        if not test_command:
            print("[INFO] tidak ada uji terdeteksi")
            return
            
        res_test = subprocess.run(test_command, cwd=temp_dir, capture_output=True, text=True)
        print("====== TEST OUTPUT ======")
        if res_test.stdout:
            print(res_test.stdout.strip())
        if res_test.stderr:
            print(res_test.stderr.strip())
        print("=========================")
        
        if res_test.returncode == 0:
            print("[PASS] Tes berhasil di lingkungan bersih.")
        else:
            print("[FAIL] Tes gagal di lingkungan bersih.")
            sys.exit(1)
            
    finally:
        print(f"Membersihkan {temp_dir}...")
        try:
            # We might need to handle read-only files in .git
            def remove_readonly(func, path, excinfo):
                os.chmod(path, 128) # stat.S_IWRITE
                func(path)
            shutil.rmtree(temp_dir, onerror=remove_readonly)
            print("Pembersihan selesai.")
        except Exception as e:
            print(f"Gagal menghapus direktori sementara: {e}")

if __name__ == '__main__':
    run_test_clone()
