
import pytest

from app.worker import validate_feature


# A valid feature payload used across the validation tests.
@pytest.fixture
def valid_feature():
    return {
        "type": "Feature",
        "properties": {
            "source_id": "SITE-001",
            "country_code": "DE",
            "region_code": "NW",
            "site_name": "Pilot Site A",
            "source_date": "2026-09-01",
        },
        "geometry": {
            "type": "Point",
            "coordinates": [7.4653, 51.5136],
        },
    }


def test_valid_feature(valid_feature):
    result = validate_feature(valid_feature, "DE", "NW")

    assert result["source_id"] == "SITE-001"
    assert result["longitude"] == 7.4653
    assert result["latitude"] == 51.5136


def test_wrong_country_is_rejected(valid_feature):
    with pytest.raises(ValueError, match="Country mismatch"):
        validate_feature(valid_feature, "FR", "NW")


def test_wrong_region_is_rejected(valid_feature):
    with pytest.raises(ValueError, match="Region mismatch"):
        validate_feature(valid_feature, "DE", "BE")


def test_invalid_geometry_is_rejected(valid_feature):
    valid_feature["geometry"]["type"] = "Polygon"

    with pytest.raises(ValueError, match="Invalid geometry"):
        validate_feature(valid_feature, "DE", "NW")


def test_out_of_range_coordinates_are_rejected(valid_feature):
    valid_feature["geometry"]["coordinates"] = [200, 51]

    with pytest.raises(ValueError, match="Coordinates out of range"):
        validate_feature(valid_feature, "DE", "NW")


def test_invalid_date_is_rejected(valid_feature):
    valid_feature["properties"]["source_date"] = "not-a-date"

    with pytest.raises(ValueError, match="Invalid date"):
        validate_feature(valid_feature, "DE", "NW")