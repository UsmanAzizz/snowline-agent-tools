import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "src"))

from snowline.cli import evaluate_package_freshness

def test_sprint51_b_six_states():
    """Syarat Lulus B: Enam keadaan penentuan status kemutakhiran paket."""
    
    sha_tag = "a06de462b6ad7e3ce14bf9f09174204a5448b80c"
    sha_head = "9dbca0c4157e6829eeda26c9a08e8e392b93d9d5"
    sha_old = "1111111111111111111111111111111111111111"
    
    # 1. commit = tag terbaru -> mutakhir (latest)
    r1 = evaluate_package_freshness(installed_commit=sha_tag, remote_head_commit=sha_head, latest_tag_commit=sha_tag, tag_name="v1.2.0")
    assert r1["status"] == "latest", f"State 1 failed: expected latest, got {r1}"
    assert r1["matched_target"] == "tag", f"State 1 failed: expected tag match, got {r1}"
    assert "v1.2.0" in r1["reason"] or sha_tag[:8] in r1["reason"], f"State 1 failed reason: {r1}"
    print("PASS: State 1 (commit = tag terbaru -> mutakhir)")

    # 2. commit = HEAD -> mutakhir (latest)
    r2 = evaluate_package_freshness(installed_commit=sha_head, remote_head_commit=sha_head, latest_tag_commit=sha_tag, tag_name="v1.2.0")
    assert r2["status"] == "latest", f"State 2 failed: expected latest, got {r2}"
    assert r2["matched_target"] == "head", f"State 2 failed: expected head match, got {r2}"
    assert "HEAD" in r2["reason"] or sha_head[:8] in r2["reason"], f"State 2 failed reason: {r2}"
    print("PASS: State 2 (commit = HEAD -> mutakhir)")

    # 3. commit = tag terbaru DAN HEAD (sama) -> mutakhir (latest)
    r3 = evaluate_package_freshness(installed_commit=sha_head, remote_head_commit=sha_head, latest_tag_commit=sha_head, tag_name="v1.2.0")
    assert r3["status"] == "latest", f"State 3 failed: expected latest, got {r3}"
    assert r3["matched_target"] == "both", f"State 3 failed: expected both match, got {r3}"
    print("PASS: State 3 (commit = tag terbaru DAN HEAD -> mutakhir)")

    # 4. commit bukan keduanya -> tertinggal (behind)
    r4 = evaluate_package_freshness(installed_commit=sha_old, remote_head_commit=sha_head, latest_tag_commit=sha_tag, tag_name="v1.2.0")
    assert r4["status"] == "behind", f"State 4 failed: expected behind, got {r4}"
    assert "tertinggal" in r4["reason"], f"State 4 failed reason: {r4}"
    print("PASS: State 4 (commit bukan keduanya -> tertinggal)")

    # 5. remote tidak terbaca (None) -> tidak ada klaim (unknown)
    r5 = evaluate_package_freshness(installed_commit=sha_tag, remote_head_commit=None, latest_tag_commit=None)
    assert r5["status"] == "unknown", f"State 5 failed: expected unknown, got {r5}"
    print("PASS: State 5 (remote tidak terbaca -> tidak ada klaim)")

    # 6. commit terpasang tidak diketahui (None) -> tidak ada klaim (unknown)
    r6 = evaluate_package_freshness(installed_commit=None, remote_head_commit=sha_head, latest_tag_commit=sha_tag)
    assert r6["status"] == "unknown", f"State 6 failed: expected unknown, got {r6}"
    print("PASS: State 6 (commit terpasang tidak diketahui -> tidak ada klaim)")

if __name__ == "__main__":
    test_sprint51_b_six_states()
    print("\nALL SPRINT 51 BAGIAN B TESTS PASSED!")
