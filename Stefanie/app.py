import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.io as pio

# Professional theme config
pio.templates.default = "plotly_white"

st.set_page_config(
    page_title="Dashboard Perang Kopi Chain Indonesia",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Professional corporate CSS (black / blue / white)
st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 1.5rem;
        background-color: #ffffff;
    }
    .stMetric {
        background: #ffffff;
        border-radius: 4px;
        padding: 1rem 0.75rem;
        border: 1px solid #d3d3d3;
        box-shadow: none;
    }
    .stMetric > div {
        text-align: center;
    }
    h1, h2, h3 {
        color: #1f3b57;
        font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
    }
    .stSidebar {
        background-color: #f5f5f5;
    }
    .stMarkdown p, .stMarkdown li {
        color: #1f3b57;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

CSV_PATH = "indonesia_coffee_chain_wars_enriched_2026.csv"


@st.cache_data
def load_data(path):
    return pd.read_csv(path)


df = load_data(CSV_PATH)

# Sidebar filters
st.sidebar.header("Filter")
city_options = sorted(df["city_location"].dropna().unique())
brand_options = sorted(df["coffee_brand"].dropna().unique())

city_sel = st.sidebar.multiselect("Kota", options=city_options, default=city_options)
brand_sel = st.sidebar.multiselect("Brand Kopi", options=brand_options, default=brand_options)

d = df[df["city_location"].isin(city_sel) & df["coffee_brand"].isin(brand_sel)]

if d.empty:
    st.warning("Tidak ada data yang cocok dengan filter yang dipilih.")
    st.stop()

# Header
st.markdown(
    "<h1 style='text-align:center; color:#1f3b57;'>Dashboard Perang Kopi Chain Indonesia</h1>",
    unsafe_allow_html=True,
)

# Top row: KPI cards
k1, k2, k3, k4 = st.columns(4)

with k1:
    st.metric("Total Transaksi", f"{d['store_transaction_id'].count():,}")

avg_margin = d["outlet_operating_margin_estimate_pct"].mean()
with k2:
    st.metric("Rata-rata Margin", f"{avg_margin:.1f}%")

brand_termahal = d.groupby("coffee_brand")["base_price_idr"].mean().idxmax()
with k3:
    st.metric("Brand Termahal", brand_termahal)

kota_terpadat = d["city_location"].value_counts().idxmax()
with k4:
    st.metric("Kota Terpadat", kota_terpadat)

# Two columns: grouped bar + pie
col1, col2 = st.columns(2)

with col1:
    margin_bar = (
        d.groupby(["coffee_brand", "store_format"])["outlet_operating_margin_estimate_pct"]
        .mean()
        .reset_index()
    )
    fig_bar = px.bar(
        margin_bar,
        x="coffee_brand",
        y="outlet_operating_margin_estimate_pct",
        color="store_format",
        barmode="group",
        color_discrete_sequence=px.colors.sequential.Blues,
        template="plotly_white",
        title="Rata-rata Margin Operasional per Brand (per Store Format)",
    )
    fig_bar.update_layout(
        xaxis_title="Coffee Brand",
        yaxis_title="Rata-rata Margin (%)",
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        font=dict(family="Segoe UI, Helvetica Neue, Arial, sans-serif", size=12, color="#1f3b57"),
        title_font=dict(size=16, color="#1f3b57"),
        legend_title_text="Store Format",
        margin=dict(t=60, b=40, l=40, r=20),
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with col2:
    driver_counts = (
        d["primary_brand_switch_driver"]
        .value_counts()
        .reset_index()
        .rename(columns={"count": "jumlah", "primary_brand_switch_driver": "driver"})
    )
    fig_pie = px.pie(
        driver_counts,
        names="driver",
        values="jumlah",
        color_discrete_sequence=px.colors.sequential.Blues,
        template="plotly_white",
        title="Distribusi Pemicu Pergantian Brand Utama",
        hole=0.35,
    )
    fig_pie.update_traces(
        sort=True,
        direction="clockwise",
        textposition="inside",
        textinfo="percent+label",
        insidetextorientation="radial",
    )
    fig_pie.update_layout(
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        font=dict(family="Segoe UI, Helvetica Neue, Arial, sans-serif", size=12, color="#1f3b57"),
        title_font=dict(size=16, color="#1f3b57"),
        legend_title_text="Driver",
        margin=dict(t=60, b=40, l=20, r=20),
    )
    st.plotly_chart(fig_pie, use_container_width=True)

# Full-width scatter with trendline per brand
fig_scatter = px.scatter(
    d,
    x="competitor_density_500m",
    y="daily_revenue_estimate_idr",
    color="coffee_brand",
    color_discrete_sequence=px.colors.sequential.Blues,
    template="plotly_white",
    trendline="ols",
    title="Densitas Kompetitor (500m) vs Omzet Harian Estimasi per Brand",
)
fig_scatter.update_layout(
    xaxis_title="Densitas Kompetitor (500m)",
    yaxis_title="Omzet Harian Estimasi (IDR)",
    legend_title="Coffee Brand",
    plot_bgcolor="#ffffff",
    paper_bgcolor="#ffffff",
    font=dict(family="Segoe UI, Helvetica Neue, Arial, sans-serif", size=12, color="#1f3b57"),
    title_font=dict(size=18, color="#1f3b57"),
    margin=dict(t=60, b=40, l=60, r=40),
)
fig_scatter.update_traces(marker=dict(size=8, opacity=0.85, line=dict(width=0.5, color="white")))
st.plotly_chart(fig_scatter, use_container_width=True)