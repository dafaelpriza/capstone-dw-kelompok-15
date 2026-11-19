import os
import pandas as pd
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ============================================
# 1. KONFIGURASI
# ============================================

FILES = {
    "var192": "data/raw/bps/2026-10-20/sdg10_10_1_1_f_v192.csv",
    "var2190": "data/raw/bps/2026-10-20/sdg10_10_1_1_d_v2190.csv",
    "var2191": "data/raw/bps/2026-10-20/sdg10_10_1_1_c_v2191.csv"
}

os.makedirs("reports/gambar", exist_ok=True)

# ============================================
# 2. MEMBACA DATA
# ============================================

daftar_data = []

for variabel, file in FILES.items():

    print(f"Membaca {variabel}...")

    if not os.path.exists(file):
        raise FileNotFoundError(f"File tidak ditemukan: {file}")

    df = pd.read_csv(file)

    kolom_wajib = [
        "wilayah", "wilayah_id", "turvar",
        "tahun", "nilai"
    ]

    for kolom in kolom_wajib:
        if kolom not in df.columns:
            raise ValueError(
                f"Kolom {kolom} tidak ditemukan pada {file}"
            )

    df["nilai"] = pd.to_numeric(
        df["nilai"].astype(str).str.replace(",", ".", regex=False),
        errors="coerce"
    )

    df["tahun"] = pd.to_numeric(
        df["tahun"], errors="coerce"
    )

    df["variabel"] = variabel

    df["seri"] = (
        df["turvar"].fillna("Tidak diketahui").astype(str)
    )

    df = df.dropna(
        subset=["wilayah", "tahun", "nilai"]
    ).copy()

    daftar_data.append(df)

data = pd.concat(daftar_data, ignore_index=True)

print("\nJumlah seluruh observasi:", len(data))
print("Jumlah wilayah:", data["wilayah"].nunique())

# ============================================
# 3. STATISTIK PER SERI
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
# 4. STATISTIK PER PROVINSI DAN SERI
# ============================================

profil_provinsi = (
    data.groupby(["variabel", "seri", "wilayah", "wilayah_id"])
    ["nilai"]
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

profil_provinsi.to_csv(
    "reports/profil_per_provinsi.csv",
    index=False
)

print("\nStatistik per provinsi berhasil disimpan.")

# ============================================
# 5. BOXPLOT PER VARIABEL
# ============================================

for variabel in FILES:

    subset = data[data["variabel"] == variabel]

    kategori = sorted(subset["seri"].unique())

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
            vert=False,
            patch_artist=True
        )

        axes[i, 0].set_title(f"Seri: {seri}")
        axes[i, 0].set_xlabel("Nilai")
        axes[i, 0].grid(axis="x", alpha=0.3)

    fig.suptitle(
        f"Boxplot {variabel} Berdasarkan Seri",
        fontsize=14
    )

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

    subset = data[data["variabel"] == variabel].copy()

    kategori = sorted(subset["seri"].unique())

    fig, axes = plt.subplots(
        len(kategori), 1,
        figsize=(14, max(5, 5 * len(kategori))),
        squeeze=False
    )

    for i, seri in enumerate(kategori):

        seri_data = subset[subset["seri"] == seri]

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
            axes[i, 0].legend(
                fontsize=7,
                loc="best"
            )

    fig.suptitle(
        f"Time Series {variabel}",
        fontsize=14
    )

    plt.tight_layout()

    plt.savefig(
        f"reports/gambar/timeseries_{variabel}.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

# ============================================
# 7. DETEKSI ANOMALI METODE IQR
# ============================================

daftar_anomali = []

for (variabel, seri, wilayah), grup in data.groupby(
    ["variabel", "seri", "wilayah"]
):

    nilai = grup["nilai"].dropna()

    if len(nilai) < 4:
        continue

    Q1 = nilai.quantile(0.25)
    Q3 = nilai.quantile(0.75)

    IQR = Q3 - Q1

    batas_bawah = Q1 - 1.5 * IQR
    batas_atas = Q3 + 1.5 * IQR

    kandidat = grup[
        (grup["nilai"] < batas_bawah) |
        (grup["nilai"] > batas_atas)
    ]

    for _, baris in kandidat.iterrows():

        if baris["nilai"] < batas_bawah:
            alasan = "Nilai di bawah batas bawah IQR"
        else:
            alasan = "Nilai di atas batas atas IQR"

        daftar_anomali.append({
            "variabel": variabel,
            "seri": seri,
            "provinsi": wilayah,
            "periode": int(baris["tahun"]),
            "nilai": baris["nilai"],
            "Q1": Q1,
            "Q3": Q3,
            "IQR": IQR,
            "batas_bawah": batas_bawah,
            "batas_atas": batas_atas,
            "alasan": alasan
        })

hasil_anomali = pd.DataFrame(daftar_anomali)

kolom_anomali = [
    "variabel", "seri", "provinsi", "periode",
    "nilai", "Q1", "Q3", "IQR",
    "batas_bawah", "batas_atas", "alasan"
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
        columns=["variabel", "seri", "jumlah_calon_anomali"]
    )

ringkasan.to_csv(
    "reports/ringkasan_anomali.csv",
    index=False
)

# ============================================
# 9. MEMBUAT LAPORAN
# ============================================

with open(
    "reports/laporan_sprint1.md",
    "w",
    encoding="utf-8"
) as f:

    f.write("# Laporan Tahap 2 - Sprint 1\n\n")

    f.write("## 1. Tujuan Analisis\n\n")
    f.write(
        "Analisis dilakukan terhadap var192, var2190, "
        "dan var2191 untuk mengetahui karakteristik "
        "statistik setiap seri dan wilayah.\n\n"
    )

    f.write("## 2. Statistik Deskriptif\n\n")
    f.write("- `profil_per_seri.csv`\n")
    f.write("- `profil_per_provinsi.csv`\n\n")

    f.write("## 3. Visualisasi\n\n")

    for variabel in FILES:

        f.write(f"### {variabel}\n\n")

        f.write(
            f"![Boxplot {variabel}]"
            f"(gambar/boxplot_{variabel}.png)\n\n"
        )

        f.write(
            f"![Time Series {variabel}]"
            f"(gambar/timeseries_{variabel}.png)\n\n"
        )

    f.write("## 4. Deteksi Calon Anomali\n\n")
    f.write(
        "Deteksi dilakukan menggunakan metode IQR "
        "dengan batas 1,5 kali IQR pada setiap kombinasi "
        "variabel, seri, dan wilayah. Hasilnya hanya "
        "merupakan calon anomali, bukan bukti kesalahan data.\n\n"
    )

    f.write(
        "Daftar hasil tersedia pada `calon_anomali.csv` "
        "dan ringkasannya pada `ringkasan_anomali.csv`.\n\n"
    )

    f.write(
        "Tidak dilakukan penghapusan, penggantian, "
        "atau perbaikan terhadap data asli.\n"
    )

print("\n====================================")
print("ANALISIS TAHAP 2 BERHASIL")
print("====================================")
print("Profil per seri       : reports/profil_per_seri.csv")
print("Profil per provinsi   : reports/profil_per_provinsi.csv")
print("Daftar calon anomali  : reports/calon_anomali.csv")
print("Ringkasan anomali     : reports/ringkasan_anomali.csv")
print("Grafik                : reports/gambar/")
print("Laporan               : reports/laporan_sprint1.md")
print("====================================")
