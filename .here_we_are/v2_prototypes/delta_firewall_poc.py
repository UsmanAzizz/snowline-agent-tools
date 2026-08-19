import re
import hashlib
import uuid
import datetime
import time

class DeltaFirewall:
    def __init__(self):
        self.seen_hashes = set()

    def _strip_variable_data(self, text: str) -> str:
        # Strip timestamps like YYYY-MM-DD HH:MM:SS
        timestamp_pattern = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}(\.\d+)?'
        # Strip UUIDs
        uuid_pattern = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
        
        stripped = re.sub(timestamp_pattern, '<TIMESTAMP>', text)
        stripped = re.sub(uuid_pattern, '<UUID>', stripped, flags=re.IGNORECASE)
        return stripped

    def process(self, error_message: str) -> str:
        stripped_message = self._strip_variable_data(error_message)
        message_hash = hashlib.sha256(stripped_message.encode('utf-8')).hexdigest()
        
        if message_hash in self.seen_hashes:
            return "[FIREWALL BLOCKED]"
        
        self.seen_hashes.add(message_hash)
        return error_message

if __name__ == '__main__':
    firewall = DeltaFirewall()
    
    for i in range(3):
        print(f"--- Iteration {i+1} ---")
        
        # Generate 50 lines of error log with changing timestamp and UUID
        current_time = (datetime.datetime.now() + datetime.timedelta(seconds=i)).strftime("%Y-%m-%d %H:%M:%S")
        current_uuid = str(uuid.uuid4())
        
        error_lines = []
        for j in range(50):
            error_lines.append(f"[{current_time}] ERROR {current_uuid} - Failure on module {j}: Critical exception occurred.")
            
        huge_error_string = "\n".join(error_lines)
        
        # Pass to firewall
        result = firewall.process(huge_error_string)
        
        if result == "[FIREWALL BLOCKED]":
            print(f"Result: {result} - Duplicate structurally similar log detected!")
        else:
            print(f"Result: Log allowed (length: {len(result)} chars)")
            
        time.sleep(1)
