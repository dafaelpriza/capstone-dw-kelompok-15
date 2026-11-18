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