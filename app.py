"""Valoria Email Agent — Streamlit App."""

import polars as pl
import streamlit as st

from agent import generate_email
from gmail_client import create_draft, get_gmail_service

PRODUCTOS = {
    "Chaqueta Eco-Trek ($295)": "Chaqueta Eco-Trek",
    "Mochila Urban Flow ($140)": "Mochila Urban Flow",
    "Kit Lumina Restore ($85)": "Kit Lumina Restore",
}

SEGMENTO_ORDEN = ["VIP", "Familias", "Gen-Z", "Carrito", "Dormidos"]


def init_session():
    defaults = {
        "step": 1,
        "df": None,
        "producto": None,
        "emails_generados": [],
        "gmail_service": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def step1_config():
    st.header("⚙️ Paso 1 — Configurar Campaña")

    producto_label = st.selectbox("Producto a promover", list(PRODUCTOS.keys()))
    archivo = st.file_uploader("Subir CSV de clientes", type=["csv"])

    if archivo and st.button("🚀 Generar Emails", type="primary"):
        df = pl.read_csv(archivo)
        st.session_state.df = df
        st.session_state.producto = PRODUCTOS[producto_label]
        st.session_state.step = 2
        st.rerun()


def step2_generate():
    st.header("🤖 Paso 2 — Generando Emails...")

    df = st.session_state.df
    producto = st.session_state.producto
    api_key = st.secrets["GROQ_API_KEY"]

    emails = []
    progress = st.progress(0, text="Iniciando...")
    total = len(df)

    for i, row in enumerate(df.iter_rows(named=True)):
        progress.progress(
            (i + 1) / total, text=f"Generando email para {row['nombre']}..."
        )
        email = generate_email(row, producto, api_key)
        emails.append(email)

    st.session_state.emails_generados = emails
    st.session_state.step = 3
    st.rerun()


def step3_preview():
    st.header("👁️ Paso 3 — Preview & Edición")

    emails = st.session_state.emails_generados
    emails_por_segmento = {}
    for e in emails:
        emails_por_segmento.setdefault(e["segmento"], []).append(e)

    tabs = st.tabs(
        [
            f"{s} ({len(emails_por_segmento.get(s, []))})"
            for s in SEGMENTO_ORDEN
            if s in emails_por_segmento
        ]
    )

    segmentos_con_data = [s for s in SEGMENTO_ORDEN if s in emails_por_segmento]
    for tab, segmento in zip(tabs, segmentos_con_data):
        with tab:
            for idx, email in enumerate(emails_por_segmento[segmento]):
                with st.expander(
                    f"📧 {email['nombre']} — {email['subject']}", expanded=(idx == 0)
                ):
                    email["subject"] = st.text_input(
                        "Asunto", value=email["subject"], key=f"sub_{segmento}_{idx}"
                    )
                    st.components.v1.html(
                        email["body_html"], height=400, scrolling=True
                    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Volver"):
            st.session_state.step = 1
            st.session_state.emails_generados = []
            st.rerun()
    with col2:
        if st.button("✅ Aprobar y Crear Borradores en Gmail →", type="primary"):
            st.session_state.step = 4
            st.rerun()


def step4_gmail():
    st.header("📧 Paso 4 — Crear Borradores en Gmail")

    emails = st.session_state.emails_generados
    st.info(f"Se crearán **{len(emails)} borradores** en tu Gmail.")

    st.subheader("Resumen por segmento")
    from collections import Counter

    counts = Counter(e["segmento"] for e in emails)
    for seg in SEGMENTO_ORDEN:
        if seg in counts:
            st.write(f"- **{seg}**: {counts[seg]} emails")

    if st.session_state.gmail_service is None:
        st.warning("Necesitas autorizar acceso a Gmail.")
        if st.button("🔐 Conectar con Gmail"):
            creds = st.secrets["google_oauth"]
            service = get_gmail_service(creds["client_id"], creds["client_secret"])
            st.session_state.gmail_service = service
            st.rerun()
    else:
        if st.button("📬 Crear todos los borradores", type="primary"):
            service = st.session_state.gmail_service
            progress = st.progress(0)
            errores = []
            for i, email in enumerate(emails):
                try:
                    create_draft(
                        service, email["to"], email["subject"], email["body_html"]
                    )
                except Exception as e:
                    errores.append(f"{email['nombre']}: {e}")
                progress.progress((i + 1) / len(emails))

            if errores:
                st.error(f"{len(errores)} errores:\n" + "\n".join(errores))
            else:
                st.success(
                    f"✅ {len(emails)} borradores creados exitosamente en Gmail."
                )
                st.balloons()
                st.markdown("[Ir a Gmail →](https://mail.google.com/mail/u/0/#drafts)")

        if st.button("← Volver al Preview"):
            st.session_state.step = 3
            st.rerun()


def main():
    st.set_page_config(
        page_title="Valoria Email Agent",
        page_icon="✉️",
        layout="wide",
    )
    st.title("✉️ Valoria Email Agent")
    st.caption("Generación hiper-personalizada de emails por segmento RFM")

    init_session()

    step = st.session_state.step
    steps_label = ["1. Configurar", "2. Generar", "3. Preview", "4. Gmail"]
    st.progress((step - 1) / 3, text=f"Paso {step} de 4 — {steps_label[step - 1]}")
    st.divider()

    if step == 1:
        step1_config()
    elif step == 2:
        step2_generate()
    elif step == 3:
        step3_preview()
    elif step == 4:
        step4_gmail()


if __name__ == "__main__":
    main()
