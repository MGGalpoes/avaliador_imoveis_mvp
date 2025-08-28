from typing import List, Dict, Any, Optional
from app.comps.connectors.sample import SampleConnector
from app.comps.connectors.olx_stub import OLXConnector
from app.comps.connectors.vivareal_stub import VivaRealConnector
from app.comps.connectors.zap_stub import ZapConnector
from app.geo.geocode import haversine_km

CONNECTORS = [
    SampleConnector(),
    OLXConnector(),
    VivaRealConnector(),
    ZapConnector(),
]

def get_comps(query: dict,
              subject_lat: Optional[float] = None,
              subject_lon: Optional[float] = None,
              radius_km: Optional[float] = None) -> List[Dict[str, Any]]:
    all_items: List[Dict[str, Any]] = []
    for c in CONNECTORS:
        try:
            items = c.search(query)
            for it in items:
                it["source"] = it.get("source") or c.name
            all_items.extend(items)
        except Exception:
            # conector falhou, segue o jogo
            continue

    # Se tiver lat/lon do assunto e do comp, calcula distância e filtra por raio
    for it in all_items:
        lat, lon = it.get("lat"), it.get("lon")
        if subject_lat is not None and subject_lon is not None and lat is not None and lon is not None:
            it["distance_km"] = haversine_km(subject_lat, subject_lon, lat, lon)
        else:
            it["distance_km"] = None

    if radius_km is not None:
        out = []
        for it in all_items:
            d = it.get("distance_km")
            if d is None or d <= radius_km:
                out.append(it)
        all_items = out

    return all_items
