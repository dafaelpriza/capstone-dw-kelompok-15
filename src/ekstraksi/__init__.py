"""Tahap 1 — Ekstraksi data mentah BPS (JSON/CSV) dan WDI (JSON)."""

from fnmatch import fnmatch
import json
from pathlib import Path
import time
import pandas as pd

from src.common.manifest import RAW, baca as baca_manifest, sha256_raw
from src.ekstraksi import bps, wdi

ROOT = Path(__file__).resolve().parents[2]

POLA = [
    ("bps/*/json/*.json", "bps_json", "Observasi"),
    ("bps/*/manifest_asal.json", "bps_manifest_asal", "Metadata / Catatan"),
    ("bps/*/*.csv", "bps_csv", "Observasi"),
    ("wdi/*/data/*.json", "wdi_si_pov_nahc", "Observasi"),
    ("wdi/*/metadata/sumber.json", "wdi_sumber", "Metadata / Catatan"),
    ("wdi/*/metadata/*_indikator.json", "wdi_meta", "Metadata / Catatan"),
]


def _selaraskan_bps_json(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    out = df.copy()
    out["sumber"] = "BPS"
    out["seri_kode"] = "var" + out["var_id"].astype(str)
    out["vervar_kode"] = out["wilayah_id"]
    out["nama_wilayah"] = out["wilayah"]
    out["rincian"] = out["turvar"]
    out["tahun_label"] = out["tahun"]
    out["turtahun_label"] = out["turtahun"]
    return out


def _selaraskan_wdi_data(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    out = df.copy()
    out["sumber"] = "WDI"
    out["seri_kode"] = out["indicator_id"]
    out["nama_wilayah"] = "Indonesia"
    out["periode"] = out["date"]
    out["nilai"] = out["value"]
    return out


def jalankan():
    mulai = time.perf_counter()
    kumpul = {nama: [] for _, nama, _ in POLA}
    if hasattr(bps, "tak_terbaca"):
        bps.tak_terbaca.clear()
    hitung = []
    manifest_asal_raw = []
    wdi_metadata_raw = {}

    manifest_list = list(baca_manifest())
    for item in manifest_list:
        berkas = item["berkas"] if isinstance(item, dict) else item
        cocok = next(
            ((nama, jenis) for pola, nama, jenis in POLA if fnmatch(berkas, pola)),
            None,
        )
        if cocok is None:
            continue
        nama, jenis = cocok
        if nama == "bps_json":
            df, meta = bps.baca_json(berkas)
            df = _selaraskan_bps_json(df)
            kumpul.setdefault("bps_meta", []).append(meta)
        elif nama == "bps_csv":
            df = bps.baca_csv(berkas)
        elif nama == "bps_manifest_asal":
            df = bps.baca_manifest_asal(berkas)
            isi_raw = json.loads((RAW / berkas).read_text(encoding="utf-8"))
            manifest_asal_raw.extend(isi_raw if isinstance(isi_raw, list) else [isi_raw])
        elif nama == "wdi_si_pov_nahc":
            df, _ = wdi.baca_data(berkas, ["SI.POV.NAHC"])
            df = _selaraskan_wdi_data(df)
        else:
            df = wdi.baca_metadata(berkas, ["SI.POV.NAHC"])
            wdi_metadata_raw[berkas] = json.loads((RAW / berkas).read_text(encoding="utf-8"))

        kumpul.setdefault(nama, []).append(df)
        sha = sha256_raw(berkas)[:8]
        hitung.append({
            "berkas": berkas,
            "pembaca": nama,
            "jenis": jenis,
            "baris": len(df),
            "sha8": sha,
        })

    hasil = {
        nama: pd.concat(daftar, ignore_index=True)
        for nama, daftar in kumpul.items()
        if daftar and nama != "bps_manifest_asal"
    }
    hasil["bps_manifest_asal"] = manifest_asal_raw
    hasil["wdi_metadata"] = wdi_metadata_raw

    t = pd.DataFrame(hitung)
    hasil["_hitung"] = t
    durasi = time.perf_counter() - mulai

    obs = t[t["jenis"] == "Observasi"]
    n_json = int(obs[obs["pembaca"] == "bps_json"]["baris"].sum())
    n_csv = int(obs[obs["pembaca"] == "bps_csv"]["baris"].sum())
    n_wdi = int(obs[obs["pembaca"] == "wdi_si_pov_nahc"]["baris"].sum())

    baris_md = [
        "# Laporan Ekstraksi — Kasus 15 (Kemiskinan dan Daerah Tertinggal)",
        "",
        f"- **Berkas di MANIFEST / dibaca:** {len(t)} / {len(manifest_list)} berkas (0 terlewat)",
        f"- **Total baris observasi mentah (BPS JSON + BPS CSV + WDI):** {n_json + n_csv + n_wdi:,} baris",
        f"- **Rincian baris observasi:** BPS JSON = {n_json:,}, BPS CSV = {n_csv:,}, WDI (`SI.POV.NAHC`) = {n_wdi:,}",
        f"- **Durasi ekstraksi:** {durasi:.2f} detik",
        "",
        "## Jumlah Baris per Berkas",
        "",
        "| Berkas (`data/raw/`) | Jenis | Jumlah Baris / Entri | SHA-256 (8 karakter awal) |",
        "|---|---|---:|---|",
    ]
    for _, r in t.iterrows():
        baris_md.append(
            f"| `{r['berkas']}` | {r['jenis']} | {r['baris']:,} | `{r['sha8']}` |"
        )

    out_md = ROOT / "reports/ekstraksi.md"
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text("\n".join(baris_md) + "\n", encoding="utf-8")
    return hasil
