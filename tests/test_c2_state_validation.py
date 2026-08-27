import os
import sys
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

def validate_state_content(content: str, actual_skills_count: int = None):
    stripped = content.strip()
    if not stripped:
        raise ValueError("STATE.md kosong.")

    # Arah b: Hanya berisi tanda hubung, garis, bintang, atau spasi
    non_placeholder = re.sub(r'[\s\-\*\#\=\_\|]+', '', stripped)
    if not non_placeholder:
        raise ValueError("STATE.md hanya berisi tanda hubung atau placeholder tanpa konten nyata.")

    if "## Terbuka" not in content or "## Empat bagian" not in content:
        raise ValueError("STATE.md tidak memuat bagian wajib (## Empat bagian / ## Terbuka).")

    # Arah c: Bandingkan angka di header dengan hitungan sebenarnya
    if actual_skills_count is None:
        templates_skills = REPO / "src" / "snowline" / "templates" / "skills"
        if templates_skills.exists():
            actual_skills_count = len([
                d for d in templates_skills.iterdir()
                if d.is_dir() and (d / "SKILL.md").exists()
            ])
        else:
            actual_skills_count = 17

    m_tools = re.search(r'tools\s+beruji\s+(\d+)\s*/\s*(\d+)', content)
    if m_tools:
        header_total = int(m_tools.group(2))
        if header_total != actual_skills_count:
            raise ValueError(
                f"Angka total skills di header ({header_total}) tidak cocok dengan jumlah sebenarnya ({actual_skills_count})."
            )

    return True

def test_c2_state_validation_directions():
    state_file = REPO / ".here_we_are" / "STATE.md"
    if not state_file.exists():
        state_file = REPO / ".agents" / "chamber" / "STATE.md"
    
    with open(state_file, "r", encoding="utf-8") as f:
        real_content = f.read()

    # Arah a: STATE.md normal -> lulus
    assert validate_state_content(real_content) is True
    print("PASS: Arah A (STATE.md normal -> validasi lulus)")

    # Arah b: STATE.md isinya tanda hubung -> uji MERAH
    hyphen_content = "---\n- - -\n---\n# ---\n"
    try:
        validate_state_content(hyphen_content)
        assert False, "Arah B gagal: konten tanda hubung tidak ditolak"
    except ValueError as e:
        assert "tanda hubung" in str(e) or "kosong" in str(e)
        print("PASS: Arah B (STATE.md berisi tanda hubung -> uji MERAH)")

    # Arah c: angka di header salah -> uji MERAH dan menyebut kedua angkanya
    corrupted_header_content = real_content.replace("13 / 17", "13 / 99")
    try:
        validate_state_content(corrupted_header_content, actual_skills_count=17)
        assert False, "Arah C gagal: angka salah tidak ditolak"
    except ValueError as e:
        err_msg = str(e)
        assert "99" in err_msg and "17" in err_msg, f"Arah C gagal: pesan galat tidak menyebut kedua angka:\n{err_msg}"
        print(f"PASS: Arah C (angka salah -> uji MERAH dan menyebut kedua angka: '{err_msg}')")

if __name__ == "__main__":
    test_c2_state_validation_directions()
    print("\nALL ENTRI C2 DIRECTIONS PASSED!")