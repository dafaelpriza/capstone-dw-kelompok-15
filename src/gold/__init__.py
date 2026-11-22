
"""Tahap 4â€“6 â€” Reshape, integrasi, dan penyimpanan data Gold."""

from src.gold import muat_sql, nasional
from pathlib import Path
import sqlite3

import pandas as pd


FOLDER_GOLD = Path("data/gold")


def _siapkan_data(silver):
    """Menyiapkan kolom dan tipe data Silver untuk proses Gold."""
    wajib = [
        "sumber", "seri_kode", "wilayah_kode", "nama_wilayah",
        "periode", "jenis_periode", "rincian", "nilai", "satuan"
    ]

    kurang = [kolom for kolom in wajib if kolom not in silver.columns]

    if kurang:
        raise ValueError(f"Kolom Silver belum lengkap: {kurang}")

    data = silver.copy()

    data["nilai"] = pd.to_numeric(data["nilai"], errors="coerce")
    data["wilayah_kode"] = pd.to_numeric(
        data["wilayah_kode"], errors="coerce"
    )

    data["periode"] = data["periode"].astype(str)
    data["rincian"] = (
        data["rincian"].fillna("Total").astype(str).str.strip()
    )

    data = data.dropna(
        subset=["wilayah_kode", "periode", "nilai", "seri_kode"]
    ).copy()

    data["wilayah_kode"] = data["wilayah_kode"].astype("Int64")

    return data


def _buat_panel_provinsi(data):
    """Membuat panel provinsi dengan indikator sebagai kolom."""

    # Nama wilayah yang menunjukkan data tingkat nasional.
    nama_nasional = {
        "indonesia",
        "nasional",
        "indonesia (nasional)"
    }

    nama_normal = (
        data["nama_wilayah"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.lower()
    )

    provinsi = data[~nama_normal.isin(nama_nasional)].copy()

    if provinsi.empty:
        raise ValueError("Tidak ditemukan data wilayah provinsi pada Silver.")

    # Menggabungkan kode seri dan rincian sebagai nama kolom indikator.
    provinsi["indikator"] = (
        provinsi["seri_kode"].astype(str)
        + "__"
        + provinsi["rincian"].str.replace(" ", "_", regex=False)
    )

    indeks = [
        "wilayah_kode",
        "nama_wilayah",
        "periode",
        "jenis_periode"
    ]

    # Memastikan satu kombinasi wilayah-periode-indikator
    # tidak memiliki lebih dari satu nilai.
    kunci = indeks + ["indikator"]

    duplikat = provinsi.duplicated(subset=kunci, keep=False)

    if duplikat.any():
        raise ValueError(
            f"Ditemukan {int(duplikat.sum())} baris dengan "
            "kombinasi wilayah, periode, dan indikator yang berulang."
        )

    panel = provinsi.pivot(
        index=indeks,
        columns="indikator",
        values="nilai"
    ).reset_index()

    panel.columns.name = None

    # Membuat grid wilayah x periode yang ditemukan pada data provinsi.
    wilayah = provinsi[
        ["wilayah_kode", "nama_wilayah"]
    ].drop_duplicates()

    periode = provinsi[
        ["periode", "jenis_periode"]
    ].drop_duplicates()

    grid = wilayah.merge(periode, how="cross")

    # Menambahkan kombinasi indikator yang belum memiliki nilai.
    indikator = sorted(provinsi["indikator"].unique())

    grid = grid.merge(panel, on=indeks, how="left")

    for nama_indikator in indikator:
        if nama_indikator not in grid.columns:
            grid[nama_indikator] = pd.NA

    kolom_utama = indeks
    kolom_indikator = sorted(
        kolom for kolom in grid.columns
        if kolom not in kolom_utama
    )

    grid = grid[kolom_utama + kolom_indikator]

    grid = grid.sort_values(
        ["wilayah_kode", "periode"]
    ).reset_index(drop=True)

    return grid


def _buat_rekonsiliasi(data):
    """Membandingkan indikator kemiskinan nasional BPS dan WDI."""

    nama_normal = (
        data["nama_wilayah"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.lower()
    )

    # Mengambil observasi nasional BPS untuk var192.
    bps = data[
        (data["sumber"].str.lower() == "bps")
        & (data["seri_kode"] == "var192")
        & (nama_normal.isin({
            "indonesia",
            "nasional",
            "indonesia (nasional)"
        }))
    ].copy()

    # Mengambil observasi WDI.
    wdi = data[
        (data["seri_kode"] == "SI.POV.NAHC")
    ].copy()

    bps_total = bps[
        bps["rincian"].str.strip().str.lower().isin(
            ["jumlah", "total"]
        )
    ]

    kolom = ["periode", "nilai"]

    bps_total = bps_total[kolom].rename(
        columns={"nilai": "nilai_bps"}
    )

    wdi = wdi[kolom].rename(
        columns={"nilai": "nilai_wdi"}
    )

    # Menggabungkan berdasarkan periode yang sama.
    rekonsiliasi = pd.merge(
        bps_total,
        wdi,
        on="periode",
        how="outer"
    )

    rekonsiliasi["selisih"] = (
        rekonsiliasi["nilai_bps"] - rekonsiliasi["nilai_wdi"]
    )

    rekonsiliasi["status"] = "Tidak dapat dibandingkan"

    tersedia = (
        rekonsiliasi["nilai_bps"].notna()
        & rekonsiliasi["nilai_wdi"].notna()
    )

    rekonsiliasi.loc[
        tersedia, "status"
    ] = "Dapat dibandingkan"

    rekonsiliasi = rekonsiliasi.sort_values(
        "periode"
    ).reset_index(drop=True)

    return rekonsiliasi


def jalankan(silver):
    """Terima Silver, tulis tabel Gold, dan kembalikan DataFrame."""

    print("Menyiapkan data Gold...")

    data = _siapkan_data(silver)

    print("Membuat panel provinsi...")
    panel = _buat_panel_provinsi(data)

    print("Membuat rekonsiliasi nasional...")
    rekonsiliasi = _buat_rekonsiliasi(data)

    hasil = {
        "panel_provinsi": panel,
        "rekonsiliasi_nasional": rekonsiliasi
    }

    # Menyimpan hasil ke Parquet.
    FOLDER_GOLD.mkdir(parents=True, exist_ok=True)

    for nama_tabel, df in hasil.items():
        lokasi = FOLDER_GOLD / f"{nama_tabel}.parquet"
        df.to_parquet(lokasi, index=False)
        print(f"Berhasil menyimpan: {lokasi} ({len(df)} baris)")

    # Menyimpan hasil ke SQLite.
    lokasi_sql = FOLDER_GOLD / "gold.sqlite"

    with sqlite3.connect(lokasi_sql) as koneksi:
        for nama_tabel, df in hasil.items():
            df.to_sql(
                nama_tabel,
                koneksi,
                if_exists="replace",
                index=False
            )

    print(f"Database Gold berhasil dibuat: {lokasi_sql}")

    nasional.jalankan(silver)
    muat_sql.jalankan()
    return hasil

