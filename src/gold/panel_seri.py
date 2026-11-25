"""Pembentukan grid provinsi x periode per seri di Gold, aturan sel, dan laporan kelengkapan."""

from pathlib import Path
import pandas as pd

NAMA_NASIONAL = {"indonesia", "nasional", "indonesia (nasional)"}

# Tahun mulai terbit resmi untuk provinsi pemekaran (susunan 38 provinsi 2025, K-001).
MULAI_TERBIT_PROVINSI = {
    650000: 2015,  # Kalimantan Utara (mulai terbit 2015-S1)
    920000: 2024,  # Papua Barat Daya (mulai terbit 2024-S1)
    950000: 2024,  # Papua Selatan (mulai terbit 2024-S1)
    960000: 2024,  # Papua Tengah (mulai terbit 2024-S1)
    970000: 2024,  # Papua Pegunungan (mulai terbit 2024-S1)
}

# Periode yang ditandai sebagai patahan seri (nilai tetap dipertahankan, K-006).
ATURAN_PATAHAN = {
    ("var192", "2008"): "patahan_seri_2008_k006",
}

PETA_STATUS_VAR192 = {
    "var192__Jumlah": "status_sel_jumlah",
    "var192__Perdesaan": "status_sel_perdesaan",
    "var192__Perkotaan": "status_sel_perkotaan",
}


def _ekstrak_tahun(periode: str) -> int:
    return int(str(periode)[:4])


def _status_sel_tunggal(nilai, wilayah_kode: int, periode: str) -> str:
    """Mengklasifikasikan satu sel menjadi terisi, belum_terbit, atau kosong."""
    if pd.notna(nilai):
        return "terisi"
    mulai = MULAI_TERBIT_PROVINSI.get(int(wilayah_kode))
    if mulai is not None and _ekstrak_tahun(periode) < mulai:
        return "belum_terbit"
    return "kosong"


def _keterangan_baris(
    seri_kode: str,
    wilayah_kode: int,
    periode: str,
    status_list: list[str],
    patahan: bool,
) -> str:
    """Menyusun label keterangan sel yang ringkas dan konsisten."""
    tag = []
    if patahan:
        tag.append(ATURAN_PATAHAN[(seri_kode, str(periode))])
    if all(s == "belum_terbit" for s in status_list):
        tag.append("belum_terbit_sebelum_pemekaran_k001")
    elif any(s == "kosong" for s in status_list):
        if int(wilayah_kode) == 310000 and seri_kode == "var192":
            tag.append("kosong_perdesaan_dki_jakarta")
        elif int(wilayah_kode) == 310000 and seri_kode in {"var2190", "var2191"}:
            tag.append("kosong_dki_jakarta_non_desa")
        else:
            tag.append("kosong_tidak_tersedia")
    return "; ".join(tag) if tag else "normal"


def bangun_panel_per_seri(data: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Membentuk grid provinsi x periode terpisah untuk setiap seri BPS dengan kolom penanda."""
    nama_normal = data["nama_wilayah"].fillna("").astype(str).str.strip().str.lower()
    provinsi = data[~nama_normal.isin(NAMA_NASIONAL)].copy()

    master_wilayah = (
        provinsi[["wilayah_kode", "nama_wilayah"]]
        .drop_duplicates()
        .sort_values("wilayah_kode")
        .reset_index(drop=True)
    )

    hasil_panel = {}
    for seri_kode in ["var192", "var2190", "var2191"]:
        sub = provinsi[provinsi["seri_kode"] == seri_kode].copy()
        if sub.empty:
            continue

        sub["indikator"] = (
            sub["seri_kode"].astype(str)
            + "__"
            + sub["rincian"].str.replace(" ", "_", regex=False)
        )

        indeks = ["wilayah_kode", "nama_wilayah", "periode", "jenis_periode"]
        duplikat = sub.duplicated(subset=indeks + ["indikator"], keep=False)
        if duplikat.any():
            raise ValueError(
                f"Ditemukan {int(duplikat.sum())} baris duplikat pada seri {seri_kode}."
            )

        pivot = sub.pivot(index=indeks, columns="indikator", values="nilai").reset_index()
        pivot.columns.name = None

        periode_seri = (
            sub[["periode", "jenis_periode"]]
            .drop_duplicates()
            .sort_values("periode")
            .reset_index(drop=True)
        )

        grid = master_wilayah.merge(periode_seri, how="cross")
        grid = grid.merge(pivot, on=indeks, how="left")

        kolom_indikator = sorted(c for c in grid.columns if "__" in c)

        # Terapkan aturan sel tanpa mengisi celah nilai.
        if seri_kode == "var192":
            for kol_ind, kol_status in PETA_STATUS_VAR192.items():
                grid[kol_status] = [
                    _status_sel_tunggal(v, wk, per)
                    for v, wk, per in zip(grid[kol_ind], grid["wilayah_kode"], grid["periode"])
                ]
            status_cols = list(PETA_STATUS_VAR192.values())
        else:
            kol_ref = kolom_indikator[0]
            grid["status_sel"] = [
                _status_sel_tunggal(v, wk, per)
                for v, wk, per in zip(grid[kol_ref], grid["wilayah_kode"], grid["periode"])
            ]
            status_cols = ["status_sel"]

        grid["penanda_patahan"] = [
            (seri_kode, str(per)) in ATURAN_PATAHAN
            and any(s == "terisi" for s in statuses)
            for per, statuses in zip(grid["periode"], zip(*(grid[c] for c in status_cols)))
        ]

        grid["keterangan_sel"] = [
            _keterangan_baris(seri_kode, wk, per, list(statuses), pat)
            for wk, per, statuses, pat in zip(
                grid["wilayah_kode"],
                grid["periode"],
                zip(*(grid[c] for c in status_cols)),
                grid["penanda_patahan"],
            )
        ]

        grid = grid.sort_values(["wilayah_kode", "periode"]).reset_index(drop=True)
        hasil_panel[f"panel_{seri_kode}"] = grid

    return hasil_panel


def perkaya_panel_gabungan(panel: pd.DataFrame, panel_seri: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Menambahkan kolom penanda sel per seri ke tabel gabungan panel_provinsi."""
    out = panel.copy()

    # Periode aktif masing-masing seri
    p_var192 = set(panel_seri["panel_var192"]["periode"].unique())
    p_var2190 = set(panel_seri["panel_var2190"]["periode"].unique())
    p_var2191 = set(panel_seri["panel_var2191"]["periode"].unique())

    for kol_ind, kol_status in PETA_STATUS_VAR192.items():
        kol_out = kol_status.replace("status_sel_", "status_sel_var192_")
        out[kol_out] = [
            "di_luar_cakupan_periode"
            if per not in p_var192
            else _status_sel_tunggal(val, wk, per)
            for val, wk, per in zip(out[kol_ind], out["wilayah_kode"], out["periode"])
        ]

    out["status_sel_var2190"] = [
        "di_luar_cakupan_periode"
        if per not in p_var2190
        else _status_sel_tunggal(val, wk, per)
        for val, wk, per in zip(out["var2190__Tidak_ada"], out["wilayah_kode"], out["periode"])
    ]

    out["status_sel_var2191"] = [
        "di_luar_cakupan_periode"
        if per not in p_var2191
        else _status_sel_tunggal(val, wk, per)
        for val, wk, per in zip(out["var2191__Jumlah"], out["wilayah_kode"], out["periode"])
    ]

    out["penanda_patahan_var192"] = [
        (str(per) == "2008") and (st_j == "terisi" or st_p == "terisi" or st_d == "terisi")
        for per, st_j, st_p, st_d in zip(
            out["periode"],
            out["status_sel_var192_jumlah"],
            out["status_sel_var192_perkotaan"],
            out["status_sel_var192_perdesaan"],
        )
    ]

    return out


def _baris_kelengkapan_sebelum(panel: pd.DataFrame) -> list[dict]:
    """Menghitung kelengkapan pada grid gabungan awal sebelum aturan sel diterapkan."""
    kolom_ind = sorted(c for c in panel.columns if "__" in c)
    n_wil = int(panel["wilayah_kode"].nunique())
    n_per = int(panel["periode"].nunique())
    total_sel = len(panel)
    baris = []
    for ind in kolom_ind:
        seri = ind.split("__")[0]
        terisi = int(panel[ind].notna().sum())
        kosong = total_sel - terisi
        baris.append({
            "tahap_aturan": "sebelum_aturan_sel",
            "seri_kode": seri,
            "indikator": ind,
            "jumlah_provinsi": n_wil,
            "jumlah_periode": n_per,
            "total_sel": total_sel,
            "sel_terisi": terisi,
            "sel_kosong": kosong,
            "sel_belum_terbit": 0,
            "sel_di_luar_cakupan": 0,
            "sel_bertanda_patahan": 0,
            "persen_terisi_grid": round(terisi / total_sel * 100, 2),
            "persen_terisi_aktif": round(terisi / total_sel * 100, 2),
        })
    return baris


def _baris_kelengkapan_sesudah(panel_seri: dict[str, pd.DataFrame]) -> list[dict]:
    """Menghitung kelengkapan per indikator sesudah grid per seri dan aturan sel diterapkan."""
    baris = []
    for nama_panel, df in panel_seri.items():
        seri = nama_panel.replace("panel_", "")
        n_wil = int(df["wilayah_kode"].nunique())
        n_per = int(df["periode"].nunique())
        total_sel = len(df)
        kolom_ind = sorted(c for c in df.columns if "__" in c)

        for ind in kolom_ind:
            kol_st = PETA_STATUS_VAR192[ind] if seri == "var192" else "status_sel"
            terisi = int((df[kol_st] == "terisi").sum())
            kosong = int((df[kol_st] == "kosong").sum())
            belum = int((df[kol_st] == "belum_terbit").sum())
            patahan = int(((df[kol_st] == "terisi") & df["penanda_patahan"]).sum())
            aktif = total_sel - belum

            baris.append({
                "tahap_aturan": "sesudah_aturan_sel",
                "seri_kode": seri,
                "indikator": ind,
                "jumlah_provinsi": n_wil,
                "jumlah_periode": n_per,
                "total_sel": total_sel,
                "sel_terisi": terisi,
                "sel_kosong": kosong,
                "sel_belum_terbit": belum,
                "sel_di_luar_cakupan": 0,
                "sel_bertanda_patahan": patahan,
                "persen_terisi_grid": round(terisi / total_sel * 100, 2),
                "persen_terisi_aktif": round(terisi / aktif * 100, 2) if aktif else 0.0,
            })
    return baris


def _rincian_celah_dan_patahan(panel_seri: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Menyusun tabel rincian sel kosong, belum terbit, dan bertanda patahan."""
    catatan = []
    for nama_panel, df in panel_seri.items():
        seri = nama_panel.replace("panel_", "")
        kolom_ind = sorted(c for c in df.columns if "__" in c)
        for ind in kolom_ind:
            kol_st = PETA_STATUS_VAR192[ind] if seri == "var192" else "status_sel"

            for kategori, mask in [
                ("kosong", df[kol_st] == "kosong"),
                ("belum_terbit", df[kol_st] == "belum_terbit"),
                ("patahan", (df[kol_st] == "terisi") & df["penanda_patahan"]),
            ]:
                sub = df.loc[mask].sort_values(["wilayah_kode", "periode"])
                for (wk, nw), grp in sub.groupby(["wilayah_kode", "nama_wilayah"]):
                    periodes = grp["periode"].tolist()
                    tag_unik = list(dict.fromkeys(
                        t.strip()
                        for s in grp["keterangan_sel"].tolist()
                        for t in str(s).split(";")
                        if t.strip()
                    ))
                    alasan = "; ".join(tag_unik)
                    catatan.append({
                        "seri_kode": seri,
                        "indikator": ind,
                        "kategori_sel": kategori,
                        "wilayah_kode": int(wk),
                        "nama_wilayah": nw,
                        "periode_awal": periodes[0],
                        "periode_akhir": periodes[-1],
                        "jumlah_sel": len(periodes),
                        "alasan": alasan,
                    })

    return pd.DataFrame(catatan)


def tulis_laporan_kelengkapan(
    panel_gabungan: pd.DataFrame,
    panel_seri: dict[str, pd.DataFrame],
    folder_reports: Path = Path("reports"),
) -> pd.DataFrame:
    """Menyimpan tabel kelengkapan sebelum/sesudah aturan sel dan laporan rinci ke reports/."""
    folder_reports.mkdir(parents=True, exist_ok=True)

    df_indikator = pd.DataFrame(
        _baris_kelengkapan_sebelum(panel_gabungan)
        + _baris_kelengkapan_sesudah(panel_seri)
    )
    df_indikator.to_csv(
        folder_reports / "kelengkapan_gold_per_seri.csv",
        index=False,
        encoding="utf-8",
    )

    df_rincian = _rincian_celah_dan_patahan(panel_seri)
    df_rincian.to_csv(
        folder_reports / "kelengkapan_gold_rincian_celah.csv",
        index=False,
        encoding="utf-8",
    )

    # Ringkasan agregat per seri (sebelum vs sesudah aturan sel)
    ringkas = (
        df_indikator.groupby(["tahap_aturan", "seri_kode"], sort=False)
        .agg(
            jumlah_indikator=("indikator", "count"),
            jumlah_provinsi=("jumlah_provinsi", "first"),
            jumlah_periode=("jumlah_periode", "first"),
            total_sel=("total_sel", "sum"),
            sel_terisi=("sel_terisi", "sum"),
            sel_kosong=("sel_kosong", "sum"),
            sel_belum_terbit=("sel_belum_terbit", "sum"),
            sel_bertanda_patahan=("sel_bertanda_patahan", "sum"),
        )
        .reset_index()
    )
    ringkas["persen_terisi_grid"] = (ringkas["sel_terisi"] / ringkas["total_sel"] * 100).round(2)
    aktif_tot = ringkas["total_sel"] - ringkas["sel_belum_terbit"]
    ringkas["persen_terisi_aktif"] = (ringkas["sel_terisi"] / aktif_tot * 100).round(2)

    baris_md = [
        "# Laporan Kelengkapan Panel Gold (Tahap 4)",
        "",
        "Dokumen ini melaporkan pembentukan ulang grid `provinsi × periode` untuk setiap seri di lapisan Gold setelah aturan sel diterapkan (`src/gold/panel_seri.py`). Sesuai keputusan tertulis (`K-003`, `K-006`, `K-011`, `K-012`), **tidak ada celah yang diisi** (tanpa imputasi maupun interpolasi); seluruh celah dan indikasi patahan diberi penanda eksplisit.",
        "",
        "## 1. Ringkasan Kelengkapan per Seri (Sebelum dan Sesudah Aturan Sel)",
        "",
        "- **Sebelum aturan sel:** satu grid gabungan `38 provinsi × 36 periode` (`panel_provinsi`, 1.368 baris/indikator) yang mencampur periode semesteran/tahunan kemiskinan dengan tahunan desa tanpa klasifikasi status sel.",
        "- **Sesudah aturan sel:** grid `provinsi × periode` dibentuk ulang per seri (`panel_var192` 38×33, `panel_var2190` 38×3, `panel_var2191` 38×3) dan setiap sel diklasifikasikan ke `terisi`, `kosong`, atau `belum_terbit`, serta ditandai `penanda_patahan`.",
        "",
        "| Tahap | Seri | Indikator | Grid | Total Sel | Terisi | Kosong | Belum Terbit | Bertanda Patahan | % Terisi (Grid) | % Terisi (Wilayah Aktif) |",
        "|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, r in ringkas.iterrows():
        tahap_label = "Sebelum aturan sel" if r["tahap_aturan"] == "sebelum_aturan_sel" else "Sesudah aturan sel"
        baris_md.append(
            f"| {tahap_label} | `{r['seri_kode']}` | {r['jumlah_indikator']} | "
            f"{r['jumlah_provinsi']}×{r['jumlah_periode']} | {r['total_sel']:,} | "
            f"{r['sel_terisi']:,} | {r['sel_kosong']:,} | {r['sel_belum_terbit']:,} | "
            f"{r['sel_bertanda_patahan']:,} | {r['persen_terisi_grid']:.2f}% | {r['persen_terisi_aktif']:.2f}% |"
        )

    baris_md.extend([
        "",
        "## 2. Kelengkapan Rinci per Indikator (Sebelum vs Sesudah Aturan Sel)",
        "",
        "| Tahap | Seri | Indikator | Total Sel | Terisi | Kosong | Belum Terbit | Bertanda Patahan | % Grid | % Aktif |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for _, r in df_indikator.iterrows():
        tahap_label = "Sebelum" if r["tahap_aturan"] == "sebelum_aturan_sel" else "Sesudah"
        baris_md.append(
            f"| {tahap_label} | `{r['seri_kode']}` | `{r['indikator']}` | {r['total_sel']:,} | "
            f"{r['sel_terisi']:,} | {r['sel_kosong']:,} | {r['sel_belum_terbit']:,} | "
            f"{r['sel_bertanda_patahan']:,} | {r['persen_terisi_grid']:.2f}% | {r['persen_terisi_aktif']:.2f}% |"
        )

    baris_md.extend([
        "",
        "## 3. Rincian Sel Kosong (`kosong`)",
        "",
        "| Seri | Indikator | Provinsi | Periode | Jumlah Sel | Keterangan |",
        "|---|---|---|---|---:|---|",
    ])
    for _, r in df_rincian[df_rincian["kategori_sel"] == "kosong"].iterrows():
        rentang = r["periode_awal"] if r["periode_awal"] == r["periode_akhir"] else f"{r['periode_awal']} s.d. {r['periode_akhir']}"
        baris_md.append(
            f"| `{r['seri_kode']}` | `{r['indikator']}` | {r['nama_wilayah']} (`{r['wilayah_kode']}`) | {rentang} | {r['jumlah_sel']} | {r['alasan']} |"
        )

    baris_md.extend([
        "",
        "## 4. Rincian Sel Belum Terbit (`belum_terbit`)",
        "",
        "| Seri | Provinsi | Kode Wilayah | Rentang Periode | Sel per Indikator | Total Sel (Semua Rincian) | Alasan |",
        "|---|---|---:|---|---:|---:|---|",
    ])
    belum_ringkas = (
        df_rincian[df_rincian["kategori_sel"] == "belum_terbit"]
        .groupby(["seri_kode", "wilayah_kode", "nama_wilayah", "periode_awal", "periode_akhir", "alasan"], as_index=False)
        .agg(sel_per_indikator=("jumlah_sel", "first"), total_sel=("jumlah_sel", "sum"))
        .sort_values(["seri_kode", "wilayah_kode"])
    )
    for _, r in belum_ringkas.iterrows():
        rentang = f"{r['periode_awal']} s.d. {r['periode_akhir']}"
        baris_md.append(
            f"| `{r['seri_kode']}` | {r['nama_wilayah']} | `{r['wilayah_kode']}` | {rentang} | "
            f"{r['sel_per_indikator']} | {r['total_sel']} | {r['alasan']} |"
        )

    baris_md.extend([
        "",
        "## 5. Rincian Sel Bertanda Patahan (`penanda_patahan`)",
        "",
    ])
    pat_ringkas = (
        df_rincian[df_rincian["kategori_sel"] == "patahan"]
        .groupby(["seri_kode", "indikator", "periode_awal"], as_index=False)
        .agg(
            jumlah_provinsi=("wilayah_kode", "nunique"),
            total_sel=("jumlah_sel", "sum"),
            alasan=("alasan", lambda s: sorted(set(t.strip() for x in s for t in str(x).split(";") if "patahan" in t))[0]),
        )
    )
    if pat_ringkas.empty:
        baris_md.append("Tidak ada sel bertanda patahan.")
    else:
        baris_md.extend([
            "| Seri | Indikator | Periode | Provinsi Terdampak | Total Sel | Dasar Keputusan |",
            "|---|---|---|---:|---:|---|",
        ])
        for _, r in pat_ringkas.iterrows():
            baris_md.append(
                f"| `{r['seri_kode']}` | `{r['indikator']}` | {r['periode_awal']} | {r['jumlah_provinsi']} | {r['total_sel']} | {r['alasan']} |"
            )

    baris_md.extend([
        "",
        "## 6. Catatan Periode Sumber dan Seri Pembanding",
        "",
        "- **Periode `2023-S2` pada `var192`:** tidak tersedia pada berkas mentah BPS (`sdg10_10_1_1_f_v192.json` hanya memuat `2023-S1` untuk tahun 2023, termasuk pada baris agregat Indonesia `9999`).",
        "- **Periode `2026-S2` pada `var192`:** belum terbit pada tanggal snapshot `2026-10-20` (`last_update` berkas `2026-08-05`), sehingga cakupan seri ditetapkan `2007` s.d. `2026-S1` (33 periode).",
        "- **Pemekaran 4 DOB Papua (`2024-S1`):** selain patahan serentak `2008` (`K-006`), pergeseran nilai `PAPUA` (`26,03%` pada `2023-S1` menjadi `17,26%` pada `2024-S1`) mencerminkan pemisahan wilayah administratif 3 DOB Papua.",
        "- **Seri pembanding nasional `SI.POV.NAHC` (WDI):** hanya mencakup tingkat nasional Indonesia (`wilayah_kode = 9999`, tidak membentuk grid provinsi); dari 66 baris mentah (1960–2025), 28 tahun terisi dan 38 tahun kosong (disimpan di `rekonsiliasi_nasional` tanpa interpolasi sesuai `K-003`).",
    ])

    (folder_reports / "kelengkapan_gold.md").write_text(
        "\n".join(baris_md) + "\n",
        encoding="utf-8",
    )

    return df_indikator
