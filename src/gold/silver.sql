CREATE TABLE IF NOT EXISTS seri (
    seri_kode VARCHAR PRIMARY KEY,
    nama VARCHAR NOT NULL,
    satuan VARCHAR NOT NULL,
    sdg_kode VARCHAR,
    cakupan VARCHAR NOT NULL,
    sumber VARCHAR NOT NULL,
    kode_sumber VARCHAR NOT NULL,
    batas_bawah DOUBLE,
    batas_atas DOUBLE,
    rujukan_tahun DOUBLE,
    catatan VARCHAR
);

CREATE TABLE IF NOT EXISTS silver (
    sumber VARCHAR NOT NULL,
    seri_kode VARCHAR NOT NULL REFERENCES seri(seri_kode),
    wilayah_kode INTEGER NOT NULL,
    nama_wilayah VARCHAR NOT NULL,
    periode VARCHAR NOT NULL,
    jenis_periode VARCHAR NOT NULL CHECK (jenis_periode IN ('tahun', 'semester', 'triwulan', 'bulan')),
    rincian VARCHAR NOT NULL,
    nilai DOUBLE NOT NULL,
    satuan VARCHAR NOT NULL,
    sdg_kode VARCHAR,
    batas_bawah DOUBLE,
    batas_atas DOUBLE,
    rujukan_tahun DOUBLE,
    _berkas_raw VARCHAR NOT NULL,
    _sha256_raw VARCHAR NOT NULL CHECK (length(_sha256_raw) = 64),
    PRIMARY KEY (sumber, seri_kode, wilayah_kode, periode, rincian, _berkas_raw),
    CHECK (batas_bawah IS NULL OR batas_atas IS NULL OR batas_bawah <= nilai),
    CHECK (batas_bawah IS NULL OR batas_atas IS NULL OR nilai <= batas_atas),
    CHECK (wilayah_kode = 9999 OR wilayah_kode BETWEEN 1100 AND 9799)
);
