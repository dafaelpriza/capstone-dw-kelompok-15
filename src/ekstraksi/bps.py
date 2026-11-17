import json
import re
from pathlib import Path
import pandas as pd
from src.common.manifest import sha256_raw


def _bersihkan_html(teks: str) -> str:
    if not teks:
        return ""
    return re.sub(r"<[^>]+>", " ", str(teks)).strip()


def _urai_payload_bps(payload: dict, rel_path: str, sha_val: str) -> tuple[list[dict], list[dict]]:
    """Membongkar satu blok payload JSON BPS menjadi baris observasi dan metadata variabel."""
    if not isinstance(payload, dict) or "datacontent" not in payload:
        return [], []

    vervar_map = {str(x["val"]): str(x["label"]).strip() for x in payload.get("vervar", [])}
    var_list = payload.get("var", [])
    var_map = {str(x["val"]): str(x["label"]).strip() for x in var_list}
    turvar_map = {str(x["val"]): str(x["label"]).strip() for x in payload.get("turvar", [])}
    tahun_map = {str(x["val"]): str(x["label"]).strip() for x in payload.get("tahun", [])}
    turtahun_map = {str(x["val"]): str(x["label"]).strip() for x in payload.get("turtahun", [])}

    # Simpan metadata var (termasuk var.note untuk bukti patahan sumber Indeks Desa)
    meta_rows = []
    for v in var_list:
        meta_rows.append({
            "seri_kode": f"var{v['val']}",
            "var_val": str(v["val"]),
            "label": str(v.get("label", "")).strip(),
            "unit": str(v.get("unit", "")).strip(),
            "subj": str(v.get("subj", "")).strip(),
            "decimal": v.get("decimal"),
            "note": _bersihkan_html(v.get("note", "")),
            "_berkas_raw": rel_path,
        })

    # Urutan panjang kode yang mungkin di tiap dimensi untuk memotong kunci datacontent
    len_vv = sorted({len(k) for k in vervar_map}, reverse=True)
    len_v = sorted({len(k) for k in var_map}, reverse=True)
    len_tv = sorted({len(k) for k in turvar_map}, reverse=True)
    len_th = sorted({len(k) for k in tahun_map}, reverse=True)
    len_tt = sorted({len(k) for k in turtahun_map}, reverse=True)

    rows = []
    for key, val in payload.get("datacontent", {}).items():
        key_str = str(key)
        cocok = None
        for l1 in len_vv:
            k_vv = key_str[:l1]
            if k_vv not in vervar_map:
                continue
            for l2 in len_v:
                k_v = key_str[l1 : l1 + l2]
                if k_v not in var_map:
                    continue
                for l3 in len_tv:
                    k_tv = key_str[l1 + l2 : l1 + l2 + l3]
                    if k_tv not in turvar_map:
                        continue
                    for l4 in len_th:
                        k_th = key_str[l1 + l2 + l3 : l1 + l2 + l3 + l4]
                        if k_th not in tahun_map:
                            continue
                        k_tt = key_str[l1 + l2 + l3 + l4 :]
                        if k_tt in turtahun_map:
                            cocok = (k_vv, k_v, k_tv, k_th, k_tt)
                            break
                    if cocok:
                        break
                if cocok:
                    break
            if cocok:
                break

        if not cocok:
            raise ValueError(f"Kunci datacontent '{key_str}' di {rel_path} tidak cocok dengan kamus kode.")

        k_vv, k_v, k_tv, k_th, k_tt = cocok
        rows.append({
            "sumber": "bps",
            "seri_kode": f"var{k_v}",
            "vervar_kode": int(k_vv),
            "nama_wilayah": vervar_map[k_vv],
            "turvar_kode": k_tv,
            "rincian": turvar_map[k_tv],
            "tahun_kode": k_th,
            "tahun_label": tahun_map[k_th],
            "turtahun_kode": k_tt,
            "turtahun_label": turtahun_map[k_tt],
            "nilai": val,
            "_berkas_raw": rel_path,
            "_sha256_raw": sha_val,
        })

    return rows, meta_rows


def jalankan() -> dict:
    """Membaca seluruh berkas BPS (3 JSON, 3 CSV, 1 catatan unduhan) tanpa membersihkan nilai."""
    raw_dir = Path("data/raw/bps")
    json_records = []
    meta_records = []
    csv_frames = []
    manifest_asal = {}

    for file_path in sorted(raw_dir.glob("**/*")):
        if not file_path.is_file():
            continue
        rel_path = str(file_path.relative_to("data/raw")).replace("\\", "/")
        sha_val = sha256_raw(rel_path)

        if file_path.name == "manifest_asal.json":
            with open(file_path, "r", encoding="utf-8") as f:
                manifest_asal = json.load(f)
            continue

        if file_path.suffix == ".json":
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            blok_list = data if isinstance(data, list) else [data]
            for blok in blok_list:
                rows, metas = _urai_payload_bps(blok, rel_path, sha_val)
                json_records.extend(rows)
                meta_records.extend(metas)

        elif file_path.suffix == ".csv":
            df_csv = pd.read_csv(file_path)
            seri_kode = next((s for s in ["var192", "var2190", "var2191"] if s.replace("var", "v") in file_path.name), "lainnya")
            df_csv["sumber"] = "bps"
            df_csv["seri_kode"] = seri_kode
            df_csv["_berkas_raw"] = rel_path
            df_csv["_sha256_raw"] = sha_val
            csv_frames.append(df_csv)

    df_json = pd.DataFrame(json_records)
    df_meta = pd.DataFrame(meta_records).drop_duplicates(subset=["seri_kode", "note", "_berkas_raw"]) if meta_records else pd.DataFrame()
    df_csv_all = pd.concat(csv_frames, ignore_index=True) if csv_frames else pd.DataFrame()

    return {
        "bps_json": df_json,
        "bps_csv": df_csv_all,
        "bps_metadata": df_meta,
        "bps_manifest_asal": manifest_asal,
    }