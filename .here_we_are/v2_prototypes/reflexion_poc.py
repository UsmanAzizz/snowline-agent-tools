import json
import os

LESSONS_FILE = "lessons_learned.json"

def get_lessons(task_prompt):
    """Retrieve relevant lessons based on keyword matching (Lightweight Semantic Search)."""
    if not os.path.exists(LESSONS_FILE):
        return None
        
    try:
        with open(LESSONS_FILE, 'r') as f:
            lessons = json.load(f)
    except Exception:
        return None
        
    relevant_lessons = []
    # Simulasi KNN/Vector Search dengan string matching sederhana
    for item in lessons:
        # Jika kata kunci (misal "TypeError" atau "undefined") muncul di prompt/error sebelumnya
        trigger_keywords = item['trigger'].split()
        for word in trigger_keywords:
            if word.lower() in task_prompt.lower():
                relevant_lessons.append(item['lesson'])
                break # Hindari duplikasi untuk lesson yang sama
                
    return relevant_lessons

def simulate_agent_session(task_prompt):
    """Simulasi agen memulai sesi baru."""
    print(f"\n--- [MEMULAI SESI BARU] ---")
    print(f"Task Prompt Asli:\n{task_prompt}")
    
    lessons = get_lessons(task_prompt)
    
    if lessons:
        print("\n[META-LEARNING] Menemukan histori kegagalan terkait! Menyuntikkan pelajaran ke System Prompt...")
        injected_prompt = f"{task_prompt}\n\n[WARNING DARI MASA LALU]:\n- " + "\n- ".join(lessons)
        print(f"\nTask Prompt Terdestilasi (Injected):\n{injected_prompt}")
        print("\n[SUCCESS] Agen berhasil menghindari kesalahan sebelum mulai mengetik kode.")
    else:
        print("\n[INFO] Tidak ada pelajaran masa lalu yang relevan. Agen beroperasi normal.")

if __name__ == "__main__":
    print("[SKENARIO 1: Tugas Biasa]")
    simulate_agent_session("Tolong buatkan fungsi penjumlahan sederhana di Python.")
    
    print("\n[SKENARIO 2: Tugas yang memicu histori kegagalan]")
    simulate_agent_session("Tolong perbaiki API kita yang melempar TypeError undefined saat mengambil data dari database eksternal.")
