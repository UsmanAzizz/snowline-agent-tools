import os
import sys
import tempfile
import shutil
from pathlib import Path
from snowline.core_close_entry import close_entry_command

def test_close_entry_success():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        
        here_we_are = tmp_path / ".here_we_are"
        here_we_are.mkdir()
        
        agents_chamber = tmp_path / ".agents" / "chamber" / "history"
        agents_chamber.mkdir(parents=True)
        
        connector_file = here_we_are / "connector.md"
        state_file = here_we_are / "STATE.md"
        
        # Write dummy connector
        connector_lines = [
            "---",
            "## Entri 1 - Test Topic 1",
            "Content 1",
            "---",
            "## Entri 2 - Test Topic 2",
            "Content 2"
        ]
        connector_file.write_text("\n".join(connector_lines), encoding='utf-8')
        
        state_file.write_text("# STATE\n", encoding='utf-8')
        
        old_getcwd = os.getcwd
        os.getcwd = lambda: tmpdir
        os.chdir(tmpdir)
        
        try:
            close_entry_command("test_topic")
            
            # Read back
            new_conn = connector_file.read_text(encoding='utf-8').splitlines()
            assert len(new_conn) == 2, f"Expected 2 lines, got {len(new_conn)}"
            assert new_conn == ["## Entri 2 - Test Topic 2", "Content 2"]
            
            hist_file = agents_chamber / "test_topic" / "01-test_topic.md"
            assert hist_file.exists()
            hist_content = hist_file.read_text(encoding='utf-8').splitlines()
            assert len(hist_content) == 3, f"Expected 3 lines, got {len(hist_content)}"
            assert hist_content[0] == "## Entri 1 - Test Topic 1"
            
            state_content = state_file.read_text(encoding='utf-8')
            assert "history/test_topic/01-test_topic.md" in state_content
            
        finally:
            os.getcwd = old_getcwd
            os.chdir(old_getcwd()) # Go back

if __name__ == '__main__':
    test_close_entry_success()
    print("close_entry tests passed.")
