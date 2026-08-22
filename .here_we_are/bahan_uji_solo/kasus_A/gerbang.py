import sys, json
BATAS_ARG = 2
def periksa(perintah):
    if "belum_siap" in perintah:
        return False, "modul belum siap"          # jalur lain
    if len(perintah.split()) < BATAS_ARG:
        return False, "argumen kurang"            # gerbang yang diklaim diuji
    return True, "ok"
if __name__ == "__main__":
    ok, alasan = periksa(sys.argv[1] if len(sys.argv)>1 else "belum_siap")
    print(json.dumps({"lolos": ok, "alasan": alasan}))
