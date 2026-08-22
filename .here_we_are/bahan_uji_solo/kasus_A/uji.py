import subprocess, sys, json
def test_gerbang_menolak():
    r = subprocess.run([sys.executable, "kasus_A/gerbang.py", "belum_siap"], capture_output=True, text=True)
    assert '"lolos": false' in r.stdout.lower(), "gerbang tidak menolak"
