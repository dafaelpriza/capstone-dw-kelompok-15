"""Pengujian unit dan integrasi aturan persiapan Gold (Tahap 4) di src/gold/panel.py."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import pandas as pd

from src.gold import panel as P

ROOT = Path(__file__).resolve().parents[1]


def _contoh_silver_dasar():
    return pd.DataFrame([
        {
            "sumber": "bps", "seri_kode": "var192", "wilayah_kode": 110000, "nama_wilayah": "ACEH",
            "periode": "2020-S1", "jenis_periode": "semester", "rincian": "Jumlah", "nilai": 14.99,
            "satuan": "persen", "_berkas_raw": "bps/2026-10-17/json/sdg10_10_1_1_f_v192.json", "_sha256_raw": "a" * 64,
        },
        {
            "sumber": "bps", "seri_kode": "var192", "wilayah_kode": 110000, "nama_wilayah": "ACEH",
            "periode": "2020-S1", "jenis_periode": "semester", "rincian": "Jumlah", "nilai": 15.10,
            "satuan": "persen", "_berkas_raw": "bps/2026-10-20/json/sdg10_10_1_1_f_v192.json", "_sha256_raw": "b" * 64,
        },
        {
            "sumber": "bps", "seri_kode": "var192", "wilayah_kode": 110000, "nama_wilayah": "ACEH",
            "periode": "2020-S1", "jenis_periode": "semester", "rincian": "Perkotaan", "nilai": 10.50,
            "satuan": "persen", "_berkas_raw": "bps/2026-10-20/json/sdg10_10_1_1_f_v192.json", "_sha256_raw": "b" * 64,
        },
        {
            "sumber": "bps", "seri_kode": "var192", "wilayah_kode": 999900, "nama_wilayah": "INDONESIA",
            "periode": "2020-S1", "jenis_periode": "semester", "rincian": "Jumlah", "nilai": 9.78,
            "satuan": "persen", "_berkas_raw": "bps/2026-10-20/json/sdg10_10_1_1_f_v192.json", "_sha256_raw": "b" * 64,
        },
        {
            "sumber": "bps", "seri_kode": "var2190", "wilayah_kode": 110000, "nama_wilayah": "ACEH",
            "periode": "2020", "jenis_periode": "tahun", "rincian": "Tidak ada", "nilai": 500.0,
            "satuan": "desa", "_berkas_raw": "bps/2026-10-20/json/sdg10_10_1_1_d_v2190.json", "_sha256_raw": "c" * 64,
        },
    ])


class TestGoldPanel(unittest.TestCase):
    def test_pilih_snapshot_terbaru(self):
        df = P.normalisasi_silver_untuk_gold(_contoh_silver_dasar())
        with tempfile.TemporaryDirectory() as tmp, patch.object(P, "REPORTS", Path(tmp)):
            hasil, info = P.pilih_snapshot(df)
        self.assertEqual(info["baris_dibuang_snapshot"], 1)
        aceh_jml = hasil[
            (hasil["seri_kode"] == "var192") & (hasil["wilayah_kode"] == 1100) & (hasil["rincian"] == "total")
        ]
        self.assertEqual(len(aceh_jml), 1)
        self.assertAlmostEqual(aceh_jml["nilai"].iloc[0], 15.10)

    def test_pilih_rincian_dan_tidak_terpilih(self):
        df = P.normalisasi_silver_untuk_gold(_contoh_silver_dasar())
        with tempfile.TemporaryDirectory() as tmp, patch.object(P, "REPORTS", Path(tmp)):
            snap, _ = P.pilih_snapshot(df)
            terpilih, info = P.pilih_rincian(snap)
        self.assertEqual(len(terpilih), 2)
        self.assertEqual(info["baris_provinsi_tidak_terpilih"], 1)
        self.assertEqual(info["baris_silver_nasional"], 1)

    def test_pilih_berkas_urutan_dan_ganda_ditolak(self):
        df = pd.DataFrame([
            {
                "indikator": "var192", "seri_kode": "var192", "rincian": "total",
                "wilayah_kode": 1100, "periode": "2020-S1", "nilai": 15.10,
                "_berkas_raw": "bps/2026-10-20/sdg10_10_1_1_f_v192.csv",
            },
            {
                "indikator": "var192", "seri_kode": "var192", "rincian": "total",
                "wilayah_kode": 1100, "periode": "2020-S1", "nilai": 15.10,
                "_berkas_raw": "bps/2026-10-20/json/sdg10_10_1_1_f_v192.json",
            },
        ])
        with tempfile.TemporaryDirectory() as tmp, patch.object(P, "REPORTS", Path(tmp)):
            pakai, info = P.pilih_berkas(df)
        self.assertEqual(len(pakai), 1)
        self.assertTrue(pakai["_berkas_raw"].iloc[0].endswith(".json"))
        self.assertEqual(info["baris_dibuang_berkas"], 1)

        duplikat_berkas = pd.concat([df.iloc[[1]], df.iloc[[1]]], ignore_index=True)
        with self.assertRaises(ValueError):
            P.pilih_berkas(duplikat_berkas)

    def test_panel_gold_aktual_dan_penanda(self):
        panel_path = ROOT / "data" / "gold" / "panel.parquet"
        silver_path = ROOT / "data" / "silver" / "silver.parquet"
        if not panel_path.exists() or not silver_path.exists():
            self.skipTest("jalankan python pipeline.py dulu")

        panel = pd.read_parquet(panel_path)
        silver = pd.read_parquet(silver_path)

        # 1. Kunci unik: tidak boleh ada lebih dari 1 baris per indikator x wilayah x periode
        self.assertFalse(panel.duplicated(["indikator", "wilayah_kode", "periode"]).any())

        # 2. Kemiskinan (var192) mempertahankan semester & tahun; desa (var2190, var2191) hanya tahunan
        self.assertEqual(set(panel.loc[panel["indikator"] == "var192", "jenis_periode"]), {"tahun", "semester"})
        self.assertEqual(set(panel.loc[panel["indikator"].isin(["var2190", "var2191"]), "jenis_periode"]), {"tahun"})

        # 3. Status sel dan nilai konsisten (tidak ada interpolasi sel kosong)
        self.assertTrue(((panel["status_sel"] == "terisi") == panel["nilai"].notna()).all())

        # 4. Penanda Sprint 1 (outlier & patahan) ikut terbawa tanpa mengubah nilai asli Silver
        self.assertGreater(panel["penanda"].notna().sum(), 0)
        self.assertTrue({"outlier", "patahan_seri", "patahan_wilayah"}.issubset(set(panel["penanda"].dropna())))

        # 5. Nilai sel terisi sama persis dengan Silver
        s_norm = P.normalisasi_silver_untuk_gold(silver)
        terisi = panel[panel["status_sel"] == "terisi"].merge(
            s_norm[["seri_kode", "wilayah_kode", "periode", "rincian", "_berkas_raw", "nilai"]],
            on=["seri_kode", "wilayah_kode", "periode", "rincian", "_berkas_raw"],
            suffixes=("", "_silver"),
        )
        self.assertEqual(len(terisi), (panel["status_sel"] == "terisi").sum())
        self.assertLess((terisi["nilai"] - terisi["nilai_silver"]).abs().max(), 1e-9)


if __name__ == "__main__":
    unittest.main()
