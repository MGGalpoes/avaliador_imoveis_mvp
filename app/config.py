from dataclasses import dataclass

@dataclass
class AppConfig:
    currency: str = "BRL"
    default_radius_km: float = 15.0
    max_radius_km: float = 35.0
    min_comps: int = 6
    target_property_type: str = "galpao"  # padrão para o nicho industrial
    # Pesos (alpha) para atenuação exponencial
    alpha_distance: float = 0.12   # quanto maior, mais penaliza distância
    alpha_recency: float = 0.10    # por mês
    alpha_area_diff: float = 1.0   # por fração de diferença relativa

# Centros aproximados (latitude, longitude) para fallback por cidade
CITY_CENTERS = {
    "Contagem": (-19.931, -44.053),
    "Betim": (-19.966, -44.196),
    "Vespasiano": (-19.689, -43.923),
    "Santa Luzia": (-19.769, -43.851),
    "Lagoa Santa": (-19.639, -43.893),
    "Belo Horizonte": (-19.922, -43.945),
}
