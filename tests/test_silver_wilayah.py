"""Memastikan kode wilayah BPS mengikuti kode baku pada JSON sumber."""

import unittest

import pandas as pd

from src.silver import _siapkan_bps


class TestKodeWilayahBPS(unittest.TestCase):
    def test_kode_provinsi_tidak_dikalikan_100(self):
        mentah = pd.DataFrame([
            {
                "seri_kode": "var192",
                "vervar_kode": 1100,
                "nama_wilayah": "ACEH",
                "tahun": "2020",
                "tahun_label": "2020",
                "turtahun_label": "Tahun",
                "rincian": "Jumlah",
                "nilai": 14.5,
                "sumber": "BPS",
                "_berkas_raw": "bps/2026-10-20/json/data.json",
                "_sha256_raw": "a" * 64,
            },
            {
                "seri_kode": "var192",
                "vervar_kode": 9999,
                "nama_wilayah": "INDONESIA",
                "tahun": "2020",
                "tahun_label": "2020",
                "turtahun_label": "Tahun",
                "rincian": "Jumlah",
                "nilai": 9.78,
                "sumber": "BPS",
                "_berkas_raw": "bps/2026-10-20/json/data.json",
                "_sha256_raw": "a" * 64,
            },
        ])

        hasil = _siapkan_bps(mentah)

        self.assertEqual(hasil["wilayah_kode"].tolist(), [1100, 9999])
        self.assertEqual(hasil["periode"].tolist(), ["2020", "2020"])
        self.assertEqual(hasil["jenis_periode"].tolist(), ["tahun", "tahun"])


if __name__ == "__main__":
    unittest.main()
