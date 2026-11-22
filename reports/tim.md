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

Berdasarkan hasil ekstraksi, integrasi, dan profiling data pada Sprint 1, ditemukan beberapa permasalahan yang perlu diperhatikan sebelum data digunakan untuk analisis lebih lanjut. Permasalahan tersebut meliputi celah panel, anomali, patahan seri, revisi data, konsistensi nilai, serta standardisasi katalog dan wilayah. Penanganan dilakukan dengan mempertahankan data yang belum terbukti salah dan mencatat setiap keputusan dalam `log-keputusan.csv`.

### 1. Celah Panel dan Missing Value

Pada indikator WDI `SI.POV.NAHC`, ditemukan **38 nilai kosong dari 66 baris data**. Nilai kosong tersebut tidak langsung dihapus atau diisi menggunakan interpolasi karena belum terdapat dasar yang cukup untuk memperkirakan nilai sebenarnya.

Penanganannya adalah:
- Nilai kosong tidak diinterpolasi, termasuk pada periode yang tidak memiliki data.
- Baris tanpa nilai tidak dimasukkan ke dalam data Silver.
- Kelengkapan data tetap dilaporkan melalui hasil profiling.
- Analisis integrasi hanya menggunakan periode yang memiliki data pada kedua sumber.

Berdasarkan keputusan K-003 dan K-005, periode yang dapat dibandingkan antara BPS dan WDI adalah **2007–2025 (19 tahun)**. Data tahun 2026 hanya tersedia pada BPS sehingga tidak digunakan dalam perbandingan kedua sumber.

### 2. Anomali dan Outlier

Hasil deteksi anomali menggunakan metode Interquartile Range (IQR) menghasilkan calon anomali pada variabel `var192` sebagai berikut:

| Seri | Jumlah calon anomali |
|---|---:|
| Jumlah | 106 |
| Perdesaan | 106 |
| Perkotaan | 87 |
| **Total penandaan** | **299** |

Angka tersebut merupakan jumlah penandaan pada masing-masing seri, bukan jumlah observasi unik. Hasil IQR digunakan sebagai alat identifikasi awal dan tidak otomatis menunjukkan kesalahan input.

Beberapa nilai tinggi pada wilayah Papua dan Papua Barat muncul secara berurutan pada beberapa periode. Berdasarkan keputusan K-009, nilai tersebut dipertahankan sebagai calon outlier yang mungkin mencerminkan kondisi sebenarnya karena belum ditemukan bukti kesalahan input.

Nilai nol pada `var192`, `var2190`, dan `var2191` juga dipertahankan sesuai keputusan K-011. Nilai nol tidak diubah menjadi missing value maupun dihapus karena belum terbukti sebagai kesalahan pencatatan.

Dengan demikian, calon anomali tetap ditandai dan didokumentasikan, tetapi tidak langsung dikoreksi atau dihapus.

### 3. Patahan Seri (Series Break)

Pada variabel `var192`, ditemukan penurunan nilai secara serentak pada tahun 2008 di berbagai provinsi. Pola tersebut terlihat pada:
- **33 provinsi** untuk seri Jumlah.
- **33 provinsi** untuk seri Perkotaan.
- **32 provinsi** untuk seri Perdesaan.

Pola penurunan yang terjadi secara bersamaan mengindikasikan kemungkinan adanya patahan seri, misalnya akibat perubahan definisi, metode pengukuran, atau proses pengumpulan data.

Berdasarkan keputusan K-006, nilai tahun 2008 tetap dipertahankan dan ditandai sebagai potensi patahan seri. Nilai tersebut tidak dikoreksi karena belum ditemukan bukti yang cukup untuk memastikan adanya perubahan metode atau definisi.

### 4. Duplikasi dan Revisi Data

Dalam pengelolaan data, perlu dibedakan antara pengulangan observasi dari snapshot yang berbeda dan perubahan nilai pada observasi yang sama.

Berdasarkan keputusan K-008:
- Observasi diidentifikasi berdasarkan kombinasi seri, wilayah, detail, tahun, dan periode.
- Nilai yang sama dari snapshot berbeda diperlakukan sebagai pengulangan observasi, bukan duplikasi yang salah.
- Jika kombinasi identitas observasi yang sama memiliki nilai berbeda pada snapshot berbeda, perubahan tersebut dicatat sebagai indikasi revisi dan riwayat nilainya dipertahankan.
- Nilai dan asal snapshot tetap disimpan sebagai informasi pembanding untuk menelusuri perubahan data.

Berdasarkan keputusan K-010, pemeriksaan revisi antar-snapshot BPS belum dapat dilakukan karena data mentah yang tersedia hanya berasal dari satu snapshot, yaitu 20 Oktober 2026. Folder JSON merupakan bagian dari snapshot yang sama sehingga tidak dapat digunakan sebagai snapshot pembanding independen. Oleh karena itu, belum dapat disimpulkan bahwa tidak terdapat revisi data. Perbedaan nilai yang ditemukan tetap perlu ditelusuri berdasarkan identitas observasi dan asal snapshot sebelum ditetapkan sebagai revisi.

Oleh karena itu, belum dapat disimpulkan bahwa tidak terdapat revisi data. Perbedaan nilai yang ditemukan tetap perlu ditelusuri berdasarkan dimensi dan asal datanya sebelum ditetapkan sebagai revisi.

### 5. Validasi Konsistensi Data

Pada variabel `var2191`, dilakukan pemeriksaan hubungan aritmetika antara jumlah desa sangat tertinggal, desa tertinggal, dan total desa.

Hasil pemeriksaan menunjukkan bahwa pada **102 pasangan wilayah-periode**, penjumlahan kategori desa sangat tertinggal dan desa tertinggal sesuai dengan nilai total. Seluruh pasangan menghasilkan selisih sebesar nol.

Berdasarkan keputusan K-007, seluruh nilai dipertahankan karena telah memenuhi pemeriksaan konsistensi aritmetika. Nilai ekstrem maupun nol tidak diubah tanpa bukti kesalahan input.

### 6. Koreksi Katalog dan Standardisasi Wilayah

Standardisasi wilayah dilakukan untuk mengatasi ketidakkonsistenan penamaan wilayah dan memastikan proses integrasi menggunakan identitas wilayah yang seragam.

Berdasarkan keputusan K-001:
- Referensi wilayah menggunakan **38 provinsi** sesuai standar kode wilayah BPS tahun 2025.
- Kode `9999` digunakan untuk wilayah Indonesia.
- Kode provinsi menggunakan kode BPS dua digit yang dikalikan 100.
- Pencocokan wilayah dilakukan berdasarkan kode, bukan hanya nama wilayah.

Pada `var192` terdapat **39 kode wilayah**, yang terdiri atas 38 provinsi dan 1 agregat Indonesia.

Selain standardisasi wilayah, dilakukan koreksi metadata indikator WDI `SI.POV.NAHC` berdasarkan keputusan K-002. Satuan indikator ditetapkan sebagai persentase penduduk karena informasi tersebut sesuai dengan nama seri dan keterangan sumber (`sourceNote`), meskipun metadata awal tidak mencantumkan satuan secara jelas.

### 7. Ringkasan Hasil Profil Data

Hasil analisis profil Sprint 1 menunjukkan:

- Total observasi yang dianalisis: **3.869 baris**.
- Jumlah wilayah: **39 wilayah**.
- `var192` Jumlah: **1.164 observasi**.
- `var192` Perdesaan: **1.133 observasi**.
- `var192` Perkotaan: **1.164 observasi**.
- `var2190` Tidak ada: **102 observasi**.
- `var2191` Desa Sangat Tertinggal: **102 observasi**.
- `var2191` Desa Tertinggal: **102 observasi**.
- `var2191` Jumlah: **102 observasi**.

Dengan demikian, `var2191` memiliki 306 observasi secara keseluruhan dari tiga kategori, sedangkan `var2190` memiliki 102 observasi.

### Kesimpulan

Secara keseluruhan, Sprint 1 menemukan beberapa permasalahan data, yaitu missing value, calon outlier, potensi patahan seri, serta ketidakkonsistenan katalog wilayah dan metadata. Penanganan dilakukan dengan prinsip mempertahankan data selama belum terdapat bukti kuat bahwa nilai tersebut merupakan kesalahan input.

Selain itu, tim telah menetapkan aturan identifikasi duplikasi dan revisi data serta mempertahankan informasi yang diperlukan untuk menelusuri perubahan nilai. Namun, revisi antar-snapshot BPS belum dapat diverifikasi karena data yang tersedia hanya berasal dari satu snapshot.

Setiap keputusan dicatat dalam `log-keputusan.csv`, sedangkan hasil profiling dan deteksi calon anomali disimpan dalam berkas laporan. Pendekatan ini menjaga keterlacakan data serta memastikan bahwa perubahan pada tahap berikutnya dapat dipertanggungjawabkan.

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