"""Konfigurasi metadata seri, satuan baku, kode SDG, dan aturan periode Kasus 15."""

# Pemetaan koreksi katalog awal (data/KASUS.md) berdasarkan metadata berkas mentah
KATALOG_SERI = {
    "var192": {
        "sumber": "BPS",
        "nama_seri": "Persentase Penduduk Miskin Menurut Provinsi dan Daerah",
        "satuan_awal": "persen",
        "satuan": "persen",
        "kode_sdg_awal": "10.1.1",
        "kode_sdg": "1.2.1",
        "butir_nasional": "10.1.1(f)",
        "sumber_metadata": "bps/2026-10-20/manifest_asal.json & json/sdg10_10_1_1_f_v192.json",
        "catatan": "Indikator global P0 terhadap garis kemiskinan nasional adalah SDG 1.2.1; berkas dinamai sdg10_10_1_1_f karena dipakai sebagai butir nasional 10.1.1(f).",
    },
    "var2190": {
        "sumber": "BPS",
        "nama_seri": "Jumlah Desa Mandiri Menurut Provinsi",
        "satuan_awal": "tidak_ada",
        "satuan": "desa",
        "kode_sdg_awal": "10.1.1",
        "kode_sdg": "10.1.1(d)",
        "butir_nasional": "10.1.1(d)",
        "sumber_metadata": "bps/2026-10-20/manifest_asal.json & json/sdg10_10_1_1_d_v2190.json",
        "catatan": "Satuan pada metadata awal tidak_ada/kosong; ditetapkan menjadi 'desa' sesuai judul tabel cacah desa dan rentang nilai bilangan bulat.",
    },
    "var2191": {
        "sumber": "BPS",
        "nama_seri": "Jumlah Desa Tertinggal Menurut Provinsi",
        "satuan_awal": "tidak_ada",
        "satuan": "desa",
        "kode_sdg_awal": "10.1.1",
        "kode_sdg": "10.1.1(c)",
        "butir_nasional": "10.1.1(c)",
        "sumber_metadata": "bps/2026-10-20/manifest_asal.json & json/sdg10_10_1_1_c_v2191.json",
        "catatan": "Satuan pada metadata awal tidak_ada/kosong; ditetapkan menjadi 'desa' sesuai judul tabel cacah desa (rincian: sangat tertinggal, tertinggal, jumlah).",
    },
    "SI.POV.NAHC": {
        "sumber": "WDI",
        "nama_seri": "Poverty headcount ratio at national poverty lines (% of population)",
        "satuan_awal": "tidak_ada",
        "satuan": "persen",
        "kode_sdg_awal": "10.1.1",
        "kode_sdg": "1.2.1",
        "butir_nasional": "10.1.1(f)",
        "sumber_metadata": "wdi/2026-10-20/metadata/sumber2_indikator.json & sumber46_indikator.json",
        "catatan": "Satuan pada katalog awal kosong; metadata WDI mencantumkan '% of population' (ditetapkan menjadi 'persen') dan termasuk dalam target indikator SDG 1.2.1.",
    },
}

# Pemetaan turtahun BPS ke format periode baku Silver (tanpa merata-ratakan semester ke tahunan)
PEMETAAN_TURTAHUN_BPS = {
    "Tahun": ("tahunan", ""),
    "Tahunan": ("tahunan", ""),
    "Semester 1": ("semester", "-S1"),
    "Semester 1 (Maret)": ("semester", "-S1"),
    "Maret": ("semester", "-S1"),
    "Semester 2": ("semester", "-S2"),
    "Semester 2 (September)": ("semester", "-S2"),
    "September": ("semester", "-S2"),
}

# ------------------------------------------------------------------ Tahap 4 (Persiapan Gold)
SERI = {
    "var192": dict(sumber="bps", tingkat="provinsi", satuan="persen", sdg="1.2.1",
                   nama="Persentase penduduk miskin (P0) menurut daerah"),
    "var2190": dict(sumber="bps", tingkat="provinsi", satuan="desa", sdg="10.1.1(d)",
                    nama="Jumlah desa mandiri"),
    "var2191": dict(sumber="bps", tingkat="provinsi", satuan="desa", sdg="10.1.1(c)",
                    nama="Jumlah desa tertinggal dan sangat tertinggal"),
    "SI.POV.NAHC": dict(sumber="wdi", tingkat="nasional", satuan="persen", sdg="1.2.1",
                        nama="Poverty headcount ratio at national poverty lines (% of population)"),
}

# Penyeragaman label rincian di Gold (rincian lain tetap di Silver dan tidak masuk panel utama)
RINCIAN_TOTAL_BPS = {"tidak ada", "jumlah", "total"}
RINCIAN_BPS = {
    "var192": ("daerah", {"Perkotaan": "URBAN", "Perdesaan": "RURAL"}),
    "var2191": ("status_desa", {"Desa Sangat Tertinggal": "sangat_tertinggal", "Desa Tertinggal": "tertinggal"}),
}

# Deret utama yang masuk panel Gold: tepat satu indikator per provinsi x periode
DERET = {
    "var192": ["total"],
    "var2190": ["total"],
    "var2191": ["total"],
}

# Urutan prioritas berkas bila satu sel memiliki lebih dari satu berkas sumber
URUTAN_BERKAS = [
    ("bps/*/json/*.json", "JSON WebAPI BPS"),
    ("bps/*/*.csv", "CSV BPS"),
]

# K-005: DKI Jakarta tidak punya desa (seluruh wilayahnya kelurahan), tidak dinilai Indeks Desa
TIDAK_TERBIT = {
    (s, 3100, str(th)): "DKI Jakarta tidak punya desa (seluruh wilayahnya kelurahan); tidak ada di ketiga tahun Indeks Desa"
    for s in ("var2190", "var2191")
    for th in (2019, 2020, 2021)
}

# K-012 / var.note: pergantian sumber & definisi Indeks Desa, serta K-006 patahan 2008 var192
_ID_DESA = {
    "2020": "var.note: Indeks Desa 2020 dari Updating Podes 2020 dan daftar desa Kepmendagri 146/2020",
    "2021": "var.note: Indeks Desa 2021 dari Pendataan Podes 2021 (2020: Updating Podes 2020)",
}
PATAHAN_DEFINISI = {
    "var192": {"2008": "K-006: penurunan serentak pada tahun 2008 di hampir seluruh provinsi"},
    "var2190": _ID_DESA,
    "var2191": _ID_DESA,
}

# Hook kolom turunan opsional di Gold; nilai asli tetap dipertahankan
GOLD_TURUNAN = {}
