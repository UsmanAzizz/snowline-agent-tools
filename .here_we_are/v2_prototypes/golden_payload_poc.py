import json
import hashlib

class GoldenPayloadBuilder:
    def __init__(self, raw_code_chunk, tools):
        self.raw_code_chunk = raw_code_chunk
        self.tools = tools

    def build_payload(self, user_message):
        # 3. Combine giant string into a special dictionary 'system_context'
        system_context = {
            "version": "1.0",
            "context_data": self.raw_code_chunk
        }

        # 2. Sort the tools list by name/keys alphabetically to ensure consistent JSON hash
        if isinstance(self.tools, dict):
            # Sort dictionary keys
            sorted_tools = dict(sorted(self.tools.items()))
        elif isinstance(self.tools, list):
            # Sort list of dictionaries by 'name' key, or sort simple list
            try:
                sorted_tools = sorted(self.tools, key=lambda x: x.get('name', str(x)))
            except AttributeError:
                sorted_tools = sorted(self.tools)
        else:
            sorted_tools = self.tools

        return {
            "system_context": system_context,
            "tools": sorted_tools,
            "user_message": user_message
        }

if __name__ == '__main__':
    # 3. Simulate giant string
    raw_code = "RAW CODE CHUNK" * 5000  
    
    # Simulate unsorted tools dictionary
    tools_dict = {
        "write_file": {"desc": "Write data to a file"},
        "read_file": {"desc": "Read data from a file"},
        "run_query": {"desc": "Run a database query"},
        "render_ui": {"desc": "Render a UI component"},
        "authenticate": {"desc": "Authenticate user"}
    }
    
    builder = GoldenPayloadBuilder(raw_code, tools_dict)
    
    # 4. Simulate 2 orders for 2 different agents
    payload_ui = builder.build_payload("User request for UI Agent: Build a login form.")
    payload_db = builder.build_payload("User request for DB Agent: Create users table.")
    
    # Prove that `tools` and `system_context` are identical
    ui_common_data = {
        "system_context": payload_ui["system_context"],
        "tools": payload_ui["tools"]
    }
    db_common_data = {
        "system_context": payload_db["system_context"],
        "tools": payload_db["tools"]
    }
    
    # Dump to JSON to compare bytes
    ui_common_json = json.dumps(ui_common_data, sort_keys=True, separators=(',', ':'))
    db_common_json = json.dumps(db_common_data, sort_keys=True, separators=(',', ':'))
    
    hash_ui_common = hashlib.md5(ui_common_json.encode('utf-8')).hexdigest()
    hash_db_common = hashlib.md5(db_common_json.encode('utf-8')).hexdigest()
    
    print("--- Golden Payload PoC ---")
    print(f"Length of raw context_data: {len(payload_ui['system_context']['context_data'])} chars")
    print(f"Tools order: {list(payload_ui['tools'].keys())}")
    
    print(f"\nHash of common parts (UI Agent): {hash_ui_common}")
    print(f"Hash of common parts (DB Agent): {hash_db_common}")
    
    if hash_ui_common == hash_db_common:
        print("\nSUCCESS: `tools` and `system_context` structures are 100% byte-for-byte identical!")
    else:
        print("\nFAILURE: Structures do not match.")
        
    print("\nDifferences in payloads (user_message):")
    print(f"UI Agent message: {payload_ui['user_message']}")
    print(f"DB Agent message: {payload_db['user_message']}")
