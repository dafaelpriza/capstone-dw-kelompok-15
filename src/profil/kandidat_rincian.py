
import pandas as pd
from pathlib import Path

# ==========================================
# 1. MENENTUKAN LOKASI FILE
# ==========================================

ROOT = Path(__file__).resolve().parents[2]

FILE_IRISAN = (
    ROOT / "reports" / "tabel" /
    "irisan_wdi_bps_var192.csv"
)

OUTPUT = (
    ROOT / "reports" / "tabel" /
    "kandidat_rincian_sebanding.csv"
)

# ==========================================
# 2. MEMBACA DATA IRISAN
# ==========================================

irisan = pd.read_csv(FILE_IRISAN)

kolom_status = [
    "ada_WDI",
    "ada_BPS_Tahunan",
    "ada_BPS_S1",
    "ada_BPS_S2"
]

for kolom in kolom_status:
    irisan[kolom] = (
        irisan[kolom]
        .astype(str)
        .str.lower()
        .eq("true")
    )

# ==========================================
# 3. MENGHITUNG IRISAN SETIAP PERIODE
# ==========================================

pasangan_periode = [
    {
        "periode": "Tahunan",
        "kolom_bps": "ada_BPS_Tahunan",
        "kolom_nilai": "Tahunan"
    },
    {
        "periode": "Semester 1 (Maret)",
        "kolom_bps": "ada_BPS_S1",
        "kolom_nilai": "S1"
    },
    {
        "periode": "Semester 2 (September)",
        "kolom_bps": "ada_BPS_S2",
        "kolom_nilai": "S2"
    }
]

hasil_periode = []

for item in pasangan_periode:

    data = irisan[
        irisan["ada_WDI"] &
        irisan[item["kolom_bps"]]
    ].copy()

    data = data.dropna(
        subset=["WDI", item["kolom_nilai"]]
    )

    tahun = data["tahun"].astype(int).tolist()

    selisih = (
        data["WDI"] - data[item["kolom_nilai"]]
    ).abs()

    rata_selisih = (
        round(selisih.mean(), 3)
        if len(selisih) > 0
        else None
    )

    hasil_periode.append({
        "periode_bps": item["periode"],
        "tahun_irisan": ", ".join(map(str, tahun)),
        "jumlah_tahun_irisan": len(tahun),
        "rata_rata_selisih_absolut": rata_selisih
    })

# ==========================================
# 4. MENENTUKAN KANDIDAT PERIODE
# ==========================================

df_periode = pd.DataFrame(hasil_periode)

# Semester 1 dan Semester 2 dipertimbangkan
# untuk periode setelah perubahan frekuensi.
s1 = df_periode[
    df_periode["periode_bps"] == "Semester 1 (Maret)"
].iloc[0]

s2 = df_periode[
    df_periode["periode_bps"] == "Semester 2 (September)"
].iloc[0]

# ==========================================
# 5. MENYUSUN TABEL KANDIDAT RINCIAN
# ==========================================

kandidat = []


# Kandidat utama: BPS Jumlah dan WDI Total
for _, row in df_periode.iterrows():

    periode = row["periode_bps"]

    if periode == "Semester 1 (Maret)":
        status = "Kandidat utama berdasarkan kelengkapan"
        dasar = (
            f"Dipilih sebagai kandidat utama karena memiliki "
            f"{row['jumlah_tahun_irisan']} tahun irisan "
            f"({row['tahun_irisan']}), lebih banyak dibandingkan "
            f"Semester 2 yang memiliki {int(s2['jumlah_tahun_irisan'])} "
            f"tahun irisan. Rata-rata selisih absolutnya juga lebih "
            f"kecil, yaitu {row['rata_rata_selisih_absolut']:.3f} "
            f"dibandingkan {s2['rata_rata_selisih_absolut']:.3f} "
            f"pada Semester 2."
        )

    elif periode == "Semester 2 (September)":
        status = "Kandidat alternatif"
        dasar = (
            f"Menjadi kandidat alternatif karena memiliki "
            f"{row['jumlah_tahun_irisan']} tahun irisan "
            f"({row['tahun_irisan']}). Observasi BPS tahun 2023 "
            f"tidak tersedia sehingga jumlah irisan lebih sedikit "
            f"dibandingkan Semester 1. Rata-rata selisih absolutnya "
            f"juga lebih besar, yaitu "
            f"{row['rata_rata_selisih_absolut']:.3f}."
        )

    else:
        status = "Kandidat untuk periode awal"
        dasar = (
            f"WDI dan BPS sama-sama memiliki data tahunan pada "
            f"tahun {row['tahun_irisan']}, dengan "
            f"{row['jumlah_tahun_irisan']} tahun irisan dan "
            f"rata-rata selisih absolut sebesar "
            f"{row['rata_rata_selisih_absolut']:.3f}."
        )

    kandidat.append({
        "seri_utama": "SI.POV.NAHC",
        "seri_pembanding": "BPS_var192",
        "rincian_utama": "Total",
        "rincian_pembanding": "Jumlah",
        "cakupan_wilayah": "Nasional Indonesia",
        "status": status,
        "alasan_keterbandingan": (
            "Keduanya memiliki cakupan nasional dan rincian "
            "total penduduk. Keduanya menggunakan satuan "
            "persen, tetapi definisi operasional dan "
            "metode pengukuran tetap perlu diverifikasi."
        ),
        "periode_bps": periode,
        "tahun_irisan": row["tahun_irisan"],
        "jumlah_tahun_irisan": row["jumlah_tahun_irisan"],
        "rata_rata_selisih_absolut": (
            row["rata_rata_selisih_absolut"]
        ),
        "dasar_pemilihan_periode": dasar
    })


# Kandidat yang tidak sebanding
kandidat_lain = [
    {
        "rincian": "Perkotaan",
        "alasan": (
            "BPS hanya mencakup penduduk perkotaan, "
            "sedangkan WDI SI.POV.NAHC yang digunakan "
            "memiliki rincian total nasional."
        )
    },
    {
        "rincian": "Perdesaan",
        "alasan": (
            "BPS hanya mencakup penduduk perdesaan, "
            "sedangkan WDI SI.POV.NAHC yang digunakan "
            "memiliki rincian total nasional."
        )
    },
    {
        "rincian": "Provinsi",
        "alasan": (
            "Cakupan data BPS berada pada tingkat provinsi, "
            "sedangkan seri WDI yang digunakan berada "
            "pada tingkat nasional."
        )
    },
    {
        "rincian": "Desa tertinggal",
        "alasan": (
            "Data merupakan hitungan desa, bukan persentase "
            "penduduk di bawah garis kemiskinan."
        )
    }
]

for item in kandidat_lain:

    kandidat.append({
        "seri_utama": "SI.POV.NAHC",
        "seri_pembanding": "BPS_var192",
        "rincian_utama": "Total",
        "rincian_pembanding": item["rincian"],
        "cakupan_wilayah": "Berbeda atau tidak sesuai",
        "status": "Tidak sebanding",
        "alasan_keterbandingan": item["alasan"],
        "periode_bps": "-",
        "tahun_irisan": "-",
        "jumlah_tahun_irisan": 0,
        "rata_rata_selisih_absolut": None,
        "dasar_pemilihan_periode": (
            "Tidak dipilih karena rincian atau cakupan "
            "tidak sesuai dengan WDI Total."
        )
    })

# ==========================================
# 6. MENYIMPAN HASIL
# ==========================================

hasil = pd.DataFrame(kandidat)

hasil.to_csv(
    OUTPUT,
    index=False
)

print("TABEL KANDIDAT BERHASIL DIPERBARUI")
print(hasil.to_string(index=False))

print("\nLokasi penyimpanan:")
print(OUTPUT)
