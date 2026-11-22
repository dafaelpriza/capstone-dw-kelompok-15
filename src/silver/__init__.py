
"""Tahap 2–4 — Profil, pembersihan, dan penyeragaman ke Silver."""

from pathlib import Path

import pandas as pd

from src.silver.metadata import (
    terapkan_satuan_dan_periode,
    tulis_dokumentasi_metadata,
    verifikasi_dari_mentah,
)


KOLOM_SILVER = [
    "sumber",
    "seri_kode",
    "wilayah_kode",
    "nama_wilayah",
    "periode",
    "jenis_periode",
    "rincian",
    "nilai",
    "satuan",
    "_berkas_raw",
    "_sha256_raw",
]


def _siapkan_bps(df):
    """Menyeragamkan data BPS."""
    if df.empty:
        return pd.DataFrame()

    data = df.copy()

    # Kode wilayah provinsi mengikuti standar skema tim.
    if "wilayah_kode" not in data.columns:
        data["wilayah_kode"] = (
            pd.to_numeric(data["vervar_kode"], errors="coerce") * 100
        )

    data["wilayah_kode"] = data["wilayah_kode"].astype("Int64")

    data["periode"] = data["tahun_label"].astype(str)

    # Informasi periode semester/tahunan berasal dari metadata BPS.
    data["turtahun"] = data["turtahun_label"]

    data = terapkan_satuan_dan_periode(data)

    data["jenis_periode"] = data["jenis_periode"].replace({
    "tahunan": "tahun"
    })
    
    data["nilai"] = pd.to_numeric(data["nilai"], errors="coerce")

    return data



def _siapkan_wdi(df):
    """Menyeragamkan data World Bank."""
    if df.empty:
        return pd.DataFrame()

    data = df.copy()

    # Kode wilayah Indonesia.
    data["wilayah_kode"] = 9999

    # Menyeragamkan format periode.
    data["periode"] = data["periode"].astype(str)
    data["jenis_periode"] = "tahun"

    # Indikator WDI merupakan persentase.
    data["satuan"] = "persen"

    # Menentukan rincian indikator.
    data["rincian"] = "Total"

    data["nilai"] = pd.to_numeric(
        data["nilai"], errors="coerce"
    )

    return data


def jalankan(mentah: dict) -> pd.DataFrame:
    """Membentuk, membersihkan, dan menyimpan tabel Silver."""

    # 1. Verifikasi metadata.
    df_seri = verifikasi_dari_mentah(mentah)
    tulis_dokumentasi_metadata(df_seri)

    # 2. Mengambil data hasil ekstraksi.
    bps = mentah.get("bps_json", pd.DataFrame())
    wdi = mentah.get("wdi_si_pov_nahc", pd.DataFrame())

    # 3. Menyeragamkan masing-masing sumber.
    bagian = []

    if not bps.empty:
        bagian.append(_siapkan_bps(bps))

    if not wdi.empty:
        bagian.append(_siapkan_wdi(wdi))

    if not bagian:
        raise ValueError("Tidak ada data BPS atau WDI untuk membentuk Silver.")

    # 4. Menggabungkan data tanpa menggabungkan nilai antar-sumber.
    silver = pd.concat(bagian, ignore_index=True)

    # 5. Memastikan kolom wajib tersedia.
    for kolom in KOLOM_SILVER:
        if kolom not in silver.columns:
            silver[kolom] = pd.NA

    silver = silver[KOLOM_SILVER].copy()

    # 6. Membersihkan nilai kosong dan tipe data.
    silver["nilai"] = pd.to_numeric(silver["nilai"], errors="coerce")
    silver["wilayah_kode"] = pd.to_numeric(
        silver["wilayah_kode"], errors="coerce"
    ).astype("Int64")

    # Observasi tanpa nilai atau kode wilayah tidak dimasukkan ke Silver.
    sebelum = len(silver)

    silver = silver.dropna(
        subset=["nilai", "wilayah_kode", "periode", "seri_kode"]
    ).copy()

    # 7. Menghapus duplikasi berdasarkan kunci Silver.
    kunci = [
        "sumber",
        "seri_kode",
        "wilayah_kode",
        "periode",
        "rincian",
        "_berkas_raw",
    ]

    jumlah_duplikat = int(silver.duplicated(subset=kunci).sum())
    silver = silver.drop_duplicates(subset=kunci, keep="first")

    # 8. Mencatat keputusan pembersihan.
    Path("reports").mkdir(parents=True, exist_ok=True)

    log = pd.DataFrame([
        {
            "keputusan": "Menghapus observasi dengan nilai, wilayah, periode, atau seri kosong",
            "jumlah": sebelum - len(
                silver
            ) - jumlah_duplikat,
        },
        {
            "keputusan": "Menghapus baris duplikat berdasarkan kunci Silver",
            "jumlah": jumlah_duplikat,
        },
    ])

    log.to_csv(
        "reports/log-keputusan.csv",
        index=False,
        encoding="utf-8-sig",
    )

    # 9. Menyimpan hasil Silver.
    Path("data/silver").mkdir(parents=True, exist_ok=True)

    silver.to_parquet(
        "data/silver/silver.parquet",
        index=False,
    )

    print(f"Silver berhasil dibuat: {len(silver)} baris.")
    print("File: data/silver/silver.parquet")

    return silver
