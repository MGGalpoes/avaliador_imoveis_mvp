# Avaliador de Imóveis — MVP (Aluguel & Venda)

Este projeto é um **MVP** (mínimo produto viável) para avaliar imóveis (com foco inicial em **galpões/ativos industriais**, mas flexível para residenciais) a partir de **endereço + fotos** e **comparáveis**.
Ele inclui:
- **API** (FastAPI) para avaliação programática (`POST /assess`).
- **App** visual (Streamlit) para uso manual (upload de fotos, formulário do imóvel e relatório).
- **Conectores** plugáveis para buscar comparáveis (ex.: OLX, Viva Real, Zap Imóveis) — **stubs incluídos** e um conector de **amostra** para rodar offline com dados fictícios.
- **Módulo de visão** simples para extrair um *score* de qualidade a partir das fotos (brilho/nitidez) e ajustar o preço recomendado.
- **Modelo hedônico leve** (estatístico) para estimar **faixas de preço** (baixo/esperado/alto) por m² e total, com pesos por **distância, recência e diferença de área**.

> ⚠️ **Aviso legal**: este MVP serve como estimativa técnica e **não substitui laudo de avaliação** oficial. **Respeite os Termos de Uso** e o `robots.txt` dos portais. Sempre prefira **APIs oficiais** ou parcerias comerciais para coleta de dados. Os conectores aqui são exemplos educacionais.

---

## Como rodar

### 1) Preparar o ambiente
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

> Dica: `torch` (para visão avançada) é opcional e **não é necessário** para o MVP.

### 2) Rodar a API (FastAPI)
```bash
uvicorn app.main:app --reload --port 8000
```
- Acesse a documentação interativa: `http://localhost:8000/docs`

### 3) Rodar a UI (Streamlit)
```bash
streamlit run streamlit_app.py
```
- Preencha os campos, envie fotos, clique **“Rodar avaliação”** e veja os resultados.

---

## Estrutura do projeto

```
avaliador_imoveis_mvp/
├── app/
│   ├── main.py                 # API FastAPI
│   ├── config.py               # Configurações globais
│   ├── schemas.py              # Pydantic (entrada/saída)
│   ├── pricing/
│   │   └── assessor.py         # Orquestra avaliação
│   ├── model/
│   │   └── hedonic.py          # Estatística/ponderação
│   ├── vision/
│   │   └── features.py         # Score de fotos (brilho/nitidez)
│   ├── geo/
│   │   └── geocode.py          # Geocodificação simples + distância
│   ├── comps/
│   │   ├── aggregator.py       # Agregação de comparáveis dos conectores
│   │   └── connectors/
│   │       ├── base.py         # Classe base de conectores
│   │       ├── sample.py       # Conector offline (dados fictícios)
│   │       ├── olx_stub.py     # Stub: onde plugar busca real da OLX
│   │       ├── vivareal_stub.py# Stub: onde plugar busca real do Viva Real
│   │       └── zap_stub.py     # Stub: onde plugar busca real do Zap Imóveis
│   ├── utils/
│   │   ├── cleaning.py         # Limpeza/conversões
│   │   └── filters.py          # Filtros de comparáveis
│   └── report/
│       └── html.py             # Geração de relatório HTML
├── data/
│   └── sample_listings.json    # Dados fictícios para testes
├── streamlit_app.py            # UI Streamlit
├── requirements.txt
└── README.md
```

---

## Como plugar conectores reais (OLX, Viva Real, Zap)

1. **Respeite os Termos de Uso** de cada portal. Idealmente use **APIs oficiais** (quando disponíveis) ou **parcerias**.
2. Edite os arquivos em `app/comps/connectors/*_stub.py`. Lá há exemplos de assinatura de função para retornar comparáveis em um **formato padronizado** (vide `base.py`).
3. Teste pelo `app/comps/aggregator.py` que agrega, normaliza e filtra as ofertas.

---

## Lógica de avaliação (resumo)

1. **Geocodificação** do endereço → lat/lon (estimador simples + fallback por cidade).
2. **Fotos** → *image_quality_score* (0 a 1) via brilho/nitidez (Pillow/NumPy).
3. **Comparáveis** → coleta agregada, normalização e filtros (raio, tipo, área).
4. **Ponderação** → pesos por distância (e^-αd), recência (e^-αt), diferença de área (e^-αa).
5. **Faixas** → quantis ponderados para *baixo* (p25), *esperado* (p50), *alto* (p75) em **R$/m²** e **total** para **aluguel** e **venda**.
6. **Ajustes** → pequeno *uplift/downgrade* linear usando `image_quality_score`.
7. **Relatório** → HTML simples com resumo, tabela de comps e justificativas.

---

## Próximos passos (sugestões)
- Conectar dados reais (APIs/integrações) e registrar *caches* para não estourar limites.
- Incorporar atributos específicos de **galpões** (pé-direito, docas, piso, energia KVA, zoneamento).
- Adicionar **modelo ML** (XGBoost/LightGBM) com *features* estruturadas + visão (CLIP opcional).
- Guardar histórico de avaliações e gerar **laudos PDF** padronizados.
- Calibrar pesos por cidade/bairro (**BH/Contagem/Betim/Vespasiano/Santa Luzia/Lagoa Santa**).

Boa avaliação! 🚀
