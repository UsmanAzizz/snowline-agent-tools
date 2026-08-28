# Archive

## Companion

Companion adalah modul analisis niat (*intent analyzer*), perutean alat, dan pemeriksa ambiguitas perintah yang sebelumnya dipaketkan di dalam Snowline Agent Tools (`.agents/skills/companion/` dan `companion_cli.py`).

### Alasan Pengarsipan
Berdasarkan hasil pengukuran dan pengujian di tiga proyek nyata:
- Ekstraksi entitas dan deteksi kata kuncinya terbukti bekerja dengan baik pada level unit test.
- Namun, penempatannya sebagai gerbang niat dinamis (*dynamic intent gate*) pada *hook* pra-eksekusi serta aturan pemanggilan wajib (*call-first rule*) menambah latensi dan overhead tanpa memberikan peningkatan signifikan terhadap akurasi pemilihan alat oleh agen di lapangan.

### Hal yang Perlu Diperhatikan Jika Dihidupkan Kembali
- Integrasi ke alur kerja agen sebaiknya bersifat analitis/penasihat murni (*advisor/read-only*), bukan sebagai gerbang pemblokir eksekusi (*fail-closed blocking gate*).
- Efektivitas perutean perintah perlu diuji lewat eksperimen komparatif terukur terhadap pemanggilan alat langsung.
