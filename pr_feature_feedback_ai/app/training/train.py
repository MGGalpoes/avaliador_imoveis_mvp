import os, csv, joblib
import numpy as np
from sklearn.linear_model import SGDRegressor

DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "labels.csv")
MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "models")
os.makedirs(MODEL_DIR, exist_ok=True)

def _load():
    X_rent, y_rent, X_sale, y_sale = [], [], [], []
    if not os.path.exists(DATA_PATH):
        return None
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        city = (r.get("city") or "").lower()
        feats = [
            float(r.get("built_area_m2") or 0),
            float(r.get("land_area_m2") or 0),
            float(r.get("ceiling_height_m") or 0),
            float(r.get("energy_capacity_kva") or 0),
            float(r.get("dock_doors") or 0),
            1.0 if city=="contagem" else 0.0,
            1.0 if city=="betim" else 0.0,
            1.0 if city=="vespasiano" else 0.0,
            1.0 if city=="santa luzia" else 0.0,
            1.0 if city=="lagoa santa" else 0.0,
        ]
        lbl = (r.get("label") or "ok").lower()

        rent_user = r.get("rent_pm2_target_user")
        sale_user = r.get("sale_pm2_target_user")
        rent_hed = float(r.get("rent_pm2_pred_hedonic") or 0)
        sale_hed = float(r.get("sale_pm2_pred_hedonic") or 0)

        if rent_user:
            y_r = float(rent_user)
        else:
            y_r = rent_hed * (1.10 if lbl=="baixo" else 0.90 if lbl=="alto" else 1.00)

        if sale_user:
            y_s = float(sale_user)
        else:
            y_s = sale_hed * (1.10 if lbl=="baixo" else 0.90 if lbl=="alto" else 1.00)

        X_rent.append(feats); y_rent.append(y_r)
        X_sale.append(feats); y_sale.append(y_s)
    return np.array(X_rent), np.array(y_rent), np.array(X_sale), np.array(y_sale)

def train():
    data = _load()
    if not data:
        return {"trained": False, "msg": "sem dados de labels"}
    Xr, yr, Xs, ys = data
    rent = SGDRegressor(random_state=42, max_iter=3000, tol=1e-3)
    sale = SGDRegressor(random_state=42, max_iter=3000, tol=1e-3)
    rent.fit(Xr, yr)
    sale.fit(Xs, ys)
    joblib.dump(rent, os.path.join(MODEL_DIR, "rent_sgd.pkl"))
    joblib.dump(sale, os.path.join(MODEL_DIR, "sale_sgd.pkl"))
    return {"trained": True, "n": int(len(yr))}
