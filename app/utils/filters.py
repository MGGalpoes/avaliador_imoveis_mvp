from typing import List, Dict, Any, Optional

def filter_comps(comps: List[Dict[str, Any]],
                 property_type: Optional[str] = None,
                 min_built: Optional[float] = None,
                 max_built: Optional[float] = None) -> List[Dict[str, Any]]:
    out = []
    for c in comps:
        if property_type and c.get("property_type") != property_type:
            continue
        area = c.get("built_area_m2")
        if area is None:
            continue
        if min_built is not None and area < min_built:
            continue
        if max_built is not None and area > max_built:
            continue
        out.append(c)
    return out
