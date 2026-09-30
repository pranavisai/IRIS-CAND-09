CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE IF NOT EXISTS sites (
    country_code CHAR(2) NOT NULL,
    source_id TEXT NOT NULL,
    region_code TEXT NOT NULL,
    site_name TEXT NOT NULL,
    geom geometry(POINT, 4326) NOT NULL,
    source_date DATE,

    PRIMARY KEY (country_code, source_id),

    CONSTRAINT valid_country_code
        CHECK (country_code ~ '^[A-Z]{2}$'),

    CONSTRAINT valid_region_code
        CHECK (length(trim(region_code)) > 0),

    CONSTRAINT valid_site_name
        CHECK (length(trim(site_name)) > 0),

    CONSTRAINT valid_geometry
        CHECK (ST_IsValid(geom))
);

CREATE INDEX IF NOT EXISTS idx_sites_geom
    ON sites USING GIST (geom);

CREATE INDEX IF NOT EXISTS idx_sites_country_region
    ON sites (country_code, region_code);