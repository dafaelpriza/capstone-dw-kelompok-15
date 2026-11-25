"""Tahap 4 — Persiapan Gold: aturan satu nilai per provinsi x periode x indikator.

Silver boleh memuat lebih dari satu baris untuk sel yang sama (misalnya dua snapshot atau
beberapa rincian). Gold tidak boleh. Modul ini menerapkan aturan pemilihan deterministik:
1. Snapshot (`pilih_snapshot`): bila terdapat >1 snapshot BPS, pilih snapshot terbaru.
2. Rincian (`pilih_rincian`): pilih deret utama per indikator (`total` dari Jumlah/Tidak ada);
   rincian lain (`Perkotaan`, `Perdesaan`, `Desa Sangat Tertinggal`, `Desa Tertinggal`) tetap
   hanya di Silver, dan baris nasional (`9999`) serta `SI.POV.NAHC` dipisah ke tabel nasional.
3. Berkas (`pilih_berkas`): bila satu sel masih punya >1 berkas, pilih menurut `URUTAN_BERKAS`
   (lalu urutan jalur); sisa sel ganda akan menghentikan pipeline.
4. Periode (`aturan_periode`): periode disimpan apa adanya (`tahun` dan `semester`); tidak ada
   perataan semester ke tahunan di Gold.
5. Grid & Penanda (`bentuk_grid_kosong`, `kumpulkan_penanda_sprint1`): sel kosong grid ikut
   ke panel dengan `status_sel`, dan penanda outlier/patahan Sprint 1 ikut ke kolom `penanda`
   tanpa mengubah nilai.

Keluaran: `data/gold/panel.parquet`, `data/gold/panel_lebar.parquet`, `reports/panel-gold.md`.
"""
from fnmatch import fnmatch
import json
from pathlib import Path

import pandas as pd

from src import konfigurasi as K
from src import wilayah as W

ROOT = Path(__file__).resolve().parents[2]
GOLD = ROOT / "data" / "gold"
REPORTS = ROOT / "reports"

KOLOM_PANEL = [
    "indikator", "seri_kode", "rincian", "wilayah_kode", "nama_wilayah",
    "periode", "jenis_periode", "nilai", "satuan", "status_sel", "penanda",
    "rujukan_tahun", "_berkas_raw", "_sha256_raw",
]
STATUS_BAKU = ("terisi", "missing", "tidak_diterbitkan", "belum_ada", "batas_lama")


def _jenis_periode(periode: str) -> str:
    p = str(periode)
    if len(p) == 4:
        return "tahun"
    if "-S" in p:
        return "semester"
    if "-Q" in p:
        return "triwulan"
    return "bulan"


def _label_indikator(seri: str, rincian: str) -> str:
    return seri if rincian == "total" else f"{seri} [{rincian}]"


def _normalisasi_rincian(seri: str, rincian: str) -> str:
    teks = str(rincian).strip()
    if teks.lower() in K.RINCIAN_TOTAL_BPS:
        return "total"
    dim, kamus = K.RINCIAN_BPS.get(seri, ("rincian", {}))
    if teks in kamus:
        return f"{dim}={kamus[teks]}"
    return teks


def normalisasi_silver_untuk_gold(silver: pd.DataFrame) -> pd.DataFrame:
    """Menyamakan kode wilayah (110000 -> 1100), jenis_periode, satuan, dan rincian."""
    wajib = [
        "sumber", "seri_kode", "wilayah_kode", "nama_wilayah",
        "periode", "jenis_periode", "rincian", "nilai", "satuan",
        "_berkas_raw", "_sha256_raw",
    ]
    kurang = [k for k in wajib if k not in silver.columns]
    if kurang:
        raise ValueError(f"Kolom Silver belum lengkap untuk Gold: {kurang}")

    df = silver.copy()
    df["sumber"] = df["sumber"].astype(str).str.lower().str.strip()
    df["seri_kode"] = df["seri_kode"].astype(str).str.strip()
    df["nilai"] = pd.to_numeric(df["nilai"], errors="coerce")
    df["wilayah_kode"] = pd.to_numeric(df["wilayah_kode"], errors="coerce")
    df = df.dropna(subset=["wilayah_kode", "periode", "nilai", "seri_kode"]).copy()
    df["wilayah_kode"] = df["wilayah_kode"].map(W.normalisasi_kode).astype("int64")
    df["nama_wilayah"] = df["wilayah_kode"].map(W.NAMA).fillna(df["nama_wilayah"].astype(str))
    df["periode"] = df["periode"].astype(str).str.strip()
    df["jenis_periode"] = df["periode"].map(_jenis_periode)
    df["rincian"] = [_normalisasi_rincian(s, r) for s, r in zip(df["seri_kode"], df["rincian"])]
    satuan_baku = {k: v["satuan"] for k, v in K.SERI.items()}
    df["satuan"] = df["seri_kode"].map(satuan_baku).fillna(df["satuan"].astype(str))
    if "rujukan_tahun" not in df.columns:
        df["rujukan_tahun"] = None
    return df


def pilih_snapshot(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Memilih snapshot terbaru per seri BPS bila terdapat >1 snapshot di Silver."""
    d = df.copy()
    bagian_jalur = d["_berkas_raw"].astype(str).str.split("/")
    d["_snapshot"] = bagian_jalur.str[1].fillna("")

    terpilih = []
    laporan = []
    for seri, grp in d.groupby("seri_kode", sort=False):
        snapshots = sorted(s for s in grp["_snapshot"].unique() if s)
        if len(snapshots) <= 1:
            terpilih.append(grp)
            continue
        terbaru = snapshots[-1]
        df_baru = grp[grp["_snapshot"] == terbaru]
        terpilih.append(df_baru)
        kunci = ["wilayah_kode", "periode", "rincian"]
        baru_idx = df_baru.drop_duplicates(kunci).set_index(kunci)["nilai"]
        for lama in snapshots[:-1]:
            df_lama = grp[grp["_snapshot"] == lama]
            lama_idx = df_lama.drop_duplicates(kunci).set_index(kunci)["nilai"]
            irisan = lama_idx.index.intersection(baru_idx.index)
            beda = int(((lama_idx.loc[irisan] - baru_idx.loc[irisan]).abs() > 1e-9).sum())
            laporan.append({
                "seri_kode": seri,
                "snapshot_dipakai": terbaru,
                "snapshot_lain": lama,
                "baris_dipakai": len(df_baru),
                "baris_lain": len(df_lama),
                "sel_sama": len(irisan),
                "nilai_berbeda": beda,
            })

    if laporan:
        REPORTS.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(laporan).to_csv(REPORTS / "snapshot-bps.csv", index=False)

    hasil = pd.concat(terpilih, ignore_index=True).drop(columns=["_snapshot"]) if terpilih else d.drop(columns=["_snapshot"])
    info = {
        "baris_dibuang_snapshot": int(len(d) - len(hasil)),
        "snapshot_ganda": len(laporan),
        "sel_snapshot_beda": int(sum(r["nilai_berbeda"] for r in laporan)),
        "daftar_snapshot": sorted(s for s in d["_snapshot"].unique() if s),
    }
    return hasil, info


def pilih_rincian(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Memilih hanya baris provinsi deret utama (`total` di `DERET`) untuk panel Gold."""
    provinsi = df[df["wilayah_kode"] != W.INDONESIA].copy()
    nasional = df[df["wilayah_kode"] == W.INDONESIA]

    bagian = []
    rincian_tersimpan_di_silver = []
    for seri, info_seri in K.SERI.items():
        if info_seri["tingkat"] != "provinsi":
            continue
        daftar_rincian = K.DERET.get(seri, ["total"])
        sub_seri = provinsi[provinsi["seri_kode"] == seri]
        dipilih = sub_seri[sub_seri["rincian"].isin(daftar_rincian)].copy()
        dipilih["indikator"] = [_label_indikator(s, r) for s, r in zip(dipilih["seri_kode"], dipilih["rincian"])]
        bagian.append(dipilih)

        ditinggal = sub_seri[~sub_seri["rincian"].isin(daftar_rincian)]
        for r_val, n_val in ditinggal["rincian"].value_counts().items():
            rincian_tersimpan_di_silver.append({"seri_kode": seri, "rincian": r_val, "baris": int(n_val)})

    terpilih = pd.concat(bagian, ignore_index=True) if bagian else provinsi.iloc[0:0].copy()
    info = {
        "baris_silver_total": int(len(df)),
        "baris_silver_provinsi": int(len(provinsi)),
        "baris_silver_nasional": int(len(nasional)),
        "baris_provinsi_tidak_terpilih": int(len(provinsi) - len(terpilih)),
        "rincian_hanya_silver": rincian_tersimpan_di_silver,
    }
    return terpilih, info


def _peringkat_berkas(berkas: str) -> int:
    pola = getattr(K, "URUTAN_BERKAS", [])
    return next((i for i, (p, _) in enumerate(pola) if fnmatch(str(berkas), p)), len(pola))


def pilih_berkas(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Memilih satu berkas per (indikator, wilayah_kode, periode) menurut URUTAN_BERKAS."""
    kunci = ["indikator", "wilayah_kode", "periode"]
    if df.empty:
        return df, {"baris_dibuang_berkas": 0, "sel_multi_berkas": 0}

    duplikat_awal = df.duplicated(subset=kunci, keep=False)
    if not duplikat_awal.any():
        return df.reset_index(drop=True), {"baris_dibuang_berkas": 0, "sel_multi_berkas": 0}

    d = df.assign(_peringkat=df["_berkas_raw"].map(_peringkat_berkas)).sort_values(
        kunci + ["_peringkat", "_berkas_raw"]
    )
    # Tolak duplikat bila dalam satu berkas dan kunci yang sama ternyata ada >1 nilai
    duplikat_berkas_sama = d.duplicated(subset=kunci + ["_berkas_raw"], keep=False)
    if duplikat_berkas_sama.any():
        raise ValueError(
            f"Gold: {int(duplikat_berkas_sama.sum())} sel ganda ditemukan pada berkas yang sama."
        )

    pakai = d.drop_duplicates(subset=kunci, keep="first").drop(columns=["_peringkat"]).reset_index(drop=True)
    lain = d.groupby(kunci)["_berkas_raw"].nunique().sub(1)
    catatan = pakai[kunci + ["_berkas_raw"]].merge(
        lain.rename("berkas_lain").reset_index(), on=kunci
    )
    catatan = catatan[catatan["berkas_lain"] > 0]
    if not catatan.empty:
        REPORTS.mkdir(parents=True, exist_ok=True)
        catatan.to_csv(REPORTS / "deret-berkas.csv", index=False)

    sisa_ganda = pakai.duplicated(subset=kunci, keep=False)
    if sisa_ganda.any():
        raise ValueError(f"Gold: {int(sisa_ganda.sum())} sel panel masih ganda sesudah aturan berkas.")

    return pakai, {
        "baris_dibuang_berkas": int(len(df) - len(pakai)),
        "sel_multi_berkas": int(len(catatan)),
    }


def aturan_periode(df: pd.DataFrame) -> pd.DataFrame:
    """Mempertahankan resolusi periode asli (kemiskinan: tahun/semester; desa: tahun) tanpa perataan."""
    out = df.copy()
    out["jenis_periode"] = out["periode"].map(_jenis_periode)
    if out.empty:
        return out

    # Pastikan seri desa (var2190, var2191) hanya berjenis tahunan
    desa_non_tahun = out[out["seri_kode"].isin(["var2190", "var2191"]) & (out["jenis_periode"] != "tahun")]
    if not desa_non_tahun.empty:
        raise ValueError(f"Seri desa memiliki periode non-tahunan di Gold: {len(desa_non_tahun)} baris.")

    ganda = out.duplicated(subset=["indikator", "wilayah_kode", "periode"], keep=False)
    if ganda.any():
        raise ValueError(f"Gold: ditemukan {int(ganda.sum())} sel ganda pada indikator x wilayah x periode.")
    return out


def bentuk_grid_kosong(terisi_df: pd.DataFrame) -> pd.DataFrame:
    """Membentuk grid 38 provinsi x periode terbit dan mengkategorikan sel kosong."""
    baris_grid = []
    baris_kosong = []
    terisi_map = {
        ind: set(zip(grp["wilayah_kode"], grp["periode"]))
        for ind, grp in terisi_df.groupby("indikator")
    }

    for ind, grp in terisi_df.groupby("indikator"):
        seri = grp["seri_kode"].iloc[0]
        rincian = grp["rincian"].iloc[0]
        satuan = grp["satuan"].iloc[0]
        ada = terisi_map.get(ind, set())
        periode_daftar = sorted(grp["periode"].unique())

        for per in periode_daftar:
            for kode in sorted(W.PROVINSI):
                if (kode, per) in ada:
                    kat, bukti = "terisi", ""
                elif not W.sudah_ada(kode, per):
                    kat = "belum_ada"
                    bukti = f"provinsi dibentuk; data penuh mulai {W.PROVINSI[kode][1]}"
                elif (seri, kode, per) in K.TIDAK_TERBIT:
                    kat = "tidak_diterbitkan"
                    bukti = K.TIDAK_TERBIT[(seri, kode, per)]
                elif (
                    kode in W.INDUK
                    and (W.INDUK[kode], per) in ada
                    and not any(w == kode and p < per for w, p in ada)
                    and not any(
                        W.INDUK.get(k) == W.INDUK[kode]
                        and W.PROVINSI[k][1] == W.PROVINSI[kode][1]
                        and (k, per) in ada
                        for k in W.PROVINSI
                    )
                ):
                    kat = "batas_lama"
                    bukti = f"{W.NAMA[W.INDUK[kode]]} masih diterbitkan dengan batas lama pada {per}; angka tidak dipecah"
                else:
                    kat = "missing"
                    bukti = "provinsi sudah ada dan penerbit tidak menyatakan angka itu tidak ada"

                baris_grid.append({
                    "seri_kode": ind,
                    "periode": per,
                    "wilayah_kode": kode,
                    "nama_wilayah": W.NAMA[kode],
                    "tingkat": "provinsi",
                    "kategori": kat,
                    "bukti": bukti,
                })
                if kat != "terisi":
                    baris_kosong.append({
                        "indikator": ind,
                        "seri_kode": seri,
                        "rincian": rincian,
                        "wilayah_kode": kode,
                        "nama_wilayah": W.NAMA[kode],
                        "periode": per,
                        "jenis_periode": _jenis_periode(per),
                        "nilai": float("nan"),
                        "satuan": satuan,
                        "status_sel": kat,
                        "rujukan_tahun": None,
                        "_berkas_raw": None,
                        "_sha256_raw": None,
                    })

    grid_df = pd.DataFrame(baris_grid)
    REPORTS.mkdir(parents=True, exist_ok=True)
    kosong_laporan = grid_df[grid_df["kategori"] != "terisi"] if not grid_df.empty else grid_df
    kosong_laporan.to_csv(REPORTS / "grid-sel-kosong.csv", index=False)

    return pd.DataFrame(baris_kosong)


def _deteksi_patahan_wilayah(terisi_df: pd.DataFrame) -> set[tuple[str, int, str]]:
    """Mendeteksi periode pertama provinsi pemekaran terbit pada provinsi induk."""
    hasil = set()
    for ind, grp in terisi_df.groupby("indikator"):
        ada = {w: sorted(x["periode"]) for w, x in grp.groupby("wilayah_kode")}
        for induk in sorted(set(W.INDUK.values())):
            angkatan = {}
            for anak_kode, parent in W.INDUK.items():
                if parent == induk and anak_kode in ada:
                    angkatan.setdefault(W.PROVINSI[anak_kode][1], []).append(anak_kode)
            for anak_list in angkatan.values():
                if induk not in ada:
                    continue
                pertama = min(min(ada[k]) for k in anak_list)
                sebelum = [p for p in ada[induk] if p < pertama]
                if sebelum and pertama in ada[induk]:
                    hasil.add((ind, int(induk), str(pertama)))
    return hasil


def kumpulkan_penanda_sprint1(panel_df: pd.DataFrame) -> pd.Series:
    """Membawa penanda patahan dan outlier dari Sprint 1 ke kolom `penanda` tanpa mengubah nilai."""
    peta: dict[tuple[str, int, str], str] = {}
    prioritas = {"outlier": 1, "perbedaan_struktural": 2, "patahan_seri": 3, "patahan_wilayah": 4}

    def _tandai(ind: str, wil: int, per: str, kategori: str) -> None:
        kunci = (ind, int(wil), str(per))
        lama = peta.get(kunci)
        if lama is None or prioritas.get(kategori, 0) >= prioritas.get(lama, 0):
            peta[kunci] = kategori

    # 1. Jika ada reports/anomali.csv terstruktur, baca langsung
    anomali_csv = REPORTS / "anomali.csv"
    if anomali_csv.exists() and anomali_csv.stat().st_size > 1:
        a = pd.read_csv(anomali_csv, dtype={"periode": str})
        for r in a.itertuples():
            _tandai(str(r.seri_kode), int(r.wilayah_kode), str(r.periode), str(r.kategori))
    else:
        # 2. Baca calon outlier hasil analisis Sprint 1 (reports/calon_anomali.csv)
        calon_csv = REPORTS / "calon_anomali.csv"
        if calon_csv.exists() and calon_csv.stat().st_size > 1:
            calon = pd.read_csv(calon_csv, dtype={"periode": str})
            utama = calon[calon["seri"].astype(str).str.strip().str.lower().isin({"jumlah", "total", "tidak ada"})]
            hitung_prov = utama.groupby(["variabel", "provinsi"]).size().to_dict()
            for r in utama.itertuples():
                try:
                    kode = W.dari_nama(r.provinsi)
                except KeyError:
                    continue
                # K-009: Papua & Papua Barat berulang -> perbedaan_struktural; lainnya -> outlier
                jml = hitung_prov.get((r.variabel, r.provinsi), 0)
                kat = "perbedaan_struktural" if (kode in {9100, 9400} and jml >= 2) else "outlier"
                _tandai(str(r.variabel), kode, str(r.periode), kat)

        # 3. Penanda patahan seri Sprint 1 (K-006 var192 2008 & PATAHAN_DEFINISI var2190/var2191 2020-2021)
        terisi = panel_df[panel_df["status_sel"] == "terisi"]
        for seri, peta_per in getattr(K, "PATAHAN_DEFINISI", {}).items():
            for per in peta_per:
                cocok = terisi[(terisi["indikator"] == seri) & (terisi["periode"] == str(per))]
                for r in cocok.itertuples():
                    _tandai(str(r.indikator), int(r.wilayah_kode), str(r.periode), "patahan_seri")

        # 4. Penanda patahan wilayah (induk saat provinsi pemekaran terbit pertama kali)
        for ind, wil, per in _deteksi_patahan_wilayah(terisi):
            _tandai(ind, wil, per, "patahan_wilayah")

    hasil = []
    for r in panel_df.itertuples():
        if r.status_sel != "terisi":
            hasil.append(None)
        else:
            hasil.append(peta.get((str(r.indikator), int(r.wilayah_kode), str(r.periode))))
    return pd.Series(hasil, index=panel_df.index, dtype="object")


def turunan(panel: pd.DataFrame) -> pd.DataFrame:
    """Kolom turunan opsional (`GOLD_TURUNAN`); nilai asli tetap dipertahankan."""
    out = panel.copy()
    for nama, (ind, fungsi) in getattr(K, "GOLD_TURUNAN", {}).items():
        out[nama] = out["nilai"].where(out["indikator"] == ind).map(fungsi)
    return out


def _perbarui_angka_json(metrik: dict) -> None:
    REPORTS.mkdir(parents=True, exist_ok=True)
    path = REPORTS / "angka.json"
    data = {}
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            data = {}
    data.update(metrik)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _tulis_laporan(panel: pd.DataFrame, lebar: pd.DataFrame, info: dict) -> None:
    ringkas = (
        panel.assign(t=panel["status_sel"] == "terisi")
        .groupby(["indikator", "satuan"])
        .agg(
            periode=("periode", lambda s: f"{s.min()}–{s.max()}" if s.nunique() > 1 else s.min()),
            jumlah_periode=("periode", "nunique"),
            sel=("t", "size"),
            terisi=("t", "sum"),
            ditandai=("penanda", lambda s: int(s.notna().sum())),
        )
        .reset_index()
    )
    status = (
        panel.pivot_table(
            index="indikator", columns="status_sel", values="wilayah_kode", aggfunc="size", fill_value=0
        )
        .reset_index()
    )
    penanda_ringkas = (
        panel[panel["penanda"].notna()]
        .groupby(["indikator", "penanda"])
        .size()
        .reset_index(name="jumlah_sel")
    )

    def _md(df: pd.DataFrame) -> str:
        if df.empty:
            return "_(kosong)_"
        cols = [str(c) for c in df.columns]
        lines = ["| " + " | ".join(cols) + " |", "|" + "|".join("---" for _ in cols) + "|"]
        for row in df.itertuples(index=False):
            lines.append("| " + " | ".join(str(v) for v in row) + " |")
        return "\n".join(lines)

    rincian_list = ", ".join(
        f"`{r['seri_kode']}` (`{r['rincian']}`: {r['baris']:,})" for r in info["rincian_hanya_silver"]
    )
    teks = "\n\n".join([
        "# Panel Gold provinsi x periode x indikator",
        "Dihasilkan `python pipeline.py` (`src/gold/panel.py`) dari Silver, grid 38 provinsi, dan penanda Sprint 1.",
        "## Aturan satu nilai per sel",
        "1. **Snapshot (`pilih_snapshot`)**: bila terdapat >1 snapshot BPS, pilih snapshot terbaru; saat ini tersedia snapshot "
        f"`{', '.join(info['daftar_snapshot']) or '-'}` (dibuang karena snapshot lama: {info['baris_dibuang_snapshot']:,}).\n"
        "2. **Rincian (`pilih_rincian`)**: satu indikator panel = deret utama (`total` hasil penyeragaman `Jumlah`/`Tidak ada`). "
        f"Rincian lain tetap hanya di Silver ({rincian_list}). Baris nasional (`9999` dan `SI.POV.NAHC`: {info['baris_silver_nasional']:,} baris) dipisah ke tabel nasional.\n"
        "3. **Berkas (`pilih_berkas`)**: bila satu sel memiliki >1 berkas, pilih menurut `URUTAN_BERKAS` (JSON WebAPI lebih dahulu daripada CSV, lalu urutan jalur) "
        f"(dibuang karena berkas ganda: {info['baris_dibuang_berkas']:,}).\n"
        "4. **Periode (`aturan_periode`)**: resolusi periode disimpan apa adanya (`var192` provinsi x periode `tahun` & `semester`; `var2190`/`var2191` provinsi x tahun `tahun`). Tidak ada perataan semester ke tahunan.\n"
        "5. **Grid & Penanda (`bentuk_grid_kosong`, `kumpulkan_penanda_sprint1`)**: sel kosong grid ikut ke panel dengan `status_sel` tanpa interpolasi; penanda `outlier`, `perbedaan_struktural`, `patahan_seri`, dan `patahan_wilayah` dari Sprint 1 terbawa di kolom `penanda` tanpa mengubah nilai.",
        f"Baris Silver provinsi yang tidak terpilih masuk panel Gold (rincian non-utama tetap di Silver): **{info['baris_provinsi_tidak_terpilih']:,}** dari {info['baris_silver_provinsi']:,} baris provinsi (total semua baris Silver yang tidak masuk panel termasuk {info['baris_silver_nasional']:,} baris nasional: **{info['baris_silver_total'] - info['sel_terisi']:,}**).",
        "## Catatan normalisasi desa",
        "Nilai `var2190` (desa mandiri) dan `var2191` (desa tertinggal) pada panel disimpan dalam satuan asli (`desa`) sesuai data mentah BPS; untuk perbandingan langsung antarprovinsi perlu dinormalisasi terhadap jumlah desa total per provinsi sebagai data pendukung.",
        "## Indikator",
        _md(ringkas),
        "## Status sel",
        _md(status),
        "## Penanda Sprint 1 terbawa ke Gold",
        _md(penanda_ringkas),
        "## Berkas keluaran",
        f"- `data/gold/panel.parquet`: {len(panel):,} baris (panjang, termasuk {info['sel_kosong']:,} sel kosong grid).\n"
        f"- `data/gold/panel_lebar.parquet`: {len(lebar):,} baris x {lebar.shape[1]} kolom (hanya {info['sel_terisi']:,} sel terisi; satu kolom per indikator).",
    ])
    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / "panel-gold.md").write_text(teks.rstrip() + "\n", encoding="utf-8")


def jalankan(silver: pd.DataFrame) -> dict:
    """Menjalankan Tahap 4 (persiapan Gold) dari tabel Silver hingga menulis panel Gold."""
    data = normalisasi_silver_untuk_gold(silver)
    data, info_snap = pilih_snapshot(data)
    terpilih, info_rin = pilih_rincian(data)
    terpilih, info_berkas = pilih_berkas(terpilih)
    terpilih = aturan_periode(terpilih)
    terpilih["status_sel"] = "terisi"

    kosong = bentuk_grid_kosong(terpilih)
    panel = pd.concat([terpilih, kosong], ignore_index=True)
    panel["nama_wilayah"] = panel["wilayah_kode"].map(W.NAMA)
    panel["jenis_periode"] = panel["periode"].map(_jenis_periode)
    satuan_baku = {k: v["satuan"] for k, v in K.SERI.items()}
    panel["satuan"] = panel["seri_kode"].map(satuan_baku)
    panel["penanda"] = kumpulkan_penanda_sprint1(panel)

    for c in ("rujukan_tahun", "_berkas_raw", "_sha256_raw"):
        if c not in panel.columns:
            panel[c] = None

    panel = turunan(panel)
    ekstra = [c for c in getattr(K, "GOLD_TURUNAN", {})]
    panel = panel[KOLOM_PANEL + ekstra].sort_values(["indikator", "periode", "wilayah_kode"]).reset_index(drop=True)
    panel["wilayah_kode"] = panel["wilayah_kode"].astype("int64")
    panel["rujukan_tahun"] = pd.to_numeric(
        panel["rujukan_tahun"].astype(object).where(panel["rujukan_tahun"].notna(), None),
        errors="coerce",
    ).astype("float64")

    GOLD.mkdir(parents=True, exist_ok=True)
    panel.to_parquet(GOLD / "panel.parquet", index=False)

    lebar = (
        panel[panel["status_sel"] == "terisi"]
        .pivot_table(
            index=["wilayah_kode", "nama_wilayah", "jenis_periode", "periode"],
            columns="indikator",
            values="nilai",
            aggfunc="first",
        )
        .reset_index()
    )
    lebar.columns.name = None
    lebar.to_parquet(GOLD / "panel_lebar.parquet", index=False)

    info = {
        **info_snap,
        **info_rin,
        **info_berkas,
        "sel_terisi": int((panel["status_sel"] == "terisi").sum()),
        "sel_kosong": int((panel["status_sel"] != "terisi").sum()),
        "sel_ditandai": int(panel["penanda"].notna().sum()),
    }
    _tulis_laporan(panel, lebar, info)
    _perbarui_angka_json({
        "seri_panel": int(panel["indikator"].nunique()),
        "baris_gold": int(len(panel)),
        "sel_gold_terisi": info["sel_terisi"],
        "sel_gold_kosong": info["sel_kosong"],
        "silver_tidak_terpilih": info["baris_provinsi_tidak_terpilih"],
        "sel_gold_ditandai": info["sel_ditandai"],
        "kolom_panel_lebar": int(lebar.shape[1]),
    })
    print(
        f"Panel Gold berhasil dibuat: {len(panel)} baris "
        f"({info['sel_terisi']} terisi, {info['sel_kosong']} kosong grid, "
        f"{info['baris_provinsi_tidak_terpilih']} baris provinsi Silver tidak terpilih)"
    )
    return {"panel": panel, "panel_lebar": lebar, "info": info}
