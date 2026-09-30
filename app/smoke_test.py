
from app.config import load_settings
from app.db import get_connection


# Quick health checks for the configured PostGIS database and region data.
def main():
    settings = load_settings()

    with get_connection(settings) as conn:
        # Check that PostGIS is available
        result = conn.execute(
            "SELECT PostGIS_Full_Version()"
        ).fetchone()

        if not result:
            raise RuntimeError("PostGIS is not available")

        print("PostGIS is available")

        # Check that the sites table exists and has data
        result = conn.execute(
            """
            SELECT COUNT(*)
            FROM sites
            WHERE country_code = %s AND region_code = %s
            """,
            (settings.country_code, settings.region_code),
        ).fetchone()

        count = result[0]

        if count == 0:
            raise RuntimeError("No sites found for configured region")

        print(f"Found {count} sites")

        # Check for missing geometries or country codes
        result = conn.execute(
            """
            SELECT COUNT(*)
            FROM sites
            WHERE country_code = %s
              AND region_code = %s
              AND (geom IS NULL OR country_code IS NULL)
            """,
            (settings.country_code, settings.region_code),
        ).fetchone()

        if result[0] != 0:
            raise RuntimeError("Invalid site records found")

        # Check the geometry SRID
        result = conn.execute(
            """
            SELECT COUNT(*)
            FROM sites
            WHERE country_code = %s
              AND region_code = %s
              AND ST_SRID(geom) != 4326
            """,
            (settings.country_code, settings.region_code),
        ).fetchone()

        if result[0] != 0:
            raise RuntimeError("Unexpected geometry SRID")

    print("Smoke test passed")


if __name__ == "__main__":
    main()