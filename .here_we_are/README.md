# .here_we_are

Catatan penelitian bersama. Bukan dokumentasi proyek, bukan aturan chamber.
Isinya: apa yang sudah kita ketahui, dengan buktinya, supaya agen mana pun bisa
melanjutkan tanpa mengulang dari nol.

Dibuat 19 Agustus 2026 setelah sprint penelitian PM + Claude Code + Gemini.

## Urutan baca

0. **`SNOWLINE_INI_APA.md` — mulai di sini kalau kamu belum tahu snowline itu
   apa, atau lupa sedang berdiri di mana.** Satu halaman: ini apa, empat hal
   yang benar-benar mengikat, enam arah dan statusnya, dan apa yang tersisa.
   Berkas lain di folder ini menganggap pembacanya sudah tahu konteksnya.
1. `00_STATUS.md` — apa yang sudah selesai, apa yang masih terbuka
2. `01_TEMUAN.md` — temuan beserta angkanya
3. `02_METODE.md` — cara mengukurnya, supaya bisa diulang
4. `03_TUGAS.md` — apa yang dikerjakan siapa
5. `04_SPRINT.md` — cara sprint dijalankan: pembagian kerja, anggaran token,
   langkah silang, dan retrospektif kesalahan rancangan sprint sebelumnya
6. `05_APA_YANG_MASIH_BERDIRI.md` — **mulai dari sini kalau kamu baru masuk
   dan butuh gambaran menyeluruh.** Menyatukan temuan lintas tugas: apa yang
   sudah mati beserta sebabnya, apa yang terukur dan tidak dibantah, dan tiga
   hal yang masih tegak
7. `v2_prototypes/PENILAIAN_QA.md` — mana dari delapan prototipe yang ikut
   runtuh bersama hipotesis yang gugur, dan mana yang tidak

## Aturan kerja di folder ini

Lahir dari kesalahan nyata malam ini, bukan dari teori.

1. **Tiap angka disertai perintah yang menghasilkannya.** Angka tanpa perintah
   dianggap kesan.

2. **Tiap kutipan makalah harus dibuka dulu dan dicocokkan judulnya.** Dua dari
   dua kutipan dalam satu laporan malam ini ternyata makalah fisika yang tidak
   berhubungan. Kesimpulannya kebetulan benar, dasarnya tidak ada.

3. **Penyebutan bukan pemakaian.** Nama tool yang muncul di dokumentasi,
   registri, atau daftar berkas bukan bukti tool itu pernah dijalankan. Bukti
   pemakaian hanya: log eksekusi, artefak keluaran, cache sesi, berkas status.

4. **Ambang ditetapkan sebelum mengukur, dan ditulis.** Kalau tidak bisa
   menyebut apa yang akan mengubah pikiranmu, jangan mulai.

5. **Ukur dulu, simpulkan sesudah.** Bukan sebaliknya. Kalau kamu bisa menyebut
   uji yang akan mematahkan klaimmu, jalankan ujinya sebelum menulis klaimnya —
   jangan menyerahkannya ke manusia.

6. **Yang tidak terverifikasi ditulis "belum terverifikasi".** Jangan ditutup
   dengan dugaan yang terdengar meyakinkan.

7. **Melenceng ke temuan menarik yang tidak ditanyakan adalah kegagalan**,
   sekalipun temuannya benar.

## WAJIB DIBACA SEBELUM MENILAI APA PUN

`agents_chamber/shared/DESIGN_PHILOSOPHY.md` memuat kutipan langsung PM tentang
maksud companion dan chamber. Kode menunjukkan **apa yang ada**; berkas itu
menyatakan **apa yang dimaksudkan**.

Menilai yang pertama tanpa yang kedua sudah menghasilkan kesimpulan yang salah
dua kali — sekali oleh QA sebelumnya (tercatat di berkas itu sendiri, baris 49),
sekali lagi oleh QA sprint ini pada 20-08.

## Cara PM ingin dikerjakan

Ini bukan aturan penelitian, ini cara berinteraksi. Sama mengikatnya.

- **Ringkas dan langsung.** Jangan berbab-bab, jangan bahasa filosofis. Detail
  panjang taruh di berkas, bukan di balasan.
- **Sedikit demi sedikit.** Satu langkah, lapor, tunggu. Jangan mendorong
  panjang, jangan menawarkan dua pilihan waktu supaya PM cepat memutuskan.
- **Jangan buru-buru menawarkan mekanisme baru.** Pola "temukan celah, tambah
  mekanisme, temukan celah lagi" sudah dibongkar dan sengaja dihindari.
- **Jangan menyelipkan temuan yang tidak ditanyakan**, sekalipun menarik dan
  benar. Kalau penting, catat di papan tugas dan sebut satu baris.
- **Commit tiap kali sebuah hasil atau vonis masuk** — papan ini pernah hilang
  sekali karena `git checkout` atas pekerjaan yang belum di-commit.
- **Push sekali di akhir tugas panjang, bukan per langkah.** Commit sering,
  push jarang.
- **Insight negatif tentang PM tidak diminta.** Temuan tentang berkas, angka,
  dan kode: silakan, setajam mungkin. Penilaian tentang orangnya: tidak.

## Di luar lingkup folder ini

Bukan tempat mencari bug, menilai mutu kode, atau merancang fitur.
Ini catatan pengukuran.
