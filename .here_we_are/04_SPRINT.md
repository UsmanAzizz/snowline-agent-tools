# Rancangan sprint penelitian

Cara kerjanya, bukan hasilnya. Hasil ada di `01_TEMUAN.md`.

## Bentuk

PM menugaskan, dua agen bekerja paralel pada bidang berbeda, saling memeriksa
di akhir. PM mengestafetkan hasil antar sesi — agen tidak berbicara langsung.

Tiap sprint punya satu pertanyaan, satu ambang yang ditulis sebelum mengukur,
dan syarat berhenti. Kalau tidak bisa menyebut apa yang akan mematahkan
hipotesisnya, sprint tidak dimulai.

## Pembagian kerja, dan dasarnya

| pihak | bidang |
|---|---|
| Gemini (Antigravity) | pengukuran pada data di disk — berkas, git, log, jejak sesi |
| Claude Code | apa pun yang butuh verifikasi ke luar — literatur, dokumentasi vendor, kemampuan harness |

Pembagian ini bukan soal kemampuan, melainkan hasil pengamatan 19 Agustus: dua
dari dua kutipan akademik Gemini ternyata makalah yang tidak berhubungan,
sementara seluruh pengukuran lokalnya cocok dengan temuan independen. Jadi
tiap pihak ditempatkan di mana buktinya bisa ia pegang.

Konsekuensinya: **agen yang ditugasi pengukuran lokal dilarang mengambil
sumber dari web.** Klaim yang butuh sumber luar dicatat sebagai pertanyaan
terbuka, diserahkan ke pihak lain.

## Langkah silang di akhir — jangan dilewati

Masing-masing menguji dua klaim pihak lain, bukan meringkasnya. Cara ini yang
menangkap kutipan palsu dan klaim pemakaian tool yang membaca penyebutan
sebagai eksekusi.

Kalau dua pihak berselisih angka, jangan diratakan. Selisih itu ditulis sebagai
tugas tersendiri (lihat T6), dan kedua angka dibekukan sampai sebabnya
ketemu.

## Anggaran token

Ditulis di muka, dilaporkan di akhir, apa adanya.

| sprint | patokan | terpakai |
|---|---|---|
| Penelitian awal (4 subagent) | tidak dipatok | 453.000 |
| Sprint token 19-08, sisi Claude Code | <=200.000 | 222.000 — **lewat 11%** |
| Sprint token 19-08, sisi Gemini | tidak dipatok | ~2.900 |

Cara menghemat yang dipakai, dan yang bukan:
- Dua subagent, bukan empat. Opus untuk yang butuh timbangan, Sonnet untuk
  penelusuran.
- Brief menuntut tabel dan angka. Laporan naratif separuhnya tidak terpakai.
- Lingkup sempit sejak awal — sebagian besar pemborosan sprint pertama adalah
  peneliti menemukan ulang hal yang sudah diketahui.
- **Bukan** dengan memotong kedalaman atau melewati uji.

Kalau tembus anggaran sebelum pertanyaannya terjawab: lapor, jangan lanjut
diam-diam.

## Retrospektif sprint 19 Agustus

Dua kesalahan rancangan, keduanya baru ketahuan setelah selesai.

**1. Ambangnya mengukur besaran yang salah.** Ditetapkan 15% penghematan
karakter. Tetapi pertanyaan sebenarnya adalah biaya tertagih, dan
`arXiv:2607.12161` mengukur pengurangan token bisa menaikkan biaya karena cache
prompt. Ambang yang ditulis di muka tetap lebih baik daripada tidak ada — ia
membuat kesalahannya kelihatan. Tapi menetapkan ambang tidak menjamin
ambangnya benar.

Pelajaran: sebelum menetapkan ambang, tanyakan besaran apa yang benar-benar
ingin diubah, bukan besaran apa yang paling gampang diukur.

**2. Metode disamakan, kriteria penilaian tidak.** Kedua pihak memakai
parameter ablasi yang identik, lalu berselisih tiga kali lipat karena kriteria
uji kecukupan tidak pernah dituliskan. Satu pihak memakai regex kata tunggal,
satu pihak menuntut baris yang benar-benar dipakai.

Pelajaran: kalau sebuah langkah melibatkan penilaian, kriterianya harus ditulis
sedetail parameternya. Parameter yang sama dengan kriteria yang berbeda bukan
metode yang sama.

## Untuk sprint berikutnya

- Ambang ditetapkan pada biaya tertagih, bukan karakter.
- Kriteria kecukupan bersama ditulis lebih dulu di `02_METODE.md`, bukan di
  kepala masing-masing.
- Langkah silang tetap dijalankan.
