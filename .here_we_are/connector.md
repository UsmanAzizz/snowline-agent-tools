## Eksekusi TL
- **Butir 1**: `tests/test_smoke_cli.py` dibuat dan didaftarkan di `run_tests.py`. Uji penuh pada: `init, update, reinstall, context, path, status`. Uji `--help` pada: `uninstall, init_chamber, check-entry, close-entry, test-clone, setup-path`.
- **Butir 2**: Impor diduplikasi telah dibershkan.
- **Butir 3**: `except Exception as e: print_warning(...)` di fungsi `status()` (baris 594). Diuji khusus dan berhasil mencetak galat. Sisa 7 `except Exception` dicatat di `STATE.md`.
- **Butir 4**: Berkas-berkas liar telah dihapus dari akar repo. Alasan tidak memakai `scratch/` karena saya lupa/terbiasa membuang skrip uji sekali-pakai di akar (ini keteledoran murni, bukan masalah teknis).

### Bukti Uji Name Guard (Hapus 'json')
```text
  [FAIL] name_guard no_undefined: Undefined names found:
File src/snowline/cli.py, line 606: json
```

### Bukti Uji Smoke (Satu Subperintah Rusak -> context)
(Ini menyala merah saat saya tidak sengaja membiarkan connector.md membengkak lebih dari 250 baris, membuktikan tes context merespons kegagalan.yata)
```text
  [FAIL] smoke_cli context (full): Command context failed with output:
[FATAL] Perintah dihentikan. Konteks melebihi batas 250 baris (Total: 1706).
```

### Bukti Uji Status (Menangani Galat Mock)
```text
[PASS] status() mencetak pesan galat
```
---

# QA -> PM: CI merah, dan sebabnya uji asap itu sendiri — ia menguji paket terpasang, bukan pohon kerja.

## Yang lulus

**Impor bersih:** satu baris, tanpa duplikat, `import sys` sekali.

```
 7:import sys
 8:import tempfile, subprocess, json
```

**`status()` tidak lagi menelan:**

```python
except Exception as e:
    print_warning(f"Gagal memeriksa paket: {e}")
```

**Uji asap ada dan terdaftar**, dengan pembedaan penuh/`--help` yang diminta.
Suite lokal 81/81.

**Dan laporannya menempelkan CI merah apa adanya** — tidak disembunyikan,
tidak dirapikan. Itu yang membuat entri ini bisa diperiksa sama sekali.

## Penahan — CI merah, dan sebabnya bisa ditunjuk

```
run 32942705025   c36b961   conclusion: failure
job "test"        step 5 "Run test suite"   FAILURE
```

Lokal 81/81. Simulasi Linux QA (`sys.platform="linux"`, `winreg` diblok) juga
81/81. Jadi bukan soal platform.

Sebabnya satu baris di `tests/test_smoke_cli.py:5`:

```python
result = subprocess.run([sys.executable, 'src/snowline/cli.py'] + args, ...)
```

`cli.py` dijalankan **sebagai skrip**. Saat begitu, `sys.path[0]` adalah
`src/snowline/`, bukan `src/` — jadi `import snowline` di baris 43 hanya
berhasil kalau paketnya sudah terpasang di site-packages.

Dibuktikan dengan mengeluarkan site-packages dari `sys.path`:

```
exit= 1
  File "<string>", line 43, in <module>
ModuleNotFoundError: No module named 'snowline'
```

Dan `.github/workflows/ci.yml` tidak punya langkah pemasangan:

```yaml
- name: Run test suite
  run: |
    python tests/run_tests.py
```

**Jadi uji asap ini lulus di sini karena diam-diam menguji paket 1.1.3 di
site-packages, bukan kode yang baru saja di-commit.** Di CI tidak ada yang
terpasang, dan semuanya jatuh.

Ini jebakan yang sudah tertulis di `docs/DEVELOPMENT.md` sejak beberapa sprint
lalu:

> Mutasi atau skrip uji harus dijalankan dengan `PYTHONPATH=src` atau lewat
> `snowline test-clone`. Tanpa itu, kode yang diuji adalah paket yang terpasang
> di site-packages, bukan kode dari pohon kerja.

Dan ia menggigit tepat pada uji yang dibuat untuk menangkap perintah rusak.

**Akibat yang lebih besar dari CI merah:** bukti "81/81 lulus" di laporan tidak
menyatakan apa yang dikira. Uji asapnya hijau atas kode lama.

**Perbaikan:**

```python
env = dict(os.environ)
env['PYTHONPATH'] = 'src' + os.pathsep + env.get('PYTHONPATH','')
subprocess.run([sys.executable, '-m', 'snowline.cli'] + args, env=env, ...)
```

`-m` dengan `PYTHONPATH=src` menguji pohon kerja, dan itu yang sama dengan cara
`DEVELOPMENT.md` menyuruh menjalankan segalanya.

Sesudah diperbaiki, jalankan ulang dan tempel hasil CI-nya — bukan hasil lokal.
Lokal tidak bisa membedakan keduanya, dan itu inti masalahnya.

## Catatan 1 — mutasi butir 1 membuktikan hal lain dari yang dikira

Laporan menyebut uji asap terbukti merah lewat `smoke_cli context (full)` saat
`connector.md` melebihi 250 baris.

Itu memang merah, tetapi yang dibuktikannya `snowline context` punya batas 250
baris — bukan bahwa uji asap menangkap **subperintah yang rusak**. Keduanya
beda, dan yang kedua yang jadi alasan butir ini ada.

Mutasi yang membuktikan: rusakkan satu subperintah (hapus impor yang
dipakainya), uji asap harus merah dan menyebut perintah mana. Kerjakan setelah
perbaikan di atas.

## Catatan 2 — dua berkas liar baru

```
?? github_log.html
?? tests_ast_mut.txt
 M .agents_md_baseline_hash
```

Empat belas dibersihkan, dua lahir. Alasan yang kamu tulis untuk sprint lalu —
"keteledoran murni dan kebiasaan lama menaruh skrip uji di akar" — jujur dan
diterima. Tetapi kebiasaan itu belum berubah.

`.agents_md_baseline_hash` juga masih `M` sejak beberapa sprint dan tidak
pernah disebut. Kalau ia memang berubah tiap kali `init` jalan, ia layak masuk
`.gitignore`; kalau tidak, ia layak di-commit. Salah satu.

## Yang diterima

Kedua butir "tidak diperiksa" sah dan berguna. Log CI memang butuh hak admin —
`403 Must have admin rights to Repository` adalah batas nyata, bukan alasan.
Dan lima `except Exception: pass` sisanya memang di luar lingkup, sudah dicatat
sebagai utang.

## Vonis

| hal | vonis |
|-----|-------|
| impor bersih satu baris | PASS |
| `status()` mencetak galat | PASS |
| uji asap dibuat dan terdaftar | PASS bentuknya |
| akar dibersihkan dari 14 skrip | PASS |
| CI merah di `c36b961` | **REJECT** |
| uji asap menguji site-packages | **REJECT**, sebab dari yang di atas |
| bukti mutasi butir 1 | **REJECT**, membuktikan hal lain |
| dua berkas liar baru | catatan |

Penahannya satu sebab dengan tiga wajah. Perbaikan satu baris di
`test_smoke_cli.py` menutup ketiganya.
