
# Data Dictionary — Kasus 15: Kemiskinan dan Daerah Tertinggal

## 1. Data Silver

Tabel Silver memiliki 11 kolom berikut

| Nama Kolom | Tipe Data | Satuan | Arti | Asal |
|---|---|---|---|---|
| sumber | string (object) | - | Menunjukkan sumber observasi, yaitu bps atau wdi. | Nilai tetap yang ditambahkan saat ekstraksi berdasarkan berkas sumber: src/ekstraksi/bps.py dan src/ekstraksi/wdi.py. |
| seri_kode | string (object) | - | Kode unik seri/indikator, yaitu var192, var2190, var2191, atau SI.POV.NAHC. | BPS: dibentuk dari kode variabel var pada JSON BPS. WDI: diambil dari indicator.id dan disaring agar sama persis dengan SI.POV.NAHC. |
| wilayah_kode | integer nullable (Int64) | Kode wilayah | Kode baku wilayah. 9999 digunakan untuk Indonesia; kode provinsi BPS dikalikan 100 sesuai keputusan pemetaan kode wilayah. | BPS: berasal dari vervar_kode lalu dikalikan 100. WDI: ditetapkan menjadi 9999 untuk Indonesia. |
| nama_wilayah | string (object) | - | Nama wilayah yang terkait dengan observasi, misalnya nama provinsi atau Indonesia. | BPS: label dimensi vervar pada JSON BPS. WDI: nama negara dari objek country.value. |
| periode | string (object) | Tahun atau semester | Periode waktu observasi. Periode tahunan menggunakan format AAAA, sedangkan periode semester menggunakan AAAA-S1 atau AAAA-S2. | BPS: berasal dari label tahun dan diseragamkan memakai label turtahun tanpa merata-ratakan semester. WDI: berasal dari date pada observasi WDI. |
| jenis_periode | string (object) | - | Menjelaskan bentuk periode observasi, yaitu tahun atau semester. | BPS: ditentukan dari metadata turtahun setelah pemetaan. WDI: ditetapkan sebagai tahun karena data WDI pada seri ini bersifat tahunan. |
| rincian | string (object) | - | Kategori/rincian dari suatu indikator. Pada BPS mengikuti label dimensi rincian; pada WDI diisi Total. | BPS: label dimensi turvar pada JSON BPS. WDI: nilai tetap Total yang ditambahkan pada tahap penyiapan Silver. |
| nilai | numerik (float64) | Mengikuti satuan | Nilai observasi indikator. Nilai dikonversi menjadi numerik; observasi tanpa nilai tidak dimasukkan ke tabel Silver. | BPS: nilai pada datacontent JSON BPS. WDI: atribut value pada observasi WDI. |
| satuan | string (object) | Persen atau desa | Satuan pengukuran nilai indikator. var192 dan SI.POV.NAHC menggunakan persen; var2190 dan var2191 menggunakan desa. | Ditetapkan berdasarkan KATALOG_SERI di src/konfigurasi.py melalui terapkan_satuan_dan_periode; WDI juga ditetapkan sebagai persen pada penyiapan Silver. |
| _berkas_raw | string (object) | Jalur berkas relatif terhadap data/raw/ | Menyimpan lokasi berkas mentah yang menghasilkan observasi, sehingga baris Silver dapat ditelusuri ke sumbernya. | Diisi saat ekstraksi BPS/WDI dari jalur relatif berkas yang sedang dibaca. |
| _sha256_raw | string (object) | SHA-256 (64 karakter heksadesimal) | Menyimpan hash SHA-256 berkas mentah sebagai identitas/integritas berkas sumber. | Dihitung saat ekstraksi menggunakan fungsi sha256_raw dari src.common.manifest, bukan ditulis manual. |

## 2. Katalog Indikator

| Kode Seri | Nama Indikator | Sumber | Satuan Baku | Keterangan |
|---|---|---|---|---|
| var192 | Persentase Penduduk Miskin Menurut Provinsi dan Daerah | BPS | persen | Kode indikator SDG baku 1.2.1; berkas BPS menggunakan label butir nasional 10.1.1(f). |
| var2190 | Jumlah Desa Mandiri Menurut Provinsi | BPS | desa | Satuan ditetapkan menjadi desa berdasarkan judul dan isi indikator. |
| var2191 | Jumlah Desa Tertinggal Menurut Provinsi | BPS | desa | Satuan ditetapkan menjadi desa berdasarkan judul dan isi indikator. |
| SI.POV.NAHC | Poverty headcount ratio at national poverty lines (% of population) | WDI | persen | Satuan persen penduduk; kode indikator SDG baku 1.2.1. |

## 3. Aturan Penyeragaman dan Pembentukan Silver

1. Data BPS yang digunakan untuk membentuk Silver berasal dari JSON BPS. Berkas CSV BPS tetap diekstrak, tetapi tidak digabungkan ke tabel Silver agar observasi yang sama tidak tercatat dua kali.
2. Kode wilayah provinsi BPS diseragamkan dengan mengalikan kode vervar dua digit dengan 100. Kode 9999 digunakan untuk Indonesia.
3. Periode BPS dipertahankan sesuai resolusi sumber. Periode tahunan disimpan sebagai AAAA; periode semester disimpan sebagai AAAA-S1 (Maret) dan AAAA-S2 (September). Nilai semester tidak dirata-ratakan menjadi nilai tahunan.
4. Data WDI untuk Indonesia diberi wilayah_kode = 9999, jenis_periode = tahun, rincian = Total, dan satuan = persen.
5. Baris tanpa nilai, wilayah_kode, periode, atau seri_kode tidak dimasukkan ke Silver.
6. Duplikasi dihapus berdasarkan kombinasi sumber, seri_kode, wilayah_kode, periode, rincian, dan _berkas_raw.

## 4. Satuan Pengukuran

| Satuan | Keterangan |
|---|---|
| persen | Persentase penduduk miskin |
| desa | Jumlah desa berdasarkan kategori indikator |

## 5. Keterlacakan Data (Data Lineage)

Setiap baris Silver membawa dua kolom metadata sumber:

- **_berkas_raw** menunjukkan jalur relatif berkas sumber di dalam folder data/raw/.
- **_sha256_raw** menunjukkan hash SHA-256 dari berkas tersebut.

Proses menelusuri satu baris Silver:
1. Baca nilai _berkas_raw pada baris yang ingin diperiksa.
2. Cari berkas dengan jalur yang sama di dalam data/raw/.
3. Hitung SHA-256 berkas tersebut dan bandingkan dengan _sha256_raw atau cocokkan dengan data/raw/MANIFEST.csv.

Contoh Penelusuran Satu Baris Silver

Sebagai contoh, salah satu observasi pada indikator persentase penduduk
miskin (var192) memiliki informasi berikut:

| Kolom | Nilai |
|---|---|
| sumber | bps |
| seri_kode | var192 |
| wilayah_kode | 640000 |
| nama_wilayah | KALIMANTAN TIMUR |
| periode | 2008 |
| jenis_periode | tahun |
| rincian | Perkotaan |
| nilai | 5.89 |
| satuan | persen |
| _berkas_raw | bps/2026-10-20/json/sdg10_10_1_1_f_v192.json |
| _sha256_raw | 8d3c028b5e6b246865af1c635fd4e835e5cd12aca7a9387fc2b53e2270771fc4 |

Berdasarkan informasi tersebut, berkas mentah dapat ditemukan pada 
lokasi: data/raw/bps/2026-10-20/json/sdg10_10_1_1_f_v192.json
Nilai _sha256_raw dapat dicocokkan dengan catatan berkas yang sama pada data/raw/MANIFEST.csv. Pada berkas JSON BPS tersebut, observasi dengan kode data 640019243210863 memiliki nilai 5.89, sesuai dengan observasi yang dicatat pada Silver.

Dengan demikian, asal observasi dapat diperiksa kembali tanpa menebak sumbernya. Daftar berkas dan hash resmi juga dicatat pada data/raw/MANIFEST.csv.


## 6. Sumber Data

- Data mentah BPS dan WDI: data/raw/.
- Manifest nama berkas dan SHA-256: data/raw/MANIFEST.csv.
- Aturan katalog seri, satuan, dan periode: src/konfigurasi.py.
- Ekstraksi BPS: src/ekstraksi/bps.py.
- Ekstraksi WDI: src/ekstraksi/wdi.py.
- Pembentukan tabel Silver: src/silver/__init__.py.
- Pembentukan tabel Gold dan aturan sel: src/gold/__init__.py, src/gold/panel_seri.py.
- Verifikasi metadata seri: src/silver/metadata.py.
- Pemeriksaan skema minimal: src/common/skema.py.
- Catatan keputusan tim: log-keputusan.csv.

## 7. Data Gold dan Kolom Penanda

Lapisan Gold (`data/gold/`) menyimpan panel tingkat provinsi per seri yang dibentuk ulang dari Silver beserta tabel gabungan dan rekonsiliasi nasional (juga dimuat ke `data/gold/gold.sqlite`). Sesuai keputusan `K-003`, `K-006`, `K-011`, dan `K-012`, **celah pada grid Gold tidak diisi** (tanpa imputasi/interpolasi) dan setiap sel diberi penanda eksplisit.

### 7.1 Daftar Tabel Gold

| Nama Tabel / Berkas | Dimensi Grid | Deskripsi |
|---|---|---|
| `panel_var192.parquet` | 38 provinsi × 33 periode (1.254 baris) | Panel kemiskinan (`var192`: `Jumlah`, `Perdesaan`, `Perkotaan`) periode `2007` s.d. `2026-S1`. |
| `panel_var2190.parquet` | 38 provinsi × 3 periode (114 baris) | Panel jumlah desa mandiri (`var2190`) periode tahunan `2019`–`2021`. |
| `panel_var2191.parquet` | 38 provinsi × 3 periode (114 baris) | Panel jumlah desa tertinggal (`var2191`: `Desa_Sangat_Tertinggal`, `Desa_Tertinggal`, `Jumlah`) periode tahunan `2019`–`2021`. |
| `panel_provinsi.parquet` | 38 provinsi × 36 periode (1.368 baris) | Panel gabungan seluruh seri BPS tingkat provinsi yang diperkaya kolom penanda per seri. |
| `rekonsiliasi_nasional.parquet` | 56 periode | Perbandingan indikator nasional Indonesia (`9999`) antara BPS `var192` (`Jumlah`) dan WDI `SI.POV.NAHC`. |
| `gudang.duckdb` | `seri` (4 baris), `silver` (3.897 baris) | Gudang relasional DuckDB dengan `PRIMARY KEY`, `FOREIGN KEY`, dan `CHECK` constraint (`src/gold/silver.sql`). |

### 7.2 Struktur Kolom Panel Gold per Seri (`panel_var192`, `panel_var2190`, `panel_var2191`)

#### Kolom Kunci dan Nilai

| Nama Kolom | Tipe Data | Satuan | Arti |
|---|---|---|---|
| `wilayah_kode` | integer nullable (`Int64`) | Kode wilayah | Kode wilayah provinsi baku (susunan 38 provinsi 2025, `K-001`). |
| `nama_wilayah` | string (`object`) | - | Nama provinsi sesuai susunan 38 provinsi 2025. |
| `periode` | string (`object`) | Tahun atau semester | Periode observasi (`AAAA` untuk tahunan; `AAAA-S1`/`AAAA-S2` untuk semesteran). |
| `jenis_periode` | string (`object`) | - | Bentuk periode: `tahun` atau `semester`. |
| `var192__Jumlah`, `var192__Perdesaan`, `var192__Perkotaan` | numerik (`float64`) | persen | Persentase penduduk miskin (`panel_var192`). Bernilai `NaN` jika sel berstatus `kosong` atau `belum_terbit`. |
| `var2190__Tidak_ada` | numerik (`float64`) | desa | Jumlah desa mandiri (`panel_var2190`). Bernilai `NaN` jika `kosong` atau `belum_terbit`. |
| `var2191__Desa_Sangat_Tertinggal`, `var2191__Desa_Tertinggal`, `var2191__Jumlah` | numerik (`float64`) | desa | Jumlah desa sangat tertinggal, tertinggal, dan jumlahnya (`panel_var2191`). Bernilai `NaN` jika `kosong` atau `belum_terbit`. |

#### Kolom Penanda (`Kolom Penanda` di Gold)

| Nama Kolom | Terdapat Pada | Tipe Data | Nilai Sah | Arti dan Aturan Penetapan |
|---|---|---|---|---|
| `status_sel_jumlah`, `status_sel_perdesaan`, `status_sel_perkotaan` | `panel_var192` | string (`object`) | `terisi`, `kosong`, `belum_terbit` | Status kelengkapan masing-masing rincian pada `panel_var192`. `terisi`: nilai observasi tersedia di Silver (termasuk `0.0` pada DKI Jakarta Perdesaan 2012-S2 & 2016-S2 sesuai `K-011`). `belum_terbit`: provinsi pemekaran belum terbentuk/terbit pada periode tersebut (Kalimantan Utara `650000` untuk `2007`–`2014-S2`; 4 DOB Papua `920000`, `950000`, `960000`, `970000` untuk `2007`–`2023-S1`). `kosong`: sel tidak terisi meski provinsi dan periode aktif (DKI Jakarta `310000` pada `Perdesaan` untuk 31 periode). |
| `status_sel` | `panel_var2190`, `panel_var2191` | string (`object`) | `terisi`, `kosong`, `belum_terbit` | Status kelengkapan sel pada panel desa (`2019`–`2021`). `terisi`: seluruh 33 provinsi non-DKI dan non-DOB Papua. `belum_terbit`: 4 DOB Papua (`920000`, `950000`, `960000`, `970000`) karena baru terbentuk setelah 2021. `kosong`: DKI Jakarta (`310000`) karena tidak memiliki wilayah administrasi desa (hanya kelurahan). |
| `penanda_patahan` | `panel_var192`, `panel_var2190`, `panel_var2191` | boolean (`bool`) | `True`, `False` | Menandai sel observasi yang berada pada titik patahan seri (`series break`). Bernilai `True` pada `panel_var192` periode `2008` untuk provinsi yang sudah terbit (penurunan serentak 2007→2008 pada 33 provinsi `Jumlah`/`Perkotaan` dan 32 provinsi `Perdesaan`, sesuai `K-006`). Nilai tetap dipertahankan tanpa koreksi. Pada `panel_var2190` dan `panel_var2191` seluruh baris bernilai `False`. |
| `keterangan_sel` | `panel_var192`, `panel_var2190`, `panel_var2191` | string (`object`) | `normal`, tag keterangan | Ringkasan alasan status sel dan patahan pada baris bersangkutan: `normal`, `patahan_seri_2008_k006`, `belum_terbit_sebelum_pemekaran_k001`, `kosong_perdesaan_dki_jakarta`, `kosong_dki_jakarta_non_desa`, atau gabungannya (`;` sebagai pemisah). |
| `status_sel_var192_jumlah`, `status_sel_var192_perdesaan`, `status_sel_var192_perkotaan`, `status_sel_var2190`, `status_sel_var2191` | `panel_provinsi` | string (`object`) | `terisi`, `kosong`, `belum_terbit`, `di_luar_cakupan_periode` | Status kelengkapan per seri pada tabel gabungan `panel_provinsi` (`38 × 36`). Nilai `di_luar_cakupan_periode` menandai sel yang kosong semata karena resolusi/rentang periode seri berbeda (mis. periode tahunan `2019`–`2021` untuk `var192`, atau periode di luar `2019`–`2021` untuk `var2190`/`var2191`). |
| `penanda_patahan_var192` | `panel_provinsi` | boolean (`bool`) | `True`, `False` | Penanda patahan seri `var192` tahun `2008` (`K-006`) pada tabel gabungan `panel_provinsi`. |

### 7.3 Laporan Kelengkapan Gold

Tabel dan ringkasan kelengkapan per seri (sebelum dan sesudah aturan sel) dihasilkan otomatis oleh `src/gold/panel_seri.py` ke:
- `reports/kelengkapan_gold_per_seri.csv` — perbandingan numerik sebelum dan sesudah aturan sel per seri dan per indikator.
- `reports/kelengkapan_gold_rincian_celah.csv` — daftar rinci setiap kelompok sel `kosong`, `belum_terbit`, dan `patahan`.
- `reports/kelengkapan_gold.md` — laporan naratif dan tabel ringkas Tahap 4.
