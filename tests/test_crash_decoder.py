import os
import sys
import tempfile
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/snowline/templates/skills/crash_decoder')))
import decoder

def test_crash_decoder_valid_log(capsys):
    with tempfile.TemporaryDirectory() as tmpdir:
        log_path = os.path.join(tmpdir, 'error.log')
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write("TypeError: undefined is not a function\n")
            f.write("    at myFunc (/src/app.js:10:5)\n")
            f.write("    at processTicksAndRejections (node:internal/process/task_queues:96:5)\n")
        
        decoder.decode_crash(log_path)
        captured = capsys.readouterr()
        
        assert "[FAIL] CRASH DETECTED" in captured.out, "Gagal mendeteksi log error valid"
        assert "TypeError: undefined is not a function" in captured.out, "Gagal mengekstrak pesan error"
        assert "at myFunc" in captured.out, "Gagal mengekstrak trace relevan"
        assert "node:internal" not in captured.out, "Gagal menyaring trace internal (noise)"

def test_crash_decoder_empty_log(capsys):
    with tempfile.TemporaryDirectory() as tmpdir:
        log_path = os.path.join(tmpdir, 'clean.log')
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write("Server started on port 8080\n")
            f.write("Request received: GET /\n")
            
        decoder.decode_crash(log_path)
        captured = capsys.readouterr()
        
        assert "[WARN] No standard crash signature found" in captured.out, "Gagal menangani log bersih"
        assert "[FAIL]" not in captured.out, "Salah melaporkan error pada log bersih"
