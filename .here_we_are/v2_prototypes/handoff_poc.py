import json
import sys

class StaticState:
    """Obyek deterministik untuk membawa variabel tanpa merusak jendela konteks."""
    def __init__(self, task_id, root_dir):
        self.task_id = task_id
        self.root_dir = root_dir
        self.files_modified = []

    def to_dict(self):
        return {
            "task_id": self.task_id,
            "root_dir": self.root_dir,
            "files_modified": self.files_modified
        }

def simulate_agent_a():
    """Simulasi Investigator yang menumpuk log pemikiran panjang."""
    print("[INFO] Agen Investigator mulai bekerja...")
    scratchpad = "Mencari root folder... ketemu. Membaca file A... bukan di sana. Membaca file B... ya ada bug. Membaca file C... mencari referensi. " * 50
    # Bayangkan scratchpad ini panjangnya 5000 token.
    token_cost_raw = len(scratchpad.split())
    
    # Rangkuman matang
    distilled_context = "Bug ditemukan di file_B.py baris 42. Masalah: variabel X tidak didefinisikan sebelum dipanggil."
    token_cost_distilled = len(distilled_context.split())
    
    state = StaticState("T-123", "/var/www/app")
    state.files_modified.append("file_B.py")
    
    print(f"[METRIC] Beban Memori Mentah (Scratchpad): ~{token_cost_raw} kata.")
    print(f"[METRIC] Beban Handoff (Distilled): ~{token_cost_distilled} kata.")
    print("[INFO] Mengeksekusi Handoff ke Executor...")
    
    return distilled_context, state

def simulate_agent_b(distilled_context, state):
    """Simulasi Executor yang hanya menerima inti pekerjaan."""
    print("\n--- [HANDOFF PROTOCOL] ---")
    print("[INFO] Agen Executor menerima tugas.")
    print(f"State: {json.dumps(state.to_dict(), indent=2)}")
    print(f"Context: {distilled_context}")
    print("[SUCCESS] Agen B langsung mengeksekusi perbaikan tanpa tersesat di log lama.")

if __name__ == "__main__":
    context, state = simulate_agent_a()
    simulate_agent_b(context, state)
