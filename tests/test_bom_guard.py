import os
from pathlib import Path

def test_no_bom_in_src():
    src_dir = Path("src")
    bom_files = []
    
    for py_file in src_dir.rglob("*.py"):
        with open(py_file, "rb") as f:
            content = f.read(3)
            if content.startswith(b"\xef\xbb\xbf"):
                bom_files.append(str(py_file))
                
    assert len(bom_files) == 0, f"Ditemukan berkas .py dengan BOM: {', '.join(bom_files)}"