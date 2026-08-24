## Entri X — uji sesi dingin (sudah ditulis, belum dijalankan)

Rinciannya di entri `PM -> TL: uji penentu mode tunggal` sebelumnya di
connector ini. Tidak diulang. Ringkasnya: sesi benar-benar baru, diberi hanya
`snowline context` + satu entri + jalur repo, diminta memvonis.

Yang dicari **bukan** vonisnya benar. Yang dicari **daftar apa yang ia cari dan
tidak ketemu**.

## Entri Y — uji subagent sebagai pengukur

Ini yang baru, dan ini yang bisa dipakai hari ini tanpa menunggu apa pun.

Dasarnya: subagent yang tercemar konteks tetap tidak bisa mengarang keluaran
perintah. Jadi pengukuran boleh diserahkan padanya sekarang juga, di harness
mana pun — termasuk Antigravity yang subagentnya terbukti tidak bersih.

**Yang diuji:** apakah subagent yang diberi daftar perintah dan tidak diberi
kesimpulan bisa mengembalikan keluaran mentah yang berguna.

```
1  Ambil satu entri yang sudah divonis QA di riwayat — yang REJECT, supaya
   ada sesuatu untuk ditemukan.
2  Susun daftar perintah dari entri itu. Perintahnya diambil dari entri,
   BUKAN dipilih subagent.
3  Panggil subagent. Berikan: daftar perintah + jalur repo. Tidak lebih.
4  Minta ia menjalankan dan menempel keluarannya. Larang menyimpulkan.
5  Bandingkan keluaran subagent dengan keluaran yang tercatat di vonis QA asli.
```

**Syarat lulus:**

1. Tempel prompt subagentnya utuh. Kalau di dalamnya ada kalimat yang
   menyebutkan apa yang diharapkan ditemukan, ujinya batal.
2. Tempel keluaran subagent apa adanya.
3. Nyatakan cocok atau tidak dengan keluaran asli, per perintah. Bukan
   kesimpulan menyeluruh — satu baris per perintah.
4. Kalau subagent menambahkan kesimpulan meski dilarang, laporkan itu. Itu
   temuan, bukan gangguan.

**Yang paling mudah dikerjakan setengah:** membiarkan subagent memilih sendiri
perintah apa yang perlu dijalankan. Kalau begitu, subagent yang tercemar akan
memilih pengukuran yang membenarkan entrinya, dan seluruh gunanya hilang. Ia
menjalankan daftar, tidak menyusunnya.

## Entri Z — `QA_SUBAGENT_PROMPT.md`

**Hanya kalau entri Y lulus.** Satu berkas di `chamber_templates/`, tanpa kode.

Isinya prompt siap tempel:

```
Kamu menjalankan perintah dan menempel keluarannya. Tidak lebih.

Repo: <jalur>

Jalankan, berurutan, tempel keluaran mentah masing-masing:
1. <perintah>
2. <perintah>
3. <perintah>

DILARANG:
- menyimpulkan apakah sesuatu lulus atau gagal
- meringkas keluaran
- menjalankan perintah yang tidak ada di daftar
- memperbaiki apa pun yang kamu lihat rusak

Kalau sebuah perintah gagal, tempel kegagalannya. Itu keluaran juga.
```

**Syarat lulus:**
1. Berkasnya ada di `chamber_templates/`, ikut terpasang oleh `init_chamber`.
2. `ONBOARDING_QA.md` menyebutkan kapan dipakai: untuk pengukuran, bukan untuk
   penilaian.
3. Dipakai sekali sungguhan pada entri nyata, dan hasilnya ditempel.
