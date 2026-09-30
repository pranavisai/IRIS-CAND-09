
import json
from datetime import date
from pathlib import Path

from app.config import load_settings
from app.migrate import run_migrations
from app.db import get_connection
from app.adapters.geojson import GeoJSONAdapter
import logging
from app.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


def validate_feature(feature, country, region):
    props = feature.get("properties") or {}
    geom = feature.get("geometry") or {}

    source_id = props.get("source_id")
    country_code = props.get("country_code")
    region_code = props.get("region_code")
    site_name = props.get("site_name")
    source_date = props.get("source_date")

    if not source_id or not country_code or not region_code or not site_name:
        raise ValueError("Required site properties are missing")

    if country_code != country:
        raise ValueError(f"Country mismatch for {source_id}")

    if region_code != region:
        raise ValueError(f"Region mismatch for {source_id}")

    if source_date:
        try:
            date.fromisoformat(source_date)
        except ValueError:
            raise ValueError(f"Invalid date for {source_id}")

    if geom.get("type") != "Point":
        raise ValueError(f"Invalid geometry for {source_id}")

    coords = geom.get("coordinates", [])
    if len(coords) != 2:
        raise ValueError(f"Invalid coordinates for {source_id}")

    lon, lat = coords

    if not (-180 <= lon <= 180 and -90 <= lat <= 90):
        raise ValueError(f"Coordinates out of range for {source_id}")

    return {
        "source_id": source_id,
        "country_code": country_code,
        "region_code": region_code,
        "site_name": site_name,
        "source_date": source_date,
        "longitude": lon,
        "latitude": lat
    }


def process_features(features, settings):
    sites = []

    for feature in features:
        sites.append(
            validate_feature(
                feature, settings.country_code, settings.region_code
            )
        )

    with get_connection(settings) as conn:
        for site in sites:
            conn.execute("""
                INSERT INTO sites (
                    country_code, source_id, region_code,
                    site_name, geom, source_date
                )
                VALUES (
                    %(country_code)s, %(source_id)s, %(region_code)s,
                    %(site_name)s, ST_SetSRID(ST_MakePoint(%(longitude)s, %(latitude)s), 4326),%(source_date)s
                )
                ON CONFLICT (country_code, source_id)
                DO UPDATE SET
                    region_code = EXCLUDED.region_code,
                    site_name = EXCLUDED.site_name,
                    geom = EXCLUDED.geom,
                    source_date = EXCLUDED.source_date
            """, site)

    return len(sites)


def main():
    settings = load_settings()
    run_migrations()

    path = Path(settings.source_endpoint)
    if not path.is_absolute():
        path = Path("/iris-cand-09") / path

    adapter = GeoJSONAdapter()
    features = adapter.load_features(str(path))
    count = process_features(features, settings)

    settings.output_path.mkdir(parents=True, exist_ok=True)

    summary = {
        "country_code": settings.country_code,
        "region_code": settings.region_code,
        "source_endpoint": settings.source_endpoint,
        "records_processed": count,
        "source_date": "2026-09-01",
        "status": "completed"
    }

    output_file = settings.output_path / "summary.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    logger.info("Processed %s sites", count)
    logger.info("Summary written to %s", output_file)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logger.exception("Worker failed")
        raise