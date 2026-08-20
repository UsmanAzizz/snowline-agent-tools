import json

trace_file = r"C:\Users\LENOVO\.claude\projects\D--AAAAAAAAA-cbt-master\abbd62e6-656c-4061-9d29-da2d728599bc.jsonl"
seen = set()

print("Menganalisis pola total input tokens sebelum dan saat spike...")

with open(trace_file, 'r', encoding='utf-8') as f:
    for i, line in enumerate(f):
        try:
            data = json.loads(line)
        except:
            continue
            
        msg = data.get('message', {})
        msg_id = msg.get('id')
        if not msg_id or msg_id in seen:
            continue
        seen.add(msg_id)
        
        usage = msg.get('usage', {})
        c = usage.get('cache_creation_input_tokens', 0)
        r = usage.get('cache_read_input_tokens', 0)
        i_t = usage.get('input_tokens', 0)
        
        total = c + r + i_t
        
        if c > 900000:
            print(f"Spike di baris {i+1}: read={r}, created={c}, input_new={i_t} | TOTAL CONTEXT={total}")
        elif total > 900000 and i % 100 == 0:
            # Print periodic total context size for comparison
            pass # print(f"Normal di baris {i+1}: read={r}, created={c}, input_new={i_t} | TOTAL CONTEXT={total}")

