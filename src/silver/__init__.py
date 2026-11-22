"""Tahap 2–4 — Profil, pembersihan, dan penyeragaman ke Silver (pertemuan II–VII). Milik tim.

Keluaran: data/silver/silver.parquet dengan skema minimal di src/common/skema.py.
Satu baris = satu seri x wilayah x periode x rincian x berkas sumber. Nilai dari sumber berbeda
TIDAK digabung di sini. Setiap keputusan pembersihan dicatat di log-keputusan.csv.
"""
from pathlib import Path
import pandas as pd

from src.common.manifest import baca as baca_manifest
from src.common.skema import KOLOM, KUNCI, periksa_silver


def _normalisasi_wilayah(wilayah_id, nama_wilayah):
    nama_str = str(nama_wilayah).strip()
    if nama_str.upper() in {"INDONESIA", "NASIONAL"} or str(wilayah_id) in {"0", "9999", "999900"}:
        return 9999, "Indonesia"
    try:
        kode_num = int(float(wilayah_id))
    except (ValueError, TypeError):
        kode_num = 0
    if kode_num >= 10000:
        kode_38 = kode_num
    elif kode_num >= 100:
        kode_38 = kode_num * 100
    else:
        kode_38 = kode_num * 10000
    return int(kode_38), nama_str.title()


def jalankan(mentah=None):
    """Terima keluaran tahap 1, tulis dan kembalikan DataFrame Silver."""
    manifest = baca_manifest()
    baris_list = []

    for berkas_rel, sha256_val in manifest.items():
        jalur = Path("data/raw") / berkas_rel
        if not jalur.exists():
            jalur = Path(berkas_rel)
        if not jalur.exists() or jalur.suffix.lower() != ".csv":
            continue

        raw_df = pd.read_csv(jalur)
        seri_kode = str(raw_df["var_id"].iloc[0]) if "var_id" in raw_df.columns and not raw_df.empty else jalur.stem

        for _, r in raw_df.iterrows():
            nilai_num = pd.to_numeric(r.get("nilai"), errors="coerce")
            if pd.isna(nilai_num):
                continue

            kode_wil, nama_wil = _normalisasi_wilayah(r.get("wilayah_id"), r.get("wilayah", ""))
            tahun_str = str(int(float(r["tahun"]))) if pd.notna(r.get("tahun")) else ""
            periode_raw = str(r.get("periode", "")).strip()

            if "semester 1" in periode_raw.lower() or periode_raw.endswith("-S1"):
                periode_baku = f"{tahun_str}-S1"
                jenis_periode = "semester"
            elif "semester 2" in periode_raw.lower() or periode_raw.endswith("-S2"):
                periode_baku = f"{tahun_str}-S2"
                jenis_periode = "semester"
            else:
                periode_baku = tahun_str
                jenis_periode = "tahun"

            rincian_val = str(r.get("turvar", "Tidak ada")).strip() or "Tidak ada"
            satuan_val = str(r.get("satuan", "")).strip() or "unit"

            baris_list.append({
                "sumber": "bps",
                "seri_kode": seri_kode,
                "wilayah_kode": int(kode_wil),
                "nama_wilayah": nama_wil,
                "periode": periode_baku,
                "jenis_periode": jenis_periode,
                "rincian": rincian_val,
                "nilai": float(nilai_num),
                "satuan": satuan_val,
                "_berkas_raw": berkas_rel,
                "_sha256_raw": sha256_val,
            })

    silver_df = pd.DataFrame(baris_list, columns=KOLOM)
    if not silver_df.empty:
        silver_df["wilayah_kode"] = silver_df["wilayah_kode"].astype("int64")
        silver_df["nilai"] = silver_df["nilai"].astype("float64")
        silver_df = silver_df.drop_duplicates(subset=KUNCI, keep="first").reset_index(drop=True)

    salah = periksa_silver(silver_df, manifest)
    if salah:
        raise ValueError("Validasi skema Silver gagal: " + "; ".join(salah))

    out_path = Path("data/silver/silver.parquet")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    silver_df.to_parquet(out_path, index=False)
    return silver_df
