import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard Kesehatan Mental Gen Z", layout="wide")
st.title("Dashboard Kesehatan Mental Gen Z Mahasiswa Indonesia")

@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    return pd.read_csv(path)

df = load_data("indonesia_kesehatan_mental_gen_z_akademik_enriched_2026.csv")

# Sidebar filters
st.sidebar.header("Filter")
prov_opts = sorted(df["provinsi_domisili_kampus"].dropna().unique().tolist())
jenjang_opts = sorted(df["jenjang_dan_rumpun_studi"].dropna().unique().tolist())

sel_prov = st.sidebar.multiselect("Provinsi Domisili Kampus", prov_opts, default=prov_opts)
sel_jenjang = st.sidebar.multiselect("Jenjang dan Rumpun Studi", jenjang_opts, default=jenjang_opts)

df_f = df[df["provinsi_domisili_kampus"].isin(sel_prov) & df["jenjang_dan_rumpun_studi"].isin(sel_jenjang)].copy()

# 1) KPI cards
st.subheader("Ringkasan KPI")
c1, c2, c3, c4 = st.columns(4)

total_resp = df_f["responden_id"].nunique() if "responden_id" in df_f.columns else len(df_f)
avg_stres = df_f["indeks_beban_stres_kumulatif"].mean() if len(df_f) else 0.0
pct_berat = (
    (df_f["kategori_keparahan_depresi_kecemasan"] == "Berat / Kritis").mean() * 100
    if len(df_f)
    else 0.0
)
pct_belum = (
    df_f["akses_layanan_konseling"].fillna("").astype(str).str.startswith("Belum Pernah").mean() * 100
    if len(df_f)
    else 0.0
)

c1.metric("Total Responden", f"{total_resp:,}".replace(",", "."))
c2.metric("Rata-rata Skor Stres", f"{avg_stres:.2f}")
c3.metric("% Berat/Kritis", f"{pct_berat:.2f}%")
c4.metric("% Belum Konseling", f"{pct_belum:.2f}%")

st.divider()

# 2) Two columns: grouped bar + pie
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Distribusi Kategori Keparahan per Jenjang/Rumpun Studi")
    sev_order = ["Minimal", "Ringan", "Sedang", "Berat / Kritis"]
    color_map = {"Minimal": "#2ca02c", "Ringan": "#98df8a", "Sedang": "#ffbf00", "Berat / Kritis": "#d62728"}
    bar_df = (
        df_f.groupby(["jenjang_dan_rumpun_studi", "kategori_keparahan_depresi_kecemasan"], as_index=False)
        .agg(jumlah=("responden_id", "count"))
    )
    if not bar_df.empty:
        fig_bar = px.bar(
            bar_df,
            x="jenjang_dan_rumpun_studi",
            y="jumlah",
            color="kategori_keparahan_depresi_kecemasan",
            barmode="group",
            category_orders={"kategori_keparahan_depresi_kecemasan": sev_order},
            color_discrete_map=color_map,
            title="Jumlah Responden per Jenjang/Rumpun (dikelompokkan oleh Kategori Keparahan)",
        )
        fig_bar.update_layout(xaxis_title="Jenjang dan Rumpun Studi", yaxis_title="Jumlah Responden", legend_title="Kategori Keparahan")
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("Tidak ada data untuk filter saat ini.")

with col_right:
    st.subheader("Distribusi Akses Layanan Konseling")
    pie_df = (
        df_f.groupby("akses_layanan_konseling", as_index=False)
        .agg(jumlah=("responden_id", "count"))
        .sort_values("jumlah", ascending=False)
    )
    if not pie_df.empty:
        fig_pie = px.pie(
            pie_df,
            names="akses_layanan_konseling",
            values="jumlah",
            title="Akses Layanan Konseling (Urut Menurun)",
        )
        fig_pie.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("Tidak ada data untuk filter saat ini.")

st.divider()

# 3) Full-width scatter with trendline
st.subheader("Durasi Layar vs Beban Stres (warna: Skor Resiliensi Psikologis)")
if len(df_f) > 0:
    fig_scatter = px.scatter(
        df_f,
        x="durasi_layar_harian_jam",
        y="indeks_beban_stres_kumulatif",
        color="skor_resiliensi_psikologis",
        color_continuous_scale="Viridis",
        trendline="ols",
        title="Durasi Layar Harian (jam) vs Indeks Beban Stres Kumulatif",
        hover_data=["responden_id", "jenjang_dan_rumpun_studi", "provinsi_domisili_kampus"],
    )
    fig_scatter.update_layout(xaxis_title="Durasi Layar Harian (jam)", yaxis_title="Indeks Beban Stres Kumulatif", coloraxis_colorbar_title="Skor Resiliensi")
    st.plotly_chart(fig_scatter, use_container_width=True)
else:
    st.info("Tidak ada data untuk filter saat ini.")
