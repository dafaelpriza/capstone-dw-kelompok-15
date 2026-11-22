# Laporan Tim — Cakrawal, Kasus 15: Kemiskinan di Daerah Tertinggal

## Ringkasan

Tim Cakrawal merupakan Kelompok 15 pada Capstone Data Wrangling 2026 dengan topik **Kemiskinan di Daerah Tertinggal**. Kasus ini termasuk dalam Klaster D, yaitu Kemiskinan dan Ketimpangan, serta berkaitan dengan Sustainable Development Goal (SDG) 10, yaitu Reduced Inequalities.

Pengolahan data berfokus pada tiga seri utama dari Badan Pusat Statistik (BPS), yaitu `var192`, `var2190`, dan `var2191`, serta seri pembanding internasional dari World Development Indicators (WDI), yaitu `SI.POV.NAHC`.

Pada Sprint 1, tim telah melakukan identifikasi sumber data, pemeriksaan awal kualitas data, dan penetapan keputusan terkait pemetaan kode wilayah, satuan indikator, penanganan nilai kosong, serta pemilihan rincian yang sebanding antara BPS dan WDI. Pemeriksaan lanjutan juga dilakukan terhadap nilai nol, calon outlier, indikasi patahan seri, konsistensi kategori, dan aturan deduplikasi. Seluruh keputusan tersebut dicatat dalam `log-keputusan.csv` dengan kode K-001 sampai K-011.

Hasil pemeriksaan menunjukkan adanya indikasi penurunan serentak pada seri `var192` dari 2007 ke 2008, nilai kemiskinan tinggi di Papua dan Papua Barat, serta nilai nol pada beberapa seri. Namun, belum ditemukan bukti yang cukup untuk menetapkan temuan tersebut sebagai galat input. Oleh karena itu, nilai-nilai tersebut dipertahankan dan tidak dilakukan koreksi tanpa dasar yang jelas.

## Data dan Lineage

Data yang digunakan berasal dari BPS dan World Development Indicators (WDI). Paket data kasus Kelompok 15 menggunakan snapshot tanggal 20 Oktober 2026 dan terdiri atas 11 berkas mentah, dengan rincian sebagai berikut.

| Sumber | Jenis berkas | Jumlah |
|---|---|---:|
| BPS | CSV | 3 |
| BPS | JSON | 3 |
| BPS | `manifest_asal.json` | 1 |
| WDI | JSON | 4 |
| **Total** | | **11** |

Seri BPS yang digunakan meliputi:

- `var192`: Persentase Penduduk Miskin (P0) menurut provinsi dan daerah, dengan satuan persen serta ketersediaan periode 2007 sampai 2026-S1.
- `var2190`: Indikator jumlah desa mandiri dengan ketersediaan data 2019–2021.
- `var2191`: Indikator desa tertinggal berdasarkan kategori Desa Sangat Tertinggal, Desa Tertinggal, dan Jumlah, dengan ketersediaan data 2019–2021.

Seri pembanding WDI adalah `SI.POV.NAHC`, yaitu rasio penduduk miskin berdasarkan garis kemiskinan nasional.

Dalam proses pembentukan data Silver, kolom `_berkas_raw` digunakan untuk menyimpan lokasi berkas sumber, sedangkan `_sha256_raw` digunakan untuk menyimpan hash berkas berdasarkan manifest. Informasi tersebut diperlukan agar setiap baris data hasil pengolahan dapat ditelusuri kembali ke sumber mentahnya.

## Masalah Data dan Penanganannya

Berdasarkan pemeriksaan awal dan analisis lanjutan, ditemukan beberapa kondisi data yang memerlukan keputusan penanganan. Permasalahan dan keputusan yang diambil dirangkum sebagai berikut.

| Kode | Permasalahan atau Temuan | Penanganan dan Alasan |
|---|---|---|
| K-001 | Perbedaan kode wilayah antara data BPS dan sumber pembanding. | Pemetaan wilayah dilakukan menggunakan kode wilayah. Indonesia menggunakan kode `9999`, sedangkan kode provinsi mengikuti kode BPS yang dikalikan 100. Penggabungan dilakukan berdasarkan kode, bukan hanya kesamaan nama wilayah. |
| K-002 | Informasi satuan pada seri pembanding WDI `SI.POV.NAHC`. | Satuan seri ditetapkan sebagai persentase berdasarkan informasi metadata seri WDI. |
| K-003 | Terdapat nilai kosong pada seri pembanding WDI. | Nilai kosong dipertahankan dan tidak diinterpolasi agar tidak menghasilkan nilai yang tidak berasal dari sumber data. Ketersediaan data dilaporkan sesuai kondisi sumber. |
| K-004 | Tidak seluruh rincian data BPS memiliki pasangan pembanding pada WDI. | Perbandingan hanya dilakukan pada seri `var192` rincian Jumlah tingkat Indonesia karena WDI tidak menyediakan rincian perkotaan dan perdesaan yang sebanding. |
| K-005 | Perbedaan rentang ketersediaan tahun antara seri BPS dan WDI. | Perbandingan dibatasi pada tahun yang beririsan, yaitu 2007–2025, sebanyak 19 tahun. |
| K-006 | Penurunan nilai `var192` secara serentak dari 2007 ke 2008 pada rincian perkotaan, perdesaan, dan jumlah. | Ditandai sebagai indikasi patahan seri karena seluruh pasangan provinsi-rincian yang dibandingkan mengalami penurunan. Nilai tetap dipertahankan karena perubahan metode atau definisi belum terkonfirmasi. |
| K-007 | Pemeriksaan konsistensi kategori pada seri `var2191`. | Seluruh 102 pasangan wilayah-tahun menunjukkan nilai Jumlah yang sama dengan penjumlahan kategori Desa Sangat Tertinggal dan Desa Tertinggal. Tidak ditemukan ketidaksesuaian aritmetika pada pemeriksaan tersebut. |
| K-008 | Potensi pengulangan observasi dan revisi antar-snapshot. | Angka sama dari snapshot berbeda diperlakukan sebagai pengulangan observasi yang sama. Angka berbeda pada kunci observasi yang sama diperlakukan sebagai revisi dan riwayat nilainya dipertahankan. |
| K-009 | Nilai kemiskinan yang tinggi di Papua dan Papua Barat pada seri `var192`. | Dipertahankan sebagai calon outlier asli karena nilai tinggi muncul pada wilayah dan periode yang berurutan serta belum ditemukan bukti galat input. |
| K-010 | Keterbatasan pemeriksaan revisi antar-snapshot. | Pemeriksaan revisi belum dapat dilakukan karena data raw BPS yang tersedia hanya berasal dari satu snapshot, yaitu 20 Oktober 2026. Oleh karena itu, belum dapat disimpulkan ada atau tidaknya revisi antar-snapshot. |
| K-011 | Ditemukan nilai nol pada seri `var192`, `var2190`, dan `var2191`. | Nilai nol dipertahankan karena belum terbukti sebagai galat input. Pemeriksaan aritmetika `var2191` menunjukkan seluruh 102 pasangan wilayah-tahun konsisten. |

Pemeriksaan lanjutan dilakukan terhadap calon outlier, indikasi patahan seri, nilai nol, konsistensi kategori, dan duplikasi. Belum ditemukan galat input yang terbukti sehingga tidak ada nilai yang diperbaiki. Pemeriksaan duplikasi berdasarkan kunci observasi pada data CSV yang tersedia tidak menemukan duplikasi. Namun, pemeriksaan revisi antar-snapshot belum dapat dilakukan karena hanya tersedia satu snapshot BPS. Selain itu, data JSON yang masih memuat struktur `datacontent` perlu diproses lebih lanjut agar dapat dibandingkan dengan hasil ekstraksi CSV secara menyeluruh. Seluruh temuan dan keputusan penanganannya dicatat dalam `log-keputusan.csv` dengan kode K-006 sampai K-011.

## Integrasi dan Perbandingan Seri

Integrasi dilakukan dengan memperhatikan kesamaan definisi indikator, satuan, cakupan wilayah, rincian, dan periode pengamatan. Hal ini diperlukan agar perbandingan antara dua sumber tidak menghasilkan kesimpulan yang keliru akibat perbedaan karakteristik data.

Pasangan pembanding utama yang ditetapkan adalah:

- BPS `var192`, wilayah Indonesia (`9999`), rincian Jumlah.
- WDI `SI.POV.NAHC`, indikator rasio penduduk miskin berdasarkan garis kemiskinan nasional.

Periode perbandingan ditetapkan pada 2007–2025 dengan total 19 tahun irisan. Perbandingan tidak dilakukan pada rincian perkotaan dan perdesaan karena WDI tidak menyediakan rincian yang sebanding.

Perbedaan nilai antara kedua sumber tidak langsung dianggap sebagai kesalahan data. Perbedaan tersebut perlu dianalisis berdasarkan kemungkinan perbedaan definisi, metode penghitungan, cakupan, dan periode rilis data.

Untuk seri jumlah desa mandiri dan desa tertinggal, pemeriksaan dilakukan berdasarkan ketersediaan data BPS dan kesesuaian agregasi wilayah. Khusus `var2191`, kategori Desa Sangat Tertinggal, Desa Tertinggal, dan Jumlah diperiksa konsistensinya. Data jumlah desa juga tidak dibandingkan antarprovinsi tanpa mempertimbangkan perbedaan ukuran dan cakupan wilayah.

## Validasi dan Reproduksibilitas

Validasi dilakukan untuk memastikan data hasil transformasi memiliki struktur dan nilai yang konsisten dengan ketentuan proyek. Pemeriksaan awal dilakukan terhadap data mentah, sedangkan pengujian terhadap struktur Silver dan Gold perlu dilanjutkan setelah tahap transformasi selesai.

| Aspek validasi | Ketentuan atau pemeriksaan |
|---|---|
| Struktur Silver | Memastikan kolom wajib tersedia dan sesuai dengan skema Silver yang telah ditetapkan. |
| Kode wilayah | Memastikan kode Indonesia `9999` dan kode provinsi menggunakan pemetaan yang konsisten. |
| Nilai kemiskinan | Memeriksa nilai persentase agar berada pada rentang 0–100 serta meninjau nilai yang berada di luar rentang tersebut. |
| Periode | Memastikan periode semester menggunakan format `YYYY-S1` atau `YYYY-S2`, sedangkan periode tahunan dibedakan secara konsisten. |
| Kategori desa | Memeriksa kesesuaian nilai Jumlah dengan penjumlahan kategori pada `var2191`. |
| Duplikasi | Memeriksa kombinasi kunci observasi dan membedakan pengulangan data dengan revisi antar-snapshot. |
| Lineage | Memastikan setiap baris Silver memiliki informasi berkas mentah dan hash sumber. |
| Reproduksibilitas | Memastikan pipeline dapat dijalankan kembali dari data mentah dan menghasilkan keluaran yang konsisten. |

Status kelulusan setiap pemeriksaan, jumlah baris Silver dan Gold, jumlah sel kosong pada grid, serta waktu eksekusi pipeline akan dilengkapi berdasarkan keluaran aktual. Pengujian perbandingan pandas dengan DuckDB atau Dask dan analisis revisi arsip WDI juga menjadi pekerjaan lanjutan sesuai tahapan proyek.

## Pembagian Tugas Tim

Tim Cakrawal terdiri atas enam anggota dengan pembagian komponen sebagai berikut.

| Anggota | Komponen | Fokus tanggung jawab |
|---|---|---|
| Dafa Elpriza | Ekstraksi dan Lineage | Mengambil dan mengumpulkan data dari berbagai sumber serta memastikan keterlacakan sumber data. |
| Najwa Putri Yopu | Validasi dan Dokumentasi | Memeriksa kualitas, akurasi, dan kesesuaian data serta mendokumentasikan proses pengolahan. |
| Helmy Surya Pratama | Profil dan Pembersihan | Memahami karakteristik data, mengidentifikasi pola, dan memeriksa kualitas data sebelum pengolahan lanjutan. |
| Manuel Frederika | Ekstraksi dan Lineage | Memperoleh data dari sumber yang tersedia dan memastikan data dapat digunakan untuk analisis berikutnya. |
| Ghiyats Thabularasa M | Integrasi, Penyimpanan, dan Skala | Menggabungkan data dari berbagai sumber menjadi struktur yang terorganisasi dan mudah dianalisis. |
| Afghanis Nursholehatunnisa | Transformasi dan Panel | Mengubah dan menyesuaikan data agar lebih terstruktur, konsisten, dan siap digunakan untuk analisis. |

## Tugas Sampingan dan Koordinasi

Selain komponen utama, setiap anggota memiliki tugas sampingan untuk mendukung kelancaran proyek.

| Anggota | Peran sampingan | Tanggung jawab |
|---|---|---|
| Ghiyats Thabularasa M | Koordinator | Mengatur jalannya pengerjaan proyek, mengoordinasikan tugas anggota, dan memastikan setiap komponen berjalan sesuai rencana. |
| Manuel Frederika | Penjaga Data dan Evaluasi | Menjaga kualitas dan konsistensi data serta mengevaluasi setiap tahapan pengolahan. |
| Dafa Elpriza | Integrator | Menghubungkan pekerjaan antaranggota agar seluruh komponen berjalan secara terpadu. |
| Afghanis Nursholehatunnisa | Analis Utama | Melakukan analisis menyeluruh, menemukan pola dan permasalahan, serta memberikan interpretasi sebagai dasar kesimpulan. |
| Helmy Surya Pratama | Reproduksi dan Demo | Memastikan proses pengolahan dapat dijalankan kembali secara konsisten dan menyiapkan demonstrasi hasil proyek. |
| Najwa Putri Yopu | Penjaga Data dan Evaluasi | Memastikan data tetap valid, proses pengolahan sesuai standar, dan hasil pekerjaan dievaluasi dengan baik. |

Pembagian komponen dan tugas sampingan mengikuti kontrak tim yang telah disepakati. Karena terdapat dua anggota pada komponen Ekstraksi dan Lineage serta dua anggota pada peran Penjaga Data dan Evaluasi, koordinasi antaranggota diperlukan agar ruang lingkup pekerjaan masing-masing tetap jelas dan tidak tumpang tindih.

## Mekanisme Komunikasi dan Penanganan Kendala Anggota

Standup mingguan dilaksanakan setiap hari Jumat pukul 19.00–20.00 WIB melalui Google Meet atau WhatsApp. Pertemuan digunakan untuk menyampaikan perkembangan pekerjaan, membahas kendala, dan memastikan tugas setiap anggota berjalan sesuai target.

Apabila terdapat anggota yang tidak aktif, tim menerapkan mekanisme berikut.

**Sprint pertama:**

1. Menghubungi anggota yang bersangkutan melalui WhatsApp untuk menanyakan kabar dan kendala yang dihadapi.
2. Memberikan waktu kepada anggota tersebut untuk merespons dan menyelesaikan tugasnya.
3. Jika belum ada respons, tugas sementara dialihkan kepada anggota lain agar progres tim tetap berjalan.

**Sprint kedua:**

1. Jika anggota masih tidak aktif, koordinator melakukan evaluasi terhadap kontribusinya.
2. Tugas dan tanggung jawab anggota tersebut dibagikan kembali kepada anggota yang aktif.
3. Kondisi tersebut dilaporkan kepada pembimbing.

## Status Pekerjaan dan Tindak Lanjut

| Tahapan | Status atau hasil yang tersedia | Tindak lanjut |
|---|---|---|
| Ekstraksi dan lineage | Paket kasus berisi 11 berkas mentah telah diidentifikasi. Data CSV dan JSON telah tersedia pada hasil ekstraksi awal. | Memastikan pembacaan seluruh sumber, mengolah struktur `datacontent` pada JSON, serta melengkapi informasi lineage. |
| Profil dan pembersihan | Pemeriksaan awal telah dilakukan terhadap karakteristik data, nilai nol, calon outlier, indikasi patahan seri, konsistensi kategori, dan aturan deduplikasi. Keputusan K-006 sampai K-011 telah dicatat. | Melanjutkan pemeriksaan setelah seluruh sumber berhasil dinormalisasi dan mendokumentasikan hasil pemeriksaan pada data yang telah terintegrasi. |
| Transformasi dan panel | Periode pembanding BPS dan WDI telah ditetapkan pada 2007–2025. | Melanjutkan implementasi transformasi dan pembentukan data Silver serta memastikan struktur panel sesuai skema. |
| Integrasi dan penyimpanan | Pasangan pembanding BPS dan WDI telah ditentukan berdasarkan kesesuaian indikator, rincian, wilayah, dan periode. | Melengkapi proses integrasi, rekonsiliasi, dan pemeriksaan agregasi seri desa. |
| Validasi dan dokumentasi | Aturan validasi dan keputusan penanganan data telah dirumuskan serta dicatat. | Melengkapi pengujian skema, lineage, reproduksibilitas, dan dokumentasi hasil akhir. |

Pada tahap ini, laporan telah mendokumentasikan sumber data, keputusan penanganan awal, dan hasil pemeriksaan Tahap 3. Pembentukan data Silver dan Gold, pengujian pipeline secara menyeluruh, serta pengisian angka hasil akhir masih perlu diselesaikan berdasarkan keluaran aktual. Jumlah baris Silver dan Gold, jumlah sel kosong pada grid, serta waktu eksekusi tidak dicantumkan sebelum hasilnya tersedia dan dapat diverifikasi dari berkas keluaran yang telah di-commit.
