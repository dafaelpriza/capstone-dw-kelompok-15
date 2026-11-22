import json
import pandas as pd
from src.common.manifest import sha256_raw

berkas = "wdi/2026-10-20/data/kelompok-06-hal-01.json"
with open(f"data/raw/{berkas}", encoding="utf-8") as f:
    meta, obs = json.load(f)

df = pd.json_normalize(obs)
df = df.rename(columns={
    "indicator.id": "seri_kode",
    "indicator.value": "nama_seri",
    "country.id": "negara_kode",
    "country.value": "negara",
})
df["_berkas_raw"] = berkas
df["_sha256_raw"] = sha256_raw(berkas)

print("Kolom:", list(df.columns))
print("Baris mentah total:", len(df))
print("Indikator unik:", df["seri_kode"].nunique())
print("Negara unik:", df["negara"].unique())

s = df[df["seri_kode"] == "SI.POV.NAHC"].copy()
print("\n=== SI.POV.NAHC ===")
print("Baris:", len(s))
if len(s) == 0:
    print("Tidak ada. Indikator mirip:")
    print(sorted(df[df["seri_kode"].str.startswith("SI.POV")]["seri_kode"].unique()))
else:
    print("Nama:", s["nama_seri"].iloc[0])
    print("Nilai null:", s["value"].isna().sum())
    print("Nilai terisi:", s["value"].notna().sum())
    terisi = s[s["value"].notna()]
    print("Tahun terisi:", terisi["date"].min(), "s.d.", terisi["date"].max())
    print("Min/median/maks:", terisi["value"].min(), terisi["value"].median(), terisi["value"].max())
    print("scale:", s["scale"].unique(), "| unit:", s["unit"].unique(),
          "| obs_status:", s["obs_status"].unique())
    print("\nTahun null:", sorted(s[s["value"].isna()]["date"].tolist()))
    print("\n", s[["date", "value"]].sort_values("date").to_string(index=False))

print("\nIndikator kembar SI.POV.*:")
print(df[df["seri_kode"].str.startswith("SI.POV")][["seri_kode", "nama_seri"]].drop_duplicates().to_string(index=False))

import os

os.makedirs("reports/tabel", exist_ok=True)

tabel = s[["seri_kode", "negara", "date", "value", "unit", "obs_status"]].copy()
tabel = tabel.rename(columns={"date": "tahun", "value": "nilai"})
tabel["tahun"] = tabel["tahun"].astype(int)
tabel["periode_jenis"] = "tahunan"
tabel["rincian"] = "total"
tabel["satuan_ditetapkan"] = "persen"
tabel["status"] = tabel["nilai"].apply(lambda v: "kosong" if pd.isna(v) else "terisi")
tabel = tabel.sort_values("tahun")
tabel.to_csv("reports/tabel/ketersediaan_wdi_si_pov_nahc.csv", index=False)
print("\nTabel tersimpan:", len(tabel), "baris")