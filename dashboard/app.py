import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
from datetime import datetime
import os

st.set_page_config(
    page_title="Global Fuel Watch",
    page_icon="⛽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Load data ──────────────────────────────────────────────────────────────

@st.cache_data(ttl=600)
def load_crude():
    path = "data/live/crude.csv"
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame()

@st.cache_data(ttl=600)
def load_fx():
    path = "data/live/fx_rates.csv"
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame()

@st.cache_data(ttl=600)
def load_latest():
    path = "data/global_latest.json"
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {}

crude_df  = load_crude()
fx_df     = load_fx()
latest    = load_latest()

# ── Header ─────────────────────────────────────────────────────────────────

st.title("🌍 Global Fuel Watch")
st.caption(f"Live global fuel price intelligence — updated every 10 minutes")

if latest:
    st.success(f"✅ Last updated: {latest.get('last_updated_utc', 'N/A')} UTC")

st.divider()

# ── Live commodity prices ───────────────────────────────────────────────────

st.subheader("🛢️ Live Commodity Prices")

if not crude_df.empty:
    latest_crude = crude_df.groupby("commodity").last().reset_index()
    cols = st.columns(3)
    commodities = {
        "brent":       ("Brent Crude", "🛢️", "USD/barrel"),
        "wti":         ("WTI Crude", "🛢️", "USD/barrel"),
        "natural_gas": ("Natural Gas", "🔥", "USD/MMBtu"),
    }
    for i, (key, (label, icon, unit)) in enumerate(commodities.items()):
        row = latest_crude[latest_crude["commodity"] == key]
        if not row.empty:
            price = float(row["price_usd"].values[0])
            date  = row["date"].values[0]
            cols[i].metric(
                label=f"{icon} {label}",
                value=f"${price:.2f}",
                delta=unit
            )

st.divider()

# ── FX Rates ───────────────────────────────────────────────────────────────

st.subheader("💱 Live FX Rates (vs USD)")

if not fx_df.empty:
    latest_fx = fx_df.groupby("pair").last().reset_index()
    latest_fx["currency"] = latest_fx["pair"].str.replace("USD/", "")
    latest_fx["rate"] = pd.to_numeric(latest_fx["rate"], errors="coerce")

    fig = px.bar(
        latest_fx.sort_values("rate", ascending=True),
        x="rate",
        y="currency",
        orientation="h",
        title="USD Exchange Rates by Currency",
        color="rate",
        color_continuous_scale="Blues",
        labels={"rate": "Units per 1 USD", "currency": "Currency"}
    )
    fig.update_layout(
        height=500,
        showlegend=False,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="white"
    )
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── Crude price history ─────────────────────────────────────────────────────

st.subheader("📈 Crude Oil Price History")

if not crude_df.empty:
    crude_df["price_usd"] = pd.to_numeric(crude_df["price_usd"], errors="coerce")
    crude_df["timestamp"] = pd.to_datetime(crude_df["timestamp"])

    fig2 = px.line(
        crude_df,
        x="timestamp",
        y="price_usd",
        color="commodity",
        title="Brent vs WTI vs Natural Gas over time",
        labels={"price_usd": "Price (USD)", "timestamp": "Time", "commodity": "Commodity"}
    )
    fig2.update_layout(
        height=400,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="white"
    )
    st.plotly_chart(fig2, use_container_width=True)

st.divider()

# ── Coverage ────────────────────────────────────────────────────────────────

st.subheader("🌐 Global Coverage")

coverage = {
    "Americas":    ["USA 🇺🇸", "Canada 🇨🇦", "Brazil 🇧🇷", "Mexico 🇲🇽"],
    "Europe":      ["UK 🇬🇧", "Germany 🇩🇪", "France 🇫🇷", "Italy 🇮🇹", "Netherlands 🇳🇱", "Norway 🇳🇴"],
    "Middle East": ["Saudi Arabia 🇸🇦", "UAE 🇦🇪", "Kuwait 🇰🇼", "Iran 🇮🇷"],
    "Asia":        ["India 🇮🇳", "China 🇨🇳", "Japan 🇯🇵", "South Korea 🇰🇷", "Indonesia 🇮🇩", "Philippines 🇵🇭"],
}

cols = st.columns(4)
for i, (region, countries) in enumerate(coverage.items()):
    with cols[i]:
        st.markdown(f"**{region}**")
        for c in countries:
            st.markdown(f"- {c}")

st.divider()
st.caption("Built by nyandajr | global-fuel-watch | Data: Alpha Vantage, Open Exchange Rates")