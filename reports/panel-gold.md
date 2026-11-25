# Panel Gold provinsi x periode x indikator

Dihasilkan `python pipeline.py` (`src/gold/panel.py`) dari Silver, grid 38 provinsi, dan penanda Sprint 1.

## Aturan satu nilai per sel

1. **Snapshot (`pilih_snapshot`)**: bila terdapat >1 snapshot BPS, pilih snapshot terbaru; saat ini tersedia snapshot `2026-10-20` (dibuang karena snapshot lama: 0).
2. **Rincian (`pilih_rincian`)**: satu indikator panel = deret utama (`total` hasil penyeragaman `Jumlah`/`Tidak ada`). Rincian lain tetap hanya di Silver (`var192` (`daerah=URBAN`: 1,131), `var192` (`daerah=RURAL`: 1,100), `var2191` (`status_desa=sangat_tertinggal`: 99), `var2191` (`status_desa=tertinggal`: 99)). Baris nasional (`9999` dan `SI.POV.NAHC`: 139 baris) dipisah ke tabel nasional.
3. **Berkas (`pilih_berkas`)**: bila satu sel memiliki >1 berkas, pilih menurut `URUTAN_BERKAS` (JSON WebAPI lebih dahulu daripada CSV, lalu urutan jalur) (dibuang karena berkas ganda: 0).
4. **Periode (`aturan_periode`)**: resolusi periode disimpan apa adanya (`var192` provinsi x periode `tahun` & `semester`; `var2190`/`var2191` provinsi x tahun `tahun`). Tidak ada perataan semester ke tahunan.
5. **Grid & Penanda (`bentuk_grid_kosong`, `kumpulkan_penanda_sprint1`)**: sel kosong grid ikut ke panel dengan `status_sel` tanpa interpolasi; penanda `outlier`, `perbedaan_struktural`, `patahan_seri`, dan `patahan_wilayah` dari Sprint 1 terbawa di kolom `penanda` tanpa mengubah nilai.

Baris Silver provinsi yang tidak terpilih masuk panel Gold (rincian non-utama tetap di Silver): **2,429** dari 3,758 baris provinsi (total semua baris Silver yang tidak masuk panel termasuk 139 baris nasional: **2,568**).

## Catatan normalisasi desa

Nilai `var2190` (desa mandiri) dan `var2191` (desa tertinggal) pada panel disimpan dalam satuan asli (`desa`) sesuai data mentah BPS; untuk perbandingan langsung antarprovinsi perlu dinormalisasi terhadap jumlah desa total per provinsi sebagai data pendukung.

## Indikator

| indikator | satuan | periode | jumlah_periode | sel | terisi | ditandai |
|---|---|---|---|---|---|---|
| var192 | persen | 2007–2026-S1 | 33 | 1254 | 1131 | 113 |
| var2190 | desa | 2019–2021 | 3 | 114 | 99 | 66 |
| var2191 | desa | 2019–2021 | 3 | 114 | 99 | 66 |

## Status sel

| indikator | batas_lama | belum_ada | terisi | tidak_diterbitkan |
|---|---|---|---|---|
| var192 | 8 | 115 | 1131 | 0 |
| var2190 | 0 | 12 | 99 | 3 |
| var2191 | 0 | 12 | 99 | 3 |

## Penanda Sprint 1 terbawa ke Gold

| indikator | penanda | jumlah_sel |
|---|---|---|
| var192 | outlier | 68 |
| var192 | patahan_seri | 33 |
| var192 | patahan_wilayah | 3 |
| var192 | perbedaan_struktural | 9 |
| var2190 | patahan_seri | 66 |
| var2191 | patahan_seri | 66 |

## Berkas keluaran

- `data/gold/panel.parquet`: 1,482 baris (panjang, termasuk 153 sel kosong grid).
- `data/gold/panel_lebar.parquet`: 1,230 baris x 7 kolom (hanya 1,329 sel terisi; satu kolom per indikator).
