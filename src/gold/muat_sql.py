"""Kartu #11 — Memuat tabel seri dan silver ke data/gold/gudang.duckdb."""

import json
from pathlib import Path
import duckdb
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DB = ROOT / "data/gold/gudang.duckdb"
SQL = ROOT / "src/gold/silver.sql"

KOLOM_SERI = [
    "seri_kode",
    "nama",
    "satuan",
    "sdg_kode",
    "cakupan",
    "sumber",
    "kode_sumber",
    "batas_bawah",
    "batas_atas",
    "rujukan_tahun",
    "catatan",
]

KOLOM_GOLD = [
    "sumber",
    "seri_kode",
    "wilayah_kode",
    "nama_wilayah",
    "periode",
    "jenis_periode",
    "rincian",
    "nilai",
    "satuan",
    "sdg_kode",
    "batas_bawah",
    "batas_atas",
    "rujukan_tahun",
    "_berkas_raw",
    "_sha256_raw",
]


def _siapkan_tabel_seri(seri_raw: pd.DataFrame) -> pd.DataFrame:
    df = seri_raw.copy()
    df["nama"] = df["nama_seri_baku"] if "nama_seri_baku" in df.columns else df.get("nama", "")
    df["satuan"] = df["satuan_baku"] if "satuan_baku" in df.columns else df.get("satuan", "")
    df["sdg_kode"] = df["kode_sdg_baku"] if "kode_sdg_baku" in df.columns else df.get("sdg_kode", None)
    df["cakupan"] = df["sumber"].apply(lambda s: "Nasional" if str(s).upper() == "WDI" else "Provinsi")
    df["kode_sumber"] = df["seri_kode"].str.replace("^var", "", regex=True)
    df["batas_bawah"] = 0.0
    df["batas_atas"] = df["satuan"].apply(lambda u: 100.0 if str(u).lower() == "persen" else None)
    if "rujukan_tahun" not in df.columns:
        df["rujukan_tahun"] = None
    df["rujukan_tahun"] = pd.to_numeric(df["rujukan_tahun"], errors="coerce")
    df["catatan"] = df["alasan_koreksi"] if "alasan_koreksi" in df.columns else df.get("catatan", None)
    return df[KOLOM_SERI]


def _siapkan_tabel_silver(silver_raw: pd.DataFrame, tabel_seri: pd.DataFrame) -> pd.DataFrame:
    d = silver_raw.copy()
    wk = pd.to_numeric(d["wilayah_kode"], errors="coerce").astype("Int64")
    d["wilayah_kode"] = wk.apply(
        lambda x: int(x // 100) if pd.notna(x) and x >= 10000 else int(x)
    )
    d["jenis_periode"] = d["jenis_periode"].replace({"tahunan": "tahun"})

    meta_map = tabel_seri.set_index("seri_kode")[["sdg_kode", "batas_bawah", "batas_atas", "rujukan_tahun"]]
    for kol in ["sdg_kode", "batas_bawah", "batas_atas", "rujukan_tahun"]:
        if kol not in d.columns:
            d[kol] = d["seri_kode"].map(meta_map[kol])

    return d[KOLOM_GOLD]


def jalankan():
    DB.parent.mkdir(parents=True, exist_ok=True)
    DB.unlink(missing_ok=True)

    con = duckdb.connect(str(DB))
    try:
        con.execute(SQL.read_text(encoding="utf-8"))

        seri_raw = pd.read_csv(ROOT / "docs/seri.csv", dtype=str).fillna("")
        tabel_seri = _siapkan_tabel_seri(seri_raw)

        silver_raw = pd.read_parquet(ROOT / "data/silver/silver.parquet")
        tabel_silver = _siapkan_tabel_silver(silver_raw, tabel_seri)

        con.register("seri_df", tabel_seri)
        con.register("silver_df", tabel_silver)
        con.execute("INSERT INTO seri SELECT * FROM seri_df")
        con.execute("INSERT INTO silver SELECT * FROM silver_df")

        jumlah = int(con.execute("SELECT count(*) FROM silver").fetchone()[0])
        assert jumlah == len(silver_raw), f"Jumlah baris DuckDB ({jumlah}) != Parquet ({len(silver_raw)})"
    finally:
        con.close()

    angka_path = ROOT / "reports/angka.json"
    angka_path.parent.mkdir(parents=True, exist_ok=True)
    angka = {}
    if angka_path.exists():
        try:
            angka = json.loads(angka_path.read_text(encoding="utf-8"))
        except Exception:
            angka = {}
    angka["baris_sql"] = jumlah
    angka_path.write_text(json.dumps(angka, indent=2) + "\n", encoding="utf-8")

    print(f"Database DuckDB berhasil dibuat: {DB} ({jumlah} baris)")
    return jumlah
