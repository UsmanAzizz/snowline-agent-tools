from pathlib import Path

# Berkas uji yang sengaja dijalankan terpisah (misal uji rilis yang butuh jaringan dan lambat)
STANDALONE_TESTS = {'test_venv_release'}

def test_tidak_ada_berkas_uji_yatim():
    berkas = {p.stem for p in Path('tests').glob('test_*.py')}
    sumber = Path('tests/run_tests.py').read_text(encoding='utf-8')
    yatim = [b for b in berkas if b not in sumber and b not in STANDALONE_TESTS]
    assert not yatim, f"berkas uji tidak terdaftar: {yatim}"

if __name__ == '__main__':
    test_tidak_ada_berkas_uji_yatim()
    print("ALL TESTS REGISTERED")
