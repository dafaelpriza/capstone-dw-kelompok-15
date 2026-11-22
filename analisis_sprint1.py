
import os
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ============================================
# 1. KONFIGURASI
# ============================================

FILE_SILVER = "data/silver/silver.parquet"
FILES = ["var192", "var2190", "var2191"]

os.makedirs("reports/gambar", exist_ok=True)

# ============================================
# 2. MEMBACA DATA SILVER
# ============================================

if not os.path.exists(FILE_SILVER):
    raise FileNotFoundError(f"File tidak ditemukan: {FILE_SILVER}")

data = pd.read_parquet(FILE_SILVER)

# Ambil data BPS saja
data = data[
    (data["sumber"] == "BPS") &
    (data["seri_kode"].isin(FILES))
].copy()

# Samakan nama kolom
data = data.rename(columns={
    "seri_kode": "variabel",
    "nama_wilayah": "wilayah",
    "wilayah_kode": "wilayah_id"
})

# Konversi nilai
data["nilai"] = pd.to_numeric(
    data["nilai"], errors="coerce"
)

# Periode disimpan sebagai teks agar tidak kehilangan data
data["periode_asli"] = data["periode"].astype(str)

# Ambil tahun untuk kebutuhan grafik saja
data["tahun"] = pd.to_numeric(
    data["periode"].astype(str).str.extract(r"(\d{4})")[0],
    errors="coerce"
)

data["seri"] = (
    data["rincian"].fillna("Tidak diketahui").astype(str)
)

# Hapus hanya baris yang tidak memiliki identitas wilayah atau nilai
data = data.dropna(
    subset=["wilayah", "nilai"]
).copy()

print("JUMLAH DATA SILVER BPS")
print("Jumlah observasi:", len(data))
print("Jumlah wilayah:", data["wilayah"].nunique())
print("\nJumlah data per variabel:")
print(data.groupby("variabel").size().to_string())

# ============================================
# 3. PROFIL PER SERI
# ============================================

profil_seri = (
    data.groupby(["variabel", "seri"])["nilai"]
    .agg(
        jumlah_data="count",
        rata_rata="mean",
        median="median",
        standar_deviasi="std",
        minimum="min",
        Q1=lambda x: x.quantile(0.25),
        Q3=lambda x: x.quantile(0.75),
        maksimum="max"
    )
    .reset_index()
)

profil_seri.to_csv(
    "reports/profil_per_seri.csv",
    index=False
)

print("\nSTATISTIK PER SERI")
print(profil_seri.to_string(index=False))

# ============================================
# 4. PROFIL PER WILAYAH
# ============================================

profil_wilayah = (
    data.groupby(
        ["variabel", "seri", "wilayah", "wilayah_id"]
    )["nilai"]
    .agg(
        jumlah_data="count",
        rata_rata="mean",
        median="median",
        standar_deviasi="std",
        minimum="min",
        Q1=lambda x: x.quantile(0.25),
        Q3=lambda x: x.quantile(0.75),
        maksimum="max"
    )
    .reset_index()
)

profil_wilayah.to_csv(
    "reports/profil_per_provinsi.csv",
    index=False
)

print("\nProfil per wilayah berhasil disimpan.")

# ============================================
# 5. BOXPLOT PER VARIABEL
# ============================================

for variabel in FILES:

    subset = data[data["variabel"] == variabel]
    kategori = sorted(subset["seri"].unique())

    if len(kategori) == 0:
        continue

    fig, axes = plt.subplots(
        len(kategori), 1,
        figsize=(12, max(5, 4 * len(kategori))),
        squeeze=False
    )

    for i, seri in enumerate(kategori):

        nilai = subset.loc[
            subset["seri"] == seri, "nilai"
        ].dropna()

        axes[i, 0].boxplot(
            nilai,
            orientation="horizontal"
        )

        axes[i, 0].set_title(f"Seri: {seri}")
        axes[i, 0].set_xlabel("Nilai")
        axes[i, 0].grid(axis="x", alpha=0.3)

    fig.suptitle(f"Boxplot {variabel}")
    plt.tight_layout()

    plt.savefig(
        f"reports/gambar/boxplot_{variabel}.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

# ============================================
# 6. TIME SERIES PER VARIABEL
# ============================================

for variabel in FILES:

    subset = data[
        (data["variabel"] == variabel) &
        (data["tahun"].notna())
    ].copy()

    kategori = sorted(subset["seri"].unique())

    if len(kategori) == 0:
        continue

    fig, axes = plt.subplots(
        len(kategori), 1,
        figsize=(14, max(5, 5 * len(kategori))),
        squeeze=False
    )

    for i, seri in enumerate(kategori):

        seri_data = subset[
            subset["seri"] == seri
        ]

        for wilayah, grup in seri_data.groupby("wilayah"):

            grup = grup.sort_values("tahun")

            axes[i, 0].plot(
                grup["tahun"],
                grup["nilai"],
                marker="o",
                markersize=3,
                label=wilayah
            )

        axes[i, 0].set_title(f"Seri: {seri}")
        axes[i, 0].set_xlabel("Tahun")
        axes[i, 0].set_ylabel("Nilai")
        axes[i, 0].grid(alpha=0.3)

        if seri_data["wilayah"].nunique() <= 15:
            axes[i, 0].legend(fontsize=7, loc="best")

    fig.suptitle(f"Time Series {variabel}")
    plt.tight_layout()

    plt.savefig(
        f"reports/gambar/timeseries_{variabel}.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

# ============================================
# 7. DETEKSI ANOMALI IQR PER WILAYAH
# ============================================

daftar_anomali = []

for (variabel, seri, wilayah), grup in data.groupby(
    ["variabel", "seri", "wilayah"]
):

    nilai = grup["nilai"].dropna()

    if len(nilai) < 4:
        continue

    q1 = nilai.quantile(0.25)
    q3 = nilai.quantile(0.75)
    iqr = q3 - q1

    batas_bawah = q1 - 1.5 * iqr
    batas_atas = q3 + 1.5 * iqr

    kandidat = grup[
        (grup["nilai"] < batas_bawah) |
        (grup["nilai"] > batas_atas)
    ]

    for _, baris in kandidat.iterrows():

        daftar_anomali.append({
            "variabel": variabel,
            "seri": seri,
            "provinsi": wilayah,
            "periode": baris["periode_asli"],
            "nilai": baris["nilai"],
            "Q1": q1,
            "Q3": q3,
            "IQR": iqr,
            "batas_bawah": batas_bawah,
            "batas_atas": batas_atas
        })

kolom_anomali = [
    "variabel", "seri", "provinsi", "periode",
    "nilai", "Q1", "Q3", "IQR",
    "batas_bawah", "batas_atas"
]

hasil_anomali = pd.DataFrame(
    daftar_anomali,
    columns=kolom_anomali
)

hasil_anomali.to_csv(
    "reports/calon_anomali.csv",
    index=False
)

# ============================================
# 8. RINGKASAN ANOMALI
# ============================================

if not hasil_anomali.empty:

    ringkasan = (
        hasil_anomali.groupby(["variabel", "seri"])
        .size()
        .reset_index(name="jumlah_calon_anomali")
    )

else:

    ringkasan = pd.DataFrame(
        columns=[
            "variabel",
            "seri",
            "jumlah_calon_anomali"
        ]
    )

ringkasan.to_csv(
    "reports/ringkasan_anomali.csv",
    index=False
)

print("\nRINGKASAN CALON ANOMALI")
print(ringkasan.to_string(index=False))

print("\n====================================")
print("ANALISIS SPRINT 1 BERHASIL")
print("====================================")
print("Profil per seri      : reports/profil_per_seri.csv")
print("Profil per wilayah   : reports/profil_per_provinsi.csv")
print("Daftar anomali       : reports/calon_anomali.csv")
print("Ringkasan anomali    : reports/ringkasan_anomali.csv")
print("Grafik               : reports/gambar/")
print("====================================")
