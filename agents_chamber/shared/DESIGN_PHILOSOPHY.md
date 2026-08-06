# DESIGN PHILOSOPHY

This file stores the theoretical, academic, and philosophical justifications for architectural decisions in the Chamber ecosystem.
By keeping philosophy here, we keep `project_context.md` strictly focused on factual history and hard rules (Zero-Bloat).

## 1. Role Specialization Validation (The MetaGPT Principle)
Our separation of roles (PM, Tech Lead, QA, Executor) is validated by principles found in MetaGPT and similar frameworks:
- **Product Manager (PM)**: Operates at the human level, defining requirements and making high-level compromises.
- **Tech Lead (TL)**: Acts as the architectural gatekeeper, orchestrating tasks and enforcing constraints (The Ledger). Never writes code directly.
- **QA / Reviewer**: Provides adversarial review. Their independence ensures that the TL's decisions and the Executor's output are stress-tested before merging.
- **Executor**: The coding engine. Focuses strictly on implementation and proving correctness through raw terminal output.

By keeping these separate, we prevent the "echo chamber" effect where a single LLM context becomes a yes-man to its own flawed ideas.

---

## 2. Definisi Asli: Apa Itu Companion, Apa Itu Chamber

*Dicatat 06 Agustus 2026, dari pernyataan langsung PM. Ditulis apa adanya — bukan parafrase — karena niat sebuah rancangan hanya bertahan kalau tercatat dengan kata-kata pemiliknya sendiri.*

### Companion

> "Companion adalah rantai pengikat agen. Ia boleh menjadi binatang pemburu buas, tapi tidak akan pernah bekerja tanpa batas."

Tujuannya, dalam kalimat PM: **mencegah agen berpikir di luar konteks prompt user.**

Konsekuensi yang mengikuti langsung dari definisi ini:

- **Rantai tidak memerintahkan perburuan.** Rantai menentukan sejauh mana yang berburu boleh pergi. Begitu companion mengeluarkan perintah eksekusi, ia berhenti menjadi rantai dan berubah menjadi pemberi perintah — dan itu pembalikan peran, bukan peningkatan kemampuan.
- **Menyarankan, tidak pernah memutuskan.** Yang memahami maksud pengguna adalah agen. Companion hanya perlu memaksa jeda.
- Karena itu `Action: EXECUTE` **bukan bagian dari rancangan awal**. PM menyatakan ia muncul entah kapan dalam proses pengembangan, tanpa pernah ada keputusan untuk menambahkannya. Bila kemudian muncul lagi, itu penyimpangan yang perlu dikembalikan — bukan fitur yang perlu dipertahankan.

**Tentang `CLARIFY`** — menurut PM, ia dimaksudkan sebagai **peringatan untuk kasus yang berdampak signifikan**, bukan penanda bahwa companion sedang bingung. Penilaian atas signifikansi diserahkan kepada agen, karena agen yang memahami konteksnya. PM menyebut padanan kata yang paling dekat: *warning*.

### Chamber

> "Chamber itu tempat di mana agen bekerja gotong royong seperti kebanyakan manusia harapkan saat ini — yang justru jadi ironi untuk manusia itu sendiri."

Catatan yang perlu menyertainya, supaya ironi itu terbaca utuh:

Agen di dalam chamber sebenarnya tidak saling bergotong royong. Mereka tidak bisa saling bicara. TL tidak pernah membaca OUTBOX QA secara langsung; PM yang membawanya. Executor tidak pernah tahu pekerjaannya ditolak; PM yang menyampaikan. Yang terlihat sebagai kerja sama tiga agen sesungguhnya adalah **satu manusia yang menjahit tiga kesendirian**. Tanpa PM, chamber berhenti dalam satu langkah.

Dan koordinasi ini berjalan mulus bukan karena agen lebih pandai bekerja sama, melainkan karena tidak ada di antara mereka yang punya ego, gengsi, atau rasa takut kehilangan muka saat pekerjaannya ditolak. Hal-hal itulah yang membuat gotong royong sulit bagi manusia — dan justru bagian itu yang tidak bisa ditiru chamber.

### Kenapa dua definisi ini dicatat

Sepanjang 05-06 Agustus 2026 ditemukan empat kali *drift* pada file yang seharusnya identik. Semuanya bisa dideteksi dengan `md5` atau `grep`.

Yang kelima berbeda jenis: **niat yang hilang.** `EXECUTE` tumbuh tanpa ada yang memutuskan menambahkannya, dan QA yang membaca seluruh 1006 baris kode companion tetap salah menyimpulkan maksudnya — sampai PM mengoreksi secara lisan. Tidak ada perintah yang bisa menangkap drift semacam itu, karena kode hanya menunjukkan **apa yang ada**, bukan **apa yang dimaksudkan**.

Halaman ini ada supaya siapa pun yang datang berikutnya punya tolok ukur untuk menilai — dan supaya PM tidak perlu hadir untuk menjelaskannya lagi.
