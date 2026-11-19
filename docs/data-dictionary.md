
# Data Dictionary — Kasus 15: Kemiskinan dan Daerah Tertinggal

## 1. Data Silver

Data Silver merupakan hasil pembersihan dan penyeragaman data dari sumber BPS dan World Development Indicators (WDI).

| Kolom | Tipe Data | Keterangan |
|---|---|---|
| sumber | String | Sumber data, yaitu BPS atau WDI |
| seri_kode | String | Kode unik indikator |
| wilayah_kode | Integer | Kode wilayah |
| nama_wilayah | String | Nama provinsi atau wilayah |
| periode | String | Periode pengamatan, misalnya 2024 atau 2024-S1 |
| jenis_periode | String | Jenis periode, yaitu tahun atau semester |
| rincian | String | Kategori atau rincian indikator |
| nilai | Float | Nilai indikator |
| satuan | String | Satuan pengukuran indikator |
| _berkas_raw | String | Nama berkas sumber data mentah |
| _sha256_raw | String | Hash SHA-256 berkas sumber |

## 2. Katalog Indikator

| Kode Seri | Nama Indikator | Sumber | Satuan |
|---|---|---|---|
| var192 | Persentase Penduduk Miskin Menurut Provinsi dan Daerah | BPS | Persen |
| var2190 | Jumlah Desa Mandiri Menurut Provinsi | BPS | Desa |
| var2191 | Jumlah Desa Tertinggal Menurut Provinsi | BPS | Desa |
| SI.POV.NAHC | Poverty headcount ratio at national poverty lines | WDI | Persen |

## 3. Data Gold

### 3.1 panel_provinsi

Tabel panel provinsi merupakan hasil penggabungan indikator berdasarkan kode wilayah dan periode.

| Kolom | Keterangan |
|---|---|
| wilayah_kode | Kode wilayah provinsi |
| nama_wilayah | Nama provinsi |
| periode | Tahun atau periode pengamatan |
| jenis_periode | Jenis periode pengamatan |
| var192__* | Nilai indikator persentase penduduk miskin |
| var2190__* | Nilai indikator jumlah desa mandiri |
| var2191__* | Nilai indikator jumlah desa tertinggal |
| SI.POV.NAHC__* | Nilai indikator kemiskinan dari WDI |

Tanda * menunjukkan rincian indikator yang menjadi bagian dari nama kolom.

### 3.2 rekonsiliasi_nasional

Tabel ini digunakan untuk membandingkan nilai indikator kemiskinan nasional dari BPS dan WDI pada periode yang sama.

| Kolom | Keterangan |
|---|---|
| periode | Periode pengamatan |
| nilai_bps | Nilai indikator dari BPS |
| nilai_wdi | Nilai indikator dari WDI |
| selisih | Selisih nilai BPS dan WDI |
| status | Keterangan ketersediaan pasangan nilai |

## 4. Satuan Pengukuran

| Satuan | Keterangan |
|---|---|
| persen | Persentase penduduk miskin |
| desa | Jumlah desa berdasarkan kategori indikator |

## 5. Sumber Data

- Badan Pusat Statistik (BPS).
- World Development Indicators (WDI), indikator SI.POV.NAHC.

Data mentah disimpan pada folder data/raw, data hasil pembersihan disimpan pada data/silver, dan hasil integrasi disimpan pada data/gold.
