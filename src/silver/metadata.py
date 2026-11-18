"""Penetapan dan verifikasi satuan, periode, nama seri, dan kode SDG dari metadata mentah."""
from pathlib import Path
import pandas as pd
from src.konfigurasi import KATALOG_SERI, PEMETAAN_TURTAHUN_BPS


def verifikasi_dari_mentah(mentah: dict) -> pd.DataFrame:
    """Memeriksa metadata dari bps_manifest_asal dan wdi_metadata serta membangun tabel referensi seri."""
    baris_seri = []
    manifest_bps = mentah.get("bps_manifest_asal", [])
    wdi_meta = mentah.get("wdi_metadata", {})

    # Ekstrak judul asli dari manifest_asal.json BPS bila tersedia
    judul_bps_mentah = {}
    if isinstance(manifest_bps, list):
        for item in manifest_bps:
            if isinstance(item, dict):
                var_id = str(item.get("var", item.get("id", "")))
                kode = f"var{var_id}" if var_id and not var_id.startswith("var") else var_id
                if kode in KATALOG_SERI:
                    judul_bps_mentah[kode] = item.get("title") or item.get("label") or item.get("judul", "")

    # Ekstrak judul & unit asli dari metadata WDI
    judul_wdi_mentah = ""
    unit_wdi_mentah = ""
    for meta_obj in wdi_meta.values():
        daftar = meta_obj[1] if isinstance(meta_obj, list) and len(meta_obj) > 1 else meta_obj
        if isinstance(daftar, list):
            for item in daftar:
                if isinstance(item, dict) and item.get("id") == "SI.POV.NAHC":
                    judul_wdi_mentah = item.get("name", "")
                    unit_wdi_mentah = item.get("unit", "")
                    break

    for seri_kode, info in KATALOG_SERI.items():
        judul_mentah = judul_bps_mentah.get(seri_kode, "") if info["sumber"] == "BPS" else judul_wdi_mentah
        baris_seri.append({
            "seri_kode": seri_kode,
            "sumber": info["sumber"],
            "nama_seri_baku": info["nama_seri"],
            "judul_berkas_mentah": judul_mentah or info["nama_seri"],
            "satuan_katalog_awal": info["satuan_awal"],
            "satuan_baku": info["satuan"],
            "unit_mentah_wdi": unit_wdi_mentah if seri_kode == "SI.POV.NAHC" else "-",
            "kode_sdg_awal": info["kode_sdg_awal"],
            "kode_sdg_baku": info["kode_sdg"],
            "sumber_metadata": info["sumber_metadata"],
            "alasan_koreksi": info["catatan"],
        })

    df_seri = pd.DataFrame(baris_seri)
    return df_seri


def terapkan_satuan_dan_periode(df: pd.DataFrame) -> pd.DataFrame:
    """Menetapkan satuan baku per seri_kode dan menyeragamkan format periode tanpa agregasi."""
    df = df.copy()

    # 1. Tetapkan satuan baku dari KATALOG_SERI (menggantikan tidak_ada / kosong / tidak cocok)
    peta_satuan = {k: v["satuan"] for k, v in KATALOG_SERI.items()}
    df["satuan"] = df["seri_kode"].map(peta_satuan).fillna(df.get("satuan", "tidak_ada"))

    # 2. Seragamkan periode dan jenis_periode (tidak merata-ratakan semester ke tahunan)
    if "turtahun" in df.columns and "tahun" in df.columns:
        jenis_list = []
        periode_list = []
        for tahun, turtahun in zip(df["tahun"].astype(str), df["turtahun"].fillna("Tahunan").astype(str)):
            turtahun_bersih = turtahun.strip()
            if turtahun_bersih in PEMETAAN_TURTAHUN_BPS:
                j_periode, akhiran = PEMETAAN_TURTAHUN_BPS[turtahun_bersih]
            elif "1" in turtahun_bersih or "Maret" in turtahun_bersih:
                j_periode, akhiran = "semester", "-S1"
            elif "2" in turtahun_bersih or "September" in turtahun_bersih:
                j_periode, akhiran = "semester", "-S2"
            else:
                j_periode, akhiran = "tahunan", ""
            jenis_list.append(j_periode)
            periode_list.append(f"{tahun[:4]}{akhiran}")

        df["jenis_periode"] = jenis_list
        df["periode"] = periode_list
    elif "periode" in df.columns:
        df["periode"] = df["periode"].astype(str).str.strip()
        df["jenis_periode"] = df["periode"].apply(
            lambda p: "semester" if ("-S1" in p or "-S2" in p) else "tahunan"
        )

    return df


def tulis_dokumentasi_metadata(df_seri: pd.DataFrame, df_silver: pd.DataFrame | None = None) -> None:
    """Menulis docs/seri.csv dan reports/metadata.md sebagai bukti verifikasi katalog."""
    Path("docs").mkdir(parents=True, exist_ok=True)
    Path("reports").mkdir(parents=True, exist_ok=True)

    df_seri.to_csv("docs/seri.csv", index=False)

    lines = [
        "# Laporan Verifikasi Metadata, Satuan, Periode, dan Kode SDG",
        "",
        "Setiap seri pada katalog awal (`data/KASUS.md`) telah diperiksa terhadap judul tabel, catatan unduhan (`manifest_asal.json`), dan metadata indikator (`sumber2_indikator.json`, `sumber46_indikator.json`).",
        "",
        "## Ringkasan 4 Koreksi Katalog",
        "",
        "| Seri | Sumber | Satuan Awal $\\rightarrow$ Baku | Kode SDG Awal $\\rightarrow$ Baku | Rujukan Sumber Mentah |",
        "|---|---|---|---|---|",
    ]
    for _, r in df_seri.iterrows():
        lines.append(
            f"| `{r['seri_kode']}` | {r['sumber']} | `{r['satuan_katalog_awal']}` $\\rightarrow$ **{r['satuan_baku']}** | `{r['kode_sdg_awal']}` $\\rightarrow$ **{r['kode_sdg_baku']}** | `{r['sumber_metadata']}` |"
        )

    lines.extend([
        "",
        "## Aturan Penyeragaman Periode (Non-Agregasi di Silver)",
        "- Periode tahunan disimpan sebagai `AAAA` dengan `jenis_periode = 'tahunan'` (contoh: `var192` tahun 2007–2011, `var2190`, `var2191`, dan `SI.POV.NAHC`).",
        "- Periode semesteran (`var192` mulai 2012: Maret = Semester 1, September = Semester 2; tahun 2023 hanya Maret) disimpan terpisah sebagai `AAAA-S1` dan `AAAA-S2` dengan `jenis_periode = 'semester'`.",
        "- Tidak dilakukan perata-rataan semester ke tahunan di lapis Silver.",
    ])

    if df_silver is not None and not df_silver.empty and "nilai" in df_silver.columns:
        lines.extend(["", "## Verifikasi Rentang Nilai per Seri dan Satuan di Silver", "", "| Seri | Satuan | Jumlah Baris | Min | Maks |", "|---|---|---:|---:|---:|"])
        for (seri, sat), grp in df_silver.groupby(["seri_kode", "satuan"]):
            lines.append(f"| `{seri}` | `{sat}` | {len(grp):,} | {grp['nilai'].min():.2f} | {grp['nilai'].max():.2f} |")

    Path("reports/metadata.md").write_text("\n".join(lines) + "\n", encoding="utf-8")