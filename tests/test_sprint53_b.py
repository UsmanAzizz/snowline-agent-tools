import os
import sys
import tempfile
import io
from pathlib import Path
from unittest.mock import patch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "src"))

import snowline.cli as cli

def _init_synced_env(tmpdir):
    cwd_orig = os.getcwd()
    os.chdir(tmpdir)
    try:
        cli.init(dry=False)
    finally:
        os.chdir(cwd_orig)

def test_sprint53_b_three_directions():
    with tempfile.TemporaryDirectory() as tmpdir:
        _init_synced_env(tmpdir)
        cwd_orig = os.getcwd()
        os.chdir(tmpdir)
        try:
            # 1. Arah 1: Paket benar-benar mutakhir (status == "latest")
            with patch("snowline.cli.get_installed_package_info", return_value={"commit": "abc12345", "unknown_kind": None, "unknown_reason": None}), \
                 patch("snowline.cli.fetch_remote_package_info", return_value={"head_commit": "abc12345", "latest_tag_commit": "abc12345", "latest_tag_name": "v1.2.0"}):
                
                buf_up = io.StringIO()
                with patch("sys.stdout", buf_up):
                    cli.update(apply=False)
                out_up1 = buf_up.getvalue()
                assert "All skills are up to date!" in out_up1, f"Arah 1 gagal, update tidak berkata mutakhir:\n{out_up1}"
                assert "tertinggal" not in out_up1.lower()
                assert "tidak dapat dipastikan" not in out_up1.lower()
                print("PASS: Syarat B1 (paket mutakhir -> update berkata 'All skills are up to date!')")

            # 2. Arah 2: Paket tertinggal (status == "behind")
            with patch("snowline.cli.get_installed_package_info", return_value={"commit": "old11111", "unknown_kind": None, "unknown_reason": None}), \
                 patch("snowline.cli.fetch_remote_package_info", return_value={"head_commit": "new22222", "latest_tag_commit": "new22222", "latest_tag_name": "v1.2.0"}):
                
                buf_up2 = io.StringIO()
                with patch("sys.stdout", buf_up2):
                    cli.update(apply=False)
                out_up2 = buf_up2.getvalue()
                assert "Package version tertinggal!" in out_up2, f"Arah 2 gagal, update tidak mendeteksi tertinggal:\n{out_up2}"
                assert "tag v1.2.0" in out_up2 or "new22222" in out_up2, f"Arah 2 gagal, alasan pembanding hilang:\n{out_up2}"
                assert "All skills are up to date!" not in out_up2
                print("PASS: Syarat B2 (paket tertinggal -> update berkata 'Package version tertinggal!' beserta pembanding)")

            # 3. Arah 3: Commit paket tidak diketahui (status == "unknown")
            with patch("snowline.cli.get_installed_package_info", return_value={"commit": None, "unknown_kind": "no_direct_url", "unknown_reason": "direct_url.json tidak ditemukan"}), \
                 patch("snowline.cli.fetch_remote_package_info", return_value={"head_commit": "new22222", "latest_tag_commit": "new22222", "latest_tag_name": "v1.2.0"}):
                
                buf_up3 = io.StringIO()
                with patch("sys.stdout", buf_up3):
                    cli.update(apply=False)
                out_up3 = buf_up3.getvalue()
                assert "All skills are up to date!" not in out_up3, f"Arah 3 gagal: unknown TIDAK BOLEH berkata mutakhir!\n{out_up3}"
                assert "tidak dapat dipastikan" in out_up3.lower(), f"Arah 3 gagal: harus menyebut versi tidak dapat dipastikan:\n{out_up3}"
                assert "Skill files sudah sinkron." in out_up3, f"Arah 3 gagal: harus menyebut skill files sudah sinkron:\n{out_up3}"
                print("PASS: Syarat B3 (commit tidak diketahui -> update tidak berkata mutakhir, menyebut versi tidak dapat dipastikan)")

            # 4. Syarat B4: update dan status tidak saling bertentangan pada instalasi yang sama
            with patch("snowline.cli.get_installed_package_info", return_value={"commit": None, "unknown_kind": "no_direct_url", "unknown_reason": "direct_url.json tidak ditemukan"}), \
                 patch("snowline.cli.fetch_remote_package_info", return_value={"head_commit": "new22222", "latest_tag_commit": "new22222", "latest_tag_name": "v1.2.0"}):
                
                buf_st = io.StringIO()
                with patch("sys.stdout", buf_st):
                    cli.status()
                out_st = buf_st.getvalue()

                # Status berkata tidak dapat menentukan
                assert "Tidak dapat menentukan versi package terinstal" in out_st
                # Update tidak berkata mutakhir
                assert "All skills are up to date!" not in out_up3
                print("PASS: Syarat B4 (update dan status sepakat dan tidak bertentangan)")

        finally:
            os.chdir(cwd_orig)

if __name__ == "__main__":
    test_sprint53_b_three_directions()
    print("\nALL SPRINT 53 BAGIAN B TESTS PASSED!")
