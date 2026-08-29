import os
import sys
import tempfile
import shutil
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "src"))

from snowline.core_close_entry import close_entry_command, validate_topic_name

def run_cli_close_entry(args: list, cwd: str):
    env = dict(os.environ)
    env["PYTHONPATH"] = str(REPO / "src")
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    cmd = [sys.executable, "-B", "-m", "snowline.cli", "close-entry"] + args
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8", env=env)

def test_close_entry_success():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        
        here_we_are = tmp_path / ".here_we_are"
        here_we_are.mkdir()
        
        agents_chamber = tmp_path / ".agents" / "chamber" / "history"
        agents_chamber.mkdir(parents=True)
        
        connector_file = here_we_are / "connector.md"
        state_file = here_we_are / "STATE.md"
        
        # Write dummy connector with 2 entries
        connector_lines = [
            "## Entri 1 - Test Topic 1",
            "Content 1",
            "---",
            "## Entri 2 - Test Topic 2",
            "Content 2"
        ]
        connector_file.write_text("\n".join(connector_lines) + "\n", encoding='utf-8')
        state_file.write_text("# STATE\n\nTUTUP lewat chamber, arsip per topik:\n```\n```\n", encoding='utf-8')
        
        res = run_cli_close_entry(["test-topic"], cwd=tmpdir)
        assert res.returncode == 0, f"close-entry failed: {res.stderr}\n{res.stdout}"
        assert "Berhasil: Entri terakhir ditutup" in res.stdout
        
        new_conn = connector_file.read_text(encoding='utf-8').splitlines()
        assert new_conn == ["## Entri 2 - Test Topic 2", "Content 2"]
        
        hist_file = here_we_are / "history" / "test-topic" / "01-test-topic.md"
        assert hist_file.exists()
        hist_content = hist_file.read_text(encoding='utf-8').splitlines()
        assert hist_content == ["## Entri 1 - Test Topic 1", "Content 1"]
        print("PASS: close-entry arah nama sah -> berhasil, connector berpindah")

def test_close_entry_rejections_and_byte_preservation():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        here_we_are = tmp_path / ".here_we_are"
        here_we_are.mkdir()
        connector_file = here_we_are / "connector.md"
        
        orig_bytes = b"# PM -> TL: Entri Asli\nBaris 1\n---\n# TL -> PM: Entri 2\nBaris 2\n"
        connector_file.write_bytes(orig_bytes)
        
        invalid_topics = [
            "",                 # Kosong persis
            "   ",              # Spasi saja
            "nama berspasi",    # Spasi di tengah
            "Sprint-50",        # Awalan Sprint
            "entri-01",         # Awalan entri
            "QA-Check",         # Awalan QA
        ]
        
        for bad_topik in invalid_topics:
            res = run_cli_close_entry([bad_topik], cwd=tmpdir)
            assert res.returncode != 0, f"close-entry should reject topic '{bad_topik}', got exit code 0"
            assert "Batal:" in res.stdout or "Batal:" in res.stderr
            
            # Verifikasi bita connector tidak berubah satu bita pun
            curr_bytes = connector_file.read_bytes()
            assert curr_bytes == orig_bytes, f"Connector bytes changed on rejected topic '{bad_topik}'!"
            
        print("PASS: close-entry arah nama tidak sah (empty, spaces, bad prefix) -> ditolak, connector utuh bita demi bita")

if __name__ == '__main__':
    test_close_entry_success()
    test_close_entry_rejections_and_byte_preservation()
    print("\nALL CLOSE-ENTRY DIRECTIONS PASSED!")
