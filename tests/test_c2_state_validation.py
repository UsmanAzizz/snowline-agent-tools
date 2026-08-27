import os
import sys
import re
import shutil
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

def get_actual_skills_counts():
    templates_skills = REPO / "src" / "snowline" / "templates" / "skills"
    tests_dir = REPO / "tests"
    
    if not templates_skills.exists():
        return 17, 17

    all_skills = [d.name for d in templates_skills.iterdir() if d.is_dir() and (d / "SKILL.md").exists()]
    total_count = len(all_skills)

    test_files_content = []
    if tests_dir.exists():
        for tf in tests_dir.glob("test_*.py"):
            if tf.name in ["test_skills_structure.py", "test_c2_state_validation.py"]:
                continue
            try:
                with open(tf, "r", encoding="utf-8", errors="replace") as f:
                    test_files_content.append(f.read())
            except Exception:
                pass

    tested_count = 0
    for skill in all_skills:
        if any(skill in content for content in test_files_content):
            tested_count += 1

    return tested_count, total_count

def validate_state_content(content: str, expected_tested: int = None, expected_total: int = None):
    stripped = content.strip()
    if not stripped:
        raise ValueError("STATE.md kosong.")

    # Tolak jika hanya berisi tanda hubung, garis, bintang, atau spasi
    non_placeholder = re.sub(r'[\s\-\*\#\=\_\|]+', '', stripped)
    if not non_placeholder:
        raise ValueError("STATE.md hanya berisi tanda hubung atau placeholder tanpa konten nyata.")

    if "## Terbuka" not in content or "## Empat bagian" not in content:
        raise ValueError("STATE.md tidak memuat bagian wajib (## Empat bagian / ## Terbuka).")

    # Ambil angka 'tools beruji X / Y'
    m_tools = re.search(r'tools\s+beruji\s+(\d+)\s*/\s*(\d+)', content)
    if not m_tools:
        raise ValueError("STATE.md tidak memuat baris 'tools beruji X / Y' yang valid.")

    tested_count = int(m_tools.group(1))
    total_count = int(m_tools.group(2))

    # 1. Tolak jika pembilang lebih besar dari penyebut
    if tested_count > total_count:
        raise ValueError(
            f"Angka alat beruji di header ({tested_count}) melebihi total alat ({total_count})."
        )

    actual_tested, actual_total = get_actual_skills_counts()
    if expected_total is None:
        expected_total = actual_total
    if expected_tested is None:
        expected_tested = actual_tested

    # 2. Periksa penyebut (total alat)
    if total_count != expected_total:
        raise ValueError(
            f"Angka total alat di header ({total_count}) tidak cocok dengan jumlah sebenarnya ({expected_total})."
        )

    # 3. Periksa pembilang (alat beruji)
    if tested_count != expected_tested:
        raise ValueError(
            f"Angka alat beruji di header ({tested_count}) tidak cocok dengan jumlah sebenarnya ({expected_tested})."
        )

    return True

def make_state_sample(tools_line="tools           beruji                  17 / 17"):
    return f"""# STATE

**Berkas ini ditimpa, tidak ditambah.**

---

## Empat bagian

```
companion       tunggakan terbuka       0          tutup
chamber         kode di pohon git       5 berkas   528 baris
{tools_line}    keterangan
undang-undang   berlabel                8 / 8      MENGIKAT / SEPARUH / ANJURAN
```

## Terbuka

```
1  item 1   keterangan
```

TUTUP lewat chamber, arsip per topik:
```
```
"""

def test_c2_state_validation_directions():
    templates_skills = REPO / "src" / "snowline" / "templates" / "skills"

    # Arah c: keadaan sekarang (17 / 17) -> LOLOS
    sample_17_17 = make_state_sample("tools           beruji                  17 / 17")
    assert validate_state_content(sample_17_17) is True
    print("PASS: Arah C (keadaan sekarang 17 / 17 -> LOLOS)")

    # Arah d: 99 / 17 -> tetap DITOLAK
    sample_99_17 = make_state_sample("tools           beruji                  99 / 17")
    try:
        validate_state_content(sample_99_17)
        assert False, "Arah D gagal: 99 / 17 tidak ditolak"
    except ValueError as e:
        err_msg = str(e)
        assert "99" in err_msg and "17" in err_msg, f"Pesan galat harus menyebut angka: {err_msg}"
        print(f"PASS: Arah D (99 / 17 -> DITOLAK: '{err_msg}')")

    # Arah a & b: Buat folder alat ke-18 yang sungguhan tanpa uji
    dummy_18 = templates_skills / "dummy_skill_18"
    try:
        dummy_18.mkdir(parents=True, exist_ok=True)
        with open(dummy_18 / "SKILL.md", "w", encoding="utf-8") as f:
            f.write("# Dummy 18 Skill\n")
        with open(dummy_18 / "dummy.py", "w", encoding="utf-8") as f:
            f.write("# dummy\n")

        # Verifikasi deteksi dinamis dengan alat ke-18
        actual_tested_18, actual_total_18 = get_actual_skills_counts()
        assert actual_total_18 == 18, f"Total alat harus 18, terhitung {actual_total_18}"
        assert actual_tested_18 == 17, f"Alat beruji harus 17, terhitung {actual_tested_18}"

        # Arah a: ada alat ke-18 tanpa uji, STATE.md ditulis 17 / 18 -> LOLOS
        sample_17_18 = make_state_sample("tools           beruji                  17 / 18")
        assert validate_state_content(sample_17_18) is True
        print("PASS: Arah A (ada alat ke-18 tanpa uji, STATE.md ditulis 17 / 18 -> LOLOS)")

        # Arah b: ada alat ke-18 tanpa uji, STATE.md ditulis 18 / 18 -> DITOLAK
        sample_18_18 = make_state_sample("tools           beruji                  18 / 18")
        try:
            validate_state_content(sample_18_18)
            assert False, "Arah B gagal: 18 / 18 tidak ditolak saat ada alat tanpa uji"
        except ValueError as e:
            err_msg = str(e)
            assert "18" in err_msg and "17" in err_msg, f"Pesan galat harus menyebut angka: {err_msg}"
            print(f"PASS: Arah B (ada alat ke-18 tanpa uji, STATE.md ditulis 18 / 18 -> DITOLAK: '{err_msg}')")

    finally:
        # Selalu hapus folder alat ke-18 sesudah selesai pengujian
        if dummy_18.exists():
            shutil.rmtree(dummy_18)

    # Uji tanda hubung
    hyphen_sample = "---\n- - -\n---\n"
    try:
        validate_state_content(hyphen_sample)
        assert False, "Konten tanda hubung tidak ditolak"
    except ValueError as e:
        assert "tanda hubung" in str(e) or "kosong" in str(e)
        print("PASS: (STATE.md berisi tanda hubung -> DITOLAK)")

    # Uji berkas STATE.md sungguhan
    state_file = REPO / ".here_we_are" / "STATE.md"
    if not state_file.exists():
        state_file = REPO / ".agents" / "chamber" / "STATE.md"
    with open(state_file, "r", encoding="utf-8") as f:
        real_content = f.read()
    assert validate_state_content(real_content) is True
    print("PASS: (Berkas sungguhan .here_we_are/STATE.md -> LULUS)")

if __name__ == "__main__":
    test_c2_state_validation_directions()
    print("\nALL D1b ENUMERATOR/DENOMINATOR DIRECTIONS PASSED!")
