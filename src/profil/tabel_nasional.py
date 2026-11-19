from pathlib import Path
import pandas as pd
from src.ekstraksi import bps, wdi


def main():
    hasil_bps = bps.jalankan()
    hasil_wdi = wdi.jalankan()

    df_bps = hasil_bps["bps_json"].copy()
    df_meta = hasil_bps["bps_metadata"].copy()
    df_wdi = hasil_wdi["wdi_si_pov_nahc"].copy()

    # 1. WDI SI.POV.NAHC (Indonesia)
    wdi_nas = df_wdi[df_wdi["negara_kode"] == "IDN"][["periode", "nilai"]].dropna().copy()
    wdi_nas["tahun"] = wdi_nas["periode"].astype(int)
    wdi_nas["kolom_seri"] = "WDI_SI.POV.NAHC_Tahunan"

    # 2. BPS var192 (Baris Indonesia, rincian Jumlah)
    v192 = df_bps[
        (df_bps["seri_kode"] == "var192")
        & (df_bps["nama_wilayah"].str.upper() == "INDONESIA")
        & (df_bps["rincian"].str.lower() == "jumlah")
    ].copy()
    v192["tahun"] = v192["tahun_label"].astype(str).str.extract(r"(\d{4})")[0].astype(int)

    def _label_v192(tt):
        tt_low = str(tt).lower()
        if "maret" in tt_low or "semester 1" in tt_low:
            return "BPS_var192_Jumlah_S1_Maret"
        if "september" in tt_low or "semester 2" in tt_low:
            return "BPS_var192_Jumlah_S2_September"
        return "BPS_var192_Jumlah_Tahunan"

    v192["kolom_seri"] = v192["turtahun_label"].apply(_label_v192)

    # 3. Seri Desa BPS (var2190 & var2191): Baris Indonesia vs Agregat Provinsi
    desa_rows = []
    for kode_desa in ["var2190", "var2191"]:
        sub = df_bps[df_bps["seri_kode"] == kode_desa].copy()
        if sub.empty:
            continue
        sub["tahun"] = sub["tahun_label"].astype(str).str.extract(r"(\d{4})")[0].astype(int)
        rincian_unik = sub["rincian"].unique()
        if len(rincian_unik) > 1 and any(r.lower() == "jumlah" for r in rincian_unik):
            sub = sub[sub["rincian"].str.lower() == "jumlah"]

        nas_bps = sub[sub["nama_wilayah"].str.upper() == "INDONESIA"].copy()
        if not nas_bps.empty:
            nas_bps["kolom_seri"] = f"BPS_{kode_desa}_Indonesia"
            desa_rows.append(nas_bps[["tahun", "kolom_seri", "nilai"]])

        prov_bps = sub[sub["nama_wilayah"].str.upper() != "INDONESIA"].copy()
        if not prov_bps.empty:
            agg_prov = prov_bps.groupby("tahun", as_index=False)["nilai"].sum()
            agg_prov["kolom_seri"] = f"BPS_{kode_desa}_Agregat_Provinsi"
            desa_rows.append(agg_prov[["tahun", "kolom_seri", "nilai"]])

    gabung = pd.concat(
        [
            wdi_nas[["tahun", "kolom_seri", "nilai"]],
            v192[["tahun", "kolom_seri", "nilai"]],
            *desa_rows,
        ],
        ignore_index=True,
    )

    tabel_nasional = (
        gabung.pivot_table(index="tahun", columns="kolom_seri", values="nilai", aggfunc="first")
        .sort_index()
        .reset_index()
    )

    out_path = Path("reports/tabel/tabel_nasional_periode_seri.csv")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tabel_nasional.to_csv(out_path, index=False)

    print("=== TABEL NASIONAL PERIODE x SERI ===")
    print(tabel_nasional.to_string(index=False))
    print("\n=== CATATAN METADATA SERI DESA ===")
    print(df_meta[df_meta["seri_kode"].isin(["var2190", "var2191"])][["seri_kode", "label", "unit", "note"]].to_string(index=False))


if __name__ == "__main__":
    main()
