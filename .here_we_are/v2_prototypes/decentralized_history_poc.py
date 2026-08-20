import json
import os
import shutil

MEMORY_ROOT = "agent_memories"

def setup_memory_folders():
    """Membuat ruang terisolasi untuk masing-masing agen."""
    if os.path.exists(MEMORY_ROOT):
        shutil.rmtree(MEMORY_ROOT)
    os.makedirs(MEMORY_ROOT)
    os.makedirs(os.path.join(MEMORY_ROOT, "executor"))
    os.makedirs(os.path.join(MEMORY_ROOT, "auditor"))
    os.makedirs(os.path.join(MEMORY_ROOT, "investigator"))

def record_history(role, task_summary, files_changed):
    """Menyimpan sejarah hanya ke ruang agen yang bersangkutan."""
    history_file = os.path.join(MEMORY_ROOT, role.lower(), "history.json")
    
    data = []
    if os.path.exists(history_file):
        with open(history_file, 'r') as f:
            data = json.load(f)
            
    # Simpan log baru
    data.append({
        "task": task_summary,
        "files_changed": files_changed
    })
    
    # Prune (Simpan hanya 5 terakhir untuk zero-bloat)
    if len(data) > 5:
        data = data[-5:]
        
    with open(history_file, 'w') as f:
        json.dump(data, f, indent=2)

def inject_history(role):
    """Menarik riwayat lokal sebelum agen bangun."""
    history_file = os.path.join(MEMORY_ROOT, role.lower(), "history.json")
    if not os.path.exists(history_file):
        return "[Tidak ada memori masa lalu untuk agen ini]"
        
    with open(history_file, 'r') as f:
        data = json.load(f)
        
    log_text = f"[HISTORY - {role.upper()}]:\n"
    for item in data:
        log_text += f"- Menyelesaikan: {item['task']}. (File diubah: {', '.join(item['files_changed'])})\n"
    return log_text

if __name__ == "__main__":
    setup_memory_folders()
    
    print("=== SNOWLINE DECENTRALIZED HISTORY (POC) ===")
    
    # 1. Orkestrator menyetujui tugas Executor
    print("\n[ORCHESTRATOR] Menyimpan histori Executor...")
    record_history("Executor", "Memperbaiki tombol login macet", ["src/Login.js", "src/Button.js"])
    
    # 2. Orkestrator menyetujui tugas Auditor
    print("[ORCHESTRATOR] Menyimpan histori Auditor...")
    record_history("Auditor", "Memindai file env yang bocor", [".gitignore"])
    record_history("Auditor", "Memperbarui dependensi rentan", ["package.json"])
    
    # 3. Simulasi membangunkan agen esok harinya
    print("\n--- KEESOKAN HARINYA ---")
    
    print("\n[SYSTEM] Membangunkan agen Executor...")
    print("Injecting Context:")
    print(inject_history("Executor"))
    
    print("\n[SYSTEM] Membangunkan agen Auditor...")
    print("Injecting Context:")
    print(inject_history("Auditor"))
