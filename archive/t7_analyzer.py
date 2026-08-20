import json
import sys

def analyze_cache_cancellations(trace_file):
    print(f"Menganalisis file dengan pelacakan context tree: {trace_file}")
    
    # Map uuid -> total context size (read + created + input)
    # or just input tokens accumulated? No, the API gives us usage directly!
    # API usage tells us the TOTAL tokens sent in this turn:
    # total_in_this_turn = cache_read + cache_creation + input_tokens
    
    total_cache_creation = 0
    avoidable_cancellations = 0
    seen_msg_ids = set()
    spikes = []
    
    context_sizes = {} # uuid -> total_tokens
    
    with open(trace_file, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                continue
                
            node_uuid = data.get('uuid') or data.get('parentUuid') # Some objects use parentUuid for their own ID if they are delta updates
            
            # The message object contains the usage
            msg = data.get('message', {})
            msg_id = msg.get('id')
            
            if msg_id:
                if msg_id in seen_msg_ids:
                    continue
                seen_msg_ids.add(msg_id)
                
                usage = msg.get('usage', {})
                if usage:
                    c = usage.get('cache_creation_input_tokens', 0)
                    r = usage.get('cache_read_input_tokens', 0)
                    i_t = usage.get('input_tokens', 0)
                    
                    total_tokens = c + r + i_t
                    if node_uuid:
                        context_sizes[node_uuid] = total_tokens
                    
                    if c > 0:
                        total_cache_creation += c
                        
                        # Cek apakah ini lonjakan yang sia-sia
                        # We don't have the parent's exact context size easily because
                        # the parent might be a user message (which doesn't have 'usage').
                        # But we know that 'i_t' (input_tokens) is the ONLY non-cached part of the payload.
                        # Wait! If the cache broke, 'cache_creation' + 'input_tokens' are the non-cached parts.
                        # Actually, if the context grew naturally, 'c' should be roughly equal to the size of the new message.
                        # If 'c' is MASSIVE (e.g. 50k) but 'i_t' is tiny (e.g. 2), it means the cache was rebuilt.
                        # QA rejected this because they said "input_tokens" is just the non-cached tokens.
                        # BUT THAT'S EXACTLY THE POINT! If input_tokens is 2, it means the entire rest of the payload was either read from cache or written to cache.
                        # If 900k tokens were written to cache, WHERE DID THEY COME FROM?
                        # They came from the history! Why were they written to cache instead of read from cache?
                        # Because the prefix broke!
                        
                        # Let's find the previous total_tokens in the same session to calculate the delta
                        # We will just keep track of the LAST known total_tokens in the main chain.
                        pass
                        
    # Let's simplify: just track the LAST total_tokens.
    # Since it's a linear conversation (mostly), total_tokens should monotonically increase.
    last_total = 0
    total_cache_creation = 0
    avoidable_cancellations = 0
    seen_msg_ids = set()
    spikes = []
    
    with open(trace_file, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            try:
                data = json.loads(line)
            except:
                continue
                
            if data.get('isSidechain') is True:
                continue
                
            msg = data.get('message', {})
            msg_id = msg.get('id')
            
            if msg_id and msg_id not in seen_msg_ids:
                seen_msg_ids.add(msg_id)
                usage = msg.get('usage', {})
                if usage:
                    c = usage.get('cache_creation_input_tokens', 0)
                    r = usage.get('cache_read_input_tokens', 0)
                    i_t = usage.get('input_tokens', 0)
                    
                    total = c + r + i_t
                    
                    if last_total > 0 and c > 5000:
                        # Pertumbuhan riil adalah seberapa banyak total konteks bertambah dari turn sebelumnya
                        growth = total - last_total
                        
                        is_avoidable = False
                        
                        # Jika penciptaan cache jauh melampaui pertumbuhan konteks sesungguhnya
                        # (misal: konteks tumbuh 5.000 token, tapi cache_creation 50.000 token)
                        # Berarti 45.000 token adalah penulisan ulang riwayat lama akibat prefix pecah!
                        if c > growth + 2000 and growth >= 0:
                            is_avoidable = True
                            # Yang sia-sia adalah (cache_creation - pertumbuhan)
                            wasted = c - growth
                            if wasted > 0:
                                avoidable_cancellations += wasted
                            spikes.append({
                                'line': i+1,
                                'c': c,
                                'r': r,
                                'growth': growth,
                                'wasted': wasted
                            })
                            
                    if total > 0:
                        last_total = total
                    
                    total_cache_creation += c

    print("-" * 50)
    print(f"Total deduplicated cache_creation: {total_cache_creation}")
    print(f"Total pembatalan terhindarkan (wasted): {avoidable_cancellations}")
    if total_cache_creation > 0:
        print(f"Persentase wasted: {(avoidable_cancellations/total_cache_creation)*100:.2f}%")
        
        print("\nTop 5 Wasted Spikes (Main Chain Only):")
        spikes = sorted(spikes, key=lambda x: x['wasted'], reverse=True)
        for s in spikes[:5]:
            print(f"Baris {s['line']}: Created={s['c']}, Growth={s['growth']}, Wasted={s['wasted']}")

if __name__ == "__main__":
    analyze_cache_cancellations(r"C:\Users\LENOVO\.claude\projects\D--AAAAAAAAA-cbt-master\abbd62e6-656c-4061-9d29-da2d728599bc.jsonl")
