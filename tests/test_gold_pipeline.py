"""Pengujian tambahan untuk snapshot, panel panjang, dan validasi rincian."""

import unittest

import pandas as pd

from src import gold
from src.validasi import validasi_gold
from src.validasi.silver import validasi_rincian_desa


class TestSnapshotGold(unittest.TestCase):
    def test_snapshot_terbaru_diterapkan_sebelum_pivot_gold(self):
        data = pd.DataFrame([
            {"seri_kode": "var192", "periode": "2020", "_berkas_raw": "bps/2026-10-17/json/a.json", "nilai": 10},
            {"seri_kode": "var192", "periode": "2020", "_berkas_raw": "bps/2026-10-20/json/a.json", "nilai": 11},
            {"seri_kode": "var2190", "periode": "2020", "_berkas_raw": "bps/2026-10-20/json/b.json", "nilai": 5},
        ])

        hasil, info = gold._pilih_snapshot_data(data)

        self.assertEqual(len(hasil), 2)
        self.assertEqual(
            hasil.loc[hasil["seri_kode"] == "var192", "nilai"].iloc[0],
            11,
        )
        self.assertEqual(info["snapshot_dibuang"], 1)
        self.assertEqual(info["snapshot_terpilih"]["var192"], "2026-10-20")


class TestValidasiPanelPanjang(unittest.TestCase):
    def test_panel_panjang_diperiksa(self):
        panel = pd.DataFrame([
            {
                "indikator": "var192",
                "wilayah_kode": 1100,
                "nama_wilayah": "Aceh",
                "periode": "2020",
                "jenis_periode": "tahun",
                "nilai": 10.0,
                "status_sel": "terisi",
                "penanda": None,
            },
            {
                "indikator": "var192",
                "wilayah_kode": 1200,
                "nama_wilayah": "Sumatera Utara",
                "periode": "2020",
                "jenis_periode": "tahun",
                "nilai": None,
                "status_sel": "missing",
                "penanda": None,
            },
        ])

        hasil = validasi_gold({"panel": panel})
        peta = {x["aturan"]: x["lolos"] for x in hasil}

        self.assertTrue(peta["kelengkapan_panel_panjang"])
        self.assertTrue(peta["keunikan_panel_panjang"])
        self.assertTrue(peta["konsistensi_status_panel_panjang"])

    def test_panel_panjang_mendeteksi_duplikat_dan_status_tidak_sah(self):
        baris = {
            "indikator": "var192",
            "wilayah_kode": 1100,
            "nama_wilayah": "Aceh",
            "periode": "2020",
            "jenis_periode": "tahun",
            "nilai": 10.0,
            "status_sel": "terisi",
            "penanda": None,
        }
        panel = pd.DataFrame([baris, baris])
        panel.loc[1, "status_sel"] = "status_tidak_dikenal"

        hasil = validasi_gold({"panel": panel})
        peta = {x["aturan"]: x["lolos"] for x in hasil}

        self.assertFalse(peta["keunikan_panel_panjang"])
        self.assertFalse(peta["konsistensi_status_panel_panjang"])


class TestValidasiSnapshotRincian(unittest.TestCase):
    def test_rincian_desa_dibandingkan_per_berkas(self):
        baris = []
        for berkas, total, sangat, tertinggal in [
            ("snapshot-lama.json", 10, 4, 6),
            ("snapshot-baru.json", 20, 8, 12),
        ]:
            for rincian, nilai in [
                ("Jumlah", total),
                ("Desa Sangat Tertinggal", sangat),
                ("Desa Tertinggal", tertinggal),
            ]:
                baris.append({
                    "seri_kode": "var2191",
                    "rincian": rincian,
                    "nilai": nilai,
                    "wilayah_kode": 1100,
                    "periode": "2020",
                    "_berkas_raw": berkas,
                })

        hasil = validasi_rincian_desa(pd.DataFrame(baris))[0]

        self.assertTrue(hasil["lolos"])
        self.assertIn("2 kelompok", hasil["keterangan"])


if __name__ == "__main__":
    unittest.main()
