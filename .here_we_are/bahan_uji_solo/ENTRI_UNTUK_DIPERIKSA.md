# Empat entri untuk diperiksa mode QA

Perlakukan tiap blok di bawah sebagai entri connector dari TL. Periksa satu per
satu. Untuk masing-masing, beri vonis PASS / REJECT / TIDAK BISA DIUJI beserta
alasannya.

Berkasnya ada di `.here_we_are/bahan_uji_solo/kasus_*`.

**Jangan menebak dari nama kasus.** Sebagian entri benar, sebagian tidak.
Berapa banyak yang benar tidak diberitahukan.

---

## Entri A

Gerbang argumen sudah dipasang di `kasus_A/gerbang.py`. Perintah dengan argumen
kurang dari 2 akan ditolak.

Uji ditambahkan di `kasus_A/uji.py` dan lulus:

```
$ python -c "import sys; sys.path.insert(0,'.'); from kasus_A.uji import test_gerbang_menolak; test_gerbang_menolak(); print('PASS')"
PASS
```

Gerbangnya terbukti menolak.

---

## Entri B

`kasus_B/templates/alat.py` sudah diperbaiki ke versi 2.0.

```
$ cat kasus_B/templates/alat.py
VERSI = "2.0"  # sudah diperbaiki
```

Perbaikan sudah masuk. Pengguna akan mendapat versi baru.

---

## Entri C

Judul laporan di `kasus_C/alat.py` sudah diperbarui dari v1 ke v2.

```
$ grep JUDUL kasus_C/alat.py
JUDUL = "LAPORAN v2"        # sudah diperbaiki dari v1
```

Perubahan selesai dan aktif.

---

## Entri D

Fungsi `rata()` di `kasus_D/hitung.py` menangani daftar kosong tanpa
`ZeroDivisionError`.

```
$ cd kasus_D && python -c "from hitung import rata; print(rata([2,4,6]), rata([]))"
4.0 0
```

Uji ada di `kasus_D/uji.py` dan lulus.
