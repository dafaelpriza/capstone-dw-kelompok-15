# Laporan Verifikasi Metadata, Satuan, Periode, dan Kode SDG

Setiap seri pada katalog awal (`data/KASUS.md`) telah diperiksa terhadap judul tabel, catatan unduhan (`manifest_asal.json`), dan metadata indikator (`sumber2_indikator.json`, `sumber46_indikator.json`).

## Ringkasan 4 Koreksi Katalog

| Seri | Sumber | Satuan Awal $\rightarrow$ Baku | Kode SDG Awal $\rightarrow$ Baku | Rujukan Sumber Mentah |
|---|---|---|---|---|
| `var192` | BPS | `persen` $\rightarrow$ **persen** | `10.1.1` $\rightarrow$ **1.2.1** | `bps/2026-10-20/manifest_asal.json & json/sdg10_10_1_1_f_v192.json` |
| `var2190` | BPS | `tidak_ada` $\rightarrow$ **desa** | `10.1.1` $\rightarrow$ **10.1.1(d)** | `bps/2026-10-20/manifest_asal.json & json/sdg10_10_1_1_d_v2190.json` |
| `var2191` | BPS | `tidak_ada` $\rightarrow$ **desa** | `10.1.1` $\rightarrow$ **10.1.1(c)** | `bps/2026-10-20/manifest_asal.json & json/sdg10_10_1_1_c_v2191.json` |
| `SI.POV.NAHC` | WDI | `tidak_ada` $\rightarrow$ **persen** | `10.1.1` $\rightarrow$ **1.2.1** | `wdi/2026-10-20/metadata/sumber2_indikator.json & sumber46_indikator.json` |

## Aturan Penyeragaman Periode (Non-Agregasi di Silver)
- Periode tahunan disimpan sebagai `AAAA` dengan `jenis_periode = 'tahunan'` (contoh: `var192` tahun 2007–2011, `var2190`, `var2191`, dan `SI.POV.NAHC`).
- Periode semesteran (`var192` mulai 2012: Maret = Semester 1, September = Semester 2; tahun 2023 hanya Maret) disimpan terpisah sebagai `AAAA-S1` dan `AAAA-S2` dengan `jenis_periode = 'semester'`.
- Tidak dilakukan perata-rataan semester ke tahunan di lapis Silver.
