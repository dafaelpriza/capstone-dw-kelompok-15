# Laporan Validasi Data

## Ringkasan

- Jumlah aturan: 16
- Aturan lolos: 16
- Aturan gagal: 0

## Hasil Pemeriksaan

| Tahap | Aturan | Status | Keterangan |
|---|---|---|---|
| Silver | rentang_var2191 | LOLOS | var2191: 306 nilai diperiksa. |
| Silver | rentang_var2190 | LOLOS | var2190: 102 nilai diperiksa. |
| Silver | rentang_var192 | LOLOS | var192: 3461 nilai diperiksa. |
| Silver | rentang_SI.POV.NAHC | LOLOS | SI.POV.NAHC: 28 nilai diperiksa. |
| Silver | keunikan_kunci | LOLOS | Ditemukan 0 baris duplikat. |
| Silver | konsistensi_satuan | LOLOS | Ditemukan 0 satuan tidak sesuai. |
| Silver | konsistensi_periode | LOLOS | Ditemukan 0 periode yang tidak sesuai. |
| Silver | penjumlahan_rincian_desa | LOLOS | 102 kelompok dapat dibandingkan; ditemukan 0 kelompok dengan selisih. |
| Gold | kelengkapan_panel | LOLOS | Panel memiliki 1368 baris dan 17 kolom. |
| Gold | keunikan_panel | LOLOS | Ditemukan 0 baris dengan kunci wilayah dan periode berulang. |
| Gold | nilai_panel | LOLOS | 7 kolom indikator diperiksa. |
| Gold | kelengkapan_rekonsiliasi | LOLOS | Tabel rekonsiliasi memiliki 56 baris. |
| Gold | konsistensi_selisih | LOLOS | 5 pasangan nilai BPS dan WDI diperiksa. |
| Gold | penanda_sel_panel_var192 | LOLOS | panel_var192: 1254 baris, 38 provinsi x 33 periode diperiksa tanpa imputasi celah. |
| Gold | penanda_sel_panel_var2190 | LOLOS | panel_var2190: 114 baris, 38 provinsi x 3 periode diperiksa tanpa imputasi celah. |
| Gold | penanda_sel_panel_var2191 | LOLOS | panel_var2191: 114 baris, 38 provinsi x 3 periode diperiksa tanpa imputasi celah. |