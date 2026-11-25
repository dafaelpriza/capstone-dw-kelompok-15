# Laporan Kelengkapan Panel Gold (Tahap 4)

Dokumen ini melaporkan pembentukan ulang grid `provinsi × periode` untuk setiap seri di lapisan Gold setelah aturan sel diterapkan (`src/gold/panel_seri.py`). Sesuai keputusan tertulis (`K-003`, `K-006`, `K-011`, `K-012`), **tidak ada celah yang diisi** (tanpa imputasi maupun interpolasi); seluruh celah dan indikasi patahan diberi penanda eksplisit.

## 1. Ringkasan Kelengkapan per Seri (Sebelum dan Sesudah Aturan Sel)

- **Sebelum aturan sel:** satu grid gabungan `38 provinsi × 36 periode` (`panel_provinsi`, 1.368 baris/indikator) yang mencampur periode semesteran/tahunan kemiskinan dengan tahunan desa tanpa klasifikasi status sel.
- **Sesudah aturan sel:** grid `provinsi × periode` dibentuk ulang per seri (`panel_var192` 38×33, `panel_var2190` 38×3, `panel_var2191` 38×3) dan setiap sel diklasifikasikan ke `terisi`, `kosong`, atau `belum_terbit`, serta ditandai `penanda_patahan`.

| Tahap | Seri | Indikator | Grid | Total Sel | Terisi | Kosong | Belum Terbit | Bertanda Patahan | % Terisi (Grid) | % Terisi (Wilayah Aktif) |
|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| Sebelum aturan sel | `var192` | 3 | 38×36 | 4,104 | 3,362 | 742 | 0 | 0 | 81.92% | 81.92% |
| Sebelum aturan sel | `var2190` | 1 | 38×36 | 1,368 | 99 | 1,269 | 0 | 0 | 7.24% | 7.24% |
| Sebelum aturan sel | `var2191` | 3 | 38×36 | 4,104 | 297 | 3,807 | 0 | 0 | 7.24% | 7.24% |
| Sesudah aturan sel | `var192` | 3 | 38×33 | 3,762 | 3,362 | 31 | 369 | 98 | 89.37% | 99.09% |
| Sesudah aturan sel | `var2190` | 1 | 38×3 | 114 | 99 | 3 | 12 | 0 | 86.84% | 97.06% |
| Sesudah aturan sel | `var2191` | 3 | 38×3 | 342 | 297 | 9 | 36 | 0 | 86.84% | 97.06% |

## 2. Kelengkapan Rinci per Indikator (Sebelum vs Sesudah Aturan Sel)

| Tahap | Seri | Indikator | Total Sel | Terisi | Kosong | Belum Terbit | Bertanda Patahan | % Grid | % Aktif |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| Sebelum | `var192` | `var192__Jumlah` | 1,368 | 1,131 | 237 | 0 | 0 | 82.68% | 82.68% |
| Sebelum | `var192` | `var192__Perdesaan` | 1,368 | 1,100 | 268 | 0 | 0 | 80.41% | 80.41% |
| Sebelum | `var192` | `var192__Perkotaan` | 1,368 | 1,131 | 237 | 0 | 0 | 82.68% | 82.68% |
| Sebelum | `var2190` | `var2190__Tidak_ada` | 1,368 | 99 | 1,269 | 0 | 0 | 7.24% | 7.24% |
| Sebelum | `var2191` | `var2191__Desa_Sangat_Tertinggal` | 1,368 | 99 | 1,269 | 0 | 0 | 7.24% | 7.24% |
| Sebelum | `var2191` | `var2191__Desa_Tertinggal` | 1,368 | 99 | 1,269 | 0 | 0 | 7.24% | 7.24% |
| Sebelum | `var2191` | `var2191__Jumlah` | 1,368 | 99 | 1,269 | 0 | 0 | 7.24% | 7.24% |
| Sesudah | `var192` | `var192__Jumlah` | 1,254 | 1,131 | 0 | 123 | 33 | 90.19% | 100.00% |
| Sesudah | `var192` | `var192__Perdesaan` | 1,254 | 1,100 | 31 | 123 | 32 | 87.72% | 97.26% |
| Sesudah | `var192` | `var192__Perkotaan` | 1,254 | 1,131 | 0 | 123 | 33 | 90.19% | 100.00% |
| Sesudah | `var2190` | `var2190__Tidak_ada` | 114 | 99 | 3 | 12 | 0 | 86.84% | 97.06% |
| Sesudah | `var2191` | `var2191__Desa_Sangat_Tertinggal` | 114 | 99 | 3 | 12 | 0 | 86.84% | 97.06% |
| Sesudah | `var2191` | `var2191__Desa_Tertinggal` | 114 | 99 | 3 | 12 | 0 | 86.84% | 97.06% |
| Sesudah | `var2191` | `var2191__Jumlah` | 114 | 99 | 3 | 12 | 0 | 86.84% | 97.06% |

## 3. Rincian Sel Kosong (`kosong`)

| Seri | Indikator | Provinsi | Periode | Jumlah Sel | Keterangan |
|---|---|---|---|---:|---|
| `var192` | `var192__Perdesaan` | DKI JAKARTA (`310000`) | 2007 s.d. 2026-S1 | 31 | kosong_perdesaan_dki_jakarta; patahan_seri_2008_k006 |
| `var2190` | `var2190__Tidak_ada` | DKI JAKARTA (`310000`) | 2019 s.d. 2021 | 3 | kosong_dki_jakarta_non_desa |
| `var2191` | `var2191__Desa_Sangat_Tertinggal` | DKI JAKARTA (`310000`) | 2019 s.d. 2021 | 3 | kosong_dki_jakarta_non_desa |
| `var2191` | `var2191__Desa_Tertinggal` | DKI JAKARTA (`310000`) | 2019 s.d. 2021 | 3 | kosong_dki_jakarta_non_desa |
| `var2191` | `var2191__Jumlah` | DKI JAKARTA (`310000`) | 2019 s.d. 2021 | 3 | kosong_dki_jakarta_non_desa |

## 4. Rincian Sel Belum Terbit (`belum_terbit`)

| Seri | Provinsi | Kode Wilayah | Rentang Periode | Sel per Indikator | Total Sel (Semua Rincian) | Alasan |
|---|---|---:|---|---:|---:|---|
| `var192` | KALIMANTAN UTARA | `650000` | 2007 s.d. 2014-S2 | 11 | 33 | belum_terbit_sebelum_pemekaran_k001 |
| `var192` | PAPUA BARAT DAYA | `920000` | 2007 s.d. 2023-S1 | 28 | 84 | belum_terbit_sebelum_pemekaran_k001 |
| `var192` | PAPUA SELATAN | `950000` | 2007 s.d. 2023-S1 | 28 | 84 | belum_terbit_sebelum_pemekaran_k001 |
| `var192` | PAPUA TENGAH | `960000` | 2007 s.d. 2023-S1 | 28 | 84 | belum_terbit_sebelum_pemekaran_k001 |
| `var192` | PAPUA PEGUNUNGAN | `970000` | 2007 s.d. 2023-S1 | 28 | 84 | belum_terbit_sebelum_pemekaran_k001 |
| `var2190` | PAPUA BARAT DAYA | `920000` | 2019 s.d. 2021 | 3 | 3 | belum_terbit_sebelum_pemekaran_k001 |
| `var2190` | PAPUA SELATAN | `950000` | 2019 s.d. 2021 | 3 | 3 | belum_terbit_sebelum_pemekaran_k001 |
| `var2190` | PAPUA TENGAH | `960000` | 2019 s.d. 2021 | 3 | 3 | belum_terbit_sebelum_pemekaran_k001 |
| `var2190` | PAPUA PEGUNUNGAN | `970000` | 2019 s.d. 2021 | 3 | 3 | belum_terbit_sebelum_pemekaran_k001 |
| `var2191` | PAPUA BARAT DAYA | `920000` | 2019 s.d. 2021 | 3 | 9 | belum_terbit_sebelum_pemekaran_k001 |
| `var2191` | PAPUA SELATAN | `950000` | 2019 s.d. 2021 | 3 | 9 | belum_terbit_sebelum_pemekaran_k001 |
| `var2191` | PAPUA TENGAH | `960000` | 2019 s.d. 2021 | 3 | 9 | belum_terbit_sebelum_pemekaran_k001 |
| `var2191` | PAPUA PEGUNUNGAN | `970000` | 2019 s.d. 2021 | 3 | 9 | belum_terbit_sebelum_pemekaran_k001 |

## 5. Rincian Sel Bertanda Patahan (`penanda_patahan`)

| Seri | Indikator | Periode | Provinsi Terdampak | Total Sel | Dasar Keputusan |
|---|---|---|---:|---:|---|
| `var192` | `var192__Jumlah` | 2008 | 33 | 33 | patahan_seri_2008_k006 |
| `var192` | `var192__Perdesaan` | 2008 | 32 | 32 | patahan_seri_2008_k006 |
| `var192` | `var192__Perkotaan` | 2008 | 33 | 33 | patahan_seri_2008_k006 |

## 6. Catatan Periode Sumber dan Seri Pembanding

- **Periode `2023-S2` pada `var192`:** tidak tersedia pada berkas mentah BPS (`sdg10_10_1_1_f_v192.json` hanya memuat `2023-S1` untuk tahun 2023, termasuk pada baris agregat Indonesia `9999`).
- **Periode `2026-S2` pada `var192`:** belum terbit pada tanggal snapshot `2026-10-20` (`last_update` berkas `2026-08-05`), sehingga cakupan seri ditetapkan `2007` s.d. `2026-S1` (33 periode).
- **Pemekaran 4 DOB Papua (`2024-S1`):** selain patahan serentak `2008` (`K-006`), pergeseran nilai `PAPUA` (`26,03%` pada `2023-S1` menjadi `17,26%` pada `2024-S1`) mencerminkan pemisahan wilayah administratif 3 DOB Papua.
- **Seri pembanding nasional `SI.POV.NAHC` (WDI):** hanya mencakup tingkat nasional Indonesia (`wilayah_kode = 9999`, tidak membentuk grid provinsi); dari 66 baris mentah (1960–2025), 28 tahun terisi dan 38 tahun kosong (disimpan di `rekonsiliasi_nasional` tanpa interpolasi sesuai `K-003`).
