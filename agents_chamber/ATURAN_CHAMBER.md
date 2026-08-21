# Aturan Chamber

Berlaku sejak 21 Agustus 2026. Menggantikan bagian saluran dan alur di
`shared/RULES.md`; sisanya (Ledger, keputusan arsitektur) tetap berlaku.

---

## 0. Kapan chamber dipakai — dan kapan tidak

Chamber punya ongkos: PM jadi jembatan manual, dan tiap iterasi butuh entri
tertulis. Memakainya untuk segalanya akan membuatnya dilanggar diam-diam, dan
protokol yang dilanggar diam-diam tidak melindungi apa pun.

Penyaringnya satu pertanyaan:

> **Kalau perubahan ini salah, apakah langsung kelihatan?**

```
kelihatan seketika     warna, teks, tata letak, salin-tempel  ->  kerjakan biasa
baru ketahuan nanti    skema data, alur penyimpanan, penilaian,
                       keamanan, migrasi, apa pun yang menyentuh
                       data orang lain                        ->  lewat chamber
```

Bukan "berisiko tinggi" — itu tidak bisa diperiksa dan tiap orang menilainya
berbeda. Yang bisa diperiksa: seberapa lama kesalahan sempat hidup sebelum ada
yang menyadarinya.

Tombol salah warna ketahuan dalam sedetik. Jawaban yang tersimpan ke paket yang
salah baru ketahuan setelah ujian selesai — dan saat itu tidak bisa diulang.

Kalau ragu, pakai chamber. Ongkos memakainya untuk hal kecil cuma waktu;
ongkos tidak memakainya untuk hal besar dibayar orang lain.

## 1. Chamber adalah protokol, bukan program

Diputuskan 21-08. `src/snowline/chamber/` kosong dan memang dibiarkan kosong.
Orchestrator sudah dua kali ditulis dan dua kali hilang; yang bertahan justru
protokolnya.

Tidak ada daemon, tidak ada skrip yang memanggil agen. Semua sinyal dijalankan
manusia. Ini juga keputusan Task 38 — memanggil CLI AI eksternal tanpa
persetujuan per-proyek adalah soal privasi, bukan sekadar kerepotan teknis.

## 2. Empat peran, dan siapa boleh memanggil siapa

```
PM        manusia            memvonis terakhir, menjembatani semua sinyal
TL        agen               memutuskan, mendelegasikan, melaporkan
QA        identitas kedua    memeriksa dengan menjalankan, bukan membaca
Pekerja   subagent           sekali pakai, mati setelah tugasnya selesai
```

**TL tidak boleh memanggil QA-nya sendiri.** Yang memilih pemeriksa adalah PM.
Alasannya bukan formalitas: agen yang memilih hakimnya sendiri sedang
memberkati pekerjaannya sendiri.

```
PM  <-> TL       dua arah
PM  <-> QA       dua arah
TL   -> pekerja  subagent sekali pakai, hasilnya ditempel mentah
QA   -> pekerja  subagent sekali pakai, hasilnya ditempel mentah
TL   -X- QA      tidak ada jalur langsung
```

Subagent boleh dipanggil siapa saja, karena ia **tidak pernah memvonis**. Ia
menyediakan bukti; yang menyimpulkan tetap peran di atasnya.

## 3. Satu saluran

`.here_we_are/connector.md`. Lima connector di `pos/*/` pensiun — tidak dihapus,
tidak dipakai.

Riwayat sebelum 21-08 ada di `shared/archive/connector_2026-08-21.md` (112 KB).
Jangan dibaca seluruhnya.

## 4. Syarat entri — ditolak sebelum isinya dibaca

- Menyatakan sesuatu selesai tanpa memuat **perintah dan keluarannya**.
- Keluaran diringkas atau dirapikan, bukan ditempel apa adanya.
- Kesimpulan menyatakan hal yang tidak ditunjukkan keluaran itu sendiri —
  termasuk bila perintahnya benar tetapi tidak menyentuh kode yang diklaim.

Kalau tidak ada keluaran untuk ditempel, vonisnya **`TIDAK BISA DIUJI`**. Itu
sah, dan lebih berguna daripada tebakan.

Ketiganya lahir dari kegagalan nyata malam 20–21 Agustus, bukan dari
kehati-hatian. Contohnya ada di arsip, sengaja tidak dihapus.

## 5. Connector adalah satu-satunya lebar pita

**Apa yang tidak ada di connector, identitas kedua tidak tahu.**

Ini bukan aturan kehormatan. Ditegakkan dengan memberi subagent **hanya entri
itu** — tanpa riwayat induk, tanpa alasan, tanpa niat. Ia dingin karena
konstruksinya, bukan karena berjanji lupa.

Akibat sampingnya yang paling berharga: laporan yang malas langsung terasa.
Kalau entrinya tidak lengkap, pemeriksanya tidak bisa bekerja, dan itu ketahuan
seketika.

## 4b. Kunci usulan — TL tidak bisa membangun sebelum mengusulkan

Butir 4 menuntut entri memuat perintah dan keluaran. Butir ini menuntut sesuatu
yang lebih awal: **usulan sebelum kode ditulis.** Bedanya, yang ini tidak
diminta — ia dikunci.

Mekanismenya sudah ada di snowline dan tinggal dipakai:

```
PM   tulis entri  +  buat .agents/task_state.json      ->  pintu terkunci
TL   boleh membaca, memindai, mengusulkan              ->  tidak bisa menulis
PM   setujui usulannya, hapus berkas itu               ->  pintu terbuka
```

Isi berkasnya:

```json
{"phase": "pseudocode_pending", "task": "<judul entri>"}
```

Selama berkas itu ada, setiap `--apply` ditolak:

```
[BLOCKED] Pseudocode untuk task ini belum disetujui user.
Task: <judul entri>
Minta user approve pseudocode dulu sebelum --apply bisa dijalankan.
```

Ditegakkan di `smart_replace/replace_text.py:22` (`check_task_state`), dan
sudah diuji: dengan berkas itu `--apply` ditolak, tanpa berkas itu `--apply`
berhasil.

**Kenapa dikunci, bukan diminta.** Selama ini TL mengusulkan lebih dulu hanya
ketika entri PM memintanya. Aturan yang bergantung pada seseorang mengingat
untuk memintanya bukan aturan — itu kebiasaan, dan kebiasaan patah saat
tergesa.

**Batasnya, dan ini harus diketahui sejak awal:** gerbang ini hanya menahan
alat tulis snowline. Kalau agen memakai editor bawaan harness-nya, ia lewat
begitu saja. Untuk menutup itu perlu hook di sisi harness, dan itu di luar
jangkauan berkas ini. Jangan memperlakukan kunci ini sebagai jaminan; ia
menahan jalur yang lewat snowline, tidak lebih.

**Kapan dipakai:** untuk entri yang membangun sesuatu. Untuk perbaikan yang
letaknya sudah jelas dan bukti kerusakannya sudah ditempel PM, mengunci hanya
menambah putaran.

## 6. Siapa yang menutup dan Menyimpan Arsip

QA memvonis PASS / REJECT / TIDAK BISA DIUJI. TL tidak bisa menutup tugas tanpa
vonis itu.

Tetapi **wewenang terakhir tetap pada PM**, dan PM boleh bertanya kapan saja:

> *Perintah mana yang menunjukkan itu?*

Satu pertanyaan itu menangkap dua kegagalan pada 21 Agustus tanpa PM membaca
satu baris kode pun.



**Catatan Arsip Resmi**:
Sisa-sisa percakapan/log connector disimpan di `agents_chamber/shared/archive/connector_<tanggal>.md`. Lokasi ini adalah satu-satunya lokasi arsip resmi. Jangan menggunakan lokasi duplikat seperti `.here_we_are/connector_archive.md`.

## 7. Batas yang perlu diketahui sejak awal

Identitas kedua menangkap klaim yang tidak didukung buktinya. Ia **tidak**
menangkap kesalahan yang lahir dari premis keliru yang ikut tertulis di entri.
Kalau premis salah ditulis dengan yakin, pemeriksa dingin akan memeriksanya di
atas premis yang sama.

Untuk itu tetap perlu PM, sesekali, dengan pertanyaan di butir 6.

## 8. Yang pensiun

```
pos/*/connector.md      lima berkas   ditandai, tidak dihapus
shared/task_board.md    beku di Task 87, arsip
src/snowline/chamber/   kosong, dan memang dibiarkan kosong
```
## 9. Uji Penolakan (Rejection Tests)

Uji penolakan harus menunjukkan dua hal — bahwa ia menolak, dan bahwa ia menerima saat syaratnya dipenuhi. Gerbang yang selalu tertutup (atau pengujian yang asersinya menerima ketiadaan seperti gagal menulis karena *crash*) tidak bisa dibedakan dari gerbang yang tidak ada.
