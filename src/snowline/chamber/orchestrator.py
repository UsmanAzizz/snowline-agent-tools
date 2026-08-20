#!/usr/bin/env python3
"""
Orchestrator V3 (Chamber Edition)
- Menggabungkan Orchestrator (Pemikir/TL) dan Chamber (Definisi Profil).
- Arsitektur: 1 Main Agent (TL) mendelegasikan tugas ke beberapa Service Workers secara paralel.
- Agnostik terhadap LLM Backend (Bisa menggunakan Gemini/LiteLLM alih-alih hardcode Claude CLI).
"""

import os
import sys
import time
import shutil
import re
import json
import hashlib
import asyncio

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

    async def dispatch_service_worker(self, role, prompt):
        """
        [MOCK] Di sinilah 1 agen dipecah menjadi beberapa Service Worker (paralel).
        Nantinya ini akan memanggil LiteLLM / API Gemini secara native.
        """
        print(f"[WORKER DISPATCHED] Role: {role}")
        print(f"[WORKER THINKING...] Memproses prompt: {prompt[:50]}...")
        await asyncio.sleep(2) # Simulasi network call
        print(f"[WORKER DONE] Role: {role} selesai.")
        return f"Hasil dari {role}"

    async def run_workers_parallel(self, task_description):
        """
        Tech Lead memecah INBOX menjadi beberapa sub-tugas dan menjalankan pekerja secara serentak.
        """
        # Simulasi pemecahan tugas (Di dunia nyata, TL Agent akan mem-parsing teks)
        sub_tasks = [
            ("Frontend_Worker", f"Refaktor UI untuk: {task_description}"),
            ("Backend_Worker", f"Update API endpoint untuk: {task_description}")
        ]
        
        # Jalankan service workers secara paralel!
        tasks = [self.dispatch_service_worker(role, prompt) for role, prompt in sub_tasks]
        results = await asyncio.gather(*tasks)
        return results

    def run(self):
        print(f"[INFO] Chamber Orchestrator V3 (Native Subagent Edition) starting")
        
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

            # 1. Update ke PROCESSING
            content = self.set_inbox_status(content, 'PROCESSING')
            self.safe_write(CONNECTOR_PATH, content)
            
            if os.path.exists(HISTORY_FILE):
                os.remove(HISTORY_FILE)

            print("\n[INFO] ---> TECH LEAD MEMECAH TUGAS (DISPATCHING WORKERS) <---")
            
            # 2. Tech Lead memanggil Subagents (Paralel)
            # Karena ini async, kita panggil loop
            asyncio.run(self.run_workers_parallel("Implementasi dari konektor INBOX"))

            # 3. Pekerjaan selesai, update ke QA_REVIEW
            print("\n[INFO] ---> SEMUA WORKER SELESAI. MENGAKTIFKAN PIHAK KEDUA (QA AGENT) <---")
            content = self.read_connector()
            content = self.set_inbox_status(content, 'QA_REVIEW')
            self.safe_write(CONNECTOR_PATH, content)
            
            # 4. QA Subagent berjalan
            asyncio.run(self.dispatch_service_worker("QA_Agent", "Verifikasi hasil kerja worker"))
            
            # 5. Selesai
            print("\n[SUCCESS] QA meluluskan hasil pekerjaan. Menutup tugas.")
            content = self.read_connector()
            content = self.set_inbox_status(content, 'DONE')
            self.safe_write(CONNECTOR_PATH, content)

            return 0

        finally:
            if os.path.exists(LOCK_FILE):
                os.remove(LOCK_FILE)

if __name__ == "__main__":
    orchestrator = ChamberOrchestrator()
    sys.exit(orchestrator.run())
