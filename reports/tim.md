# Laporan tim — <Nama tim>, kasus <NN> <judul kasus>

Satu dokumen bersama, enam bagian. Angka harus dapat ditarik ulang dari `data/silver`, `data/gold`,
dan `log-keputusan.csv` yang sudah di-*commit*.

## Ringkasan

Tim Cakrawal merupakan Kelompok 15 pada Capstone Data Wrangling 2026 dengan topik **Kemiskinan di Daerah Tertinggal**. Kasus ini termasuk dalam Klaster D, yaitu Kemiskinan dan Ketimpangan, serta berkaitan dengan Sustainable Development Goal (SDG) 10, yaitu Reduced Inequalities.

Pengolahan data berfokus pada tiga seri utama dari Badan Pusat Statistik (BPS), yaitu `var192`, `var2190`, dan `var2191`, serta seri pembanding internasional dari World Development Indicators (WDI), yaitu `SI.POV.NAHC`.

Pada Sprint 1, tim telah melakukan identifikasi sumber data, pemeriksaan awal kualitas data, dan penetapan keputusan terkait pemetaan kode wilayah, satuan indikator, penanganan nilai kosong, serta pemilihan rincian yang sebanding antara BPS dan WDI. Pemeriksaan lanjutan juga dilakukan terhadap nilai nol, calon outlier, indikasi patahan seri, konsistensi kategori, dan aturan deduplikasi. Seluruh keputusan tersebut dicatat dalam `log-keputusan.csv` dengan kode K-001 sampai K-011.

Hasil pemeriksaan menunjukkan adanya indikasi penurunan serentak pada seri `var192` dari 2007 ke 2008, nilai kemiskinan tinggi di Papua dan Papua Barat, serta nilai nol pada beberapa seri. Namun, belum ditemukan bukti yang cukup untuk menetapkan temuan tersebut sebagai galat input. Oleh karena itu, nilai-nilai tersebut dipertahankan dan tidak dilakukan koreksi tanpa dasar yang jelas.

## Data dan lineage
Sumber dan format mentah, jumlah berkas, cara `_berkas_raw`/`_sha256_raw` dibentuk, dan hasil tarik
ulang API (bila dilakukan): apa yang berubah sejak snapshot 17–20 Oktober 2026.

## Masalah data dan penanganannya
Tabel masalah yang ditemukan (missing, outlier, patahan seri, duplikat, format, wilayah) dengan
jumlah baris terdampak, keputusan, dan alternatif yang ditolak. Rujuk id di `log-keputusan.csv`.

## Integrasi dan Perbandingan Seri

Integrasi dilakukan dengan memperhatikan kesamaan definisi indikator, satuan, cakupan wilayah, rincian, dan periode pengamatan. Hal ini diperlukan agar perbandingan antara dua sumber tidak menghasilkan kesimpulan yang keliru akibat perbedaan karakteristik data.

Pasangan pembanding utama yang ditetapkan adalah:

- BPS `var192`, wilayah Indonesia (`9999`), rincian Jumlah.
- WDI `SI.POV.NAHC`, indikator rasio penduduk miskin berdasarkan garis kemiskinan nasional.

Periode perbandingan ditetapkan pada 2007–2025 dengan total 19 tahun irisan. Perbandingan tidak dilakukan pada rincian perkotaan dan perdesaan karena WDI tidak menyediakan rincian yang sebanding.

Perbedaan nilai antara kedua sumber tidak langsung dianggap sebagai kesalahan data. Perbedaan tersebut perlu dianalisis berdasarkan kemungkinan perbedaan definisi, metode penghitungan, cakupan, dan periode rilis data.

Untuk seri jumlah desa mandiri dan desa tertinggal, pemeriksaan dilakukan berdasarkan ketersediaan data BPS dan kesesuaian agregasi wilayah. Khusus `var2191`, kategori Desa Sangat Tertinggal, Desa Tertinggal, dan Jumlah diperiksa konsistensinya. Data jumlah desa juga tidak dibandingkan antarprovinsi tanpa mempertimbangkan perbedaan ukuran dan cakupan wilayah.

## Validasi dan reproduksibilitas
Skema validasi (aturan, hasil lolos/gagal), waktu `python pipeline.py` dari nol, perbandingan pandas
vs DuckDB/Dask, dan keterbatasan yang tersisa.

## Pembagian kerja
| Anggota | NIM | Komponen | Tugas sampingan | Bagian laporan yang ditulis |
|---|---|---|---|---|
