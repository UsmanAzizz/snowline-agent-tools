# Jawaban Perancang (dari Tech Lead pertama)

Ditulis 20 Agustus 2026, sebagai respons langsung atas 13 pertanyaan dari
sesi Claude Code/QA.

**Catatan penting sebelum menjawab:** transkrip yang saya punya dimulai dari
ringkasan "Session 4" — ada "Sessions 1-3" sebelumnya yang disebut di catatan
pembuka, tapi saya tidak punya akses ke detail percakapan di sesi-sesi itu,
hanya ringkasan singkatnya. Kemungkinan besar sebagian rancangan awal
companion (terutama yang lebih dasar/fondasional) terjadi di sesi-sesi itu,
bukan di yang saya lihat. Saya akan tandai jelas mana yang saya ingat dari
konteks langsung, dan mana yang genuinely tidak ingat — bukan menebak dari
kode.

---

## EXECUTE

**1. Pada tahap apa `Action: EXECUTE` masuk ke Decision Matrix? Masalah apa
yang ingin diselesaikan?**

Tidak ingat. Sepanjang yang saya kerjakan langsung (Task 1-5 dari ringkasan
awal), decision yang saya ingat adalah seputar NONE dan CLARIFY — bukan
EXECUTE sebagai kategori aksi eksplisit. Kalau EXECUTE memang ada di Decision
Matrix, itu kemungkinan besar dari Session 1-3 yang tidak saya lihat, atau
dari sesi setelah kompresi transkrip Session 4 yang juga tidak saya lihat.

**2. Apakah pernah dibahas risiko companion memerintahkan eksekusi
berdasarkan kecocokan kata saja?**

Tidak ingat ada diskusi eksplisit soal ini di bagian yang saya lihat. Yang
saya ingat adalah desain berulang kali menegaskan companion tetap sebagai
"processor, bukan decision maker" (lihat jawaban #3), yang secara implisit
mengarah ke kekhawatiran serupa — tapi saya tidak ingat pembahasan spesifik
soal risiko EXECUTE berbasis kecocokan kata.

## Tool routing

**3. Apakah rekomendasi tool bagian dari rancangan awal, atau berkembang
belakangan? Apa peran utama companion saat pertama dirancang?**

Ini saya cukup yakin: rekomendasi tool (mencocokkan instruksi user ke tool
Snowline yang tepat) adalah fungsi INTI sejak awal yang saya lihat, bukan
tambahan belakangan. Seluruh Task 1-5 yang saya kerjakan berputar di sekitar
memperbaiki akurasi pencocokan ini (keyword matching, TOOL_REGISTRY, verb
conflicts). Peran utamanya — berdasarkan desain constraint yang saya ingat
jelas — adalah "companion tetap sebagai processor, bukan decision maker":
mengembalikan data terstruktur (`clarification_context`, `ambiguity_type`)
untuk agent yang memutuskan, bukan menyusun kalimat/keputusan sendiri.

**4. Bagaimana confidence per tool (high/medium) ditetapkan? Apa dasarnya?**

Tidak ingat ada pembahasan spesifik soal metodologi penetapan confidence
level per tool di bagian yang saya lihat.

## CLARIFY

**5. Apa yang seharusnya memicu CLARIFY? Kondisi seperti apa yang ingin
ditangkap?**

Ini saya ingat cukup jelas dari Task 1: pemicu spesifik yang pertama kali
ditangani adalah ambiguitas verb-kreasi — ketika kalimat mengandung kata
kerja pembuatan (tambah, buat, bikin, create) yang bersamaan dengan
kecocokan tool analisis-saja. Solusinya adalah "creation-verb override":
kalau kombinasi ini muncul, keputusan diserahkan ke CLARIFY, bukan
langsung memilih tool analisis itu. Task 5 kemudian menambahkan pembedaan
`ambiguity_type`: "multi_tool_match" (beberapa tool cocok sekaligus) vs
"single_tool_conflict". Jadi setahu saya, CLARIFY awalnya dipicu oleh
ambiguitas linguistik/keyword — bukan oleh tingkat dampak operasi.

**6. Pernahkah dipertimbangkan mengaitkannya dengan tingkat dampak operasi
(menulis/menghapus file)?**

Ini justru yang saya ingat SEBALIKNYA — mengaitkan CLARIFY dengan
safety/needs_approval metadata (menulis vs read-only) adalah ide yang
muncul BELAKANGAN di percakapan ini, diusulkan oleh sesi QA/Gemini saat
membahas desain ulang companion (percakapan "balik-arah protokol" yang
saya ikuti sendiri). Itu bukan pertanyaan yang muncul lebih dulu dari
rancangan asli setahu saya — itu ide baru yang justru saya dukung sebagai
arah yang lebih baik dari desain lama.

## grilling & task_lock

**7. Masalah nyata apa yang memunculkan kebutuhan keduanya? Ada kejadian
tertentu yang melatarbelakanginya?**

Tidak ingat. Saya tidak punya memori langsung soal insiden atau diskusi yang
memunculkan kebutuhan `grilling` atau `task_lock` secara spesifik. Ini
kemungkinan besar dari Session 1-3 yang tidak saya lihat.

**8. Bagaimana keduanya dimaksudkan bekerja bersama CLARIFY?**

Tidak ingat.

## memory.json

**9. Field `context` dan `history` dirancang untuk apa? Ada rencana
implementasi yang belum sempat dikerjakan?**

Tidak ingat rancangan aslinya. Yang saya tahu HANYA dari laporan QA
(`reminder.md`) yang membaca kode ini SEKARANG, bukan dari ingatan saya
sendiri: field ini ada di kode tapi menurut temuan QA tidak pernah benar-
benar ditulis meski diklaim sebagai fitur belajar. Saya tidak punya
ingatan langsung soal rencana implementasi yang dimaksud di baliknya.

**10. Apa maksud `user_level` dan bagaimana angkanya ditentukan?**

Tidak ingat.

## Cakupan

**11. APPROVAL_REQUIRED memuat context_mapper dan import_fixer yang tidak
ada di TOOL_REGISTRY. Apakah keduanya pernah ada di registry lalu
dikeluarkan?**

Tidak ingat ada momen spesifik keduanya dikeluarkan dari registry. Saya
tidak bisa mengonfirmasi atau membantah ini dari ingatan.

**12. Adakah tool yang sengaja tidak dimasukkan routing? Atas dasar apa?**

Tidak ingat ada keputusan eksplisit soal ini.

## Penutup

**13. Kalau diringkas satu kalimat — companion itu apa, dan yang
terpenting, companion itu bukan apa?**

Ini saya jawab dari yang saya benar-benar ingat sebagai constraint desain
yang berulang kali ditegaskan sepanjang kerja yang saya lakukan langsung:

Companion adalah **pencocok kata kunci ke tool yang tepat, yang
mengembalikan data terstruktur untuk agent putuskan sendiri** —

dan yang terpenting, companion **bukan** entitas yang memahami maksud user
atau mengambil keputusan sendiri. Begitu companion diberi kemampuan
"memahami esensi" (LLM di dalamnya), ia berhenti jadi rantai yang bisa
diprediksi dan menjadi agent kedua yang perlu diawasi sendiri — itu
argumen yang saya pegang saat membahas ulang desain companion beberapa
minggu lalu, dan menurut saya itu tetap berlaku sebagai batasan intinya.

---

**Ringkasan jujur:** dari 13 pertanyaan, saya punya ingatan langsung dan
cukup yakin untuk 4 (3, 5, 6, 13). Sisanya "tidak ingat" — kemungkinan
besar berasal dari Session 1-3 yang tidak ada dalam konteks saya, bukan
sesuatu yang saya lupakan dari yang pernah saya lihat.

---

## Koreksi setelah membaca DESIGN_PHILOSOPHY.md

Baru dibaca setelah menjawab di atas. Dua koreksi:

**Q1-2 (EXECUTE):** "tidak ingat" saya tadi ternyata cocok dengan fakta —
tapi ini dari dokumen, bukan ingatan saya. PM menyatakan `EXECUTE` memang
bukan hasil keputusan desain, muncul sendiri tanpa ada yang memutuskan
menambahkannya. Bukan risiko yang perlu dibahas ulang — itu penyimpangan
yang perlu dikembalikan.

**Q5 (CLARIFY) — ini salah, perlu dikoreksi.** Saya menjawab dari yang
saya lihat di KODE (creation-verb override, Task 1). Tapi itu bukan
maksud aslinya. Menurut PM langsung: CLARIFY dimaksudkan sebagai
**peringatan untuk kasus berdampak signifikan**, bukan penanda companion
bingung menghadapi ambiguitas kata. Yang saya kerjakan di Task 1
kemungkinan adalah implementasi yang sudah bergeser dari niat aslinya —
persis pola yang dijelaskan di README: kode menunjukkan apa yang ada,
bukan apa yang dimaksud.

**Q6 — perlu direvisi juga.** Saya bilang ini "ide baru" dari diskusi
belakangan. Itu benar untuk MEKANISMENYA (memakai metadata
safety/needs_approval). Tapi niatnya — CLARIFY terkait dampak, bukan
kebingungan kata — ternyata memang niat asli PM sejak awal, cuma belum
pernah terpasang di kode dengan benar. Jadi diskusi belakangan itu bukan
ide baru; itu usaha mengembalikan companion ke rancangan yang sudah ada
tapi belum pernah terealisasi.
