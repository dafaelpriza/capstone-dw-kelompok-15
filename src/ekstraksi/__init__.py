from fnmatch import fnmatch
import pandas as pd

from src import konfigurasi as K
from src.common.manifest import baca as baca_manifest
from src.ekstraksi import bps, wdi
from src.laporan import catat, tabel_md, tulis

POLA = [
    ("bps/*/json/*.json", "bps_json", "data"),
    ("bps/*/manifest_asal.json", "bps_manifest_asal", "meta"),
    ("bps/*/*.csv", "bps_csv", "data"),
    ("wdi/*/data/*.json", "wdi_data", "data"),
    ("wdi/*/metadata/sumber.json", "wdi_sumber", "meta"),
    ("wdi/*/metadata/*_indikator.json", "wdi_meta", "meta"),
]


def _seri(sumber):
    return [k for k, s in K.SERI.items() if s["sumber"] == sumber]


def jalankan():
    kumpul = {nama: [] for _, nama, _ in POLA}
    bps.tak_terbaca.clear()
    hitung = []

    for berkas in baca_manifest():
        cocok = next(
            ((nama, peran) for pola, nama, peran in POLA if fnmatch(berkas, pola)),
            None,
        )
        if cocok is None:
            continue
        nama, peran = cocok
        if nama == "bps_json":
            df, meta = bps.baca_json(berkas)
            kumpul["bps_meta"] = kumpul.get("bps_meta", []) + [meta]
        elif nama == "bps_csv":
            df = bps.baca_csv(berkas)
        elif nama == "bps_manifest_asal":
            df = bps.baca_manifest_asal(berkas)
        elif nama == "wdi_data":
            df, _ = wdi.baca_data(berkas, _seri("wdi"))
        else:
            df = wdi.baca_metadata(berkas, _seri("wdi"))

        kumpul.setdefault(nama, []).append(df)
        hitung.append({
            "berkas": berkas,
            "pembaca": nama,
            "peran": peran,
            "baris": len(df),
        })

    sisa = sorted(set(baca_manifest()) - {h["berkas"] for h in hitung})
    assert not sisa, f"berkas MANIFEST belum punya pembaca: {sisa}"

    hasil = {
        nama: pd.concat(daftar, ignore_index=True)
        for nama, daftar in kumpul.items()
        if daftar
    }
    hasil["_hitung"] = pd.DataFrame(hitung)
    t = hasil["_hitung"]
    data = t[t["peran"] == "data"]

    catat(
        kunci_bps_tak_terbaca=len(bps.tak_terbaca),
        berkas_manifest=len(set(baca_manifest())),
        berkas_dibaca=len(t),
        berkas_data=len(data),
        baris_mentah=int(data["baris"].sum()),
    )
    tulis(
        "ekstraksi.md",
        "\n\n".join([
            "# Ekstraksi: jumlah baris per berkas",
            tabel_md(t),
            f"Jumlah: {len(t)} berkas dari {len(set(baca_manifest()))} di MANIFEST.",
        ]),
    )
    return hasil