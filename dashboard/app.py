import glob
import json
import os
from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

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

@st.cache_data(ttl=600)
def load_pump_prices():
    """One row per country with its latest known price per fuel type,
    from data/pump_prices/<CODE>.csv -- only countries that actually have
    a scraper get a file here, so this is naturally the honest subset,
    not the full 20-country wishlist.
    """
    rows = []
    for path in sorted(glob.glob("data/pump_prices/*.csv")):
        country = os.path.splitext(os.path.basename(path))[0]
        try:
            df = pd.read_csv(path)
        except pd.errors.EmptyDataError:
            continue
        if df.empty:
            continue
        latest_ts = df["timestamp"].max()
        for _, r in df[df["timestamp"] == latest_ts].iterrows():
            rows.append(r.to_dict() | {"country_code": country})
    return pd.DataFrame(rows)

crude_df  = load_crude()
fx_df     = load_fx()
latest    = load_latest()
pump_df   = load_pump_prices()

COUNTRY_LABELS = {
    "UK": "United Kingdom 🇬🇧", "US": "United States 🇺🇸", "FR": "France 🇫🇷",
    "CA": "Canada 🇨🇦", "BR": "Brazil 🇧🇷", "MX": "Mexico 🇲🇽",
    "IT": "Italy 🇮🇹", "NO": "Norway 🇳🇴", "JP": "Japan 🇯🇵",
}

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

# ── Retail pump prices ──────────────────────────────────────────────────────

st.subheader("⛽ Retail Pump Prices, by Country")
st.caption(
    "Only countries with a real, verified government or statistical-agency "
    "source are shown here — see each country's `source` for exactly which "
    "one. Not every country tracks every fuel type; only what its real "
    "source actually publishes is shown."
)

if not pump_df.empty:
    pump_df["label"] = pump_df["country_code"].map(COUNTRY_LABELS).fillna(pump_df["country_code"])
    fuel_tabs = st.tabs(sorted(pump_df["fuel_type"].unique()))
    for tab, fuel in zip(fuel_tabs, sorted(pump_df["fuel_type"].unique())):
        with tab:
            sub = pump_df[pump_df["fuel_type"] == fuel].copy()
            sub["price"] = pd.to_numeric(sub["price"], errors="coerce")
            fig = px.bar(
                sub.sort_values("price"),
                x="price", y="label", orientation="h",
                color="currency",
                text=sub.apply(lambda r: f"{r['price']:.3f} {r['unit']}", axis=1),
                labels={"price": "Price (local currency)", "label": "Country"},
            )
            fig.update_layout(
                height=max(220, 60 * len(sub)),
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font_color="white",
                showlegend=False,
            )
            st.plotly_chart(fig, use_container_width=True)
            st.caption(
                "Sources: " + " · ".join(
                    f"{row['label']} ({row['date']})" for _, row in sub.iterrows()
                )
            )
else:
    st.info("No pump price data yet — the VM's cron job writes this every 4 hours.")

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

st.subheader("🌐 Coverage — What's Actually Real")
st.caption(
    "This used to list all 20 countries as if every one had real retail "
    "price data. It didn't — 19 of the 21 per-country scrapers were empty "
    "placeholders. Fixed here to show the honest current state instead."
)

live_countries = sorted(pump_df["country_code"].unique()) if not pump_df.empty else []
no_source = ["SA", "UAE", "KW", "IR", "IN", "CN", "ID", "PH"]
needs_key = ["DE", "KR"]
unreachable = ["NL"]

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"**✅ Live now ({len(live_countries)})**")
    for c in live_countries:
        st.markdown(f"- {COUNTRY_LABELS.get(c, c)}")
with col2:
    st.markdown(f"**❌ No public source exists ({len(no_source)})**")
    st.caption("Subsidized/administered prices, no machine-readable feed found")
    for c in no_source:
        st.markdown(f"- {c}")
with col3:
    st.markdown(f"**🔑 Needs a free API key ({len(needs_key)})**")
    st.caption("Real source, instant signup, not completed yet")
    for c in needs_key:
        st.markdown(f"- {c}")
with col4:
    st.markdown(f"**🌐 Currently unreachable ({len(unreachable)})**")
    st.caption("Real source, blocked from this network")
    for c in unreachable:
        st.markdown(f"- {c}")

st.divider()
st.caption("Built by nyandajr | global-fuel-watch | Crude/FX: Alpha Vantage | Pump prices: government/statistical-agency sources, see README")