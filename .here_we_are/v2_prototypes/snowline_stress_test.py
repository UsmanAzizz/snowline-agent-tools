import os
import subprocess
import time

SANDBOX_DIR = "sandbox_app"
CALC_FILE = os.path.join(SANDBOX_DIR, "calculator.js")

class ChaosOrchestrator:
    def __init__(self):
        self.max_retries = 3
        
    def simulate_bad_agent(self, attempt):
        """Mensimulasikan LLM yang ngeyel dan menulis kode rusak."""
        print(f"\n[AGEN PALSU] Mengambil alih... (Attempt {attempt})")
        
        with open(CALC_FILE, 'r') as f:
            content = f.read()
            
        if attempt == 1:
            print("  -> Menulis sintaks yang rusak (menghilangkan kurung).")
            bad_content = content.replace("return a + b;", "return a + b") # Bukan syntax error di JS, but let's make it a real error
            bad_content = content.replace("function multiply(a, b) {", "function multiply(a, b)")
        elif attempt == 2:
            print("  -> Menulis sintaks benar, tapi logika makin kacau (mengubah jadi a - b).")
            bad_content = content.replace("return a + b;", "return a - b;")
        else:
            print("  -> Menolak bekerja, hanya menulis teks markdown.")
            bad_content = "Maaf, saya tidak bisa membantu hal ini."
            
        with open(CALC_FILE, 'w') as f:
            f.write(bad_content)

    def check_syntax(self):
        """Gate 1: Syntax Check menggunakan node --check"""
        print("\n[GATE 1] Syntax Guardian...")
        result = subprocess.run(["node", "--check", "calculator.js"], cwd=SANDBOX_DIR, capture_output=True, text=True)
        if result.returncode != 0:
            print("[FAIL] Syntax Guardian menolak kode:")
            print(result.stderr.strip())
            return False
        print("[PASS] Sintaks Valid.")
        return True

    def check_logic(self):
        """Gate 2: Logic Check menggunakan test.js"""
        print("\n[GATE 2] QA Guardian (Logic Test)...")
        result = subprocess.run(["node", "test.js"], cwd=SANDBOX_DIR, capture_output=True, text=True)
        if result.returncode != 0:
            print("[FAIL] QA Guardian menolak logika:")
            print(result.stderr.strip())
            return False
        print("[PASS] Logika Valid.")
        return True

    def run_rollback(self):
        print("\n[STALEMATE DETECTED] Mengaktifkan Emergency Git Rollback!")
        subprocess.run(["git", "reset", "--hard"], cwd=SANDBOX_DIR)
        print("[ROLLBACK BERHASIL] Kode kembali suci.")

    def run_chaos_test(self):
        print("=== MEMULAI CHAOS TEST (LIVE FIRE) ===")
        
        attempt = 1
        while attempt <= self.max_retries:
            self.simulate_bad_agent(attempt)
            
            if self.check_syntax():
                if self.check_logic():
                    print("\n[SUCCESS] Agen berhasil secara ajaib.")
                    break
            
            print(f"[ORCHESTRATOR] Mengembalikan ke Agen. Percobaan ke-{attempt} gagal.")
            attempt += 1
            time.sleep(1)
            
        if attempt > self.max_retries:
            self.run_rollback()

if __name__ == "__main__":
    tester = ChaosOrchestrator()
    tester.run_chaos_test()
