[KONTEKS PROYEK]
Ini project snowline-agent-tools - toolkit Python buat AI coding agent (Claude Code, Gemini/Antigravity). Companion.py adalah intent analyzer yang baca instruksi user dan nyaranin tool mana yang dipakai, tanpa mengambil keputusan sendiri (agent yang tetap mutusin). Baca CURRENT_STATE.md dan AGENTS.md di root project untuk detail lengkap sebelum mulai kerja apa pun.

[LATAR BELAKANG TASK INI]
Rencana Phase 7 ini diambil dari 25 poin "insight" yang digenerate Gemini saat evaluasi ekosistem berulang kali (user cuma bilang "lagi", "more" berkali-kali). Sebagian besar poin adalah scope inflation (multi-agent OS, LSP/tree-sitter integration, auto git branching, "Double Agent Architecture", positioning sebagai saingan LangChain) - SUDAH DITOLAK karena tidak sesuai skala proyek personal ini (satu user, level programmer 3/10, kebutuhan project CBT dan persuratan desa). Ini pola yang sama seperti TASK 7 "Agent-Free Execution" yang sudah ditolak jauh sebelumnya di histori proyek ini.

Dua poin dari Gemini juga FAKTUAL SALAH - poin 7 mengklaim smart_replace tidak punya syntax validation (padahal sudah ada ast.parse untuk Python dan node --check untuk JS), dan poin 9 mengklaim tidak ada dry-run enforcement (padahal dry-run sudah jadi default, --apply ditolak otomatis untuk risiko Medium/High tanpa --apply-validated). Ini contoh nyata kenapa analisis yang "kedengaran meyakinkan" perlu diverifikasi, bukan diterima mentah.

Hanya 3 poin dari 25 itu yang diambil karena genuinely applicable ke skala proyek ini. Kerjakan SATU PER SATU, jangan sekaligus - laporkan dengan bukti, tunggu approval user sebelum lanjut ke task berikutnya.

Jika task ini menyentuh LEBIH DARI 3 file sekaligus, WAJIB jalankan companion task_lock dulu (python .agents/skills/companion_cli.py task start <task_id> "<deskripsi>") SEBELUM operasi filesystem apa pun - ini guard yang sudah ada di AGENTS.md, lahir dari insiden nyata sebelumnya di proyek ini.

---

[TASK 7.1] Diff Visibility di smart_replace

Masalah: File smart_replace/replace_text.py saat ini hanya melaporkan "[SUCCESS] Berhasil memodifikasi N file" setelah --apply berhasil, tidak menunjukkan APA isi perubahannya. User/agent harus buka file manual untuk verifikasi hasil.

Rencana: Setelah --apply atau --apply-validated berhasil menulis file, tampilkan diff sederhana (baris yang dihapus vs ditambahkan) untuk tiap file yang diubah. Tidak perlu library diff eksternal - variabel content (isi lama) dan new_content (isi baru) sudah tersedia di memory saat loop pending_writes berjalan di dalam main(). Bisa pakai modul difflib bawaan Python (difflib.unified_diff) untuk generate diff sederhana.

Live-test wajib, output mentah: Jalankan smart_replace --apply pada 1 file dengan perubahan kecil dan jelas (misal ganti satu nama variabel), tunjukkan command asli dan output literal - harus menampilkan diff yang jelas (baris lama vs baris baru dengan tanda - dan +), bukan hanya pesan sukses generik.

---

[TASK 7.2] Prefix Error Tool vs Error Project

Masalah: Jika ada bug di dalam script .agents/skills/ sendiri (misal KeyError atau AttributeError di kode Python tool itu sendiri), traceback yang muncul di terminal tidak dibedakan dari error yang berasal dari kode project milik user. AI yang menjalankan tool bisa bingung dan mencoba "memperbaiki" kode project padahal yang rusak adalah tool internalnya.

Rencana: Bungkus pemanggilan main() di smart_replace/replace_text.py dan smart_search/code_finder.py (dua tool dulu sebagai percobaan awal, bukan semua sekaligus) dengan try-except di level paling luar. Jika terjadi exception yang tidak tertangani, cetak dulu pesan "[TOOL ERROR - ini bug internal snowline, BUKAN masalah di kode project Anda]" sebelum menampilkan traceback aslinya, lalu exit dengan kode error yang jelas.

Live-test wajib, output mentah: Simulasikan bug internal (misal sisipkan sementara baris yang sengaja error di salah satu tool), jalankan, tunjukkan command dan output literal yang membuktikan pesan pembeda itu muncul sebelum traceback. Kembalikan kode tool ke kondisi normal (hapus baris sengaja error) setelah pengujian selesai, dan buktikan tool kembali berfungsi normal.

---

[TASK 7.3] Severity Threshold di Project Guardian

Masalah: project_guardian/guardian.py sudah mengklasifikasikan temuan sebagai CRITICAL/HIGH/LOW, tapi AGENTS.md belum punya instruksi eksplisit yang mewajibkan AI berhenti kalau ada temuan CRITICAL - saat ini AI bisa saja menyebutkan temuan itu lalu tetap lanjut ke instruksi berikutnya tanpa jeda.

Rencana: Tambahkan section baru ke AGENTS.md (dan sinkronkan ke AGENTS_TEMPLATE.md seperti biasa): "Jika project_guardian melaporkan severity CRITICAL, AI WAJIB berhenti dan melaporkan temuan itu ke user terlebih dahulu SEBELUM melanjutkan task atau instruksi lain apa pun. Tidak boleh dilanjutkan tanpa konfirmasi eksplisit dari user, meskipun instruksi asal tidak menyebutkan soal keamanan."

Live-test wajib, output mentah: Jalankan project_guardian pada project yang punya kerentanan CRITICAL (bisa disimulasikan dengan menaruh dummy credential/API key palsu di file test sementara), tunjukkan output mentah project_guardian yang mendeteksi CRITICAL, lalu tunjukkan bahwa berdasarkan aturan baru ini, AI akan berhenti dan melapor - bukan otomatis lanjut ke instruksi berikutnya. Hapus file test dummy setelah selesai.

---

[ATURAN WAJIB YANG SUDAH ADA DI AGENTS.md, TETAP HARUS DIIKUTI]
- Command asli dan output literal WAJIB ditampilkan untuk setiap live-test, tidak boleh diringkas, dipotong, atau diganti placeholder seperti "[Output: ALL]" atau tabel "✅ Passed"
- Setiap klaim status selesai WAJIB pakai fakta/angka spesifik yang bisa dipatahkan (falsifiable), sertakan tingkat verifikasi eksplisit ("diverifikasi langsung dengan X" atau "belum diverifikasi ulang")
- Dilarang bahasa superlatif/menenangkan: "sempurna", "100%", "bekerja dengan baik", "sudah OK" - ganti dengan fakta konkret
- Setelah masing-masing dari 3 task selesai dengan bukti, commit dengan pesan jelas, lalu tunggu instruksi lanjut

Mulai dari