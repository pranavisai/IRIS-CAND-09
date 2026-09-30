
from app.config import Settings


# Check that config values are normalized and validated consistently.
def test_country_and_region_are_normalized():
    settings = Settings(
        country_code="de",
        region_code="nw",
        source_endpoint="fixtures/sites.geojson",
        db_name="iris",
        db_user="iris_user",
        db_password="test",
        db_host="db",
        db_port=5432,
        output_path="/app/output",
    )

    assert settings.country_code == "DE"
    assert settings.region_code == "NW"


def test_database_url():
    settings = Settings(
        country_code="DE",
        region_code="NW",
        source_endpoint="fixtures/sites.geojson",
        db_name="iris",
        db_user="iris_user",
        db_password="test",
        db_host="db",
        db_port=5432,
        output_path="/app/output",
    )

    assert settings.database_url == (
        "postgresql://iris_user:test@db:5432/iris"
    )