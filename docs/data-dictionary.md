
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

Dengan demikian, asal observasi dapat diperiksa kembali tanpa menebak sumbernya. Daftar berkas dan hash resmi juga dicatat pada data/raw/MANIFEST.csv.


## 6. Sumber Data

- Data mentah BPS dan WDI: data/raw/.
- Manifest nama berkas dan SHA-256: data/raw/MANIFEST.csv.
- Aturan katalog seri, satuan, dan periode: src/konfigurasi.py.
- Ekstraksi BPS: src/ekstraksi/bps.py.
- Ekstraksi WDI: src/ekstraksi/wdi.py.
- Pembentukan tabel Silver: src/silver/__init__.py.
- Verifikasi metadata seri: src/silver/metadata.py.
- Pemeriksaan skema minimal: src/common/skema.py.
- Catatan keputusan tim: log-keputusan.csv.
