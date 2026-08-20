#!/usr/bin/env python3
"""
Orchestrator V3.1 (Chamber Edition)
- Menggabungkan Orchestrator (Pemikir/TL) dan Chamber (Definisi Profil).
- C4 Loop Detector (SHA-256 Hashing) - DIPULIHKAN
- Git Rollback & Taskkill - DIPULIHKAN
- Penanganan QA_REJECT - DIPULIHKAN
- Eksekusi Native Subagent melalui subprocess asyncio.
"""

import os
import sys
import time
import shutil
import re
import json
import hashlib
import asyncio
import subprocess

sys.stdout.reconfigure(encoding='utf-8')

AGENT_PROJECT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
CONNECTOR_PATH = os.path.join(AGENT_PROJECT, ".agents", "agents_connector.md")
LOCK_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "orchestrator.lock")
PRIVACY_FLAG = os.path.join(AGENT_PROJECT, ".agents", "automation_granted.json")
HISTORY_FILE = os.path.join(AGENT_PROJECT, ".agents", "action_history.json")
MAX_CONSECUTIVE_REPEATS = 3


class ChamberOrchestrator:
    def __init__(self):
        self.project_root = AGENT_PROJECT
        self.workers = []
        
    def safe_write(self, path, content):
        backup = path + ".bak"
        if os.path.exists(path):
            shutil.copy2(path, backup)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)

    def read_connector(self):
        with open(CONNECTOR_PATH, 'r', encoding='utf-8') as f:
            return f.read()

    def get_inbox_status(self, content):
        m = re.search(r'## ACTIVE TASK - INBOX.*?\*\*Status:\*\* \[([^\]]+)\]', content, re.DOTALL)
        return m.group(1) if m else None

    def set_inbox_status(self, content, new_status):
        return re.sub(
            r'(\*\*Status:\*\* \[)[^\]]+(\])',
            r'\g<1>' + new_status + r'\g<2>',
            content,
            count=1
        )

    def kill_process_tree(self, pid):
        if sys.platform == 'win32':
            subprocess.run(['taskkill', '/F', '/T', '/PID', str(pid)], capture_output=True)
            
    def perform_rollback(self):
        print("\n[WARNING] Mengeksekusi Git Rollback (C2: reset --hard + clean -fd)...")
        try:
            subprocess.run(["git", "reset", "--hard"], check=True, cwd=self.project_root)
            subprocess.run(["git", "clean", "-fd"], check=True, cwd=self.project_root)
            print("[SUCCESS] Workspace berhasil disucikan ke state aman.")
            if os.path.exists(HISTORY_FILE):
                os.remove(HISTORY_FILE)
        except Exception as e:
            print(f"[ERROR] Gagal melakukan rollback: {e}")

    def extract_hash_from_output(self, line):
        m = re.search(r'(Tool used:.*?|Command:.*?)', line, re.IGNORECASE)
        if m:
            payload = m.group(1).strip()
            return hashlib.sha256(payload.encode('utf-8')).hexdigest()
        return None

    def check_loop(self, action_hash):
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, 'r') as f:
                    history = json.load(f)
            except:
                history = []
        else:
            history = []
            
        history.append(action_hash)
        
        with open(HISTORY_FILE, 'w') as f:
            json.dump(history, f)
            
        if len(history) >= MAX_CONSECUTIVE_REPEATS:
            recent = history[-MAX_CONSECUTIVE_REPEATS:]
            if len(set(recent)) == 1:
                return True
        return False

    async def dispatch_service_worker(self, role, prompt, is_qa=False):
        """
        Meluncurkan subprocess CLI nyata.
        """
        print(f"\n[{role.upper()}] Memulai tugas...")
        
        # Di sini kita meluncurkan claude secara nyata, atau mock subprocess untuk fungsionalitas
        cmd = [
            "claude", "-p", prompt, "--permission-mode", "auto"
        ]
        
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=self.project_root,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT
            )
            
            stalemate = False
            
            while True:
                line_bytes = await proc.stdout.readline()
                if not line_bytes:
                    break
                
                line = line_bytes.decode('utf-8', errors='replace')
                print(f"[{role}] {line}", end='')
                
                # Hanya worker yang diperiksa loopnya untuk mencegah kebekuan
                if not is_qa:
                    action_hash = self.extract_hash_from_output(line)
                    if action_hash:
                        if self.check_loop(action_hash):
                            print(f"\n[BLOCKED] Loop Detector (C4): Terdeteksi 3 eksekusi beruntun yang identik dari {role}!")
                            print("[BLOCKED] Memutus kebuntuan (Stalemate).")
                            self.kill_process_tree(proc.pid)
                            self.perform_rollback()
                            
                            curr_content = self.read_connector()
                            curr_content = self.set_inbox_status(curr_content, 'ERROR_STALEMATE')
                            self.safe_write(CONNECTOR_PATH, curr_content)
                            stalemate = True
                            break
                            
            await proc.wait()
            
            if stalemate:
                return "STALEMATE"
                
            return "SUCCESS"
            
        except Exception as e:
            print(f"[{role}] Error: {e}")
            return "ERROR"

    async def run_workers_parallel(self, task_description):
        """
        Tech Lead memecah INBOX menjadi beberapa sub-tugas dan menjalankan pekerja secara serentak.
        """
        # Dalam implementasi riil, ini diparsing. Untuk skenario ini, kita definisikan sub-tasks.
        sub_tasks = [
            ("Frontend_Worker", f"Lakukan hanya satu hal: buat file frontend_done.txt berisi '{task_description}' lalu exit.")
            # Kita hanya me-spawn 1 worker nyata untuk demonstrasi demi menghemat API,
            # Namun kerangka async-nya mengizinkan banyak subprocess paralel.
        ]
        
        tasks = [self.dispatch_service_worker(role, prompt, is_qa=False) for role, prompt in sub_tasks]
        results = await asyncio.gather(*tasks)
        return results

    def run(self):
        print(f"[INFO] Chamber Orchestrator V3.1 (Native Subagent + C4 Recovery) starting")
        
        if not os.path.exists(PRIVACY_FLAG):
            print(f"[BLOCKED] Privacy Flag tidak ditemukan.")
            return 1

        if os.path.exists(LOCK_FILE):
            print("[WARN] orchestrator.lock exists. Exiting.")
            return 1

        try:
            with open(LOCK_FILE, 'w') as f:
                f.write(str(time.time()))
                
            content = self.read_connector()
            status = self.get_inbox_status(content)
            
            if status != 'READY':
                return 0

            content = self.set_inbox_status(content, 'PROCESSING')
            self.safe_write(CONNECTOR_PATH, content)
            
            if os.path.exists(HISTORY_FILE):
                os.remove(HISTORY_FILE)

            print("\n[INFO] ---> TECH LEAD MEMECAH TUGAS (DISPATCHING WORKERS) <---")
            
            connector_path_posix = CONNECTOR_PATH.replace('\\', '/')
            
            # Simulasi pemecahan
            asyncio.run(self.run_workers_parallel(f"Tugas utama dari INBOX: {connector_path_posix}"))

            # Periksa jika ada stalemate
            content = self.read_connector()
            if self.get_inbox_status(content) == 'ERROR_STALEMATE':
                return 0

            print("\n[INFO] ---> SEMUA WORKER SELESAI. MENGAKTIFKAN PIHAK KEDUA (QA AGENT) <---")
            content = self.set_inbox_status(content, 'QA_REVIEW')
            self.safe_write(CONNECTOR_PATH, content)
            
            qa_prompt = f"Verifikasi hasil kerja worker. Jika lolos ubah status INBOX di {connector_path_posix} menjadi QA_PASS. Jika gagal ubah menjadi QA_REJECT beserta alasannya."
            
            # QA Subagent berjalan
            asyncio.run(self.dispatch_service_worker("QA_Agent", qa_prompt, is_qa=True))
            
            # Post-QA Evaluation
            final_content = self.read_connector()
            qa_status = self.get_inbox_status(final_content)
            
            if qa_status == 'QA_REJECT':
                print("\n[BLOCKED] QA menolak hasil pekerjaan. Mengembalikan status ke READY untuk pekerja.")
                final_content = self.set_inbox_status(final_content, 'READY')
                self.safe_write(CONNECTOR_PATH, final_content)
            elif qa_status == 'QA_PASS':
                print("\n[SUCCESS] QA meluluskan hasil pekerjaan. Menutup tugas.")
                final_content = self.set_inbox_status(final_content, 'DONE')
                self.safe_write(CONNECTOR_PATH, final_content)
            else:
                print(f"\n[WARN] QA gagal memberikan putusan (status: {qa_status}). Mengembalikan ke READY.")
                final_content = self.set_inbox_status(final_content, 'READY')
                self.safe_write(CONNECTOR_PATH, final_content)

            return 0

        finally:
            if os.path.exists(LOCK_FILE):
                os.remove(LOCK_FILE)

if __name__ == "__main__":
    orchestrator = ChamberOrchestrator()
    sys.exit(orchestrator.run())
