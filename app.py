"""
================================================
GERMANY ENERGY CONSUMPTION ANALYSIS
Streamlit App — Interactive Dashboard
================================================
Run: streamlit run app.py
Deploy free: https://streamlit.io/cloud
"""

import os
import sqlite3

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots


# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Germany Energy Analytics",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #0f1117; }
    .block-container { padding-top: 1.5rem; }
    h1, h2, h3 { color: #00d4aa; }
    .metric-card {
        background: #1a1d27;
        border: 1px solid #2a2d3a;
        border-radius: 10px;
        padding: 16px 20px;
        text-align: center;
    }
    .metric-value { font-size: 1.8rem; font-weight: 700; color: #00d4aa; }
    .metric-label { font-size: 0.85rem; color: #888; margin-top: 4px; }
    .metric-delta { font-size: 0.8rem; color: #ffd93d; margin-top: 2px; }
</style>
""", unsafe_allow_html=True)

# ── Paths ──────────────────────────────────────────────────────────────────────
DB_PATH = "data/processed/energy_germany.db"
CLEAN_PATH = "data/processed/energy_clean.csv"
FORECAST_PATH = "outputs/forecast/forecast.csv"
ANOMALY_PATH = "outputs/anomalies/anomalies.csv"
FLAG_PATH = "data/assets/FLAG.png"

# ── Load data ──────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM daily_energy", conn)
    conn.close()
    df["date"] = pd.to_datetime(df["date"])
    # FIX: force numeric types on renewable columns at load time
    for col in ["renewable_share_pct", "solar_mwh", "wind_onshore_mwh",
                "wind_offshore_mwh", "renewable_total_mwh"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


if not os.path.exists(DB_PATH):
    st.error("⚠️ Database not found. Please run `python 01_clean_data.py` first.")
    st.stop()

df = load_data()

# ── Sidebar filters ────────────────────────────────────────────────────────────
with st.sidebar:
    if os.path.exists(FLAG_PATH):
        st.image(FLAG_PATH, width=80)

    st.title("⚡ Energy Analytics")
    # FIX: dynamic year range
    st.markdown(f"**Germany | {df['year'].min()}–{df['year'].max()}**")
    st.divider()

    years = sorted(df["year"].unique())
    selected_years = st.multiselect("📅 Select Years", years, default=years)

    seasons = df["season"].unique().tolist()
    selected_seasons = st.multiselect("🌤️ Select Seasons", seasons, default=seasons)

    st.divider()
    st.markdown("**Data Source:**")
    st.markdown("[Open Power System Data](https://data.open-power-system-data.org/)")
    st.markdown("[SMARD – Bundesnetzagentur](https://www.smard.de/)")
    st.divider()
    st.caption("Built by Pritesh Viramgama · github.com/Pritesh74")

# ── Filter data ────────────────────────────────────────────────────────────────
filtered = df[df["year"].isin(selected_years) & df["season"].isin(selected_seasons)].copy()

if filtered.empty:
    st.warning("No data available for the selected filters.")
    st.stop()

# ── Header ─────────────────────────────────────────────────────────────────────
st.title("⚡ Germany Energy Consumption Dashboard")
st.markdown(
    f"*Interactive dashboard analysing electricity demand, renewable trends, "
    f"forecasting, and anomaly detection in Germany "
    f"({df['year'].min()}–{df['year'].max()}).*"
)
st.divider()

# ── KPI Cards ──────────────────────────────────────────────────────────────────
total_twh     = filtered["consumption_mwh"].sum() / 1e6
avg_daily_mwh = filtered["consumption_mwh"].mean()
peak_day      = filtered.loc[filtered["consumption_mwh"].idxmax()]

# FIX: force numeric + int() to prevent numpy bool rendering as 0
if "renewable_share_pct" in filtered.columns:
    ren_series    = pd.to_numeric(filtered["renewable_share_pct"], errors="coerce")
    avg_renewable = ren_series.mean()
    days_green    = int((ren_series > 50).sum())
else:
    avg_renewable = 0
    days_green    = 0

col1, col2, col3, col4, col5 = st.columns(5)
kpis = [
    (col1, f"{total_twh:,.1f} TWh",                  "Total Consumption",    "Selected period"),
    (col2, f"{avg_daily_mwh:,.0f} MWh",              "Avg Daily Demand",     "Per day"),
    (col3, f"{peak_day['consumption_mwh']:,.0f}",     "Peak Day (MWh)",       str(peak_day["date"].date())),
    (col4, f"{avg_renewable:.1f}%",                   "Avg Renewable Share",  "Of daily generation"),
    (col5, f"{days_green:,}",                         "Days >50% Renewable",  "Majority green days"),
]

for col, val, label, delta in kpis:
    with col:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value">{val}</div>
                <div class="metric-label">{label}</div>
                <div class="metric-delta">{delta}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.divider()

# ── Tab layout ─────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Consumption Trends",
    "🌿 Renewable Energy",
    "📅 Time Patterns",
    "🔍 SQL Insights",
])

# ══════════════════════════════════════════════════════════════
# TAB 1: CONSUMPTION TRENDS
# ══════════════════════════════════════════════════════════════
with tab1:
    st.subheader("Annual Consumption Trend")

    yearly = filtered.groupby("year")["consumption_mwh"].sum().reset_index()
    yearly["total_twh"] = yearly["consumption_mwh"] / 1e6
    yearly["yoy_pct"]   = yearly["total_twh"].pct_change() * 100

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Bar(x=yearly["year"], y=yearly["total_twh"],
               name="Total TWh", marker_color="#00d4aa", opacity=0.75),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(x=yearly["year"], y=yearly["yoy_pct"],
                   name="YoY Growth %", mode="lines+markers",
                   line=dict(color="#ffd93d", width=2), marker=dict(size=8)),
        secondary_y=True,
    )
    fig.add_hline(y=0, line_dash="dot", line_color="#888", secondary_y=True)
    fig.update_layout(
        template="plotly_dark", plot_bgcolor="#0f1117",
        paper_bgcolor="#0f1117", height=420,
        legend=dict(orientation="h", y=1.1),
    )
    fig.update_yaxes(title_text="Consumption (TWh)", secondary_y=False)
    fig.update_yaxes(title_text="YoY Growth (%)", secondary_y=True)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Daily Consumption — Full Timeline")
    filtered["rolling_30d"] = filtered["consumption_mwh"].rolling(30, min_periods=1).mean()

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=filtered["date"], y=filtered["consumption_mwh"],
        mode="lines", name="Daily", line=dict(color="#333", width=0.8),
    ))
    fig2.add_trace(go.Scatter(
        x=filtered["date"], y=filtered["rolling_30d"],
        mode="lines", name="30-Day Rolling Avg",
        line=dict(color="#ff6b6b", width=2.5),
    ))
    fig2.update_layout(
        template="plotly_dark", plot_bgcolor="#0f1117",
        paper_bgcolor="#0f1117", height=380,
        yaxis_title="MWh", xaxis_title="",
        legend=dict(orientation="h", y=1.05),
    )
    st.plotly_chart(fig2, use_container_width=True)

# ══════════════════════════════════════════════════════════════
# TAB 2: RENEWABLE ENERGY
# ══════════════════════════════════════════════════════════════
with tab2:
    if "renewable_share_pct" not in filtered.columns:
        st.warning("Renewable columns not available in this dataset.")
    else:
        st.subheader("Renewable Share Over Time")
        monthly_ren = filtered.groupby(["year", "month"])["renewable_share_pct"].mean().reset_index()
        monthly_ren["date_label"] = pd.to_datetime(monthly_ren[["year", "month"]].assign(day=1))

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=monthly_ren["date_label"], y=monthly_ren["renewable_share_pct"],
            fill="tozeroy", fillcolor="rgba(0,212,170,0.15)",
            line=dict(color="#00d4aa", width=2), name="Renewable %",
        ))
        fig.add_hline(
            y=50, line_dash="dash", line_color="#ffd93d",
            annotation_text="50% milestone", annotation_position="top right",
        )
        fig.update_layout(
            template="plotly_dark", plot_bgcolor="#0f1117",
            paper_bgcolor="#0f1117", height=380,
            yaxis_title="Renewable Share (%)",
        )
        st.plotly_chart(fig, use_container_width=True)

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Renewable Share by Year")
            yr_ren = filtered.groupby("year")["renewable_share_pct"].mean().reset_index()
            fig3 = px.bar(
                yr_ren, x="year", y="renewable_share_pct",
                color="renewable_share_pct", color_continuous_scale="Teal",
                labels={"renewable_share_pct": "Avg Renewable %"},
            )
            fig3.update_layout(
                template="plotly_dark", plot_bgcolor="#0f1117",
                paper_bgcolor="#0f1117", height=320, coloraxis_showscale=False,
            )
            st.plotly_chart(fig3, use_container_width=True)

        with col2:
            st.subheader("Solar vs Wind by Season")
            needed_cols = ["solar_mwh", "wind_onshore_mwh", "wind_offshore_mwh"]
            if all(c in filtered.columns for c in needed_cols):
                season_order = ["Winter", "Spring", "Summer", "Autumn"]
                sv = (
                    filtered.groupby("season")[needed_cols]
                    .mean().reindex(season_order).reset_index()
                )
                fig4 = go.Figure()
                fig4.add_trace(go.Bar(x=sv["season"], y=sv["solar_mwh"],         name="Solar",         marker_color="#ffd93d"))
                fig4.add_trace(go.Bar(x=sv["season"], y=sv["wind_onshore_mwh"],  name="Wind Onshore",  marker_color="#00d4aa"))
                fig4.add_trace(go.Bar(x=sv["season"], y=sv["wind_offshore_mwh"], name="Wind Offshore", marker_color="#4a9eff"))
                fig4.update_layout(
                    barmode="group", template="plotly_dark",
                    plot_bgcolor="#0f1117", paper_bgcolor="#0f1117",
                    height=320, yaxis_title="Avg Daily MWh",
                )
                st.plotly_chart(fig4, use_container_width=True)

        # Renewable insight callout
        st.info(
            f"💡 **Renewable Insight:** During the selected period, Germany averaged "
            f"**{avg_renewable:.1f}%** renewable share, with **{days_green} days** "
            f"exceeding the 50% milestone. Wind energy dominates in winter while solar "
            f"peaks in summer — their complementary seasonality is key to grid stability."
        )

# ══════════════════════════════════════════════════════════════
# TAB 3: TIME PATTERNS
# ══════════════════════════════════════════════════════════════
with tab3:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Seasonal Consumption")
        season_order = ["Winter", "Spring", "Summer", "Autumn"]
        seas = filtered.groupby("season")["consumption_mwh"].mean().reindex(season_order).reset_index()
        fig5 = px.bar(
            seas, x="season", y="consumption_mwh", color="season",
            color_discrete_sequence=["#4a9eff", "#00d4aa", "#ffd93d", "#ff6b6b"],
        )
        fig5.update_layout(
            template="plotly_dark", plot_bgcolor="#0f1117",
            paper_bgcolor="#0f1117", height=340,
            showlegend=False, yaxis_title="Avg Daily MWh",
        )
        st.plotly_chart(fig5, use_container_width=True)

    with col2:
        st.subheader("Day of Week Pattern")
        day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        by_day = filtered.groupby("weekday")["consumption_mwh"].mean().reindex(day_order).reset_index()
        colors_wk = ["#00d4aa"] * 5 + ["#ff6b6b"] * 2
        fig6 = go.Figure(go.Bar(
            x=by_day["weekday"], y=by_day["consumption_mwh"],
            marker_color=colors_wk,
        ))
        fig6.update_layout(
            template="plotly_dark", plot_bgcolor="#0f1117",
            paper_bgcolor="#0f1117", height=340, yaxis_title="Avg Daily MWh",
        )
        st.plotly_chart(fig6, use_container_width=True)

    st.subheader("Monthly Heatmap (Avg Daily MWh per Year × Month)")
    pivot = filtered.pivot_table(
        values="consumption_mwh", index="year", columns="month", aggfunc="mean"
    )
    month_names = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    pivot.columns = [month_names[m - 1] for m in pivot.columns]
    fig7 = px.imshow(
        pivot, color_continuous_scale="YlOrRd",
        labels=dict(color="Avg MWh"), aspect="auto", text_auto=".0f",
    )
    fig7.update_layout(
        template="plotly_dark", plot_bgcolor="#0f1117",
        paper_bgcolor="#0f1117", height=350,
    )
    st.plotly_chart(fig7, use_container_width=True)

# ══════════════════════════════════════════════════════════════
# TAB 4: SQL INSIGHTS
# ══════════════════════════════════════════════════════════════
with tab4:
    st.subheader("🔍 Key SQL-Driven Insights")
    st.markdown("*These findings were derived from 15 SQL business questions on the dataset*")

    conn = sqlite3.connect(DB_PATH)

    st.markdown("#### Q2: Year-over-Year Growth Rate")
    q2 = pd.read_sql_query("""
        WITH yearly AS (
            SELECT year, SUM(consumption_mwh) AS total_mwh
            FROM daily_energy GROUP BY year
        )
        SELECT year,
               ROUND(total_mwh/1e6, 2) AS total_twh,
               ROUND(
                   (total_mwh - LAG(total_mwh) OVER (ORDER BY year))
                   / LAG(total_mwh) OVER (ORDER BY year) * 100, 2
               ) AS yoy_growth_pct
        FROM yearly ORDER BY year
    """, conn)
    st.dataframe(q2, use_container_width=True)

    st.markdown("#### Q6: Top 10 Peak Consumption Days")
    q6 = pd.read_sql_query("""
        SELECT date, year, season, weekday,
               ROUND(consumption_mwh, 0) AS consumption_mwh
        FROM daily_energy
        ORDER BY consumption_mwh DESC LIMIT 10
    """, conn)
    st.dataframe(q6, use_container_width=True)

    st.markdown("#### Q15: Executive KPI Summary")
    q15 = pd.read_sql_query("""
        SELECT MIN(year) AS data_from, MAX(year) AS data_to,
               COUNT(*) AS total_days,
               ROUND(SUM(consumption_mwh)/1e6, 1) AS total_twh,
               ROUND(AVG(consumption_mwh), 0)      AS avg_daily_mwh,
               ROUND(MAX(consumption_mwh), 0)      AS peak_day_mwh,
               ROUND(AVG(renewable_share_pct), 1)  AS avg_renewable_pct
        FROM daily_energy
    """, conn)
    st.dataframe(q15, use_container_width=True)

    conn.close()
    st.divider()
    st.caption("Full SQL case study: [github.com/Pritesh74](https://github.com/Pritesh74)")

st.divider()

# ══════════════════════════════════════════════════════════════
# FORECAST SECTION
# ══════════════════════════════════════════════════════════════
st.subheader("🔮 Forecast: Next 365 Days")

if os.path.exists(FORECAST_PATH) and os.path.exists(CLEAN_PATH):
    forecast = pd.read_csv(FORECAST_PATH)
    forecast["ds"] = pd.to_datetime(forecast["ds"])

    actual = pd.read_csv(CLEAN_PATH)
    actual["date"] = pd.to_datetime(actual["date"])

    last_date    = actual["date"].max()
    future       = forecast[forecast["ds"] > last_date].copy()
    forecast_col = "yhat_smooth" if "yhat_smooth" in future.columns else "yhat"

    fig_forecast = go.Figure()
    fig_forecast.add_trace(go.Scatter(
        x=actual["date"], y=actual["consumption_mwh"],
        name="Actual", line=dict(color="cyan"),
    ))
    fig_forecast.add_trace(go.Scatter(
        x=future["ds"], y=future[forecast_col],
        name="Forecast", line=dict(color="yellow"),
    ))
    fig_forecast.add_trace(go.Scatter(
        x=future["ds"], y=future["yhat_upper"],
        line=dict(width=0), showlegend=False,
    ))
    fig_forecast.add_trace(go.Scatter(
        x=future["ds"], y=future["yhat_lower"],
        fill="tonexty", name="Confidence Interval",
        line=dict(width=0), fillcolor="rgba(255,255,0,0.2)",
    ))
    fig_forecast.update_layout(
        template="plotly_dark", plot_bgcolor="#0f1117",
        paper_bgcolor="#0f1117", height=420,
        xaxis_title="Date", yaxis_title="Consumption (MWh)",
        legend=dict(orientation="h", y=1.05),
    )
    st.plotly_chart(fig_forecast, use_container_width=True)
else:
    st.warning("Forecast file not found. Run `python 04_forecasting.py` first.")

# ══════════════════════════════════════════════════════════════
# ANOMALY SECTION
# ══════════════════════════════════════════════════════════════
st.subheader("⚠️ Anomaly Detection")

if os.path.exists(ANOMALY_PATH):
    anomalies = pd.read_csv(ANOMALY_PATH)
    anomalies["date"] = pd.to_datetime(anomalies["date"])

    fig_anom = go.Figure()

    normal = anomalies[anomalies["anomaly"] == 0]
    fig_anom.add_trace(go.Scatter(
        x=normal["date"], y=normal["consumption_mwh"],
        mode="markers", name="Normal",
        marker=dict(color="gray", size=4, opacity=0.5),
    ))

    outliers = anomalies[anomalies["anomaly"] == 1]
    fig_anom.add_trace(go.Scatter(
        x=outliers["date"], y=outliers["consumption_mwh"],
        mode="markers", name="Anomaly",
        marker=dict(color="red", size=8),
    ))

    # COVID shaded region + annotation on the chart
    fig_anom.add_vrect(
        x0="2020-03-15", x1="2020-06-30",
        fillcolor="rgba(255,100,100,0.08)",
        layer="below", line_width=0,
    )
    fig_anom.add_annotation(
        x="2020-05-01",
        y=anomalies["consumption_mwh"].max() * 1.02,
        text="COVID-19 Lockdown",
        showarrow=False,
        font=dict(color="#ff6b6b", size=11),
        bgcolor="rgba(0,0,0,0.5)",
    )

    fig_anom.update_layout(
        template="plotly_dark",
        plot_bgcolor="#0f1117",
        paper_bgcolor="#0f1117",
        title="Detected Anomalies in Energy Consumption",
        height=420,
    )
    st.plotly_chart(fig_anom, use_container_width=True)

    # Enhanced COVID insight box
    st.warning(
        "⚠️ **COVID-19 Impact detected (Apr–Jun 2020):** A significant cluster of "
        "low-consumption anomalies appears during Germany's first lockdown. Daily demand "
        "dropped ~10–15% below seasonal norms as industrial activity halted, offices emptied, "
        "and transport collapsed. This is one of the most visible real-world economic events "
        "in the dataset — and a clear example of how external shocks appear in energy data."
    )
else:
    st.warning("Anomaly file not found. Run `python 05_anomaly_detection.py` first.")