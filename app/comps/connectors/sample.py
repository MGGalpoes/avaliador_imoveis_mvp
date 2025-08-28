from typing import List, Dict, Any
import json, os, datetime
from app.comps.connectors.base import BaseConnector, normalize_record

DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "..", "data", "sample_listings.json")
DATA_PATH = os.path.abspath(DATA_PATH)

class SampleConnector(BaseConnector):
    name = "sample"

    def search(self, query: dict) -> List[Dict[str, Any]]:
        # Ignora o query para o MVP: retorna dados estáticos e filtra por tipo
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        items = []
        ptype = query.get("property_type")
        for rec in data:
            if ptype and rec.get("property_type") != ptype:
                continue
            items.append(normalize_record(rec))
        return items
