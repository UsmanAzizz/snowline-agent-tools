# Aturan Chamber

Berlaku sejak 21 Agustus 2026. Menggantikan bagian saluran dan alur di
`shared/RULES.md`; sisanya (Ledger, keputusan arsitektur) tetap berlaku.

---

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

## 6. Siapa yang menutup

QA memvonis PASS / REJECT / TIDAK BISA DIUJI. TL tidak bisa menutup tugas tanpa
vonis itu.

Tetapi **wewenang terakhir tetap pada PM**, dan PM boleh bertanya kapan saja:

> *Perintah mana yang menunjukkan itu?*

Satu pertanyaan itu menangkap dua kegagalan pada 21 Agustus tanpa PM membaca
satu baris kode pun.

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
