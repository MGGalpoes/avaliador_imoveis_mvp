# Stub do conector OLX
# IMPORTANTE: Respeite termos de uso / robots.txt. Prefira APIs/parcerias oficiais.
# Estrutura esperada: retornar uma lista de dicionários padronizados (ver base.py).

from typing import List, Dict, Any
from app.comps.connectors.base import BaseConnector, normalize_record

class OLXConnector(BaseConnector):
    name = "olx"

    def search(self, query: dict) -> List[Dict[str, Any]]:
        # TODO: implementar busca real (API/parceria) e fazer parsing
        # Exemplo de retorno vazio para o MVP
        return []
