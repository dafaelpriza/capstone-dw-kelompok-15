import json
from pathlib import Path
import pandas as pd
from src.common.manifest import sha256_raw


def jalankan() -> dict:
    """Membaca berkas JSON WDI (data & metadata), menyaring kode persis SI.POV.NAHC."""
    raw_dir = Path("data/raw/wdi")
    records = []
    metadata_wdi = {}

    for file_path in sorted(raw_dir.glob("**/*.json")):
        rel_path = str(file_path.relative_to("data/raw")).replace("\\", "/")
        sha_val = sha256_raw(rel_path)

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if "metadata" in file_path.parts:
            metadata_wdi[rel_path] = data
            continue

        # Struktur API World Bank: [info_halaman, daftar_observasi]
        observasi = data[1] if isinstance(data, list) and len(data) > 1 and isinstance(data[1], list) else []

        for item in observasi:
            if not isinstance(item, dict):
                continue
            ind = item.get("indicator") or {}
            # Penyaringan kode persis (bukan substring/awalan)
            if ind.get("id") != "SI.POV.NAHC":
                continue

            negara = item.get("country") or {}
            records.append({
                "sumber": "wdi",
                "seri_kode": "SI.POV.NAHC",
                "seri_nama": ind.get("value", ""),
                "negara_kode": item.get("countryiso3code") or negara.get("id"),
                "nama_wilayah": negara.get("value", "Indonesia"),
                "periode": str(item.get("date", "")),
                "nilai": item.get("value"),  # None / null dipertahankan apa adanya
                "decimal": item.get("decimal"),
                "_berkas_raw": rel_path,
                "_sha256_raw": sha_val,
            })

    df_wdi = pd.DataFrame(records)
    return {
        "wdi_si_pov_nahc": df_wdi,
        "wdi_metadata": metadata_wdi,
    }