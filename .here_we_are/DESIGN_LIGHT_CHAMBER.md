# Rancangan: chamber yang tidak membengkak

Usulan PM 22 Agustus, dirapikan. Belum diputuskan, belum dibangun.

---

## Masalahnya, dengan angka

```
connector.md         2.374 baris, 91 KB, 33 entri     dalam satu hari
arsip 21-08          3.316 baris                      hasil rotasi pertama
```

Rotasi sudah dilakukan sekali kemarin. Sehari kemudian ambangnya hampir
tersentuh lagi. Rotasi berbasis ukuran cuma menunda, tidak menyelesaikan.

Dan arsipnya satu berkas besar per tanggal. Untuk mencari "apa yang dulu kita
putuskan soal cache", seseorang harus memindai 3.316 baris yang isinya
bercampur.

## Empat aturan yang diusulkan

### 1. Connector adalah meja kerja, bukan buku besar

Isinya **hanya tugas yang sedang berjalan**. Begitu QA menutup sebuah entri,
entri itu keluar dari connector — bukan tetap di sana sebagai riwayat.

Setelah semua entri tutup, connector kosong lagi. Kepala berkasnya tetap.

### 2. Riwayat disusun per topik, bukan per tanggal

```
.agents/chamber/history/
    encoding/
    caching/
    rejection-tests/
    guardian/
    role-lock/
    dependency-map/
```

Tanggal tetap ada **di dalam** berkasnya, bukan sebagai nama foldernya.

Alasannya praktis: pertanyaan yang muncul nanti berbentuk *"apa yang sudah kita
putuskan soal X"*, bukan *"apa yang terjadi tanggal 22"*. Susunan harus
mengikuti bentuk pertanyaannya.

### 3. Satu berkas riwayat maksimal 300 baris

Kalau sebuah topik melewati 300 baris, ia dipecah — biasanya karena topiknya
memang dua hal:

```
history/guardian/01-false-positives.md
history/guardian/02-npm-audit-scope.md
```

Bukan `guardian-part1.md` dan `guardian-part2.md`. Pecahannya berdasarkan isi.

### 4. Hanya di sektor yang volumenya membenarkan

Tidak semua hal butuh struktur folder. Yang butuh cuma yang tumbuh terus:

```
butuh folder     riwayat entri chamber       tumbuh tiap sprint
tidak butuh      STATE.md                    ditimpa, ukurannya tetap
tidak butuh      CHAMBER_RULES.md            tumbuh pelan, dibaca utuh
tidak butuh      catatan riset bernomor      beku, tidak bertambah lagi
```

Menerapkan struktur folder ke berkas yang tidak tumbuh cuma menambah tingkat
tanpa memberi apa-apa.

---

## Yang hilang, dan cara menambalnya

Mengosongkan connector menghilangkan satu hal: **urutan cerita.** Sekarang
seseorang bisa membaca connector dari atas ke bawah dan melihat bagaimana satu
temuan menuntun ke temuan berikutnya. Setelah dipecah per topik, itu hilang.

Tambalannya di `STATE.md`, yang memang sudah memuat daftar entri tutup. Cukup
tambahkan jalurnya:

```
9   encoding    open() tanpa utf-8 menjatuhkan splicer   history/encoding/01-utf8.md
11  cache       batal saat kode alatnya berubah          history/caching/01-tool-hash.md
```

Satu baris per topik. Ceritanya hilang, indeksnya tetap.

## Siapa yang memindahkan

Kalau manual, tidak akan terjadi — sudah terbukti tiga kali malam ini untuk
hal-hal kecil yang dilaporkan selesai tetapi tidak dikerjakan.

Jadi perlu perintah:

```bash
snowline close-entry <topik>
```

Yang: mengambil entri terakhir dari connector, memindahkannya ke
`history/<topik>/`, memberi nomor urut, menambahkan satu baris ke `STATE.md`,
dan menghapusnya dari connector.

Kalau berkas tujuannya sudah melewati 300 baris, perintahnya berhenti dan
menyuruh memecah topiknya lebih dulu. Sama polanya dengan batas 250 baris di
`snowline context`.

## Batas yang harus disadari

Aturan "yang selesai dimusnahkan dari connector" hanya aman kalau
pemindahannya **tidak menghapus**. Entri pindah, bukan hilang.

Malam ini ada satu kejadian yang relevan: rotasi connector oleh TL memindahkan
645 baris, dan QA memeriksa 645 baris itu masuk ke arsip sebelum menerimanya.
Pemeriksaan yang sama harus berlaku untuk `close-entry` — jumlah baris keluar
harus sama dengan jumlah baris masuk.

## Kalau ini dibangun

Urutannya: perintah `close-entry` dulu, baru pemecahan riwayat lama. Memecah
arsip 3.316 baris secara manual sebelum perintahnya ada berarti mengerjakannya
dua kali.
