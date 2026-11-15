import os
import pandas as pd

os.makedirs("reports/tabel", exist_ok=True)

kandidat = pd.DataFrame([
    {"rincian_bps": "jumlah (9999)", "padanan_wdi": "SI.POV.NAHC (total nasional)",
     "sebanding": "ya",
     "alasan": "Keduanya persen penduduk di bawah garis kemiskinan nasional, tingkat nasional. Jenis periode berbeda: BPS semester/tahunan, WDI tahunan. Selisih rata-rata |WDI-S1| 0,032 vs |WDI-S2| 0,258 (n=14 dan 13). Definisi WDI: persentase penduduk di bawah garis kemiskinan nasional (sourceNote, sumber2_indikator.json); metadata tidak menyebut semester BPS yang dipakai."},
    {"rincian_bps": "perkotaan (9999)", "padanan_wdi": "tidak ada",
     "sebanding": "tidak",
     "alasan": "Di berkas WDI hanya ada SI.POV.DDAY dan SI.POV.NAHC, tidak ada versi perkotaan."},
    {"rincian_bps": "perdesaan (9999)", "padanan_wdi": "tidak ada",
     "sebanding": "tidak",
     "alasan": "Sama seperti perkotaan: tidak ada indikator perdesaan di berkas WDI."},
    {"rincian_bps": "provinsi (semua rincian)", "padanan_wdi": "tidak ada",
     "sebanding": "tidak",
     "alasan": "WDI hanya tingkat nasional (Indonesia)."},
    {"rincian_bps": "desa tertinggal (var2190, var2191)", "padanan_wdi": "tidak ada",
     "sebanding": "tidak",
     "alasan": "Hitungan desa, bukan persen; tidak punya pembanding di paket (panduan kelompok bagian 3)."},
])
kandidat.to_csv("reports/tabel/kandidat_rincian_sebanding.csv", index=False)
print(kandidat.to_string(index=False))