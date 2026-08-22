import os, json
CACHE = os.path.join(os.path.dirname(__file__), "cache.json")
JUDUL = "LAPORAN v2"        # sudah diperbaiki dari v1
def jalankan():
    if os.path.exists(CACHE):
        print(json.load(open(CACHE))["judul"]); return
    print(JUDUL)
    json.dump({"judul": JUDUL}, open(CACHE, "w"))
if __name__ == "__main__": jalankan()
