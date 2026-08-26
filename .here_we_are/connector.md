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