import json
import sys
import re

# --- MOCK ROUTING MATRIX ---
ROUTING_MATRIX = [
    {
        "keywords": [r"(?i)perbaiki", r"(?i)fix", r"(?i)refactor", r"(?i)tambah fitur", r"(?i)ubah"],
        "route": "CHAMBER_PIPELINE",
        "description": "Tugas kompleks yang butuh Investigator dan Executor."
    },
    {
        "keywords": [r"(?i)audit", r"(?i)keamanan", r"(?i)security", r"(?i)cek kerentanan"],
        "route": "SUBAGENT_AUDITOR",
        "description": "Tugas spesifik untuk agen spesialis keamanan."
    },
    {
        "keywords": [r"(?i)cari", r"(?i)temukan", r"(?i)baca", r"(?i)jelaskan"],
        "route": "SOLO_AGENT",
        "description": "Tugas baca sederhana, bisa dikerjakan langsung."
    }
]

def analyze_intent_and_route(user_prompt):
    """Menganalisis prompt user dan mengembalikan rute eksekusi."""
    print(f"\n[USER PROMPT]: '{user_prompt}'")
    print("[COMPANION] Sedang menganalisis intensi...")
    
    for rule in ROUTING_MATRIX:
        for keyword in rule["keywords"]:
            if re.search(keyword, user_prompt):
                return rule["route"], rule["description"]
                
    # Fallback
    return "SOLO_AGENT", "Intensi tidak jelas, ditangani perlahan oleh agen utama."

def mock_orchestrator(route, description):
    """Simulasi Orkestrator merespons arahan Companion."""
    print(f"-> [ROUTING DECISION]: {route}")
    print(f"-> [ALASAN]: {description}")
    
    if route == "CHAMBER_PIPELINE":
        print("-> [ACTION]: Menginisiasi State Machine (snowline_core_v2.py)...")
        print("             - Membangunkan Investigator")
        print("             - Menyiapkan Handoff Protocol")
    elif route == "SOLO_AGENT":
        print("-> [ACTION]: Dieksekusi langsung di jendela chat ini menggunakan tool bawaan.")
    elif route == "SUBAGENT_AUDITOR":
        print("-> [ACTION]: Melempar payload ke Security Auditor Agent.")
    else:
        print("-> [ACTION]: Fallback eksekusi.")

if __name__ == "__main__":
    print("=== SNOWLINE COMPANION V2 (PROTOTYPE) ===")
    
    prompt_1 = "Tolong cari di mana fungsi handleSubmit didefinisikan."
    route, desc = analyze_intent_and_route(prompt_1)
    mock_orchestrator(route, desc)
    
    prompt_2 = "Aplikasi saya macet saat login, tolong perbaiki bug-nya."
    route, desc = analyze_intent_and_route(prompt_2)
    mock_orchestrator(route, desc)
    
    prompt_3 = "Cek apakah ada hardcoded password atau masalah keamanan di repo ini."
    route, desc = analyze_intent_and_route(prompt_3)
    mock_orchestrator(route, desc)
