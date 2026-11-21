# Laporan tim â€” <Nama tim>, kasus <NN> <judul kasus>

Satu dokumen bersama, enam bagian. Angka harus dapat ditarik ulang dari `data/silver`, `data/gold`,
dan `log-keputusan.csv` yang sudah di-*commit*.

## Ringkasan
Kasus, seri yang ditangani, dan satu kalimat temuan utama tentang kualitas datanya.

## Data dan lineage
Sumber dan format mentah, jumlah berkas, cara `_berkas_raw`/`_sha256_raw` dibentuk, dan hasil tarik
ulang API (bila dilakukan): apa yang berubah sejak snapshot 17â€“20 Oktober 2026.

## Masalah data dan penanganannya
Tabel masalah yang ditemukan (missing, outlier, patahan seri, duplikat, format, wilayah) dengan
jumlah baris terdampak, keputusan, dan alternatif yang ditolak. Rujuk id di `log-keputusan.csv`.

## Integrasi dan rekonsiliasi
Seri utama vs pembanding nasional: selisih, penjelasannya (definisi, metode, vintage, granularitas),
dan hasil analisis revisi dari arsip WDI.

## Validasi dan reproduksibilitas
Skema validasi (aturan, hasil lolos/gagal), waktu `python pipeline.py` dari nol, perbandingan pandas
vs DuckDB/Dask, dan keterbatasan yang tersisa.

### Draf Pemilihan Basis Data SQL (DuckDB) vs Penyimpanan JSON Mentah (Kartu #11)
- **Alasan memilih DuckDB:** (1) Bersifat *embedded* (*zero-config*, berjalan langsung di Python tanpa server terpisah seperti PostgreSQL sehingga reproduksibel lewat python pipeline.py); (2) Mesin analitik kolumnar (*OLAP*) yang terintegrasi langsung dengan Pandas dan Parquet; serta (3) Menegakkan tipe data ketat, PRIMARY KEY 6 kolom (sumber, seri_kode, wilayah_kode, periode, rincian, _berkas_raw), FOREIGN KEY ke tabel seri, dan CHECK constraint (wilayah_kode, rentang nilai, panjang _sha256_raw = 64) sesuai src/gold/silver.sql (selaras dengan alternatif gold.sqlite tanpa mengubah jumlah 3.897 baris).
- **Perbandingan dengan menyimpan respons JSON mentah sebagai dokumen:** Penyimpanan dokumen JSON mentah cocok sebagai arsip *read-only* di data/raw/ untuk menjaga *lineage* asli, tetapi lambat untuk kueri analitik karena struktur bersarang BPS dan WDI harus di-*parse* berulang kali serta tidak memiliki penegakan tipe kolom, integritas referensial (FOREIGN KEY), maupun pencegahan duplikasi otomatis seperti pada DuckDB. Rincian lengkap tersedia pada eports/gudang-sql.md.

## Pembagian kerja
| Anggota | NIM | Komponen | Tugas sampingan | Bagian laporan yang ditulis |
|---|---|---|---|---|

