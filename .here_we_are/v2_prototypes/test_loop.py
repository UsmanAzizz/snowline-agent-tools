import subprocess
import sys

def test_loop():
    print("--- ITERATION 1 ---")
    subprocess.run(["python", "loop_detector.py", "run_tests", '{"test_file": "App.test.jsx"}'])
    print("--- ITERATION 2 ---")
    subprocess.run(["python", "loop_detector.py", "run_tests", '{"test_file": "App.test.jsx"}'])
    print("--- ITERATION 3 ---")
    result = subprocess.run(["python", "loop_detector.py", "run_tests", '{"test_file": "App.test.jsx"}'])
    
    if result.returncode == 1:
        print("\n[SUCCESS] Stalemate berhasil diblokir pada iterasi ketiga.")
    else:
        print("\n[FAIL] Stalemate tidak terblokir.")

if __name__ == "__main__":
    test_loop()
