import json

class GeoJSONAdapter:
    def load_features(self, source: str) -> list[dict]:
        with open(source, "r", encoding="utf-8") as f:
            data = json.load(f)

        if data.get("type") != "FeatureCollection":
            raise ValueError("Invalid GeoJSON format")

        features = data.get("features")

        if not isinstance(features, list):
            raise ValueError("GeoJSON features must be a list")

        return features

    