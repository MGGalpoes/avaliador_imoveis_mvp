from typing import Dict, Any
from app.schemas import PropertyInput
from app.config import AppConfig
from app.geo.geocode import geocode
from app.comps.aggregator import get_comps
from app.utils.filters import filter_comps
from app.model.hedonic import estimate_from_comps
from app.vision.features import photos_score
import os, joblib, numpy as np

def _adjust_by_image(ppm2: float, img_score: float) -> float:
    factor = (img_score - 0.5) * 0.10  # ±5%
    return ppm2 * (1.0 + factor)

def _featurize(subject: dict):
    return np.array([
        [
            subject.get("built_area_m2") or 0,
            subject.get("land_area_m2") or 0,
            subject.get("ceiling_height_m") or 0,
            subject.get("energy_capacity_kva") or 0,
            subject.get("dock_doors") or 0,
            1.0 if (subject.get("city") or "").lower()=="contagem" else 0.0,
            1.0 if (subject.get("city") or "").lower()=="betim" else 0.0,
            1.0 if (subject.get("city") or "").lower()=="vespasiano" else 0.0,
            1.0 if (subject.get("city") or "").lower()=="santa luzia" else 0.0,
            1.0 if (subject.get("city") or "").lower()=="lagoa santa" else 0.0,
        ]
    ])

def assess(payload: Dict[str, Any]) -> Dict[str, Any]:
    cfg = AppConfig()
    subject = PropertyInput(**payload)
    latlon = geocode(subject.address, subject.city, subject.state, subject.country)
    lat, lon = (latlon if latlon else (None, None))

    photo_paths = [p.path for p in (subject.photos or []) if p.path]
    img_score = photos_score(photo_paths)

    query = {
        "city": subject.city,
        "state": subject.state,
        "country": subject.country,
        "property_type": subject.property_type,
    }
    comps_all = get_comps(query, lat, lon, cfg.default_radius_km)

    min_built = subject.built_area_m2 * 0.5
    max_built = subject.built_area_m2 * 2.0
    comps_all = filter_comps(comps_all, property_type=subject.property_type, min_built=min_built, max_built=max_built)

    radius = cfg.default_radius_km
    while len(comps_all) < cfg.min_comps and radius < cfg.max_radius_km:
        radius = min(radius + 5.0, cfg.max_radius_km)
        comps_all = get_comps(query, lat, lon, radius)
        comps_all = filter_comps(comps_all, property_type=subject.property_type, min_built=min_built, max_built=max_built)

    comps_rental = [c for c in comps_all if c.get("is_rental") is True]
    comps_sale   = [c for c in comps_all if c.get("is_rental") is False]

    subj_dict = subject.model_dump()
    subj_dict.update({"lat": lat, "lon": lon})

    rent_ranges, comps_r_w = estimate_from_comps(
        subj_dict, comps_rental,
        cfg.alpha_distance, cfg.alpha_recency, cfg.alpha_area_diff
    )
    sale_ranges, comps_s_w = estimate_from_comps(
        subj_dict, comps_sale,
        cfg.alpha_distance, cfg.alpha_recency, cfg.alpha_area_diff
    )

    # IA (se existir modelo treinado)
    models_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "models"))
    rent_model_path = os.path.join(models_dir, "rent_sgd.pkl")
    sale_model_path = os.path.join(models_dir, "sale_sgd.pkl")
    w_hed, w_ai = 0.6, 0.4
    X = _featurize(subj_dict)

    ai_rent_pm2 = ai_sale_pm2 = None
    try:
        if os.path.exists(rent_model_path):
            rent_m = joblib.load(rent_model_path)
            ai_rent_pm2 = float(rent_m.predict(X)[0])
        if os.path.exists(sale_model_path):
            sale_m = joblib.load(sale_model_path)
            ai_sale_pm2 = float(sale_m.predict(X)[0])
    except Exception:
        pass

    rent_p50 = rent_ranges["p50"]
    sale_p50 = sale_ranges["p50"]
    if ai_rent_pm2:
        rent_p50 = w_hed*rent_p50 + w_ai*ai_rent_pm2
    if ai_sale_pm2:
        sale_p50 = w_hed*sale_p50 + w_ai*ai_sale_pm2

    rent_low, rent_high = rent_ranges["low"], rent_ranges["high"]
    sale_low, sale_high = sale_ranges["low"], sale_ranges["high"]

    rent_low, rent_p50, rent_high = [_adjust_by_image(x, img_score) for x in (rent_low, rent_p50, rent_high)]
    sale_low, sale_p50, sale_high = [_adjust_by_image(x, img_score) for x in (sale_low, sale_p50, sale_high)]

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
                "Se houver modelo treinado, combina IA (40%) + hedônico (60%) no valor alvo (P50)."
            ]
        }
    }
    return result
