import json

berkas = "wdi/2026-10-20/data/kelompok-06-hal-01.json"
with open(f"data/raw/{berkas}", encoding="utf-8") as f:
    isi = json.load(f)

print(type(isi), len(isi))
print(isi[0])        # metadata halaman
print(isi[1][:2])    # dua pengamatan pertama