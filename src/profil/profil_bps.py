
import pandas as pd
from pathlib import Path

# Menentukan direktori utama repository
ROOT = Path(__file__).resolve().parents[2]

# Lokasi file sumber BPS
INPUT = (
    ROOT
    / "data"
    / "raw"
    / "bps"
    / "2026-10-20"
    / "sdg10_10_1_1_f_v192.csv"
)

# Lokasi penyimpanan hasil
OUTPUT = (
    ROOT
    / "reports"
    / "tabel"
    / "ketersediaan_bps_var192.csv"
)

# Membaca data
if not INPUT.exists():
    raise FileNotFoundError(f"File tidak ditemukan: {INPUT}")

data = pd.read_csv(INPUT)

# Memastikan kolom yang diperlukan tersedia
kolom_wajib = [
    "wilayah_id",
    "wilayah",
    "turvar_id",
    "turvar",
    "tahun",
    "periode_id",
    "periode",
    "nilai",
    "satuan"
]

kolom_hilang = [
    kolom for kolom in kolom_wajib
    if kolom not in data.columns
]

if kolom_hilang:
    raise ValueError(
        f"Kolom tidak ditemukan: {kolom_hilang}"
    )

# Mengubah tipe data
data["tahun"] = pd.to_numeric(
    data["tahun"], errors="coerce"
)

data["nilai"] = pd.to_numeric(
    data["nilai"], errors="coerce"
)

# Membuat profil ketersediaan berdasarkan
# wilayah, rincian, periode, dan satuan
hasil = (
    data.groupby(
        [
            "wilayah_id",
            "wilayah",
            "turvar_id",
            "turvar",
            "periode_id",
            "periode",
            "satuan"
        ],
        dropna=False
    )
    .agg(
        tahun_awal=("tahun", "min"),
        tahun_akhir=("tahun", "max"),
        jumlah_observasi=("nilai", "count"),
        jumlah_baris=("tahun", "count")
    )
    .reset_index()
)

# Mengurutkan hasil
hasil = hasil.sort_values(
    by=[
        "wilayah_id",
        "turvar_id",
        "periode_id"
    ]
)

# Menyimpan hasil
OUTPUT.parent.mkdir(
    parents=True,
    exist_ok=True
)

hasil.to_csv(
    OUTPUT,
    index=False
)

print("\nTABEL KETERSEDIAAN BPS BERHASIL DIBUAT")
print(f"Jumlah kelompok data: {len(hasil)}")
print(f"Lokasi hasil: {OUTPUT}")

print("\nHASIL PROFIL BPS:")
print(hasil.to_string(index=False))
