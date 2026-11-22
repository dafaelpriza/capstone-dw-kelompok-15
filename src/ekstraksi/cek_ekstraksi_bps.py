# CEK JUMLAH OTOMATIS EKSTRAKSI BPS (KASUS 15)

import pandas as pd
from src.ekstraksi import bps

berkas_bps = [
    "bps/2026-10-20/sdg10_10_1_1_f_v192.csv",
    "bps/2026-10-20/json/sdg10_10_1_1_f_v192.json",
    "bps/2026-10-20/sdg10_10_1_1_d_v2190.csv",
    "bps/2026-10-20/json/sdg10_10_1_1_d_v2190.json",
    "bps/2026-10-20/sdg10_10_1_1_c_v2191.csv",
    "bps/2026-10-20/json/sdg10_10_1_1_c_v2191.json",
]

hasil = []
bps.tak_terbaca.clear()

for berkas in berkas_bps:
    if berkas.endswith(".csv"):
        df = bps.baca_csv(berkas)
    else:
        df, _ = bps.baca_json(berkas)

    assert "_berkas_raw" in df.columns
    assert "_sha256_raw" in df.columns
    assert df["_berkas_raw"].notna().all()
    assert df["_sha256_raw"].notna().all()
    assert df["_berkas_raw"].nunique() == 1
    assert df["_sha256_raw"].nunique() == 1

    hasil.append({
        "berkas": berkas,
        "sha256_raw": df["_sha256_raw"].iloc[0],
        "jumlah_baris": len(df),
        "jumlah_lineage": df["_sha256_raw"].nunique(),
        "status": "BERHASIL",
    })

    print(f"\nBerkas: {berkas}")
    print("Jumlah baris:", len(df))
    print("SHA-256:", df["_sha256_raw"].iloc[0])
    print(df.head(1).to_string(index=False))

assert len(bps.tak_terbaca) == 0, f"Ada kunci tak terbaca: {len(bps.tak_terbaca)}"

laporan = pd.DataFrame(hasil)
print("\n=== LAPORAN EKSTRAKSI BPS (KASUS 15) ===")
print(laporan[["berkas", "jumlah_baris", "jumlah_lineage", "status"]].to_string(index=False))

laporan.to_csv("reports/hasil-ekstraksi-bps.csv", index=False)
assert laporan["jumlah_baris"].sum() == 7738

print("\nTotal baris BPS (CSV + JSON):", laporan["jumlah_baris"].sum())
print("Kunci JSON tak terbaca:", len(bps.tak_terbaca))
print("Seluruh pemeriksaan berhasil.")
