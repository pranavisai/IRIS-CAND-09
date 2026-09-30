
from typing import Protocol


class DataAdapter(Protocol):
    def load_features(self, source: str) -> list[dict]:
        """Load source records in a common GeoJSON feature format."""
        ...