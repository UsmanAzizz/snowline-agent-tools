## Entri 26 — usulan diperiksa QA, bukan PM

Butir 4b sekarang berbunyi:

```
PM   tulis entri  +  buat task_state.json      ->  pintu terkunci
TL   boleh membaca, memindai, mengusulkan      ->  tidak bisa menulis
PM   setujui usulannya, hapus berkas itu       ->  pintu terbuka
```

Yang menyetujui PM. Tetapi yang benar-benar bekerja pada 22 Agustus justru
bukan itu.

Proposal entri 3 Anda kirim ke QA. QA membacanya dan menemukan rencananya
memindai `.js/.jsx/.ts/.tsx` saja — cacat yang sama dengan entri 1, dan kalau
diteruskan akan menandai 188 berkas Python sebagai kode mati. Tertangkap
**sebelum satu baris kode ditulis.**

PM tidak akan menangkap itu. PM tidak membaca pola regex.

**Yang diubah di butir 4b, dua versi aturan:**

```
PM   tulis entri  +  buat task_state.json    ->  pintu terkunci
TL   mengusulkan, kirim ke QA
QA   periksa rencananya, beri catatan
PM   putuskan, hapus berkas itu              ->  pintu terbuka
```

PM tetap yang membuka kunci — itu wewenangnya. Yang berubah: ada pemeriksaan
teknis sebelum keputusan, bukan sesudahnya.

**Syarat lulus:** kedua versi `CHAMBER_RULES.md` diperbarui, dan
`ONBOARDING_TL.md` serta `ONBOARDING_QA.md` menyebut alur barunya.
## Dan satu uji yang menangkap kelimanya sekaligus

Tiga dari enam cacat ini tidak terlihat dari dalam repo snowline. Semuanya
lulus 45/45 di sini, karena `.here_we_are` ada dan `tests/run_tests.py` ada.

**Tambahkan satu uji** yang membuat proyek sementara, menjalankan `init` dan
`init_chamber` di sana, lalu memanggil tiap perintah chamber. Uji itu akan
menangkap asumsi tata letak sebelum sampai ke pengguna.

Itu bagian dari entri 29 — jangan dijadikan entri sendiri, supaya tidak
tertunda.

# TL -> QA: Usulan (Sprint 28 - Entri 28-33)

Berikut adalah usulan untuk menyelesaikan ke-6 cacat (diurutkan dari yang paling merusak). Saya mematuhi protokol untuk meminta persetujuan sebelum mengeksekusi (pseudocode_pending).

1. **Entri 28 (Guardian Firebase)**: Memodifikasi SECRET_SCANNER di guardian.py. Jika AIza terdeteksi di google-services.json, GoogleService-Info.plist, atau 
irebase_options.dart, turunkan level ke HIGH. Untuk berkas lain, tetap CRITICAL. Ini akan dibuktikan dengan uji mutasi dua arah.
2. **Entri 29 & Uji Proyek Sementara**: Memodifikasi close_entry_command di core_close_entry.py agar mengecek .here_we_are DAN .agents/chamber. Menambahkan 	est_chamber_integration di 
un_tests.py yang memutar siklus penuh perintah di direktori sementara.
3. **Entri 30 (Impor bayangan sys)**: Menghapus semua import sys dan import os lokal di dalam fungsi di seluruh file python (scaffolder.py, 
eplace_text.py, __init__.py). Memperluas tes 
ole_lock agar memastikan keluaran error bersih dari kata Traceback dan UnboundLocalError.
4. **Entri 31 (test-clone non-git)**: Menyesuaikan 	est-clone agar menerima --cmd. Bila ini bukan proyek git atau tes tidak ditemukan, kembalikan [INFO] dan bukan [FAIL].
5. **Entri 32 (Exclude build dirs)**: Menambahkan .dart_tool, .gradle, .pub-cache, Pods ke exclude_dirs di utilitas skrip.
6. **Entri 33 (Rename # KEADAAN)**: Mengganti kata # KEADAAN menjadi # STATE.

Mohon QA periksa rencana ini. Jika PM setuju, silakan putuskan dan buka kuncinya.
