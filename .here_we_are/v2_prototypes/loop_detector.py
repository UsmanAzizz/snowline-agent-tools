import hashlib
import json
import os
import sys
import subprocess

HISTORY_FILE = "action_history.json"
MAX_CONSECUTIVE_REPEATS = 3

def compute_hash(action_name, args_dict):
    """Compute a deterministic hash of the action and its arguments."""
    payload = json.dumps({"action": action_name, "args": args_dict}, sort_keys=True)
    return hashlib.sha256(payload.encode('utf-8')).hexdigest()

def clear_history():
    """Clear the action history file."""
    if os.path.exists(HISTORY_FILE):
        os.remove(HISTORY_FILE)
        print(f"[OK] Histori aksi dibersihkan ({HISTORY_FILE}).")

def perform_rollback():
    """Execute git reset --hard to clear tainted context."""
    print("[WARNING] Mengeksekusi Git Rollback (reset --hard)...")
    try:
        # Menjalankan reset dari root repository
        subprocess.run(["git", "reset", "--hard"], check=True, cwd=os.path.dirname(os.path.abspath(__file__)))
        print("[SUCCESS] Workspace berhasil dikembalikan ke state aman.")
        clear_history()
    except Exception as e:
        print(f"[ERROR] Gagal melakukan rollback: {e}")

def record_action(action_name, args_dict):
    """Record action and check for stalemate loop."""
    action_hash = compute_hash(action_name, args_dict)
    
    # Load history
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            history = json.load(f)
    else:
        history = []
        
    history.append({
        "action": action_name,
        "args": args_dict,
        "hash": action_hash
    })
    
    # Save history
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)
        
    # Check for consecutive repeats
    if len(history) >= MAX_CONSECUTIVE_REPEATS:
        recent_hashes = [item['hash'] for item in history[-MAX_CONSECUTIVE_REPEATS:]]
        if len(set(recent_hashes)) == 1:
            print(f"\n[BLOCKED] Loop Detector: Terdeteksi {MAX_CONSECUTIVE_REPEATS} eksekusi beruntun yang identik!")
            print(f"Action Hash: {action_hash}")
            print(f"Mengirim sinyal TERMINATE untuk memecah stalemate.")
            perform_rollback()
            return False # Indicates loop detected
            
    return True # Action allowed

if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--clear":
        clear_history()
        sys.exit(0)

    if len(sys.argv) < 3:
        print("Usage: python loop_detector.py <action_name> <json_args>")
        print("       python loop_detector.py --clear")
        sys.exit(1)
        
    action_name = sys.argv[1]
    try:
        args_dict = json.loads(sys.argv[2])
    except json.JSONDecodeError:
        print("Error: args must be valid JSON.")
        sys.exit(1)
        
    allowed = record_action(action_name, args_dict)
    if not allowed:
        sys.exit(1)
    else:
        print(f"[OK] Aksi dicatat: {action_name}")
        sys.exit(0)
