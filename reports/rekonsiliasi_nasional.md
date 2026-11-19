# Daftar Pasangan Rekonsiliasi & Catatan Keterbandingan (Kasus 15)

Tabel gabungan baris nasional (periode × seri) tersimpan pada: `reports/tabel/tabel_nasional_periode_seri.csv`.

## 1. Daftar Pasangan Rekonsiliasi

| No | Seri Utama (BPS) | Seri Pembanding | Rincian yang Dipakai | Periode Beririsan | Catatan Keterbandingan |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | `var192` (Persentase Penduduk Miskin - BPS) | `SI.POV.NAHC` (*Poverty headcount ratio at national poverty lines* - WDI) | Baris **INDONESIA**, rincian **Jumlah** (total Perkotaan + Perdesaan), satuan **Persen (%)** | **19 tahun** (2007–2025) | **Sebanding dengan penyesuaian semester & pembulatan:**<br>• **2007–2011 (5 tahun):** BPS menyajikan angka tahunan, dan WDI menggunakan angka tahunan tersebut dibulatkan 1 desimal (`\|WDI − BPS\| ≤ 0,05`).<br>• **2012–2025 (14 tahun):** BPS menyajikan data per semester (Maret/S1 dan September/S2). Pencocokan numerik membuktikan WDI menggunakan angka **Semester 1 (Maret)** dengan rata-rata selisih absolut `0,032` poin persen (murni pembulatan 1 desimal, mis. `11,96 → 12,0` pada 2012 dan `8,47 → 8,5` pada 2025), sedangkan selisih terhadap S2 mencapai rata-rata `0,258` poin persen. |
| 2 | `var2190` (Jumlah Desa Tertinggal - BPS) | Agregat Provinsi vs Baris **INDONESIA** pada berkas BPS | Seluruh provinsi vs baris total **INDONESIA** (bila tersedia), satuan **Desa** | Sesuai ketersediaan tahun pada `tabel_nasional_periode_seri.csv` | **Tidak ada pembanding eksternal di paket WDI:** WDI hanya memuat indikator persentase kemiskinan nasional (`SI.POV.NAHC`, `SI.POV.DDAY`). Rekonsiliasi dilakukan secara internal antar-tingkat wilayah BPS (`Σ Provinsi` vs baris `INDONESIA`) serta memperhatikan catatan metadata (`var.note`) terkait patahan sumber/definisi indeks desa. |
| 3 | `var2191` (Seri Desa Pembanding/Lanjutan - BPS) | Agregat Provinsi vs Baris **INDONESIA** pada berkas BPS | Seluruh provinsi vs baris total **INDONESIA** (bila tersedia), satuan **Desa** | Sesuai ketersediaan tahun pada `tabel_nasional_periode_seri.csv` | **Tidak ada pembanding eksternal di paket WDI:** Sama seperti `var2190`, tidak tersedia padanan di WDI sehingga diverifikasi melalui konsistensi penjumlahan provinsi terhadap baris total nasional BPS. |

## 2. Rincian yang Tidak Dipakai dalam Rekonsiliasi Nasional
- **Rincian Perkotaan & Perdesaan (`var192`):** Tidak memiliki padanan pada paket WDI (`SI.POV.NAHC` hanya menyajikan agregat nasional).
- **Level Provinsi (`var192`):** Tidak memiliki padanan pada WDI karena WDI hanya mencakup tingkat negara (`IDN`).
