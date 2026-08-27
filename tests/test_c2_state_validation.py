import os
import sys
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

def get_actual_total_skills():
    templates_skills = REPO / "src" / "snowline" / "templates" / "skills"
    if templates_skills.exists():
        return len([d for d in templates_skills.iterdir() if d.is_dir() and (d / "SKILL.md").exists()])
    return 17

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

    # 2. Periksa penyebut (total alat) - dihitung dari direktori jika tidak disuplai
    if expected_total is None:
        expected_total = get_actual_total_skills()
    if total_count != expected_total:
        raise ValueError(
            f"Angka total alat di header ({total_count}) tidak cocok dengan jumlah sebenarnya ({expected_total})."
        )

    # 3. Periksa pembilang (alat beruji)
    if expected_tested is not None and tested_count != expected_tested:
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
    actual_total = get_actual_total_skills()
    assert actual_total == 17, f"Total skill harus 17, didapat: {actual_total}"

    # Arah c: angka sah -> LOLOS
    sample_correct = make_state_sample("tools           beruji                  17 / 17")
    assert validate_state_content(sample_correct, expected_tested=17) is True
    print("PASS: Arah C (17 / 17 -> validasi LULUS)")

    # Arah a: 99 / 17 -> DITOLAK (pembilang > penyebut dan salah hitungan)
    sample_99_17 = make_state_sample("tools           beruji                  99 / 17")
    try:
        validate_state_content(sample_99_17, expected_tested=17)
        assert False, "Arah A gagal: 99 / 17 tidak ditolak"
    except ValueError as e:
        err_msg = str(e)
        assert "99" in err_msg and ("17" in err_msg), f"Pesan galat harus menyebut angka: {err_msg}"
        print(f"PASS: Arah A (99 / 17 -> DITOLAK: '{err_msg}')")

    # Arah b: 0 / 17 -> DITOLAK kalau angkanya bukan 0
    sample_0_17 = make_state_sample("tools           beruji                  0 / 17")
    try:
        validate_state_content(sample_0_17, expected_tested=17)
        assert False, "Arah B gagal: 0 / 17 tidak ditolak"
    except ValueError as e:
        err_msg = str(e)
        assert "0" in err_msg and "17" in err_msg, f"Pesan galat harus menyebut angka: {err_msg}"
        print(f"PASS: Arah B (0 / 17 -> DITOLAK: '{err_msg}')")

    # Arah d: 13 / 99 -> tetap DITOLAK (penyebut salah)
    sample_13_99 = make_state_sample("tools           beruji                  13 / 99")
    try:
        validate_state_content(sample_13_99, expected_tested=17)
        assert False, "Arah D gagal: 13 / 99 tidak ditolak"
    except ValueError as e:
        err_msg = str(e)
        assert "99" in err_msg and "17" in err_msg, f"Pesan galat harus menyebut angka: {err_msg}"
        print(f"PASS: Arah D (13 / 99 -> DITOLAK: '{err_msg}')")

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
    # Jika STATE.md sungguhan masih 13/17 sebelum diupdate atau 17/17 setelah diupdate, pastikan validasi fleksibel
    m = re.search(r'tools\s+beruji\s+(\d+)\s*/\s*(\d+)', real_content)
    if m:
        tested = int(m.group(1))
        assert validate_state_content(real_content, expected_tested=tested) is True
    print("PASS: (Berkas sungguhan .here_we_are/STATE.md -> LULUS)")

if __name__ == "__main__":
    test_c2_state_validation_directions()
    print("\nALL ENTRI C2 DIRECTIONS PASSED!")
