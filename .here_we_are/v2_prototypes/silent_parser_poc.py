import json
import re

class SilentDelegationParser:
    def parse(self, text: str) -> dict:
        # Mencari blok kode JSON menggunakan regex
        match = re.search(r'```(?:json)?\s*(.*?)\s*```', text, re.DOTALL | re.IGNORECASE)
        if match:
            json_string = match.group(1).strip()
        else:
            # Jika tidak ada blok kode, coba parse string mentah
            json_string = text.strip()
            
        try:
            return json.loads(json_string)
        except json.JSONDecodeError:
            return {"error": "Failed to parse JSON"}

if __name__ == '__main__':
    parser = SilentDelegationParser()
    
    print("Test 1: Clean JSON string")
    clean_json = '{"status": "ok", "data": [1, 2, 3]}'
    print(f"Input: {clean_json}")
    print(f"Output: {parser.parse(clean_json)}\n")
    
    print("Test 2: Dirty JSON with chit-chat")
    chatty_json = '''Halo! Saya telah menemukan datanya. Berikut hasilnya:
```json
{"status": "ok", "data": [1,2,3]}
```
Semoga hari Anda menyenangkan!'''
    print(f"Input: {chatty_json}")
    print(f"Output: {parser.parse(chatty_json)}\n")
    
    print("Test 3: Invalid JSON")
    invalid_json = '''Berikut hasilnya:
```json
{"status": "ok", "data": [1,2,3] # missing bracket
```'''
    print(f"Input: {invalid_json}")
    print(f"Output: {parser.parse(invalid_json)}\n")
