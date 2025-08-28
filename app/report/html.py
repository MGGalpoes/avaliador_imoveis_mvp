from typing import Dict, Any, List
from jinja2 import Template

TEMPLATE = Template("""
<!DOCTYPE html>
<html lang="pt-br">
<head>
  <meta charset="utf-8" />
  <title>Relatório de Avaliação</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 24px; }
    h1 { margin-bottom: 0; }
    .subtitle { color: #555; margin-top: 4px; }
    table { border-collapse: collapse; width: 100%; margin-top: 14px;}
    th, td { border: 1px solid #ddd; padding: 8px; }
    th { background: #f6f6f6; }
    .chip { display: inline-block; padding: 4px 8px; margin-right: 6px; background: #efefef; border-radius: 6px; }
  </style>
</head>
<body>
  <h1>Avaliação — {{ city }}, {{ state }}</h1>
  <div class="subtitle">{{ address }}</div>

  <h2>Resultado</h2>
  <div>
    <div class="chip">Qualidade das fotos: {{ (image_score*100)|round(0) }}%</div>
    <div class="chip">Tipo: {{ property_type }}</div>
    <div class="chip">Área construída: {{ built_area_m2 }} m²</div>
  </div>

  <h3>Aluguel</h3>
  <ul>
    <li>R$/m² (baixo): <b>{{ rental.low_pm2 | round(2) }}</b> — total: <b>{{ rental.low_total | round(0) }}</b></li>
    <li>R$/m² (esperado): <b>{{ rental.p50_pm2 | round(2) }}</b> — total: <b>{{ rental.p50_total | round(0) }}</b></li>
    <li>R$/m² (alto): <b>{{ rental.high_pm2 | round(2) }}</b> — total: <b>{{ rental.high_total | round(0) }}</b></li>
  </ul>

  <h3>Venda</h3>
  <ul>
    <li>R$/m² (baixo): <b>{{ sale.low_pm2 | round(0) }}</b> — total: <b>{{ sale.low_total | round(0) }}</b></li>
    <li>R$/m² (esperado): <b>{{ sale.p50_pm2 | round(0) }}</b> — total: <b>{{ sale.p50_total | round(0) }}</b></li>
    <li>R$/m² (alto): <b>{{ sale.high_pm2 | round(0) }}</b> — total: <b>{{ sale.high_total | round(0) }}</b></li>
  </ul>

  <h2>Comparáveis utilizados ({{ comps|length }})</h2>
  <table>
    <thead>
      <tr>
        <th>Fonte</th><th>Título</th><th>Cidade</th><th>Área (m²)</th><th>Preço</th><th>R$/m²</th><th>Distância (km)</th><th>Recência (meses)</th><th>Peso</th>
      </tr>
    </thead>
    <tbody>
      {% for c in comps %}
      <tr>
        <td>{{ c.source }}</td>
        <td>{{ c.title }}</td>
        <td>{{ c.city }}</td>
        <td>{{ c.built_area_m2 }}</td>
        <td>{{ (c.price_total or c.price_per_m2 * c.built_area_m2) | round(0) }}</td>
        <td>{{ c.price_per_m2 | round(2) }}</td>
        <td>{{ (c.distance_km or 0) | round(1) }}</td>
        <td>{{ c.months_since | round(1) }}</td>
        <td>{{ c.weight | round(3) }}</td>
      </tr>
      {% endfor %}
    </tbody>
  </table>

  <p style="margin-top: 24px; color: #777;">
    Nota: resultado estimativo com base em fontes públicas e heurísticas. Recomenda-se validação local e ajustes conforme especificações do ativo (pé-direito, docas, piso, KVA, zoneamento, incentivos fiscais etc.).
  </p>
</body>
</html>
""")

def render_html(context: Dict[str, Any]) -> str:
    return TEMPLATE.render(**context)
