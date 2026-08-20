import json
import sys
import os

# --- MOCK TOOL SCHEMAS ---
READ_ONLY_TOOLS = ["selective_reader", "smart_search", "smart_tree", "delta_firewall"]
WRITE_ONLY_TOOLS = ["write_to_file", "syntax_guardian", "auto_scaffolder"]
REVIEW_TOOLS = ["selective_reader"] # Reviewer hanya membaca

# --- STATE MACHINE CLASSES ---
class AgentState:
    def __init__(self, role, tools_allowed):
        self.role = role
        self.tools_allowed = tools_allowed

class Orchestrator:
    def __init__(self):
        self.retry_count = 0
        self.max_retries = 3
        self.original_task = "Tombol login macet, tolong perbaiki dan pastikan warnanya merah."
        
    def check_tool_permission(self, agent, tool_name):
        if tool_name not in agent.tools_allowed:
            return False, f"[DENIED] {agent.role} dilarang keras mengakses fungsi {tool_name}!"
        return True, "[OK] Akses diizinkan."

    def run_investigator(self):
        print("\n=== FASE 1: INVESTIGASI ===")
        investigator = AgentState("Investigator", READ_ONLY_TOOLS)
        print("[INFO] Investigator dipaksa menyerahkan Distilled Context (Handoff Protocol).")
        return "Bug ditemukan di file config.js baris 20. Variabel undefined."

    def run_executor(self, context, attempt):
        print("\n=== FASE 2: EKSEKUSI ===")
        executor = AgentState("Executor", WRITE_ONLY_TOOLS)
        print(f"Executor (Attempt {attempt}) menerima konteks: '{context}'")
        
        # Pintu 1: Syntax Guardian
        print("\n[GATE 1: SYNTAX GUARDIAN]")
        if attempt == 1:
            print("[FAIL] Syntax Guardian: Ada tanda kurung yang hilang!")
            self.retry_count += 1
            return False, "Syntax error"
        else:
            print("[PASS] Syntax Guardian: Kode valid.")
            
        # Pintu 2: QA Guardian (Deterministik)
        print("\n[GATE 2: QA GUARDIAN (UNIT TEST)]")
        if attempt == 2:
            print("[FAIL] QA Guardian: `npm test` gagal! TypeError: Cannot read property 'color'")
            self.retry_count += 1
            return False, "Unit test failed"
        else:
            print("[PASS] QA Guardian: Semua test biner lolos.")
            
        # Pintu 3: Reviewer Subagent (Semantik)
        print("\n[GATE 3: REVIEWER SUBAGENT (SEMANTIK)]")
        reviewer = AgentState("Reviewer", REVIEW_TOOLS)
        print(f"Reviewer membandingkan hasil dengan instruksi awal: '{self.original_task}'")
        if attempt == 3:
            print("[FAIL] Reviewer Subagent: 'Kodenya jalan, tapi Anda membuat tombolnya biru. User minta warna merah!'")
            self.retry_count += 1
            return False, "Semantic requirement failed"
        else:
            print("[PASS] Reviewer Subagent: 'Sempurna. Tombol sudah merah dan bug teratasi.'")
            
        return True, "Success"

    def trigger_stalemate(self):
        print("\n=== FATAL: STALEMATE DETECTED ===")
        print("[LOOP DETECTOR] Batas retry (3) terlampaui.")
        print("[ROLLBACK] Mengeksekusi 'git reset --hard' dan merestart siklus memori.")
        
    def start_pipeline(self):
        print("\n--- SNOWLINE ORCHESTRATOR V2 (PROTOTYPE) ---")
        context = self.run_investigator()
        
        attempt = 1
        while self.retry_count <= self.max_retries: # Allow exactly 4 attempts to show 3 fails then success on 4th? No, if 3 fails it rolls back.
            success, reason = self.run_executor(context, attempt)
            
            if success:
                print("\n[APROVAL AKHIR] Seluruh lapisan QA memberikan cap stempel! Orkestrator menyerahkan laporan ke pengguna.")
                break
                
            print(f"[REJECTED] Dikembalikan ke Executor. Alasan: {reason}. (Retry: {self.retry_count}/{self.max_retries})")
            
            if self.retry_count >= self.max_retries:
                self.trigger_stalemate()
                break
                
            attempt += 1
                
        print("\n--- SIKLUS ORKESTRATOR SELESAI ---")

if __name__ == "__main__":
    orchestrator = Orchestrator()
    orchestrator.start_pipeline()
