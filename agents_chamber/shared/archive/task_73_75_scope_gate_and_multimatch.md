# Task 73-75 — Gate Scope Menyeluruh & Perbaikan Multi-Match Companion

*Diarsipkan oleh `pos/2. QA` (Opus 4.8 / Claude Code), 06 Agustus 2026, sesuai SOP `shared/archive/README.md`.*
*Status: ketiganya DONE. Commit: `03aef8b`, `450e0b4`.*

---

## Task 73 — Hapus salinan bayangan `is_file_in_scope` (REJECT → PASS)

**Temuan awal:** `smart_replace` menyimpan implementasi kedua `is_file_in_scope` di dalam `except ImportError`, melanggar Ledger #18.

**Putaran 1 — REJECT.** Fallback dihapus, tapi tool jadi mati total:
```
$ python replace_text.py . "xyz123" "abc456"     # ada kecocokan
ModuleNotFoundError: No module named 'scope_guardian'
exit=1
```
File yang disasar berada **di dalam** scope — tool mati sebelum sempat memeriksa.

**Akar masalah yang baru ketahuan:** import shared itu **tidak pernah bekerja sejak awal**. Saat dipanggil sesuai dokumentasi, `sys.path[0]` adalah folder `smart_replace`, bukan induknya, dan tidak ada penambahan `sys.path`. Jadi yang selama ini benar-benar dieksekusi adalah blok fallback — bukan modul bersama.

Artinya Ledger #18 terpenuhi di atas kertas dan dilanggar dalam eksekusi, tanpa ada yang menyadarinya. Itu juga menjelaskan kenapa kedua implementasi masih identik saat diuji: bukan karena disiplin sinkronisasi, tapi karena hanya satu yang hidup.

**Putaran 2 — PASS.** Resolusi path ditambahkan sebelum import:
```python
_SKILLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # -> .agents/skills
if _SKILLS not in sys.path:
    sys.path.insert(0, _SKILLS)
from scope_guardian.scripts.scope_check import is_file_in_scope
```
Bukti gerbang benar-benar bekerja:
```
dalam scope (.py, 4 kecocokan)  -> berjalan normal, exit 0, tanpa traceback
luar scope (.md)                -> [BLOCKED] File is OUT OF SCOPE, exit 1
```

---

## Task 74 — Gate scope di 3 tool penulis file (REJECT → PASS)

**Putaran 1 — REJECT.** Gate terpasang, tapi `context_mapper` dan `auto_scaffolder` memeriksa **direktori**, bukan file yang akan ditulis:
```
Target: ...\.agents/knowledge                <- direktori
Target: D:\AAAAAAAAA\open_source_agents      <- direktori
```
Dibuktikan bukan sekadar scope sempit — dengan scope yang **sengaja mengizinkan** `*.md` pun tetap diblokir, karena direktori tidak akan pernah cocok pola berbasis ekstensi. Kedua tool jadi tidak bisa dipakai dengan konfigurasi apa pun.

**Putaran 2 — PASS.** Pemeriksaan diarahkan ke file:
```
context_mapper  scope izinkan *.md  -> [OK] Knowledge Catalog dibuat        exit=0
                scope tolak *.md    -> [BLOCKED] Target: ...PROJECT_STRUCTURE.md
auto_scaffolder scope izinkan *.jsx -> TestComp.jsx dibuat                  exit=0
                scope tolak *.jsx   -> [BLOCKED] Target: ...TestComp2.jsx
```

**Hasil akhir — empat tool penulis file kini semuanya bergate:**

| Tool | Sebelum | Sesudah |
|---|---|---|
| `smart_replace` | import gagal diam-diam, fallback lokal yang jalan | satu implementasi, benar-benar terpakai |
| `import_fixer` | menimpa file sumber tanpa gate | diblokir bila di luar scope |
| `context_mapper` | menulis tanpa gate | diblokir bila di luar scope |
| `auto_scaffolder` | menulis tanpa gate | diblokir bila di luar scope |

*Catatan:* lima tool lain (`clean_sweeper`, `companion`, `project_guardian`, `selective_reader`, `smart_search`) juga menulis file, tapi hanya cache/state internal — tidak menyentuh file pengguna. `clean_sweeper` terverifikasi **tidak menghapus apa pun** (tidak ada `os.remove`/`rmtree`/`unlink`).

---

## Task 75 — Multi-match: `CLARIFY` kosong → `KONFIRMASI` berkandidat (PASS)

**Masalah:** companion sudah menghitung dan mengurutkan kandidat terkuat, lalu memilih diam. Warningnya menyala terbalik — `"analisa struktur project"` (read-only) kena warning, `"ganti semua axios jadi fetch"` (replace massal) lolos.

**Perbaikan & hasil:**
```
SEBELUM: CLARIFY 10, KONFIRMASI 10   (dari 20 kalimat uji)
SESUDAH: KONFIRMASI 16, CLARIFY 4

Action: KONFIRMASI
  Tool (suggested): deep_analyzer (high)
  Alternatives: smart_tree (medium)
```
Pemicu `CLARIFY` lain tidak ikut melemah — `creation-verb` dan `tool tidak tersedia` tetap `CLARIFY`.

**Ledger #1 juga mendapat Carve-out #2** (Task 75): modul internal murni — stateless, tanpa efek samping, tidak menyentuh file — boleh dibagikan antar-tool. Alasannya: kegagalan akibat *coupling* bersifat keras dan langsung terlihat, sementara *drift* akibat penggandaan bersifat diam. Contoh: `tree_gen`.

---

## BACKLOG MINOR — belum dikerjakan, jangan sampai hilang

**B1. Pesan `grilling` bertentangan dengan `Action`.**
```
Action: KONFIRMASI
Grilling Check:
  needs_grilling: True
  reason: Confidence MEDIUM - perlu clarify      <- masih menyebut "clarify"
```
`core_grilling.py` belum ikut disesuaikan setelah Task 75. Tidak berbahaya (agen membaca baris `Action`), tapi dua baris ini saling bertentangan. Perbaikan: ganti kata `clarify` menjadi `konfirmasi` pada jalur `MEDIUM`.

**B2. `issubset` pada himpunan kosong memicu override yang keliru.**
Pada `"buat komponen baru namanya ProductCard"`, `matched_tools` kosong namun `clarification_note` tetap berbunyi *"Creation verb detected but only analysis tools matched"*. Sebabnya `matched_tool_names.issubset(analysis_tools)` bernilai `True` untuk himpunan kosong. Hasil akhirnya kebetulan benar (`CLARIFY`), hanya alasannya salah. Perbaikan: tambahkan syarat `matched_tool_names` tidak kosong sebelum override.

---

## Pelajaran proses dari rangkaian ini

Lima REJECT sepanjang hari (T65 C2, T67 P2, T71, T73, T74) berpola sama: **yang diuji adalah "perintahnya jalan tanpa error", bukan "efeknya benar-benar terjadi".** Sorting yang tak pernah dieksekusi, flag yang tak menimpa apa pun, gate yang memblokir segalanya — semuanya lolos pengujian pihak yang mengerjakan.

Dua pola khusus untuk gerbang keamanan:
1. **Versi pertama selalu menutup terlalu rapat** — tool mati, atau semua target diblokir. Arah kegagalannya benar, tapi berarti setiap perubahan gate **wajib diuji dua sisi**: yang sah harus lolos, yang tidak sah harus ditolak. Menguji satu sisi saja selalu terlihat berhasil.
2. **Pengujian dengan nihil kecocokan menipu.** `check_scope` hanya terpanggil bila ada file yang benar-benar akan ditulis; uji tanpa kecocokan akan lulus tanpa pernah menyentuh gerbangnya.
