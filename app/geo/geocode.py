from typing import Optional, Tuple
from app.config import CITY_CENTERS
import math

def geocode(address: str, city: str, state: str, country: str) -> Optional[Tuple[float, float]]:
    """
    Geocodificação simplificada: tenta *match* de cidade.
    Em produção, substitua por Nominatim/OSM ou Google Geocoding API.
    """
    if city in CITY_CENTERS:
        return CITY_CENTERS[city]
    # fallback trivial: retorna None se não souber
    return None

def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = (math.sin(dphi/2)**2 +
         math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2)
    return 2 * R * math.asin(math.sqrt(a))
