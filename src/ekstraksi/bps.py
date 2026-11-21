import json
import pandas as pd
from src.common.manifest import RAW, sha256_raw

tak_terbaca = []


def _kamus(daftar):
    return {str(x["val"]): x["label"] for x in daftar}


def potong_kunci(kunci, kode_var, wilayah, rincian, tahun, periode):
    panjang = lambda kamus: sorted({len(k) for k in kamus})
    sah = []
    for lw in panjang(wilayah):
        for lr in panjang(rincian):
            for lp in panjang(periode):
                lt = len(kunci) - lw - len(kode_var) - lr - lp
                if lt not in panjang(tahun):
                    continue
                i = 0
                k_wil = kunci[i : i + lw]; i += lw
                k_var = kunci[i : i + len(kode_var)]; i += len(kode_var)
                k_rin = kunci[i : i + lr]; i += lr
                k_th = kunci[i : i + lt]; i += lt
                k_per = kunci[i:]
                if (
                    k_var == kode_var
                    and k_wil in wilayah
                    and k_rin in rincian
                    and k_th in tahun
                    and k_per in periode
                ):
                    sah.append((k_wil, k_rin, k_th, k_per))
    if len(sah) > 1:
        raise ValueError(f"kunci {kunci}: {len(sah)} cara memotong")
    return sah[0] if sah else None


def baca_json(jalur):
    halaman_semua = json.loads((RAW / jalur).read_text(encoding="utf-8"))
    baris, meta = [], []
    for no_hal, hal in enumerate(halaman_semua, start=1):
        var = hal["var"][0]
        wilayah = _kamus(hal["vervar"])
        rincian = _kamus(hal["turvar"])
        tahun = _kamus(hal["tahun"])
        periode = _kamus(hal["turtahun"])
        kode_var = str(var["val"])
        for kunci_data, nilai in hal["datacontent"].items():
            potong = potong_kunci(kunci_data, kode_var, wilayah, rincian, tahun, periode)
            if potong is None:
                tak_terbaca.append({
                    "_berkas_raw": jalur,
                    "halaman": no_hal,
                    "kunci": kunci_data,
                    "nilai": nilai,
                })
                continue
            k_wil, k_rin, k_th, k_per = potong
            baris.append({
                "var_id": kode_var,
                "wilayah_id": k_wil,
                "wilayah": wilayah[k_wil],
                "turvar_id": k_rin,
                "turvar": rincian[k_rin],
                "tahun_id": k_th,
                "tahun": tahun[k_th],
                "turtahun_id": k_per,
                "turtahun": periode[k_per],
                "nilai": nilai,
                "_halaman": no_hal,
            })
        meta.append({
            "var_id": kode_var,
            "judul": var["label"],
            "satuan": var.get("unit", ""),
            "catatan": var.get("note", ""),
            "definisi": var.get("def", ""),
            "desimal": var.get("decimal"),
            "last_update": hal.get("last_update"),
            "tahun_terbit": ",".join(tahun.values()),
            "_halaman": no_hal,
        })
    df = pd.DataFrame(baris)
    df["_berkas_raw"] = jalur
    df["_sha256_raw"] = sha256_raw(jalur)
    return df, pd.DataFrame(meta)


def baca_csv(jalur):
    df = pd.read_csv(RAW / jalur, dtype=str, keep_default_na=False, encoding="utf-8")
    df["_berkas_raw"] = jalur
    df["_sha256_raw"] = sha256_raw(jalur)
    return df


def baca_manifest_asal(jalur):
    isi = json.loads((RAW / jalur).read_text(encoding="utf-8"))
    daftar = isi if isinstance(isi, list) else [isi]
    df = pd.DataFrame(daftar)
    df["_berkas_raw"] = jalur
    df["_sha256_raw"] = sha256_raw(jalur)
    return df