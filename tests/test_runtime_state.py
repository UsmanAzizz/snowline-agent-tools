"""Menjaga agar .gitignore dan pemeriksa berkas usang tidak berbeda pendapat.

Dulu keduanya punya daftar sendiri-sendiri. `.gitignore` tahu
`session_cache.json` itu keadaan lokal; pemeriksa usang tidak. Akibatnya di
proyek nyata 27 berkas bawaan snowline dilaporkan [USANG] — semuanya salah,
dan label itu jadi kebisingan yang orang belajar abaikan.

Sekarang keduanya dibangun dari satu daftar. Uji ini memeriksa tiga hal:

1. Tiap butir di daftar itu benar-benar muncul di `.gitignore` yang ditulis.
2. Tiap butir itu tidak ditandai [USANG] waktu berkasnya ada.
3. Berkas yang memang asing TETAP ditandai [USANG].

Nomor 3 yang menjaga supaya pengecualiannya tidak kelebaran. Tanpa itu,
"tidak ada yang usang" bisa dicapai dengan mematikan seluruh fiturnya.
"""
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
    build_agents_gitignore,
    is_runtime_state,
)


def _jalankan(args, cwd):
    env = dict(os.environ)
    env["PYTHONPATH"] = str(REPO / "src") + os.pathsep + env.get("PYTHONPATH", "")
    return subprocess.run(
        [sys.executable, "-m", "snowline.cli"] + args,
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


if __name__ == "__main__":
    test_runtime_state_sepakat()
    test_keadaan_lokal_tidak_ditandai_usang()
    print(chr(10) + "RUNTIME STATE OK!")
