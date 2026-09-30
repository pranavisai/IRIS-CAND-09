
from typing import Protocol


# Shared interface for every source-specific adapter in the app.
class DataAdapter(Protocol):
    def load_features(self, source: str) -> list[dict]:
        """Load source records in a common GeoJSON feature format."""
        ...