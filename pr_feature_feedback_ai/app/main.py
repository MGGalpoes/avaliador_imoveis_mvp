from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from app.schemas import PropertyInput, AssessmentResult
from app.pricing.assessor import assess
from app.training.feedback import save_feedback
from app.training.train import train

app = FastAPI(title="Avaliador de Imóveis — MVP", version="0.2.0")

# CORS (ajuste os domínios em produção)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/assess", response_model=AssessmentResult)
def post_assess(payload: PropertyInput):
    return assess(payload.model_dump())

class FeedbackIn(BaseModel):
    mode: str  # "rent" | "sale" | "both"
    label: str # "ok" | "alto" | "baixo" | "corrigido"
    rent_pm2_target_user: Optional[float] = None
    sale_pm2_target_user: Optional[float] = None
    subject: PropertyInput
    preds_hedonic: dict  # {"rent_pm2": float, "sale_pm2": float}

@app.post("/feedback")
def post_feedback(fb: FeedbackIn):
    save_feedback({
        "mode": fb.mode,
        "label": fb.label,
        "city": fb.subject.city,
        "state": fb.subject.state,
        "property_type": fb.subject.property_type,
        "built_area_m2": fb.subject.built_area_m2,
        "land_area_m2": fb.subject.land_area_m2,
        "ceiling_height_m": fb.subject.ceiling_height_m,
        "energy_capacity_kva": fb.subject.energy_capacity_kva,
        "dock_doors": fb.subject.dock_doors,
        "rent_pm2_pred_hedonic": fb.preds_hedonic.get("rent_pm2"),
        "sale_pm2_pred_hedonic": fb.preds_hedonic.get("sale_pm2"),
        "rent_pm2_target_user": fb.rent_pm2_target_user,
        "sale_pm2_target_user": fb.sale_pm2_target_user,
    })
    return {"ok": True}

@app.post("/train")
def post_train():
    return train()
