from typing import List, Dict, Any, Tuple
from datetime import datetime
import math

def _months_since(date_str: str) -> float:
    if not date_str:
        return 1.0
    try:
        d = datetime.fromisoformat(date_str)
    except Exception:
        # tenta formatos comuns
        try:
            d = datetime.strptime(date_str, "%Y-%m-%d")
        except Exception:
            return 1.0
    delta = datetime.now() - d
    return max(delta.days / 30.0, 0.0)

def _weighted_quantile(values, weights, q):
    # Quantil ponderado (q em [0,1])
    # Ordena por valor
    pairs = sorted(zip(values, weights), key=lambda x: x[0])
    cum_w = 0.0
    total_w = sum(weights)
    if total_w <= 0:
        total_w = 1.0
    threshold = q * total_w
    for v, w in pairs:
        cum_w += w
        if cum_w >= threshold:
            return v
    return pairs[-1][0] if pairs else 0.0

def estimate_from_comps(subject: Dict[str, Any],
                        comps: List[Dict[str, Any]],
                        alpha_distance: float,
                        alpha_recency: float,
                        alpha_area_diff: float) -> Tuple[Dict[str, float], List[Dict[str, Any]]]:
    """
    Calcula faixas (p25/p50/p75) de preço por m² e total, com pesos:
      w = exp(-αd * dist) * exp(-αt * meses) * exp(-αa * |Δárea_rel|)
    Retorna (faixas, comps_ponderados).
    """
    built = subject.get("built_area_m2") or 1.0
    price_per_m2_vals = []
    weights = []
    comps_out = []

    for c in comps:
        ppm2 = c.get("price_per_m2")
        total = c.get("price_total")
        area = c.get("built_area_m2")
        if not ppm2:
            # se não veio por m², tenta inferir
            if total and area:
                ppm2 = total / max(area, 1.0)
        if not ppm2:
            continue

        # Pesos
        dist = c.get("distance_km") or 0.0
        months = _months_since(c.get("date_posted"))
        # diferença relativa de área
        a_rel = 0.0
        if area and built:
            a_rel = abs(area - built) / max(built, 1.0)

        w = math.exp(-alpha_distance * dist) * math.exp(-alpha_recency * months) * math.exp(-alpha_area_diff * a_rel)

        price_per_m2_vals.append(ppm2)
        weights.append(w)

        c2 = dict(c)
        c2["weight"] = w
        c2["months_since"] = months
        comps_out.append(c2)

    if not price_per_m2_vals:
        # fallback defensivo
        return {"low": 0.0, "p50": 0.0, "high": 0.0, "total_low": 0.0, "total_p50": 0.0, "total_high": 0.0}, comps_out

    p25 = _weighted_quantile(price_per_m2_vals, weights, 0.25)
    p50 = _weighted_quantile(price_per_m2_vals, weights, 0.5)
    p75 = _weighted_quantile(price_per_m2_vals, weights, 0.75)

    return {
        "low": p25,
        "p50": p50,
        "high": p75,
        "total_low": p25 * built,
        "total_p50": p50 * built,
        "total_high": p75 * built,
    }, comps_out
