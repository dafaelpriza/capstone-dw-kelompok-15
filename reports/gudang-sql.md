# Rancangan Gudang SQL & Alasan Pemilihan Basis Data (Kartu #11)

Dokumen ini merupakan draf bagian teknis untuk laporan tim (`reports/tim.md`) terkait perancangan skema relasional (`src/gold/silver.sql`), pemuatan otomatis (`src/gold/muat_sql.py`), dan pemilihan mesin basis data untuk lapisan Gold.

## 1. Struktur Skema Relasional (`src/gold/silver.sql`)
- **`seri` (4 baris):** Tabel referensi katalog indikator dengan `PRIMARY KEY (seri_kode)` yang menyimpan nama seri baku, satuan, kode SDG, cakupan, sumber, kode sumber, batas nilai (`batas_bawah`, `batas_atas`), `rujukan_tahun` (numerik), dan catatan metadata.
- **`silver` (3.897 baris):** Tabel fakta observasi dengan `FOREIGN KEY (seri_kode) REFERENCES seri(seri_kode)`, `PRIMARY KEY` komposit 6 kolom `(sumber, seri_kode, wilayah_kode, periode, rincian, _berkas_raw)` untuk menjaga *lineage* hingga ke berkas sumber, serta `CHECK` constraint untuk `jenis_periode`, panjang `_sha256_raw` (64 karakter SHA-256), rentang nilai (`batas_bawah <= nilai <= batas_atas`), dan validitas `wilayah_kode` (`9999` untuk nasional atau `1100..9799` untuk provinsi).

## 2. Alasan Pemilihan Basis Data: DuckDB
1. **Tanpa Server (*Embedded* / *Zero-Config*):** DuckDB berjalan langsung di dalam proses Python (`import duckdb`) dalam satu berkas lokal (`data/gold/gudang.duckdb`) tanpa memerlukan layanan *daemon* terpisah seperti PostgreSQL, sehingga memudahkan reproduksibilitas `python pipeline.py` di berbagai perangkat anggota tim.
2. **Penyimpanan Kolom (*Columnar OLAP*) & Integrasi Langsung dengan Parquet/Pandas:** DuckDB membaca `DataFrame` Pandas dan berkas Parquet secara langsung (*zero-copy*) serta sangat cepat untuk kueri analitik lintas provinsi dan lintas tahun dibandingkan basis data transaksional berbasis baris (*row-oriented*) seperti SQLite.
3. **Penegakan Integritas Skema (*Strict Typing & Constraints*):** Berbeda dengan SQLite yang bersifat *dynamic typing* secara bawaan, DuckDB menegakkan tipe data ketat (`INTEGER`, `DOUBLE`, `VARCHAR`) serta memeriksa `PRIMARY KEY`, `FOREIGN KEY`, dan `CHECK` constraint secara penuh saat proses `INSERT`.

## 3. Perbandingan Singkat: DuckDB Relasional vs Menyimpan Respons JSON Mentah sebagai Dokumen

| Aspek | Basis Data Relasional (DuckDB) | Penyimpanan Dokumen JSON Mentah |
|---|---|---|
| **Struktur & Skema** | Terstruktur (*schema-on-write*); tipe kolom, `PRIMARY KEY` 6 kolom, `FOREIGN KEY`, dan `CHECK` constraint ditegakkan otomatis saat muat data. | Semi-terstruktur (*schema-on-read*); struktur bersarang (*nested*) berbeda antara BPS (`datacontent`, `vervar`, `turvar`) dan WDI (`[metadata, records]`). |
| **Efisiensi Kueri & Agregasi** | Sangat cepat berkat penyimpanan kolumnar; filter wilayah, periode, atau penggabungan antarseri cukup dengan kueri SQL standar. | Lambat untuk analitik karena harus mem-parsing seluruh berkas teks JSON dan meratakan (*flatten*) struktur bersarang setiap kali dianalisis. |
| **Jaminan Kualitas & Duplikasi** | Mencegah baris duplikat, `wilayah_kode` di luar rentang, atau nilai di luar batas satuan sebelum data masuk ke lapisan analitik. | Tidak ada validasi skema bawaan; nilai kosong, kode wilayah tidak konsisten, atau duplikasi antarunduhan rawan lolos tanpa terdeteksi. |
| **Peran dalam Pipeline** | **Lapisan Gold / Analitik (`data/gold/gudang.duckdb`):** Siap pakai untuk kueri lintas seri, validasi akhir, dan pelaporan. | **Lapisan Raw / Arsip (`data/raw/`):** Tetap dipertahankan secara *read-only* dengan verifikasi `SHA-256` sebagai bukti asal-usul (*lineage*) data asli. |
