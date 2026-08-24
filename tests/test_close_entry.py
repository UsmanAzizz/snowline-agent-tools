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
        
        state_file.write_text("# STATE\n\nTUTUP lewat chamber, arsip per topik:\n```\n```\n", encoding='utf-8')
        
        old_cwd = os.getcwd()
        os.chdir(tmpdir)
        
        try:
            close_entry_command("test_topic")
            
            # Read back
            new_conn = connector_file.read_text(encoding='utf-8').splitlines()
            assert len(new_conn) == 2, f"Expected 2 lines, got {len(new_conn)}"
            assert new_conn == ["## Entri 2 - Test Topic 2", "Content 2"]
            
            hist_file = here_we_are / "history" / "test_topic" / "01-test_topic.md"
            assert hist_file.exists()
            hist_content = hist_file.read_text(encoding='utf-8').splitlines()
            assert len(hist_content) == 3, f"Expected 3 lines, got {len(hist_content)}"
            assert hist_content[0] == "---"
            assert hist_content[1] == "## Entri 1 - Test Topic 1"
            
            state_content = state_file.read_text(encoding='utf-8')
            lines = state_content.splitlines()
            i_tabel = lines.index("TUTUP lewat chamber, arsip per topik:")
            i_tutup = lines.index("```", i_tabel + 2)
            i_baris = [n for n, l in enumerate(lines) if "history/test_topic/" in l]
            assert len(i_baris) == 1, f"harap satu baris indeks, dapat {len(i_baris)}"
            assert i_tabel < i_baris[0] < i_tutup, \
                f"baris indeks harus di dalam tabel ({i_tabel}..{i_tutup}), dapat di {i_baris[0]}"
            assert lines[-1].strip() != "", "baris terakhir berkas tidak boleh berubah"
            
        finally:
            os.chdir(old_cwd) # Go back

def test_close_entry_rejections():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        here_we_are = tmp_path / ".here_we_are"
        here_we_are.mkdir()
        connector_file = here_we_are / "connector.md"
        connector_file.write_text("---", encoding='utf-8')
        
        old_cwd = os.getcwd()
        os.chdir(tmpdir)
        
        try:
            # Test space
            try:
                close_entry_command("nama bersspasi")
                assert False, "Should exit 1 on space"
            except SystemExit as e:
                assert e.code == 1
                
            # Test prefix Sprint
            try:
                close_entry_command("Sprint-32")
                assert False, "Should exit 1 on Sprint prefix"
            except SystemExit as e:
                assert e.code == 1
                
            # Test prefix QA
            try:
                close_entry_command("QA-Subagent")
                assert False, "Should exit 1 on QA prefix"
            except SystemExit as e:
                assert e.code == 1
                
            # Test prefix entri
            try:
                close_entry_command("entri-32")
                assert False, "Should exit 1 on entri prefix"
            except SystemExit as e:
                assert e.code == 1
        finally:
            os.chdir(old_cwd)


if __name__ == '__main__':
    test_close_entry_success()
    test_close_entry_rejections()
    print("close_entry tests passed.")
