"""Kartu #10 — Tabel nasional dan daftar pasangan rekonsiliasi (Tahap 3 - Gold)."""

from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
WILAYAH_INDONESIA = 9999
SERI_PROYEKSI = {"var2190", "var2191"}
SERI_AKTIF = ["var192", "var2190", "var2191", "SI.POV.NAHC"]

PASANGAN = [
    {
        "id": "P1",
        "seri_kiri": "var192",
        "seri_kanan": "SI.POV.NAHC",
        "jenis": "selisih",
        "semester": "S1",
        "perlakuan": "selisih pembulatan WDI (K-014)",
    },
    {
        "id": "P2",
        "seri_kiri": "var2191",
        "seri_kanan": "var2190",
        "jenis": "konteks",
        "semester": "-",
        "perlakuan": "konteks, tanpa Indonesia (K-013)",
    },
]


def tabel_nasional(silver):
    """Matriks periode x seri untuk baris Indonesia (9999) dengan rincian total/jumlah."""
    rincian_norm = silver["rincian"].fillna("").astype(str).str.strip().str.lower()
    s = silver[
        (pd.to_numeric(silver["wilayah_kode"], errors="coerce") == WILAYAH_INDONESIA)
        & (rincian_norm.isin(["total", "jumlah"]))
        & (silver["seri_kode"].isin(SERI_AKTIF))
    ]
    t = s.pivot_table(
        index="periode", columns="seri_kode", values="nilai", aggfunc="first"
    ).sort_index()
    out_csv = ROOT / "reports/tabel-nasional.csv"
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    t.to_csv(out_csv, encoding="utf-8")
    return t


def irisan(silver, semester_utama="S1"):
    """Menyaring seri non-proyeksi dan mengambil semester utama (S1) tanpa merata-ratakan S1 & S2 (K-006)."""
    s = silver[~silver["seri_kode"].isin(SERI_PROYEKSI)].copy()
    if semester_utama:
        s = s[
            (s["jenis_periode"] == "tahun")
            | (
                (s["jenis_periode"] == "semester")
                & (s["periode"].astype(str).str.endswith(semester_utama))
            )
        ]
    s["tahun_irisan"] = s["periode"].astype(str).str.slice(0, 4)
    return s


def jalankan(silver):
    nas = tabel_nasional(silver)
    s_p1 = irisan(silver, semester_utama="S1")
    s_all = silver.copy()
    s_all["tahun_irisan"] = s_all["periode"].astype(str).str.slice(0, 4)

    hasil = []
    for pas in PASANGAN:
        sumber_df = s_all if pas["jenis"] == "konteks" else s_p1
        a = sumber_df[sumber_df["seri_kode"] == pas["seri_kiri"]]
        b = sumber_df[sumber_df["seri_kode"] == pas["seri_kanan"]]
        years = sorted(set(a["tahun_irisan"]) & set(b["tahun_irisan"]))
        hasil.append({
            "id": pas["id"],
            "kiri": pas["seri_kiri"],
            "kanan": pas["seri_kanan"],
            "jenis": pas["jenis"],
            "tahun": ", ".join(years),
            "jumlah_tahun": len(years),
            "semester": pas.get("semester", "-"),
            "perlakuan": pas["perlakuan"],
        })

    df_hasil = pd.DataFrame(hasil)

    baris_md = [
        "# Pasangan rekonsiliasi",
        "",
        "Dihasilkan `python pipeline.py` (`src/gold/nasional.py`).",
        "",
        "| id | kiri | kanan | jenis | tahun | jumlah_tahun | semester | perlakuan |",
        "|---|---|---|---|---|---:|---|---|",
    ]
    for _, r in df_hasil.iterrows():
        baris_md.append(
            f"| {r['id']} | {r['kiri']} | {r['kanan']} | {r['jenis']} | "
            f"{r['tahun']} | {r['jumlah_tahun']} | {r['semester']} | {r['perlakuan']} |"
        )
    baris_md.extend([
        "",
        "Selisih numerik belum dihitung di Sprint 1.",
    ])

    out_md = ROOT / "reports/pasangan-rekonsiliasi.md"
    out_md.write_text("\n".join(baris_md) + "\n", encoding="utf-8")

    return nas, df_hasil
