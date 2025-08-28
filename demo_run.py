from app.pricing.assessor import assess

payload = {
    "address": "Av. João César de Oliveira, 3000",
    "city": "Contagem",
    "state": "MG",
    "country": "BR",
    "property_type": "galpao",
    "built_area_m2": 1500.0,
    "land_area_m2": 2000.0,
    "bedrooms": 0, "bathrooms": 3, "parking": 5,
    "ceiling_height_m": 9.0, "energy_capacity_kva": 75.0, "dock_doors": 2,
    "photos": []  # para o demo offline
}

res = assess(payload)
print("=== Avaliação (resumo) ===")
print("Renda (R$/m²):", round(res["rental"]["per_m2_target"], 2), " | Total:", round(res["rental"]["total_target"], 0))
print("Venda (R$/m²):", round(res["sale"]["per_m2_target"], 0), " | Total:", round(res["sale"]["total_target"], 0))
