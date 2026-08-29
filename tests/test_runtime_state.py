import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "src"))

from snowline.cli import (  # noqa: E402
    RUNTIME_STATE_FILES,
    RUNTIME_STATE_DIRS,
    PROTECTED_FILES,
    is_protected,
    build_agents_gitignore,
    is_runtime_state,
)


def _jalankan(args, cwd):
    env = dict(os.environ)
    env["PYTHONPATH"] = str(REPO / "src") + os.pathsep + env.get("PYTHONPATH", "")
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(
        [sys.executable, "-B", "-m", "snowline.cli"] + args,
        cwd=cwd, capture_output=True, text=True, env=env, timeout=120,
    )


def test_runtime_state_sepakat():
    gi = build_agents_gitignore()

    # 1. Tiap butir daftar muncul di .gitignore
    for nama in RUNTIME_STATE_FILES:
        assert nama in gi, (
            "'" + nama + "' ada di RUNTIME_STATE_FILES tetapi tidak muncul di "
            ".gitignore. Kedua daftar itu harus dibangun dari sumber yang sama."
        )
    for d in RUNTIME_STATE_DIRS:
        if d == "__pycache__":
            continue
        assert d + "/" in gi, (
            "'" + d + "' ada di RUNTIME_STATE_DIRS tetapi tidak muncul di .gitignore."
        )

    # 2. is_runtime_state mengenali semuanya, termasuk pemisah Windows
    for nama in RUNTIME_STATE_FILES:
        assert is_runtime_state(nama), "is_runtime_state gagal mengenali " + nama
    for d in RUNTIME_STATE_DIRS:
        assert is_runtime_state(d + "/isi.json"), (
            "is_runtime_state gagal mengenali isi folder " + d
        )
        assert is_runtime_state(d.replace("/", chr(92)) + chr(92) + "isi.json"), (
            "is_runtime_state gagal mengenali jalur bergaya Windows di " + d
        )

    # 3. Yang asing tetap dikenali sebagai bukan keadaan lokal
    for asing in ("skills/berkas_asing.md", "hooks/quality_gate.py", "agents.md"):
        assert not is_runtime_state(asing), (
            "'" + asing + "' salah dianggap keadaan lokal. Pengecualiannya "
            "kelebaran — berkas asing tidak akan pernah ditandai usang lagi."
        )

    print("PASS: daftar keadaan lokal sepakat dengan .gitignore")


def test_keadaan_lokal_tidak_ditandai_usang():
    with tempfile.TemporaryDirectory() as tmp:
        hasil = _jalankan(["init", "--apply"], tmp)
        assert hasil.returncode == 0, "init gagal: " + hasil.stderr

        agents = Path(tmp) / ".agents"

        # Buat berkas untuk tiap butir keadaan lokal
        for nama in RUNTIME_STATE_FILES:
            f = agents / nama
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text("{}" + chr(10), encoding="utf-8")
        for d in RUNTIME_STATE_DIRS:
            folder = agents / d
            folder.mkdir(parents=True, exist_ok=True)
            (folder / "contoh.json").write_text("{}" + chr(10), encoding="utf-8")

        # Dan satu berkas yang memang asing
        (agents / "skills" / "berkas_asing.md").write_text("x" + chr(10), encoding="utf-8")

        keluaran = _jalankan(["update"], tmp).stdout
        usang = [b for b in keluaran.split(chr(10)) if "[USANG]" in b and "Catatan" not in b]

        asing = [b for b in usang if "berkas_asing" in b]
        assert len(asing) == 1, (
            "berkas asing seharusnya tetap ditandai usang, tetapi tidak. "
            "Baris usang: " + repr(usang)
        )

        palsu = [b for b in usang if "berkas_asing" not in b]
        assert not palsu, (
            "Ada " + str(len(palsu)) + " keadaan lokal yang salah ditandai usang:"
            + chr(10) + chr(10).join(palsu[:6])
        )

        print("PASS: " + str(len(RUNTIME_STATE_FILES) + len(RUNTIME_STATE_DIRS))
              + " butir keadaan lokal tidak ditandai usang, berkas asing tetap ditandai")


def test_protected_case_insensitive_and_obsolete_preservation():
    """Sprint 50 Entri 5: PROTECTED tidak peka huruf di update dan status."""
    with tempfile.TemporaryDirectory() as tmp:
        res_init = _jalankan(["init", "--apply"], tmp)
        assert res_init.returncode == 0, f"init gagal: {res_init.stderr}"
        
        agents = Path(tmp) / ".agents"
        
        # 1. Buat 3 variasi huruf berkas terlindungi
        # Di Windows berkas dengan nama beda huruf adalah sama di disk,
        # jadi kita uji satu per satu untuk memastikan perbandingan string tidak peka huruf.
        variations = ["project_context.md", "PROJECT_CONTEXT.md", "Project_Context.md"]
        for var_name in variations:
            f = agents / var_name
            f.write_text("catatan konteks proyek", encoding="utf-8")
            
            # Uji di snowline update
            res_update = _jalankan(["update"], tmp)
            assert res_update.returncode == 0
            usang_update = [b for b in res_update.stdout.splitlines() if "[USANG]" in b and "Catatan" not in b]
            assert not any(var_name in line or "project_context" in line.lower() for line in usang_update), (
                f"Kegagalan di update: {var_name} salah ditandai USANG!\nKeluaran:\n{res_update.stdout}"
            )
            
            # Uji di snowline status
            res_status = _jalankan(["status"], tmp)
            assert res_status.returncode == 0
            usang_status = [b for b in res_status.stdout.splitlines() if "[USANG]" in b and "Catatan" not in b]
            assert not any(var_name in line or "project_context" in line.lower() for line in usang_status), (
                f"Kegagalan di status: {var_name} salah ditandai USANG!\nKeluaran:\n{res_status.stdout}"
            )
            
            f.unlink()

        # 2. Arah kontrol: Berkas asing (tidak terlindungi) TETAP ditandai USANG
        berkas_asing = agents / "catatan_saya.md"
        berkas_asing.write_text("catatan pribadi", encoding="utf-8")
        
        res_update_asing = _jalankan(["update"], tmp)
        usang_up = [b for b in res_update_asing.stdout.splitlines() if "[USANG]" in b and "Catatan" not in b]
        assert any("catatan_saya.md" in line for line in usang_up), (
            f"catatan_saya.md harus tetap ditandai USANG di update!\nKeluaran:\n{res_update_asing.stdout}"
        )
        
        res_status_asing = _jalankan(["status"], tmp)
        usang_st = [b for b in res_status_asing.stdout.splitlines() if "[USANG]" in b and "Catatan" not in b]
        assert any("catatan_saya.md" in line for line in usang_st), (
            f"catatan_saya.md harus tetap ditandai USANG di status!\nKeluaran:\n{res_status_asing.stdout}"
        )
        
        print("PASS: project_context.md (3 variasi huruf) TIDAK usang, catatan_saya.md TETAP usang di update & status")


if __name__ == "__main__":
    test_runtime_state_sepakat()
    test_keadaan_lokal_tidak_ditandai_usang()
    test_protected_case_insensitive_and_obsolete_preservation()
    print("\nALL RUNTIME STATE & PROTECTED TESTS PASSED!")
