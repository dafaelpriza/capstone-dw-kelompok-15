"""Tahap 1 — Ekstraksi (pertemuan X). Milik tim.

Baca setiap berkas di data/raw/ (CSV, JSON WebAPI BPS, XLSX BNPB, SDMX ILO, JSON WDI) menjadi
DataFrame mentah yang setia pada sumbernya: jangan membersihkan di sini, cukup ratakan struktur
dan catat asal tiap baris (`_berkas_raw` relatif data/raw/, `_sha256_raw` dari src.common.manifest).
"""


"""def jalankan():
        Kembalikan {nama_sumber: DataFrame mentah}.
    raise NotImplementedError("Tahap 1: tulis pembaca untuk tiap format di data/raw/")"""


"""Tahap 1 — Ekstraksi. Milik tim."""

from src.ekstraksi import wdi

"""def jalankan():
   #Mengembalikan kamus data DataFrame mentah.
    # Memanggil modul pembaca wdi yang sudah dibuat
    hasil_wdi = wdi.jalankan()
    
    return hasil_wdi"""

"""Tahap 1 — Ekstraksi. Milik tim."""

from src.ekstraksi import wdi, bps

"""Tahap 1 — Ekstraksi. Milik tim.

Baca setiap berkas di data/raw/ menjadi DataFrame mentah yang setia pada sumbernya:
jangan membersihkan di sini, cukup ratakan struktur dan catat asal tiap baris
(`_berkas_raw` relatif data/raw/, `_sha256_raw` dari src.common.manifest).
"""
import time
from pathlib import Path
import pandas as pd

from src.common.hasil import tulis_hasil
from src.common.manifest import baca as baca_manifest
from src.ekstraksi import bps, wdi


def _tulis_laporan_ekstraksi(hasil: dict, manifest: dict, durasi: float) -> None:
    """Menulis ringkasan jumlah baris per berkas ke reports/ekstraksi.md."""
    baris_per_berkas = {}

    for df in [hasil.get("bps_json"), hasil.get("bps_csv"), hasil.get("wdi_si_pov_nahc")]:
        if isinstance(df, pd.DataFrame) and not df.empty and "_berkas_raw" in df.columns:
            for berkas, cnt in df["_berkas_raw"].value_counts().items():
                baris_per_berkas[berkas] = baris_per_berkas.get(berkas, 0) + int(cnt)

    # Catat juga berkas non-observasi (catatan unduhan & metadata JSON) yang ikut dibaca
    if hasil.get("bps_manifest_asal"):
        baris_per_berkas["bps/2026-10-20/manifest_asal.json"] = len(hasil["bps_manifest_asal"])
    for meta_path, meta_obj in hasil.get("wdi_metadata", {}).items():
        jml = len(meta_obj[1]) if isinstance(meta_obj, list) and len(meta_obj) > 1 and isinstance(meta_obj[1], list) else len(meta_obj)
        baris_per_berkas[meta_path] = jml

    terlewat = sorted(set(manifest.keys()) - set(baris_per_berkas.keys()))
    assert not terlewat, f"Ada berkas MANIFEST yang terlewat saat ekstraksi: {terlewat}"

    total_baris_data = (
        len(hasil["bps_json"])
        + len(hasil["bps_csv"])
        + len(hasil["wdi_si_pov_nahc"])
    )

    lines = [
        "# Laporan Ekstraksi — Kasus 15 (Kemiskinan dan Daerah Tertinggal)",
        "",
        f"- **Berkas di MANIFEST / dibaca:** {len(baris_per_berkas)} / {len(manifest)} berkas (0 terlewat)",
        f"- **Total baris observasi mentah (BPS JSON + BPS CSV + WDI):** {total_baris_data:,} baris",
        f"- **Rincian baris observasi:** BPS JSON = {len(hasil['bps_json']):,}, BPS CSV = {len(hasil['bps_csv']):,}, WDI (`SI.POV.NAHC`) = {len(hasil['wdi_si_pov_nahc']):,}",
        f"- **Durasi ekstraksi:** {durasi:.2f} detik",
        "",
        "## Jumlah Baris per Berkas",
        "",
        "| Berkas (`data/raw/`) | Jenis | Jumlah Baris / Entri | SHA-256 (8 karakter awal) |",
        "|---|---|---:|---|",
    ]

    for berkas in sorted(manifest.keys()):
        jenis = "Observasi" if any(berkas.endswith(ext) for ext in (".csv", ".json")) and "metadata" not in berkas and "manifest_asal" not in berkas else "Metadata / Catatan"
        lines.append(f"| `{berkas}` | {jenis} | {baris_per_berkas.get(berkas, 0):,} | `{manifest[berkas][:8]}` |")

    out_path = Path("reports/ekstraksi.md")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def jalankan() -> dict:
    """Mengembalikan kamus data DataFrame mentah dari semua sumber dan memverifikasi MANIFEST."""
    mulai = time.time()
    manifest = baca_manifest()

    hasil = {}
    hasil.update(wdi.jalankan())
    hasil.update(bps.jalankan())

    durasi = time.time() - mulai
    _tulis_laporan_ekstraksi(hasil, manifest, durasi)

    # Catat metrik komponen Ekstraksi & Lineage untuk NIM 124450131
    total_baris_data = len(hasil["bps_json"]) + len(hasil["bps_csv"]) + len(hasil["wdi_si_pov_nahc"])
    tulis_hasil(
        "124450131",
        {
            "berkas_manifest": len(manifest),
            "berkas_dibaca": len(manifest),
            "baris_bps_json": len(hasil["bps_json"]),
            "baris_bps_csv": len(hasil["bps_csv"]),
            "baris_wdi": len(hasil["wdi_si_pov_nahc"]),
            "baris_mentah_total": total_baris_data,
        },
        seed=0,
        durasi_detik=durasi,
    )

    return hasil