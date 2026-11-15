import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

os.makedirs("reports/tabel", exist_ok=True)
os.makedirs("reports/gambar", exist_ok=True)

# --- BPS: hanya Indonesia (9999), rincian Jumlah ---
bps = pd.read_csv("data/raw/bps/2026-10-20/sdg10_10_1_1_f_v192.csv")
ind = bps[(bps["wilayah_id"] == 9999)].copy()
print("Baris Indonesia (semua rincian):", len(ind))
print("Rincian pada baris Indonesia:", sorted(ind["turvar"].unique()))

jum = ind[ind["turvar"] == "Jumlah"].copy()
jum["jenis"] = jum["periode"].map({
    "Semester 1 (Maret)": "S1",
    "Semester 2 (September)": "S2",
    "Tahunan": "Tahunan",
})
lebar = jum.pivot_table(index="tahun", columns="jenis", values="nilai", aggfunc="first")

# --- WDI: tabel yang sudah disimpan ---
wdi = pd.read_csv("reports/tabel/ketersediaan_wdi_si_pov_nahc.csv")
wdi = wdi[["tahun", "nilai"]].rename(columns={"nilai": "WDI"}).set_index("tahun")

gab = wdi.join(lebar, how="outer").loc[2007:2026]
gab["ada_WDI"] = gab["WDI"].notna()
gab["ada_BPS_Tahunan"] = gab["Tahunan"].notna()
gab["ada_BPS_S1"] = gab["S1"].notna()
gab["ada_BPS_S2"] = gab["S2"].notna()
gab["irisan_WDI_BPS"] = gab["ada_WDI"] & (gab["ada_BPS_Tahunan"] | gab["ada_BPS_S1"] | gab["ada_BPS_S2"])
gab["selisih_WDI_S1"] = gab["WDI"] - gab["S1"]
gab["selisih_WDI_S2"] = gab["WDI"] - gab["S2"]
gab["selisih_WDI_Tahunan"] = gab["WDI"] - gab["Tahunan"]

gab.reset_index().to_csv("reports/tabel/irisan_wdi_bps_var192.csv", index=False)
print("\n", gab[["WDI", "Tahunan", "S1", "S2", "irisan_WDI_BPS"]].to_string())
print("\nJumlah tahun irisan:", int(gab["irisan_WDI_BPS"].sum()))
print("Tahun irisan:", gab[gab["irisan_WDI_BPS"]].index.min(), "s.d.", gab[gab["irisan_WDI_BPS"]].index.max())

# Rata-rata selisih absolut (hanya pengamatan awal, bukan penetapan)
for k in ["selisih_WDI_S1", "selisih_WDI_S2", "selisih_WDI_Tahunan"]:
    print(k, "rata-rata |selisih|:", round(gab[k].abs().mean(), 3), "| n:", int(gab[k].notna().sum()))

# --- Grafik ---
plt.figure(figsize=(10, 5))
plt.plot(gab.index, gab["WDI"], "k-o", label="WDI SI.POV.NAHC")
plt.plot(gab.index, gab["Tahunan"], "s", label="BPS Tahunan")
plt.plot(gab.index, gab["S1"], "^-", label="BPS S1 (Maret)")
plt.plot(gab.index, gab["S2"], "v-", label="BPS S2 (September)")
plt.ylabel("% penduduk miskin")
plt.xlabel("Tahun")
plt.title("WDI vs BPS var192 (Indonesia, rincian jumlah)")
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("reports/gambar/wdi_vs_bps_var192.png", dpi=150)
print("\nGrafik tersimpan: reports/gambar/wdi_vs_bps_var192.png")