import os
import sys
import unittest
import traceback
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tests"))

from run_tests import TestRunner

class CustomEmptyError(Exception):
    pass

def test_runner_error_formatting():
    runner = TestRunner()

    # 1. Assert tanpa pesan (harus memuat nama berkas, nomor baris, dan bunyi baris assert)
    def dummy_assert_no_message():
        val = 42
        assert val == 99

    runner.run("dummy assert no msg", dummy_assert_no_message)
    res0 = runner.results[-1]
    assert ("test_runner_error_format.py" in res0 or "dummy assert no msg" in res0), f"Gagal format no msg: {res0}"
    assert "assert val == 99" in res0, f"Gagal memuat baris assert: {res0}"
    assert ":" in res0 and "->" in res0, f"Format tidak memuat nomor baris/panah: {res0}"
    print(f"PASS: Uji assert tanpa pesan -> {res0.strip()}")

    # 2. Assert dengan pesan eksplisit (pesan asli TIDAK berubah)
    def dummy_assert_with_message():
        assert False, "custom error message exactly preserved"

    runner.run("dummy assert with msg", dummy_assert_with_message)
    res1 = runner.results[-1]
    assert res1 == "  [FAIL] dummy assert with msg: custom error message exactly preserved", f"Pesan eksplisit berubah: {res1}"
    print(f"PASS: Uji assert dengan pesan -> {res1.strip()}")

    # 3. Exception non-AssertionError tanpa pesan (misal CustomEmptyError())
    def dummy_error_no_message():
        raise CustomEmptyError()

    runner.run("dummy error no msg", dummy_error_no_message)
    res2 = runner.results[-1]
    assert "[ERROR]" in res2, f"Expected [ERROR], got: {res2}"
    assert "CustomEmptyError" in res2, f"Expected CustomEmptyError, got: {res2}"
    assert ("test_runner_error_format.py" in res2 or "raise CustomEmptyError" in res2), f"Expected file/code, got: {res2}"
    print(f"PASS: Uji exception tanpa pesan -> {res2.strip()}")

    # 4. Exception non-AssertionError dengan pesan
    def dummy_error_with_message():
        raise ValueError("nilai tidak valid")

    runner.run("dummy error with msg", dummy_error_with_message)
    res3 = runner.results[-1]
    assert "[ERROR]" in res3 and "nilai tidak valid" in res3, f"Expected error with msg, got: {res3}"
    print(f"PASS: Uji exception dengan pesan -> {res3.strip()}")

if __name__ == "__main__":
    test_runner_error_formatting()
    print("\nALL RUNNER FORMATTING TESTS PASSED!")
