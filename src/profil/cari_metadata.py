import json, glob

for jalur in glob.glob("data/raw/wdi/2026-10-20/metadata/*.json"):
    with open(jalur, encoding="utf-8") as f:
        teks = f.read()
    if "SI.POV.NAHC" not in teks:
        print(jalur, "-> tidak ada")
        continue
    print(jalur, "-> ADA")
    isi = json.loads(teks)

    def cari(x):
        if isinstance(x, dict):
            if x.get("id") == "SI.POV.NAHC":
                print(json.dumps(x, indent=2, ensure_ascii=False)[:3000])
                return True
            return any(cari(v) for v in x.values())
        if isinstance(x, list):
            return any(cari(v) for v in x)
        return False

    cari(isi)