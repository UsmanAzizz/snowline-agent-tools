import json

trace_file = r"C:\Users\LENOVO\.claude\projects\D--AAAAAAAAA-cbt-master\abbd62e6-656c-4061-9d29-da2d728599bc.jsonl"
with open(trace_file, 'r', encoding='utf-8') as f:
    for line in f:
        try:
            data = json.loads(line)
        except:
            continue
        if 'message' in data and data.get('isSidechain') is False:
            print(json.dumps(data, indent=2))
            break
