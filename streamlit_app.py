import streamlit as st
from app.schemas import PropertyInput, PhotoInput
from app.pricing.assessor import assess
from app.report.html import render_html
import os, tempfile, base64, json

st.set_page_config(page_title="Avaliador de Imóveis — MVP", layout="centered")

st.title("Avaliador de Imóveis — MVP")
st.caption("Estimativa rápida de aluguel e venda com base em endereço, fotos e comparáveis (dados de exemplo).")

with st.form("form"):
    col1, col2 = st.columns(2)
    with col1:
        address = st.text_input("Endereço", "Av. João César de Oliveira, 3000")
        city = st.text_input("Cidade", "Contagem")
        state = st.text_input("Estado (UF)", "MG")
        country = st.text_input("País", "BR")

    with col2:
        property_type = st.selectbox("Tipo do imóvel", ["galpao", "apartamento", "casa", "sala", "loja", "terreno", "outro"], index=0)
        built_area_m2 = st.number_input("Área construída (m²)", value=1500.0, step=50.0, min_value=50.0)
        land_area_m2 = st.number_input("Área do terreno (m²)", value=2000.0, step=50.0, min_value=0.0)

    st.markdown("**Atributos adicionais (opcional)**")
    col3, col4, col5 = st.columns(3)
    with col3:
        bedrooms = st.number_input("Quartos", value=0, min_value=0, step=1)
        ceiling_height_m = st.number_input("Pé-direito (m)", value=8.0, step=0.5, min_value=0.0)
    with col4:
        bathrooms = st.number_input("Banheiros", value=2, min_value=0, step=1)
        energy_capacity_kva = st.number_input("Energia (kVA)", value=75.0, step=5.0, min_value=0.0)
    with col5:
        parking = st.number_input("Vagas", value=4, min_value=0, step=1)
        dock_doors = st.number_input("Docas", value=2, min_value=0, step=1)

    photos_files = st.file_uploader("Fotos (JPG/PNG)", accept_multiple_files=True, type=["jpg","jpeg","png"])

    submitted = st.form_submit_button("Rodar avaliação")

if submitted:
    # Salva fotos temporariamente
    photo_inputs = []
    if photos_files:
        tmpdir = tempfile.mkdtemp()
        for f in photos_files:
            path = os.path.join(tmpdir, f.name)
            with open(path, "wb") as out:
                out.write(f.getbuffer())
            photo_inputs.append(PhotoInput(path=path))
    payload = PropertyInput(
        address=address, city=city, state=state, country=country,
        property_type=property_type, built_area_m2=built_area_m2, land_area_m2=land_area_m2,
        bedrooms=bedrooms, bathrooms=bathrooms, parking=parking,
        ceiling_height_m=ceiling_height_m, energy_capacity_kva=energy_capacity_kva, dock_doors=dock_doors,
        photos=photo_inputs
    ).model_dump()

    with st.spinner("Calculando..."):
        res = assess(payload)

    st.subheader("Resultado (resumo)")
    c1, c2 = st.columns(2)
    with c1:
        st.metric("Aluguel — R$/m² (esperado)", f"{res['rental']['per_m2_target']:.2f}")
        st.metric("Aluguel — total (esperado)", f"R$ {res['rental']['total_target']:.0f}")
    with c2:
        st.metric("Venda — R$/m² (esperado)", f"{res['sale']['per_m2_target']:.0f}")
        st.metric("Venda — total (esperado)", f"R$ {res['sale']['total_target']:.0f}")

    st.caption(f"Qualidade média das fotos: {res['image_quality_score']*100:.0f}%")

    with st.expander("Ver faixas completas"):
        st.write({
            "aluguel": res["rental"],
            "venda": res["sale"],
        })

    with st.expander("Comparáveis utilizados"):
        st.write(res["comps_used"])

    # Relatório HTML para download
    html = render_html({
        "address": res["address_geocoded"]["address"],
        "city": res["address_geocoded"]["city"],
        "state": res["address_geocoded"]["state"],
        "property_type": property_type,
        "built_area_m2": built_area_m2,
        "image_score": res["image_quality_score"],
        "rental": {
            "low_pm2": res["rental"]["per_m2_low"],
            "p50_pm2": res["rental"]["per_m2_target"],
            "high_pm2": res["rental"]["per_m2_high"],
            "low_total": res["rental"]["total_low"],
            "p50_total": res["rental"]["total_target"],
            "high_total": res["rental"]["total_high"],
        },
        "sale": {
            "low_pm2": res["sale"]["per_m2_low"],
            "p50_pm2": res["sale"]["per_m2_target"],
            "high_pm2": res["sale"]["per_m2_high"],
            "low_total": res["sale"]["total_low"],
            "p50_total": res["sale"]["total_target"],
            "high_total": res["sale"]["total_high"],
        },
        "comps": res["comps_used"]
    })
    fname = "relatorio_avaliacao.html"
    path = os.path.join(os.getcwd(), fname)
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)

    st.success("Relatório gerado.")
    st.download_button("Baixar relatório HTML", data=html, file_name=fname, mime="text/html")
