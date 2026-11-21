
"""Tahap 8 — Validasi dan dokumentasi Silver dan Gold."""

from pathlib import Path
import pandas as pd

from src.validasi import silver as validasi_silver


def validasi_gold(gold):
    """Memeriksa kualitas tabel Gold."""

    hasil = []

    if not isinstance(gold, dict):
        return [{
            "tahap": "Gold",
            "aturan": "struktur_gold",
            "lolos": False,
            "keterangan": "Keluaran Gold harus berupa dictionary."
        }]

    # Memeriksa ketersediaan tabel panel.
    panel = gold.get("panel_provinsi")

    if not isinstance(panel, pd.DataFrame):
        hasil.append({
            "tahap": "Gold",
            "aturan": "kelengkapan_panel",
            "lolos": False,
            "keterangan": "Tabel panel_provinsi tidak tersedia."
        })
    else:
        kunci = [
            "wilayah_kode", "nama_wilayah",
            "periode", "jenis_periode"
        ]

        lengkap = set(kunci).issubset(panel.columns)

        hasil.append({
            "tahap": "Gold",
            "aturan": "kelengkapan_panel",
            "lolos": lengkap,
            "keterangan": (
                f"Panel memiliki {len(panel)} baris dan "
                f"{len(panel.columns)} kolom."
                if lengkap else "Kolom utama panel belum lengkap."
            )
        })

        if lengkap:
            duplikat = panel.duplicated(
                subset=kunci, keep=False
            )

            hasil.append({
                "tahap": "Gold",
                "aturan": "keunikan_panel",
                "lolos": not duplikat.any(),
                "keterangan": (
                    f"Ditemukan {int(duplikat.sum())} "
                    "baris dengan kunci wilayah dan periode berulang."
                )
            })

        kolom_indikator = [
            kolom for kolom in panel.columns
            if "__" in kolom
        ]

        if kolom_indikator:
            numerik = panel[kolom_indikator].apply(
                pd.to_numeric, errors="coerce"
            )

            valid = (
                panel[kolom_indikator].isna()
                | numerik.notna()
            ).all().all()

            hasil.append({
                "tahap": "Gold",
                "aturan": "nilai_panel",
                "lolos": bool(valid),
                "keterangan": (
                    f"{len(kolom_indikator)} kolom indikator "
                    "diperiksa."
                )
            })

    # Memeriksa tabel rekonsiliasi.
    rekonsiliasi = gold.get("rekonsiliasi_nasional")

    if not isinstance(rekonsiliasi, pd.DataFrame):
        hasil.append({
            "tahap": "Gold",
            "aturan": "kelengkapan_rekonsiliasi",
            "lolos": False,
            "keterangan": "Tabel rekonsiliasi nasional tidak tersedia."
        })
    else:
        wajib = {
            "periode", "nilai_bps", "nilai_wdi",
            "selisih", "status"
        }

        lengkap = wajib.issubset(rekonsiliasi.columns)

        hasil.append({
            "tahap": "Gold",
            "aturan": "kelengkapan_rekonsiliasi",
            "lolos": lengkap,
            "keterangan": (
                f"Tabel rekonsiliasi memiliki "
                f"{len(rekonsiliasi)} baris."
                if lengkap else "Kolom rekonsiliasi belum lengkap."
            )
        })

        if lengkap:
            tersedia = (
                rekonsiliasi["nilai_bps"].notna()
                & rekonsiliasi["nilai_wdi"].notna()
            )

            selisih_harapan = (
                rekonsiliasi.loc[tersedia, "nilai_bps"]
                - rekonsiliasi.loc[tersedia, "nilai_wdi"]
            )

            selisih_sesuai = (
                selisih_harapan
                - rekonsiliasi.loc[tersedia, "selisih"]
            ).abs().lt(1e-9).all()

            hasil.append({
                "tahap": "Gold",
                "aturan": "konsistensi_selisih",
                "lolos": bool(selisih_sesuai),
                "keterangan": (
                    f"{int(tersedia.sum())} pasangan nilai "
                    "BPS dan WDI diperiksa."
                )
            })

    return hasil


def jalankan(silver, gold):
    """Menjalankan validasi Silver dan Gold serta membuat laporan."""

    hasil_silver = validasi_silver.jalankan(silver)
    hasil_gold = validasi_gold(gold)

    semua_hasil = (
        [{"tahap": "Silver", **item} for item in hasil_silver]
        + hasil_gold
    )

    jumlah_lolos = sum(
        bool(item["lolos"]) for item in semua_hasil
    )
    jumlah_gagal = len(semua_hasil) - jumlah_lolos

    # Menyiapkan folder laporan.
    Path("reports").mkdir(parents=True, exist_ok=True)

    laporan = [
        "# Laporan Validasi Data",
        "",
        "## Ringkasan",
        "",
        f"- Jumlah aturan: {len(semua_hasil)}",
        f"- Aturan lolos: {jumlah_lolos}",
        f"- Aturan gagal: {jumlah_gagal}",
        "",
        "## Hasil Pemeriksaan",
        "",
        "| Tahap | Aturan | Status | Keterangan |",
        "|---|---|---|---|"
    ]

    for item in semua_hasil:
        status = "LOLOS" if item["lolos"] else "GAGAL"
        keterangan = str(item["keterangan"]).replace("|", "/")

        laporan.append(
            f"| {item['tahap']} | {item['aturan']} "
            f"| {status} | {keterangan} |"
        )

    with open(
        "reports/validasi.md", "w", encoding="utf-8"
    ) as file:
        file.write("\n".join(laporan))

    print("\n=== HASIL VALIDASI ===")
    print(f"Jumlah aturan : {len(semua_hasil)}")
    print(f"Aturan lolos  : {jumlah_lolos}")
    print(f"Aturan gagal  : {jumlah_gagal}")
    print("Laporan       : reports/validasi.md")

    # Mencatat metrik Validasi untuk NIM 124450123
    from src.common.hasil import tulis_hasil

    tulis_hasil(
        "124450123",
        {
            "aturan_validasi": len(semua_hasil),
            "aturan_lolos": jumlah_lolos,
            "aturan_gagal": jumlah_gagal
        },
        seed=0
    )
    
    return semua_hasil

