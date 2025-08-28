# Stub do conector Zap Imóveis
# IMPORTANTE: Respeite termos de uso / robots.txt. Prefira APIs/parcerias oficiais.

from typing import List, Dict, Any
from app.comps.connectors.base import BaseConnector, normalize_record

class ZapConnector(BaseConnector):
    name = "zap"

    def search(self, query: dict) -> List[Dict[str, Any]]:
        # TODO: implementar busca real (API/parceria) e fazer parsing
        return []
