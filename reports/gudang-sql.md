# Rancangan Gudang SQL & Alasan Pemilihan Basis Data (Kartu #11)

Dokumen ini merupakan draf bagian teknis untuk laporan tim (`reports/tim.md`) terkait perancangan skema relasional (`src/gold/silver.sql`), pemuatan otomatis (`src/gold/muat_sql.py`), dan pemilihan mesin basis data untuk lapisan Gold.

## 1. Struktur Skema Relasional (`src/gold/silver.sql`)

- **`seri` (4 baris):** Tabel referensi katalog indikator dengan `PRIMARY KEY (seri_kode)` yang menyimpan nama seri baku, satuan, kode SDG, cakupan, sumber, kode sumber, batas nilai (`batas_bawah`, `batas_atas`), `rujukan_tahun` (numerik), dan catatan metadata.
- **`silver` (3.869 baris):** Tabel fakta observasi dengan `FOREIGN KEY (seri_kode) REFERENCES seri(seri_kode)`, serta `PRIMARY KEY` komposit 6 kolom `(sumber, seri_kode, wilayah_kode, periode, rincian, _berkas_raw)` untuk menjaga *lineage* hingga ke berkas sumber. Tabel juga memiliki `CHECK` constraint untuk `jenis_periode`, panjang `_sha256_raw` (64 karakter SHA-256), rentang nilai (`batas_bawah <= nilai <= batas_atas` ketika batas tersedia), dan validitas `wilayah_kode` (`9999` untuk nasional atau `1100..9799` untuk provinsi).

Pemuatan pertama berhasil dijalankan melalui `src/gold/muat_sql.py`. Hasil pemeriksaan database menunjukkan 4 baris pada tabel `seri`, 3.869 baris pada tabel `silver`, seluruh constraint berhasil diterapkan, dan tidak ditemukan baris Silver yang tidak memiliki pasangan referensi pada tabel `seri` (*orphan records* = 0).

## 2. Alasan Pemilihan Basis Data: DuckDB

1. **Tanpa Server (*Embedded* / *Zero-Config*):** DuckDB berjalan langsung di dalam proses Python (`import duckdb`) dan menyimpan database dalam satu berkas lokal (`data/gold/gudang.duckdb`). Tidak diperlukan layanan *daemon* terpisah seperti PostgreSQL. Hal ini memudahkan proses pengembangan dan reproduksibilitas pipeline di perangkat anggota tim.
2. **Cocok untuk Analisis Data dan Integrasi Parquet/Pandas:** DuckDB mendukung kueri analitik dan dapat digunakan bersama Pandas serta Parquet. Fitur ini sesuai dengan kebutuhan proyek yang mengolah data observasi dan melakukan agregasi lintas wilayah, seri, serta periode.
3. **Penegakan Integritas Skema:** DuckDB mendukung tipe data kolom yang jelas seperti `INTEGER`, `DOUBLE`, dan `VARCHAR`, serta constraint seperti `PRIMARY KEY`, `FOREIGN KEY`, `NOT NULL`, dan `CHECK`. Constraint tersebut membantu menjaga konsistensi data ketika proses pemuatan dilakukan.

## 3. Perbandingan Singkat: DuckDB Relasional vs Menyimpan Respons JSON Mentah sebagai Dokumen

| Aspek | Basis Data Relasional (DuckDB) | Penyimpanan Dokumen JSON Mentah |
|---|---|---|
| **Struktur & Skema** | Terstruktur (*schema-on-write*); tipe kolom, `PRIMARY KEY` komposit, `FOREIGN KEY`, dan `CHECK` constraint diterapkan pada tabel. | Semi-terstruktur (*schema-on-read*); struktur bersarang dapat berbeda antara BPS (`datacontent`, `vervar`, `turvar`) dan WDI (`metadata`, `records`). |
| **Efisiensi Kueri & Agregasi** | Mendukung kueri SQL untuk filter wilayah, periode, agregasi, dan penggabungan antarseri. | Analisis biasanya memerlukan pembacaan, parsing, dan perataan (*flatten*) struktur JSON terlebih dahulu. |
| **Jaminan Kualitas & Duplikasi** | Constraint membantu mencegah duplikasi berdasarkan primary key serta memvalidasi relasi dan aturan nilai yang ditentukan pada skema. | Tidak memiliki penegakan constraint relasional secara otomatis; validasi dan pemeriksaan duplikasi perlu dilakukan melalui kode tambahan. |
| **Peran dalam Pipeline** | **Lapisan Gold / Analitik (`data/gold/gudang.duckdb`):** Digunakan untuk menyimpan tabel terstruktur yang siap dianalisis dan dikueri. | **Lapisan Raw / Arsip (`data/raw/`):** Tetap dipertahankan sebagai dokumen sumber dengan verifikasi `SHA-256` untuk menjaga bukti asal-usul (*lineage*) data asli. |

