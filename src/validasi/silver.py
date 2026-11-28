"""Validasi kualitas data pada tahap Silver."""

import pandas as pd
import re

from src.konfigurasi import KATALOG_SERI


def validasi_rentang(df):
    """Memeriksa rentang nilai indikator."""
    hasil = []

    if "seri_kode" not in df.columns or "nilai" not in df.columns:
        return [{"aturan": "rentang_nilai", "lolos": False,
                 "keterangan": "Kolom seri_kode atau nilai tidak tersedia."}]

    data = df.copy()
    data["nilai"] = pd.to_numeric(data["nilai"], errors="coerce")

    for seri in data["seri_kode"].dropna().unique():
        subset = data[data["seri_kode"] == seri]
        nilai = subset["nilai"].dropna()

        if seri in ["var192", "SI.POV.NAHC"]:
            lolos = not nilai.empty and nilai.between(0, 100).all()
        elif seri in ["var2190", "var2191"]:
            lolos = not nilai.empty and (nilai >= 0).all()
        else:
            continue

        hasil.append({
            "aturan": f"rentang_{seri}",
            "lolos": bool(lolos),
            "keterangan": f"{seri}: {len(nilai)} nilai diperiksa."
        })

    return hasil


def validasi_keunikan(df):
    """Memeriksa duplikasi berdasarkan kunci Silver."""
    kunci = [
        "sumber", "seri_kode", "wilayah_kode",
        "periode", "rincian", "_berkas_raw"
    ]

    if not set(kunci).issubset(df.columns):
        return [{
            "aturan": "keunikan_kunci",
            "lolos": False,
            "keterangan": "Kolom kunci Silver belum lengkap."
        }]

    duplikat = df.duplicated(subset=kunci, keep=False)

    return [{
        "aturan": "keunikan_kunci",
        "lolos": not duplikat.any(),
        "keterangan": f"Ditemukan {int(duplikat.sum())} baris duplikat."
    }]


def validasi_satuan(df):
    """Memeriksa kesesuaian satuan dengan katalog seri."""
    if not {"seri_kode", "satuan"}.issubset(df.columns):
        return [{
            "aturan": "konsistensi_satuan",
            "lolos": False,
            "keterangan": "Kolom seri_kode atau satuan tidak tersedia."
        }]

    data = df.copy()
    data["satuan_harapan"] = data["seri_kode"].map(
        {k: v["satuan"] for k, v in KATALOG_SERI.items()}
    )

    diperiksa = data.dropna(subset=["satuan_harapan"])

    salah = diperiksa[
        diperiksa["satuan"] != diperiksa["satuan_harapan"]
    ]

    return [{
        "aturan": "konsistensi_satuan",
        "lolos": not salah.any(axis=1).any(),
        "keterangan": f"Ditemukan {len(salah)} satuan tidak sesuai."
    }]


def validasi_periode(df):
    """Memeriksa kesesuaian format periode."""
    if not {"periode", "jenis_periode"}.issubset(df.columns):
        return [{
            "aturan": "konsistensi_periode",
            "lolos": False,
            "keterangan": "Kolom periode atau jenis_periode tidak tersedia."
        }]

    pola = {
        "tahun": r"\d{4}",
        "semester": r"\d{4}-S[12]",
        "triwulan": r"\d{4}-Q[1-4]",
        "bulan": r"\d{4}-(0[1-9]|1[0-2])"
    }

    salah = []

    for _, baris in df.iterrows():
        jenis = str(baris["jenis_periode"])
        periode = str(baris["periode"])

        if jenis not in pola or not re.fullmatch(pola[jenis], periode):
            salah.append(periode)

    return [{
        "aturan": "konsistensi_periode",
        "lolos": len(salah) == 0,
        "keterangan": f"Ditemukan {len(salah)} periode yang tidak sesuai."
    }]


def validasi_rincian_desa(df):
    """Membandingkan jumlah rincian desa dengan nilai total."""
    wajib = {"seri_kode", "rincian", "nilai", "wilayah_kode", "periode"}

    if not wajib.issubset(df.columns):
        return [{
            "aturan": "penjumlahan_rincian_desa",
            "lolos": False,
            "keterangan": "Kolom untuk pemeriksaan rincian desa belum lengkap."
        }]

    data = df[df["seri_kode"] == "var2191"].copy()

    if data.empty:
        return [{
            "aturan": "penjumlahan_rincian_desa",
            "lolos": True,
            "keterangan": "Tidak ada data var2191 untuk diperiksa."
        }]

    data["nilai"] = pd.to_numeric(data["nilai"], errors="coerce")
    data["rincian_normal"] = data["rincian"].astype(str).str.strip().str.lower()

    # Jika Silver memuat beberapa snapshot, jumlah rincian dibandingkan
    # di dalam berkas yang sama agar total dari snapshot berbeda tidak tercampur.
    kunci = ["wilayah_kode", "periode"]
    if "_berkas_raw" in data.columns:
        kunci.append("_berkas_raw")

    diperiksa = 0
    selisih = []

    for identitas, grup in data.groupby(kunci, dropna=False):
        total = grup.loc[
            grup["rincian_normal"].isin(["jumlah", "total"]), "nilai"
        ]

        detail = grup.loc[
            ~grup["rincian_normal"].isin(["jumlah", "total"]), "nilai"
        ].dropna()

        if not total.empty and not detail.empty:
            diperiksa += 1
            jumlah_detail = detail.sum()

            if abs(jumlah_detail - total.iloc[0]) >= 1e-9:
                selisih.append(identitas)

    return [{
        "aturan": "penjumlahan_rincian_desa",
        "lolos": len(selisih) == 0,
        "keterangan": (
            f"{diperiksa} kelompok dapat dibandingkan; "
            f"ditemukan {len(selisih)} kelompok dengan selisih."
        )
    }]


def jalankan(df_silver):
    """Menjalankan seluruh aturan validasi Silver."""
    aturan = []

    aturan.extend(validasi_rentang(df_silver))
    aturan.extend(validasi_keunikan(df_silver))
    aturan.extend(validasi_satuan(df_silver))
    aturan.extend(validasi_periode(df_silver))
    aturan.extend(validasi_rincian_desa(df_silver))

    return aturan
