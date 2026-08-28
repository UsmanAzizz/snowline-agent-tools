# Panduan Pengujian Snowline

Kamu diminta memakai paket alat agen ini untuk mengerjakan pekerjaan sungguhan
di proyek tempat kamu berada sekarang, lalu melaporkan apa yang terjadi.

Ini bukan tinjauan dan bukan penilaian. Jangan menulis apakah snowline bagus,
berguna, atau menjanjikan. Tulis apa yang kamu jalankan dan apa yang keluar.

## Aturan

1. **Dilarang memperbaiki.** Jangan menambal kode, mengubah konfigurasi, atau
   mengakali perintah supaya jalan. Kalau macet, catat macetnya lalu lanjut ke
   tugas berikutnya.
2. **Dilarang meringkas keluaran.** Tempel mentah. Tidak boleh ada
   "*(dan 46 berkas lainnya)*" atau "*keluarannya panjang*". Kalau memang
   panjang, tempel 15 baris pertama dan 5 baris terakhir, dan katakan berapa
   baris yang dipotong.
3. **Tidak ada klaim tanpa keluaran.** Kalimat "berhasil", "jalan", atau
   "sesuai harapan" hanya boleh muncul tepat di bawah keluaran yang
   menunjukkannya.
4. **Dilarang membaca sumber snowline.** Jangan membuka repositori
   `snowline-agent-tools`, jangan membaca `site-packages/snowline/`. Kamu
   menguji dari luar, seperti pengguna baru. Kalau jawabannya tidak ada di
   `--help`, di `.agents/`, atau di keluaran perintah, itu temuan — bukan
   alasan membuka kode.
5. **Catat tebakan.** Setiap kali kamu harus menerka cara memakai sesuatu
   karena tidak ada yang memberitahumu, tulis terkaanmu dan dari mana kamu
   menerkanya.
6. **Kerjakan berurutan.** M1 sampai M10, jangan dilompati. Kalau satu tugas
   tidak bisa dikerjakan, tulis kenapa di tempatnya, lalu lanjut.
7. **Pakai alat dari proyek ini saja.** Semua skrip yang kamu jalankan harus
   berasal dari `.agents/` proyek tempat kamu sekarang. Jangan memanggil
   skrip dari proyek lain di mesin ini, walaupun jalurnya kamu tahu.

Tuangkan semuanya ke `TEST_REPORT.md` yang ada di folder yang sama dengan
berkas ini. Bagian-bagiannya sudah bernomor sama dengan tugasnya.

---

## M0 — Lingkungan

Sebelum apa pun: catat sistem operasi, versi Python, dan **versi persis
snowline yang akan kamu uji**.

Tempel perintah yang membuktikan versinya. Kalau kamu tidak bisa memastikannya,
tulis itu apa adanya dan sebutkan apa saja yang sudah kamu coba.

## M1 — Masuk tanpa dituntun

Kamu belum tahu apa-apa tentang paket ini. Cari tahu sendiri apa yang bisa
dilakukannya.

Catat **ongkos masuk**: berapa detik dari perintah pertamamu sampai kamu tahu
alat mana yang akan kamu pakai untuk pekerjaan sungguhan. Dan catat berapa
perintah yang kamu jalankan sebelum sampai di sana.

## M2 — Memilih alat

Cari sesuatu yang sungguhan di proyek ini — nama fungsi, rute, atau
konfigurasi yang benar-benar ingin kamu ketahui letaknya. Bukan contoh dari
dokumentasi.

Tempel perintah dan keluaran mentahnya.

Lalu jawab tiga hal, jujur:

- Bagaimana kamu memutuskan memakai alat itu? Sebutkan apa yang kamu baca atau
  jalankan sebelum memutuskan.
- Sebelum memutuskan, kamu sudah tahu mau memakai apa, atau kamu mencari tahu
  dulu?
- Adakah sesuatu di paket ini yang membantumu memilih? Kalau kamu mencarinya
  dan tidak menemukan, tulis itu.

## M3 — Satu suntingan sungguhan

Pilih satu perubahan kecil yang benar-benar berguna di proyek ini. Kerjakan
lewat alat tulis snowline, bukan lewat editor bawaanmu.

Tempel: perintah pratinjau, keluarannya, perintah terap, keluarannya, dan
bukti berkasnya berubah.

Lalu: berapa langkah yang dibutuhkan dibanding kalau kamu menyuntingnya
langsung?

## M4 — Batas tulis

Cari tahu apakah ada cara membatasi berkas mana yang boleh ditulis. Kalau ada,
pasang batas itu.

Uji **dua arah**, dan tempel keduanya:

```
berkas di dalam batas   -> apa yang terjadi
berkas di luar batas    -> apa yang terjadi
```

Satu arah saja tidak cukup. Penjaga yang menolak semuanya dan penjaga yang
meloloskan semuanya sama-sama tampak bekerja kalau cuma diuji satu arah.

## M5 — Chamber: pasang dan baca

Pasang protokol chamber di proyek ini. Tempel keluarannya.

Lalu baca aturannya dan jawab tanpa membuka kode:

- Ada berapa peran, dan siapa memutuskan apa?
- Apa yang membuat sebuah entri **ditolak sebelum dibaca**?
- Sinyal satu kata itu apa, dan siapa yang mengirimnya?

Kalau salah satu tidak bisa kamu jawab dari dokumen yang ada, tulis "tidak
terjawab dari dokumen" — jangan menerka.

## M6 — Chamber: gerbang entri, dua arah

Tulis entri ke connector lewat perintah yang disediakan snowline — bukan
dengan menyunting berkasnya langsung.

Uji dua arah, tempel keduanya mentah:

```
entri yang mengklaim sesuatu selesai, tanpa perintah dan keluaran
entri yang sama, dengan perintah dan keluaran mentahnya
```

Lalu coba satu hal lagi: tulis entri dengan judul yang formatnya sengaja
salah. Catat apa yang terjadi pada berkas connector — bertambah, berubah,
atau utuh. Sebutkan cara kamu memastikannya.

## M7 — Satu agen, dua sesi

Chamber menuntut TL dan QA bukan sesi yang sama. Kamu cuma satu agen.

Kerjakan bagian TL-nya:

1. Ambil satu tugas kecil yang nyata di proyek ini.
2. Kerjakan.
3. Tulis laporan TL ke connector, lengkap dengan perintah dan keluaran mentah.
4. Serahkan peran ke QA menurut apa pun yang diperintahkan chamber.
5. **Berhenti.** Jangan meninjau pekerjaanmu sendiri.

Yang dilaporkan: pada langkah 4, apa persisnya yang kamu lakukan, dan dari
mana kamu tahu harus melakukannya. Kalau tidak ada perintah atau berkas yang
mengurusnya dan kamu harus mengarang caranya sendiri, tulis itu — termasuk
apa yang kamu karang.

Sesudah berhenti, tulis satu baris untuk manusia yang membaca laporan ini:
apa yang harus dia lakukan supaya sesi QA bisa mulai.

## M8 — Subagen QA

Chamber menyediakan naskah untuk subagen QA. Pakai.

Jalankan satu subagen dengan naskah itu untuk memeriksa pekerjaan M3 atau M7.

Tempel: apa yang kamu berikan ke subagen, dan apa yang dikembalikannya, utuh.

Lalu jawab: apakah subagen itu bisa memeriksa tanpa kamu beritahu jawabannya?
Kalau kamu terpaksa menyelipkan konteks supaya ia berguna, tulis konteks apa
— itu justru temuan yang dicari.

## M9 — Alat yang tidak kamu sentuh

Daftar alat di paket ini lebih panjang dari yang kamu pakai hari ini.

Tulis mana saja yang **tidak** kamu sentuh, dan untuk masing-masing satu
alasan: tidak relevan, tidak ketemu, tidak paham, atau tidak sempat.

Empat alasan itu berbeda dan yang membedakannya penting.

## M10 — Rapikan catatan

Connector di proyek ini sekarang punya beberapa entri.

Rapikan: pindahkan yang sudah selesai ke arsip, dan pastikan tidak ada baris
yang hilang di perjalanan.

Yang dilaporkan: perintah apa yang kamu pakai, dan **dari mana kamu tahu
perintah itu ada**. Kalau kamu tidak menemukan cara yang disediakan lalu
mengarang caranya sendiri, tulis itu — termasuk apa yang kamu karang.

---

## Sesudah semua tugas

Pertanyaan penutup ada di bagian 10 sampai 15 `TEST_REPORT.md`. Jawab
sesudah kamu selesai, bukan sambil jalan.
