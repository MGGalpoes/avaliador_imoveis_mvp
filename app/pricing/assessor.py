from typing import Dict, Any, List, Optional
from app.schemas import PropertyInput
from app.config import AppConfig
from app.geo.geocode import geocode
from app.comps.aggregator import get_comps
from app.utils.filters import filter_comps
from app.model.hedonic import estimate_from_comps
from app.vision.features import photos_score
from datetime import datetime

def _adjust_by_image(ppm2: float, img_score: float) -> float:
    # Ajuste leve: -5% a +5% conforme score (0→-5%, 0.5→0%, 1→+5%)
    factor = (img_score - 0.5) * 0.10
    return ppm2 * (1.0 + factor)

def assess(payload: Dict[str, Any]) -> Dict[str, Any]:
    cfg = AppConfig()
    subject = PropertyInput(**payload)
    # Geocodificação (simplificada)
    latlon = geocode(subject.address, subject.city, subject.state, subject.country)
    lat, lon = (latlon if latlon else (None, None))

    # Fotografia -> score
    photo_paths = [p.path for p in (subject.photos or []) if p.path]
    img_score = photos_score(photo_paths)

    # Consulta de comparáveis (conectores) — início com raio padrão
    query = {
        "city": subject.city,
        "state": subject.state,
        "country": subject.country,
        "property_type": subject.property_type,
    }
    comps_all = get_comps(query, lat, lon, cfg.default_radius_km)

    # Filtros básicos por área (~0.5x a 2.0x do assunto)
    min_built = subject.built_area_m2 * 0.5
    max_built = subject.built_area_m2 * 2.0
    comps_all = filter_comps(comps_all, property_type=subject.property_type, min_built=min_built, max_built=max_built)

    # Se insuficiente, ampliar raio
    radius = cfg.default_radius_km
    while len(comps_all) < cfg.min_comps and radius < cfg.max_radius_km:
        radius = min(radius + 5.0, cfg.max_radius_km)
        comps_all = get_comps(query, lat, lon, radius)
        comps_all = filter_comps(comps_all, property_type=subject.property_type, min_built=min_built, max_built=max_built)

    # Divide em aluguel vs venda
    comps_rental = [c for c in comps_all if c.get("is_rental") is True]
    comps_sale   = [c for c in comps_all if c.get("is_rental") is False]

    subj_dict = subject.model_dump()
    subj_dict.update({"lat": lat, "lon": lon})

    # Avalia aluguel
    rent_ranges, comps_r_w = estimate_from_comps(
        subj_dict, comps_rental,
        cfg.alpha_distance, cfg.alpha_recency, cfg.alpha_area_diff
    )

    # Avalia venda
    sale_ranges, comps_s_w = estimate_from_comps(
        subj_dict, comps_sale,
        cfg.alpha_distance, cfg.alpha_recency, cfg.alpha_area_diff
    )

    # Ajuste por qualidade de fotos (leve)
    rent_low, rent_p50, rent_high = [_adjust_by_image(x, img_score) for x in (rent_ranges["low"], rent_ranges["p50"], rent_ranges["high"])]
    sale_low, sale_p50, sale_high = [_adjust_by_image(x, img_score) for x in (sale_ranges["low"], sale_ranges["p50"], sale_ranges["high"])]

    built = max(subject.built_area_m2, 1.0)

    result = {
        "address_geocoded": {
            "address": subject.address,
            "city": subject.city, "state": subject.state, "country": subject.country,
            "lat": lat, "lon": lon
        },
        "image_quality_score": img_score,
        "comps_used": (comps_r_w + comps_s_w),
        "rental": {
            "per_m2_low": rent_low,
            "per_m2_target": rent_p50,
            "per_m2_high": rent_high,
            "total_low": rent_low * built,
            "total_target": rent_p50 * built,
            "total_high": rent_high * built,
        },
        "sale": {
            "per_m2_low": sale_low,
            "per_m2_target": sale_p50,
            "per_m2_high": sale_high,
            "total_low": sale_low * built,
            "total_target": sale_p50 * built,
            "total_high": sale_high * built,
        },
        "explainability": {
            "weights": {
                "alpha_distance": cfg.alpha_distance,
                "alpha_recency": cfg.alpha_recency,
                "alpha_area_diff": cfg.alpha_area_diff,
            },
            "filters": {
                "radius_km": radius,
                "min_built": min_built,
                "max_built": max_built,
            },
            "notes": [
                "Faixas baseadas em quantis ponderados (25/50/75%).",
                "Ajuste leve por qualidade das fotos (±5% máx.).",
            ]
        }
    }
    return result
