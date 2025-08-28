from fastapi import FastAPI
from app.schemas import PropertyInput, AssessmentResult
from app.pricing.assessor import assess

app = FastAPI(title="Avaliador de Imóveis — MVP", version="0.1.0")

@app.post("/assess", response_model=AssessmentResult)
def post_assess(payload: PropertyInput):
    result = assess(payload.model_dump())
    return result
