from typing import Optional

def safe_float(x) -> Optional[float]:
    try:
        return float(x)
    except Exception:
        return None

def to_brl(x: float) -> str:
    return f"R$ {x:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
