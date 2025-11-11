# =====================================
# KI Invest Dashboard - High-End Version
# =====================================

import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import openai

# =============================
# Page Config
# =============================
st.set_page_config(page_title="KI Invest Dashboard", layout="wide", initial_sidebar_state="expanded")

# =============================
# Custom CSS für High-End Dashboard
# =============================
st.markdown("""
<style>
body {background-color: #f7f9fc; font-family: 'Helvetica Neue', sans-serif;}
h1 {color: #4B0082;}
.metric-container {
    padding: 20px; 
    border-radius: 12px; 
    background-color: #ffffff; 
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    transition: transform 0.2s, box-shadow 0.2s;
}
.metric-container:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 25px rgba(0,0,0,0.2);
}
.stButton>button {
    background-color: #4B0082; color: white; border-radius: 8px; padding: 0.5em 1em;
    transition: background-color 0.2s;
}
.stButton>button:hover {background-color: #6a00b8;}
</style>
""", unsafe_allow_html=True)

# =============================
# Header / Hero
# =============================
st.markdown("<h1 style='text-align:center;'>💎 KI Invest Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;font-size:18px;'>Investieren leicht gemacht – Rendite simulieren & KI-Tipps erhalten</p>", unsafe_allow_html=True)
st.markdown("---")

# =============================
# Sidebar Navigation
# =============================
st.sidebar.title("Navigation")
page = st.sidebar.radio("Gehe zu:", ["Startseite", "Simulation", "Live Daten", "KI Tipps", "Info"])

# =============================
# Startseite
# =============================
if page == "Startseite":
    st.subheader("Willkommen bei KI Invest MVP")
    st.markdown("""
    - 💰 Monatlich investieren & Rendite simulieren  
    - 📊 Live Krypto-Markt analysieren  
    - 🤖 KI Investment Tipps direkt erhalten  
    """)
    st.image("https://images.unsplash.com/photo-1565372918055-5e7bce20538d?auto=format&fit=crop&w=800&q=80", use_column_width=True)
    if st.button("Jetzt zur Simulation"):
        st.experimental_set_query_params(tab="Simulation")

# =============================
# Simulation
# =============================
if page == "Simulation":
    st.subheader("💹 Rendite Simulation")
    betrag = st.number_input("Monatlicher Betrag (€)", min_value=10, value=700, step=50)
    jahre = st.number_input("Zeitraum (Jahre)", min_value=1, value=20)
    risiko = st.selectbox("Risiko", ["konservativ", "ausgewogen", "aggressiv"])
    rendite = {"konservativ": 0.05, "ausgewogen": 0.08, "aggressiv": 0.12}
    rate = rendite[risiko]
    endwert = betrag * ((1 + rate)**jahre - 1) / rate

    # KPI-Karten
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"<div class='metric-container'><h3>Endwert 💰</h3><p style='font-size:20px'>{int(endwert):,} €</p></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='metric-container'><h3>Monatlicher Beitrag 🏦</h3><p style='font-size:20px'>{betrag} €</p></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='metric-container'><h3>Rendite/Jahr 📈</h3><p style='font-size:20px'>{rate*100:.1f}%</p></div>", unsafe_allow_html=True)

    # Portfolio Wachstum
    growth = [betrag * ((1 + rate)**i - 1) / rate for i in range(1, jahre+1)]
    df_growth = pd.DataFrame({"Jahr": range(1, jahre+1), "Wert": growth})
    fig_growth = px.line(df_growth, x="Jahr", y="Wert", title="Portfolio Wachstum", markers=True,
                         template="plotly_white", line_shape="spline")
    st.plotly_chart(fig_growth, use_container_width=True)

    # Tabelle Jahreswerte
    df_table = pd.DataFrame({
        "Jahr": range(1, jahre+1),
        "Portfolio Wert (€)": [int(v) for v in growth],
        "Beitrag kumuliert (€)": [int(betrag*i*12) for i in range(1, jahre+1)]
    })
    st.subheader("Jährliche Übersicht")
    st.dataframe(df_table)

# =============================
# Live Daten
# =============================
if page == "Live Daten":
    st.subheader("📊 Live Krypto-Daten Top 10")
    COINGECKO_URL = "https://api.coingecko.com/api/v3/coins/markets"
    PARAMS = {"vs_currency": "eur", "order": "market_cap_desc", "per_page": 10, "page": 1}
    try:
        response = requests.get(COINGECKO_URL, params=PARAMS)
        data = response.json()
        df = pd.DataFrame(data)
        df_display = df[["symbol", "current_price", "price_change_percentage_24h"]]
        df_display["change_color"] = df_display["price_change_percentage_24h"].apply(lambda x: "green" if x >= 0 else "red")
        st.dataframe(df_display[["symbol", "current_price", "price_change_percentage_24h"]])

        fig = px.bar(df_display, x="symbol", y="current_price",
                     color="price_change_percentage_24h",
                     title="Preis & 24h Veränderung",
                     color_continuous_scale=px.colors.sequential.Plasma,
                     template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)
    except:
        st.write("Daten konnten nicht geladen werden.")

# =============================
# KI Tipps
# =============================
if page == "KI Tipps":
    st.subheader("🤖 KI Investment Tipps")
    user_input = st.text_area("Beschreibe dein Portfolio oder deine Strategie")
    openai.api_key = st.secrets.get("OPENAI_API_KEY")
    if st.button("Tipp holen"):
        if user_input and openai.api_key:
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": user_input}]
                )
                tip = response.choices[0].message.content
                st.markdown(f"<div class='metric-container'>{tip}</div>", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Fehler bei KI: {e}")
        else:
            st.warning("Bitte Text eingeben und API-Key setzen.")

# =============================
# Info
# =============================
if page == "Info":
    st.subheader("ℹ️ Über KI Invest MVP")
    st.markdown("""
    - Version: Beta 2025  
    - Entwickler: Dein Name  
    - Ziel: Multi-Millionen Menschen helfen, frühzeitig zu investieren  
    - Kontakt: support@ki-invest.com  
    """)

# =============================
# Footer
# =============================
st.markdown("---")
st.markdown("<p style='text-align:center;'>© 2025 KI Invest MVP – Beta Version</p>", unsafe_allow_html=True)
