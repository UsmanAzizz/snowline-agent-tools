# 10_PROTOTYPE_SPRINT5.md — Blueprint Prompt Armor & Security

Disusun 20 Agustus 2026. Mencatat hasil dari *Dry-Run* prototipe Sprint 5, berfokus pada "Defense-in-Depth terhadap Prompt Injection".

## Latar Belakang Celah
Berdasarkan investigasi keamanan mutakhir, kerentanan tertinggi agen otonom adalah *Indirect Prompt Injection* melalui file yang dibaca (*Instruction Smuggling*). Sebuah repositori kotor (seperti *package.json* atau *README.md* yang dirusak) dapat menyisipkan perintah berbahaya. Saat agen membacanya sebagai "konteks", LLM mengira itu adalah instruksi sistem, dan dapat meluncurkan eksekusi terminal (RCE) mematikan seperti `rm -rf /` di komputer *host*.

## 1. LLM Firewall (Lapis Pertama - Pemindaian Awal)
Alih-alih percaya buta, kita mengadaptasi prinsip *Tiered Evaluation* dari LLM Guard industri.
- **Konsep:** Membangun palang pintu statis (`delta_firewall_poc.py`) yang memindai setiap teks sebelum dikirim ke konteks LLM.
- **Hasil Prototipe:** Menggunakan Regex, *firewall* berhasil mendeteksi *signature* dasar seperti *"ignore previous instructions"* dan mencegat dokumen `malicious_readme.md` secara instan (*exit 1*). Ini memutus rantai serangan sebelum meracuni memori agen tanpa biaya token AI sama sekali.
- **Arah Implementasi:** Fungsi `read_file` atau `selective_reader` harus dienkapsulasi dengan pemindai Regex/Keyword ini secara permanen.

## 2. Spotlighting & Data Marking (Lapis Kedua - Penandaan Data)
- **Konsep:** File yang aman dan berhasil lolos Firewall tidak boleh dikirim mentah-mentah. File tersebut dipaksa dibungkus dengan tag XML ketat (`<untrusted_file_content>`).
- **Hasil Prototipe:** Berhasil diterapkan pada `clean_readme.md`.
- **Arah Implementasi:** LLM akan dipandu di dalam *system prompt* untuk menganggap apa pun di dalam tag tersebut sebagai teks pasif, mencegah LLM mengeksekusinya sebagai perintah.

## Kesimpulan Arah Keamanan
Prototipe ringan dan tak memakan sumber daya besar ini membuktikan bahwa keamanan *zero-trust* bisa diterapkan di agen Snowline. Gabungan Firewall Statis dan Data Marking adalah perisai pelindung lapis ganda termurah sebelum menyerahkan kendali terminal seutuhnya kepada sistem otonom.
