import json

trace_file = r"C:\Users\LENOVO\.claude\projects\D--AAAAAAAAA-cbt-master\abbd62e6-656c-4061-9d29-da2d728599bc.jsonl"
seen = set()
total_cache = 0
total_read = 0

with open(trace_file, 'r', encoding='utf-8') as f:
    for line in f:
        try:
            data = json.loads(line)
        except:
            continue
        
        msg = data.get('message', {})
        msg_id = msg.get('id')
        if not msg_id:
            continue
            
        if msg_id in seen:
            continue
            
        seen.add(msg_id)
        
        usage = msg.get('usage', {})
        total_cache += usage.get('cache_creation_input_tokens', 0)
        total_read += usage.get('cache_read_input_tokens', 0)

print(f"Deduplicated cache_creation_input_tokens: {total_cache}")
print(f"Deduplicated cache_read_input_tokens: {total_read}")
