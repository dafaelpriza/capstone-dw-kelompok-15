"""Kamus wilayah: susunan 38 provinsi tahun 2025 dan kode Indonesia dari setiap sumber.

Aturan Sprint 0 (log K-001): wilayah_kode = kode dua digit BPS x 100, Indonesia = 9999.
Angka sebelum sebuah provinsi dibentuk tidak dipecah dari provinsi induknya; sel provinsi baru
pada tahun-tahun itu dikategorikan "belum_ada" di grid, bukan missing.
"""
import re

INDONESIA = 9999

# kode: (nama baku, tahun pertama provinsi punya data setahun penuh)
PROVINSI = {
    1100: ("Aceh", 1950), 1200: ("Sumatera Utara", 1950), 1300: ("Sumatera Barat", 1958),
    1400: ("Riau", 1958), 1500: ("Jambi", 1958), 1600: ("Sumatera Selatan", 1950),
    1700: ("Bengkulu", 1968), 1800: ("Lampung", 1964), 1900: ("Kepulauan Bangka Belitung", 2001),
    2100: ("Kepulauan Riau", 2003), 3100: ("DKI Jakarta", 1950), 3200: ("Jawa Barat", 1950),
    3300: ("Jawa Tengah", 1950), 3400: ("DI Yogyakarta", 1950), 3500: ("Jawa Timur", 1950),
    3600: ("Banten", 2001), 5100: ("Bali", 1958), 5200: ("Nusa Tenggara Barat", 1958),
    5300: ("Nusa Tenggara Timur", 1958), 6100: ("Kalimantan Barat", 1956), 6200: ("Kalimantan Tengah", 1958),
    6300: ("Kalimantan Selatan", 1956), 6400: ("Kalimantan Timur", 1956), 6500: ("Kalimantan Utara", 2013),
    7100: ("Sulawesi Utara", 1964), 7200: ("Sulawesi Tengah", 1964), 7300: ("Sulawesi Selatan", 1964),
    7400: ("Sulawesi Tenggara", 1964), 7500: ("Gorontalo", 2001), 7600: ("Sulawesi Barat", 2005),
    8100: ("Maluku", 1950), 8200: ("Maluku Utara", 2000), 9100: ("Papua Barat", 2004),
    9200: ("Papua Barat Daya", 2023), 9400: ("Papua", 1969), 9500: ("Papua Selatan", 2023),
    9600: ("Papua Tengah", 2023), 9700: ("Papua Pegunungan", 2023),
}

# Provinsi pemekaran -> provinsi induk.
INDUK = {
    1900: 1600, 2100: 1400, 3600: 3200, 6500: 6400,
    7500: 7100, 7600: 7300, 8200: 8100, 9100: 9400,
    9200: 9100, 9500: 9400, 9600: 9400, 9700: 9400,
}

NAMA = {kode: nama for kode, (nama, _) in PROVINSI.items()} | {INDONESIA: "Indonesia"}

ALIAS = {
    ("PAPUA", "PENGUNUNGAN"): 9700,
    ("D", "I", "YOGYAKARTA"): 3400,
    ("DAERAH", "ISTIMEWA", "YOGYAKARTA"): 3400,
    ("DKI", "JAKARTA", "RAYA"): 3100,
    ("JAKARTA", "RAYA"): 3100,
    ("NANGGROE", "ACEH", "DARUSSALAM"): 1100,
    ("P", "A", "P", "U", "A"): 9400,
}


def normalisasi_kode(kode) -> int:
    """Menyamakan kode wilayah Silver (termasuk 110000/999900) ke kode baku 1100..9700 atau 9999."""
    val = int(kode)
    if val >= 10000:
        return val // 100
    return val


def sudah_ada(kode: int, tahun) -> bool:
    """True bila provinsi `kode` sudah dibentuk pada `tahun` (Indonesia selalu True)."""
    if kode == INDONESIA:
        return True
    return int(str(tahun)[:4]) >= PROVINSI[kode][1]


def _baku(nama: str) -> list[str]:
    t = re.sub(r"<[^>]+>", "", str(nama)).upper().replace("KEP. ", "KEPULAUAN ")
    return re.sub(r"[^A-Z ]+", " ", t).split()


def dari_nama(nama: str) -> int:
    """Mengubah nama wilayah BPS menjadi kode baku 1100..9700 atau 9999."""
    k = tuple(_baku(nama))
    if k[:1] == ("PROVINSI",):
        k = k[1:]
    if k == ("INDONESIA",):
        return INDONESIA
    for kode, n in NAMA.items():
        if tuple(_baku(n)) == k:
            return kode
    if k in ALIAS:
        return ALIAS[k]
    raise KeyError(f"nama wilayah {nama!r} belum ada di kamus")
