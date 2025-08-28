from typing import List, Dict, Any
from abc import ABC, abstractmethod

STANDARD_FIELDS = [
    "id", "title", "address", "city", "state", "lat", "lon", "url", "source",
    "property_type", "built_area_m2", "land_area_m2", "bedrooms", "bathrooms", "parking",
    "is_rental", "price_total", "price_per_m2", "date_posted", "extras"
]

class BaseConnector(ABC):
    name: str

    @abstractmethod
    def search(self, query: dict) -> List[Dict[str, Any]]:
        """
        Retorna lista de dicionários padronizados (campos em STANDARD_FIELDS).
        """
        pass

def normalize_record(rec: Dict[str, Any]) -> Dict[str, Any]:
    # Garante presença de campos padrão
    for k in STANDARD_FIELDS:
        rec.setdefault(k, None)
    return rec
