import json
import sys

# Impor dari skrip sebelumnya
try:
    from delta_firewall_poc import DeltaFirewall
    from silent_parser_poc import SilentDelegationParser
    from golden_payload_poc import GoldenPayloadBuilder
    from agnostic_adapter_poc import AdapterFactory
    from semgrep_wrapper_poc import parse_semgrep_output
except ImportError as e:
    print(f"Gagal mengimpor modul komponen: {e}")
    sys.exit(1)

class SnowlineV2Orchestrator:
    def __init__(self):
        # Inisialisasi komponen
        self.firewall = DeltaFirewall()
        self.parser = SilentDelegationParser()
        
        # Tools dummy untuk GoldenPayloadBuilder
        mock_tools = [
            {"name": "run_semgrep", "description": "Run semgrep on codebase"}
        ]
        mock_code_chunk = "def example(): pass"
        self.payload_builder = GoldenPayloadBuilder(mock_code_chunk, mock_tools)
        
        self.adapter = AdapterFactory.get_adapter("anthropic")

    def run_agent_turn(self, agent_name, instruction, mock_tool_output_from_llm):
        print(f"\n--- Memulai Giliran Agen: {agent_name} ---")
        print(f"Instruksi: {instruction}")

        # 1. Bangun payload via GoldenPayloadBuilder dan terjemahkan via AdapterFactory
        golden_payload = self.payload_builder.build_payload(instruction)
        formatted_payload = self.adapter.format_payload(golden_payload)
        print("[Orchestrator] Payload berhasil dibangun dan diterjemahkan (adapter: Anthropic).")

        # 2. Cegat output menggunakan DeltaFirewall
        firewall_result = self.firewall.process(mock_tool_output_from_llm)
        if firewall_result == "[FIREWALL BLOCKED]":
            warning = "Peringatan Firewall: Output diblokir karena berulang atau tidak aman."
            print(f"[Orchestrator] {warning}")
            return {"status": "blocked", "reason": warning}
        
        print("[Orchestrator] Firewall: Output diizinkan lolos.")

        # 3. Ekstrak JSON dengan SilentDelegationParser
        parsed_json = self.parser.parse(mock_tool_output_from_llm)
        if "error" in parsed_json:
             print("[Orchestrator] Gagal mengurai JSON dari output.")
             return {"status": "error", "reason": parsed_json["error"]}

        print(f"[Orchestrator] JSON berhasil diurai: {parsed_json}")

        # 4. Teruskan JSON ke simulasi pembungkus statis (misal run_semgrep)
        print("[Orchestrator] Menjalankan pembungkus statis semgrep (simulasi)...")
        # Simulasi output semgrep mentah
        raw_semgrep_simulated = '''
        {
          "errors": [],
          "paths": {"scanned": ["app.py"]},
          "results": [
            {
              "check_id": "simulated-xss",
              "path": "app.py",
              "start": {"line": 10},
              "extra": {"message": "Simulated XSS warning."}
            }
          ]
        }
        '''
        
        # Mengeksekusi parser statis
        semgrep_parsed = parse_semgrep_output(raw_semgrep_simulated)
        results = [
            {
                "wrapper": "semgrep",
                "parsed_output": semgrep_parsed
            }
        ]
        
        return {"status": "success", "results": results}

if __name__ == '__main__':
    orchestrator = SnowlineV2Orchestrator()
    
    # Skenario 1: Output LLM Valid
    mock_llm_response_1 = '''Berikut adalah pemanggilan alatnya:
```json
{
  "tool": "run_semgrep",
  "args": {"target": "src/"}
}
```
'''
    res1 = orchestrator.run_agent_turn("SecurityAgent", "Tolong periksa kerentanan keamanan.", mock_llm_response_1)
    print("Hasil Skenario 1:", res1)
    
    # Skenario 2: Output LLM Valid namun berulang (memicu DeltaFirewall)
    # Kami akan memberikan pesan yang persis sama sehingga hash-nya cocok dengan yang sudah dilihat
    mock_llm_response_2 = mock_llm_response_1
    res2 = orchestrator.run_agent_turn("SecurityAgent", "Tolong periksa lagi (mengulang tool yang sama).", mock_llm_response_2)
    print("Hasil Skenario 2:", res2)
