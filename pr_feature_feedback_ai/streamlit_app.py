import streamlit as st
import requests, os, tempfile
from app.schemas import PropertyInput, PhotoInput
from app.pricing.assessor import assess  # mantemos local por enquanto
from app.report.html import render_html

st.set_page_config(page_title="Avaliador de Imóveis — MVP", layout="centered")

st.title("Avaliador de Imóveis — MVP + IA (aprendizado com seu feedback)")
st.caption("Dê feedback nas previsões, corrija valores alvo e treine um modelo que aprende com você.")

API_URL = os.getenv("API_URL")  # se quiser apontar para uma API externa

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
    # salvar fotos temporariamente
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

    # chamar local (função) ou API externa, se API_URL definido
    if API_URL:
        res = requests.post(f"{API_URL.rstrip('/')}/assess", json=payload, timeout=60).json()
    else:
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

    # --- Feedback UI ---
    st.markdown("### O que achou dessas estimativas?")
    cols = st.columns(4)
    with cols[0]:
        if st.button("👍 OK"):
            label = "ok"; rent_user = None; sale_user = None
            fb = {
                "mode": "both", "label": label,
                "rent_pm2_target_user": rent_user, "sale_pm2_target_user": sale_user,
                "subject": payload,
                "preds_hedonic": {
                    "rent_pm2": res["rental"]["per_m2_target"],
                    "sale_pm2": res["sale"]["per_m2_target"],
                }
            }
            if API_URL:
                requests.post(f"{API_URL.rstrip('/')}/feedback", json=fb, timeout=30)
            else:
                # fallback: chama localmente via requests para manter formato (não temos endpoint local)
                import app.training.feedback as fbmod
                fbmod.save_feedback({
                    "mode": "both", "label": label,
                    "city": payload["city"], "state": payload["state"],
                    "property_type": payload["property_type"],
                    "built_area_m2": payload["built_area_m2"], "land_area_m2": payload["land_area_m2"],
                    "ceiling_height_m": payload["ceiling_height_m"], "energy_capacity_kva": payload["energy_capacity_kva"],
                    "dock_doors": payload["dock_doors"],
                    "rent_pm2_pred_hedonic": res["rental"]["per_m2_target"],
                    "sale_pm2_pred_hedonic": res["sale"]["per_m2_target"],
                    "rent_pm2_target_user": None, "sale_pm2_target_user": None,
                })
            st.success("Feedback salvo: OK")

    with cols[1]:
        if st.button("⬆️ Alto demais"):
            label = "alto"; rent_user = None; sale_user = None
            fb = {
                "mode": "both", "label": label,
                "rent_pm2_target_user": rent_user, "sale_pm2_target_user": sale_user,
                "subject": payload,
                "preds_hedonic": {
                    "rent_pm2": res["rental"]["per_m2_target"],
                    "sale_pm2": res["sale"]["per_m2_target"],
                }
            }
            if API_URL:
                requests.post(f"{API_URL.rstrip('/')}/feedback", json=fb, timeout=30)
            else:
                import app.training.feedback as fbmod
                fbmod.save_feedback({
                    "mode": "both", "label": label,
                    "city": payload["city"], "state": payload["state"],
                    "property_type": payload["property_type"],
                    "built_area_m2": payload["built_area_m2"], "land_area_m2": payload["land_area_m2"],
                    "ceiling_height_m": payload["ceiling_height_m"], "energy_capacity_kva": payload["energy_capacity_kva"],
                    "dock_doors": payload["dock_doors"],
                    "rent_pm2_pred_hedonic": res["rental"]["per_m2_target"],
                    "sale_pm2_pred_hedonic": res["sale"]["per_m2_target"],
                    "rent_pm2_target_user": None, "sale_pm2_target_user": None,
                })
            st.success("Feedback salvo: Alto")

    with cols[2]:
        if st.button("⬇️ Baixo demais"):
            label = "baixo"; rent_user = None; sale_user = None
            fb = {
                "mode": "both", "label": label,
                "rent_pm2_target_user": rent_user, "sale_pm2_target_user": sale_user,
                "subject": payload,
                "preds_hedonic": {
                    "rent_pm2": res["rental"]["per_m2_target"],
                    "sale_pm2": res["sale"]["per_m2_target"],
                }
            }
            if API_URL:
                requests.post(f"{API_URL.rstrip('/')}/feedback", json=fb, timeout=30)
            else:
                import app.training.feedback as fbmod
                fbmod.save_feedback({
                    "mode": "both", "label": label,
                    "city": payload["city"], "state": payload["state"],
                    "property_type": payload["property_type"],
                    "built_area_m2": payload["built_area_m2"], "land_area_m2": payload["land_area_m2"],
                    "ceiling_height_m": payload["ceiling_height_m"], "energy_capacity_kva": payload["energy_capacity_kva"],
                    "dock_doors": payload["dock_doors"],
                    "rent_pm2_pred_hedonic": res["rental"]["per_m2_target"],
                    "sale_pm2_pred_hedonic": res["sale"]["per_m2_target"],
                    "rent_pm2_target_user": None, "sale_pm2_target_user": None,
                })
            st.success("Feedback salvo: Baixo")

    with cols[3]:
        with st.popover("✍️ Corrigir valores"):
            new_rent = st.number_input("Novo R$/m² (aluguel)", min_value=0.0, value=float(res["rental"]["per_m2_target"]))
            new_sale = st.number_input("Novo R$/m² (venda)", min_value=0.0, value=float(res["sale"]["per_m2_target"]))
            if st.button("Salvar correção"):
                fb = {
                    "mode": "both", "label": "corrigido",
                    "rent_pm2_target_user": new_rent, "sale_pm2_target_user": new_sale,
                    "subject": payload,
                    "preds_hedonic": {
                        "rent_pm2": res["rental"]["per_m2_target"],
                        "sale_pm2": res["sale"]["per_m2_target"],
                    }
                }
                if API_URL:
                    requests.post(f"{API_URL.rstrip('/')}/feedback", json=fb, timeout=30)
                else:
                    import app.training.feedback as fbmod
                    fbmod.save_feedback({
                        "mode": "both", "label": "corrigido",
                        "city": payload["city"], "state": payload["state"],
                        "property_type": payload["property_type"],
                        "built_area_m2": payload["built_area_m2"], "land_area_m2": payload["land_area_m2"],
                        "ceiling_height_m": payload["ceiling_height_m"], "energy_capacity_kva": payload["energy_capacity_kva"],
                        "dock_doors": payload["dock_doors"],
                        "rent_pm2_pred_hedonic": res["rental"]["per_m2_target"],
                        "sale_pm2_pred_hedonic": res["sale"]["per_m2_target"],
                        "rent_pm2_target_user": new_rent, "sale_pm2_target_user": new_sale,
                    })
                st.success("Correção salva")

    st.markdown("---")
    train_col1, train_col2 = st.columns([1,2])
    with train_col1:
        if st.button("Treinar agora (IA)"):
            if API_URL:
                out = requests.post(f"{API_URL.rstrip('/')}/train", timeout=120).json()
            else:
                # chamada local: import direto
                from app.training.train import train
                out = train()
            if out.get("trained"):
                st.success(f"Modelo treinado com {out.get('n')} exemplos.")
            else:
                st.warning(out.get("msg", "Sem dados para treinar."))

    # Relatório HTML
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
    st.download_button("Baixar relatório HTML", data=html, file_name="relatorio_avaliacao.html", mime="text/html")
