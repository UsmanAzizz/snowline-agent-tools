import sys
import os
import time
import datetime

# Pastikan dapat mengimpor dari direktori yang sama
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from snowline_core_v2 import SnowlineV2Orchestrator

def run_simulation():
    print("="*60)
    print(" SIMULASI END-TO-END: MENCEGAH INFINITE LOOP LLM")
    print("="*60)

    # Inisiasi orchestrator
    orchestrator = SnowlineV2Orchestrator()

    instruction = "Tolong periksa kerentanan keamanan pada src/auth."

    # --- Panggilan 1 ---
    print("\n[!] LLM Mengirim Panggilan 1 (String panjang kotor)")
    time_1 = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    uuid_1 = "123e4567-e89b-12d3-a456-426614174000"
    
    mock_llm_output_1 = f"""Halo Agen Induk! Saya segera memproses tugas ini.
Berikut adalah log proses dari internal service saya:
[{time_1}] INFO {uuid_1} - Starting analysis
[{time_1}] DEBUG {uuid_1} - Analyzing tree...
Saya telah menemukan titik pemeriksaan. Berikut adalah instruksi untuk dijalankan:

```json
{{
  "tool": "run_semgrep",
  "args": {{"target": "src/auth"}}
}}
```
Semoga berhasil! Jika ada error, saya akan mencoba lagi.
"""

    print(">>> Eksekusi Orchestrator (Panggilan 1) <<<")
    print("Step 1: Payload Build -> (Terjadi dalam orchestrator.run_agent_turn)")
    print("Step 2: Firewall Check -> (Memeriksa apakah hash output sama)")
    print("Step 3: Parse -> (Mengekstrak JSON dari teks chatty)")
    
    result_1 = orchestrator.run_agent_turn("InfiniteLoopAgent", instruction, mock_llm_output_1)
    
    print("\n[Hasil Panggilan 1]:")
    print(result_1)
    print("-" * 60)

    # Beri jeda 1 detik untuk membedakan timestamp
    time.sleep(1)

    # --- Panggilan 2 ---
    print("\n[!] LLM Terjebak Loop / Panik (Mengirim struktur pesan yang persis sama, hanya beda Timestamp)")
    time_2 = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    uuid_2 = "987fcdeb-51a2-43d7-9012-345678901234"
    
    # Pesan yang sama persis strukturnya, hanya beda waktu dan UUID
    mock_llm_output_2 = f"""Halo Agen Induk! Saya segera memproses tugas ini.
Berikut adalah log proses dari internal service saya:
[{time_2}] INFO {uuid_2} - Starting analysis
[{time_2}] DEBUG {uuid_2} - Analyzing tree...
Saya telah menemukan titik pemeriksaan. Berikut adalah instruksi untuk dijalankan:

```json
{{
  "tool": "run_semgrep",
  "args": {{"target": "src/auth"}}
}}
```
Semoga berhasil! Jika ada error, saya akan mencoba lagi.
"""

    print(">>> Eksekusi Orchestrator (Panggilan 2) <<<")
    print("Step 1: Payload Build -> (Terjadi dalam orchestrator.run_agent_turn)")
    print("Step 2: Firewall Check -> (Harus memblokir karena struktur string sama dengan sebelumnya)")
    print("Step 3: Parse -> (Tidak akan dicapai jika diblokir)")
    
    result_2 = orchestrator.run_agent_turn("InfiniteLoopAgent", instruction, mock_llm_output_2)
    
    print("\n[Hasil Panggilan 2]:")
    print(result_2)
    print("="*60)
    print(" SIMULASI SELESAI")
    print("="*60)


if __name__ == '__main__':
    run_simulation()
