from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict, Any

PropertyType = Literal["galpao", "apartamento", "casa", "sala", "loja", "terreno", "outro"]

class PhotoInput(BaseModel):
    path: Optional[str] = None   # caminho local do arquivo (UI)
    url: Optional[str] = None    # opcional: URL remota (conectores online)

class PropertyInput(BaseModel):
    address: str
    city: str
    state: str = "MG"
    country: str = "BR"
    property_type: PropertyType = "galpao"
    built_area_m2: float = Field(..., gt=0)
    land_area_m2: Optional[float] = None
    bedrooms: Optional[int] = 0
    bathrooms: Optional[int] = 0
    parking: Optional[int] = 0
    ceiling_height_m: Optional[float] = None # industrial
    energy_capacity_kva: Optional[float] = None # industrial
    dock_doors: Optional[int] = None # industrial
    photos: Optional[List[PhotoInput]] = []

class AssessmentResult(BaseModel):
    address_geocoded: Dict[str, Any]
    image_quality_score: float
    comps_used: List[Dict[str, Any]]
    rental: Dict[str, Any]
    sale: Dict[str, Any]
    explainability: Dict[str, Any]
