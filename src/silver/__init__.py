"""Tahap 2–4 — Profil, pembersihan, dan penyeragaman ke Silver (pertemuan II–VII). Milik tim.

Keluaran: data/silver/silver.parquet dengan skema minimal di src/common/skema.py.
Satu baris = satu seri x wilayah x periode x rincian x berkas sumber. Nilai dari sumber berbeda
TIDAK digabung di sini. Setiap keputusan pembersihan dicatat di log-keputusan.csv.
"""

'''
def jalankan(mentah):
    """Terima keluaran tahap 1, tulis dan kembalikan DataFrame Silver."""
    raise NotImplementedError("Tahap 2–4: profil, missing, outlier/patahan, duplikat, format periode dan wilayah")
'''

"""Tahap 2–4 — Profil, pembersihan, dan penyeragaman ke Silver."""
import pandas as pd
from src.silver.metadata import (
    terapkan_satuan_dan_periode,
    tulis_dokumentasi_metadata,
    verifikasi_dari_mentah,
)


def jalankan(mentah: dict) -> pd.DataFrame:
    """Terima keluaran tahap 1, verifikasi metadata, dan siapkan penyeragaman Silver."""
    # 1. Verifikasi metadata dari berkas mentah & tulis docs/seri.csv + reports/metadata.md
    df_seri = verifikasi_dari_mentah(mentah)
    tulis_dokumentasi_metadata(df_seri)

    # 2. Gabungkan sumber mentah untuk diterapkan satuan baku & format periode
    # (Catatan: langkah pembersihan grid/anomali & penyimpanan silver.parquet menyusul dari komponen Pembersihan)
    raise NotImplementedError(
        "Metadata & satuan baku siap (docs/seri.csv & reports/metadata.md dibuat). "
        "Lanjutkan penggabungan pembersihan & pembentukan data/silver/silver.parquet."
    )