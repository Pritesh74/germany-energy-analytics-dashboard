"""
================================================
GERMANY ENERGY CONSUMPTION ANALYSIS
Script 03 — EDA & Visualizations
================================================
Run: python 03_eda.py
Outputs all charts to: outputs/charts/
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import sqlite3
import os

# ── Style ──────────────────────────────────────────────────────────────────────
plt.rcParams.update({
    "figure.facecolor": "#0f1117",
    "axes.facecolor":   "#0f1117",
    "axes.edgecolor":   "#333333",
    "axes.labelcolor":  "#cccccc",
    "xtick.color":      "#888888",
    "ytick.color":      "#888888",
    "text.color":       "#eeeeee",
    "grid.color":       "#222222",
    "grid.linestyle":   "--",
    "grid.linewidth":   0.5,
    "font.family":      "DejaVu Sans",
    "font.size":        11,
})

ACCENT   = "#00d4aa"   # teal
ACCENT2  = "#ff6b6b"   # coral
ACCENT3  = "#ffd93d"   # yellow
BLUE     = "#4a9eff"
OUT_DIR  = "outputs/charts"
os.makedirs(OUT_DIR, exist_ok=True)

def save(fig, name):
    path = f"{OUT_DIR}/{name}.png"
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    print(f"✅ Saved: {path}")
    plt.close(fig)

# ── Load data ──────────────────────────────────────────────────────────────────
conn = sqlite3.connect("data/processed/energy_germany.db")
df   = pd.read_sql_query("SELECT * FROM daily_energy", conn)
conn.close()

df["date"] = pd.to_datetime(df["date"])
df = df.sort_values("date")

print(f"📊 Loaded {len(df):,} daily records")
print(f"   Date range: {df['date'].min().date()} → {df['date'].max().date()}")
print(f"   Columns: {list(df.columns)}\n")

# ═══════════════════════════════════════════════════════════════════════════════
# CHART 1: Annual Consumption Trend (Bar + Line)
# ═══════════════════════════════════════════════════════════════════════════════
yearly = df.groupby("year")["consumption_mwh"].sum() / 1e6  # TWh

fig, ax = plt.subplots(figsize=(10, 5))
bars = ax.bar(yearly.index, yearly.values, color=ACCENT, alpha=0.7, width=0.6)
ax.plot(yearly.index, yearly.values, "o-", color=ACCENT3, lw=2, ms=7, zorder=5)
for bar, val in zip(bars, yearly.values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
            f"{val:.0f} TWh", ha="center", color="#eeeeee", fontsize=9)
ax.set_title("Germany Annual Energy Consumption (TWh)", fontsize=14, pad=15)
ax.set_xlabel("Year"); ax.set_ylabel("Total Consumption (TWh)")
ax.yaxis.grid(True); ax.set_axisbelow(True)
save(fig, "01_annual_consumption_trend")

# ═══════════════════════════════════════════════════════════════════════════════
# CHART 2: Seasonal Average Consumption
# ═══════════════════════════════════════════════════════════════════════════════
season_order = ["Winter", "Spring", "Summer", "Autumn"]
seasonal = df.groupby("season")["consumption_mwh"].mean().reindex(season_order)
colors   = [BLUE, ACCENT, ACCENT3, ACCENT2]

fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.bar(seasonal.index, seasonal.values, color=colors, alpha=0.85, width=0.5)
for bar, val in zip(bars, seasonal.values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 100,
            f"{val:,.0f}", ha="center", fontsize=9, color="#eeeeee")
ax.set_title("Average Daily Consumption by Season (MWh)", fontsize=14, pad=15)
ax.set_ylabel("Avg Daily MWh"); ax.yaxis.grid(True); ax.set_axisbelow(True)
save(fig, "02_seasonal_consumption")

# ═══════════════════════════════════════════════════════════════════════════════
# CHART 3: Monthly Heatmap (Year × Month)
# ═══════════════════════════════════════════════════════════════════════════════
pivot = df.pivot_table(values="consumption_mwh", index="year", columns="month", aggfunc="mean")
month_names = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
pivot.columns = month_names

fig, ax = plt.subplots(figsize=(12, 6))
sns.heatmap(pivot, ax=ax, cmap="YlOrRd", annot=True, fmt=".0f",
            linewidths=0.5, linecolor="#0f1117",
            cbar_kws={"label": "Avg Daily MWh"})
ax.set_title("Average Daily Consumption Heatmap (MWh) — Year × Month", fontsize=13, pad=15)
ax.set_xlabel("Month"); ax.set_ylabel("Year")
save(fig, "03_monthly_heatmap")

# ═══════════════════════════════════════════════════════════════════════════════
# CHART 4: Weekday vs Weekend
# ═══════════════════════════════════════════════════════════════════════════════
weekday_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
by_day = df.groupby("weekday")["consumption_mwh"].mean().reindex(weekday_order)
colors_wk = [ACCENT]*5 + [ACCENT2]*2

fig, ax = plt.subplots(figsize=(9, 5))
bars = ax.bar(by_day.index, by_day.values, color=colors_wk, alpha=0.85, width=0.6)
for bar, val in zip(bars, by_day.values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 100,
            f"{val:,.0f}", ha="center", fontsize=8, color="#eeeeee")
ax.set_title("Average Energy Consumption by Day of Week (MWh)", fontsize=13, pad=15)
ax.set_ylabel("Avg Daily MWh"); ax.yaxis.grid(True); ax.set_axisbelow(True)
ax.legend(handles=[
    plt.Rectangle((0,0),1,1, color=ACCENT, alpha=0.85, label="Weekday"),
    plt.Rectangle((0,0),1,1, color=ACCENT2, alpha=0.85, label="Weekend"),
], loc="upper right")
save(fig, "04_weekday_consumption")

# ═══════════════════════════════════════════════════════════════════════════════
# CHART 5: Renewable Share Trend Over Time
# ═══════════════════════════════════════════════════════════════════════════════
if "renewable_share_pct" in df.columns:
    monthly_ren = df.groupby(["year", "month"])["renewable_share_pct"].mean().reset_index()
    monthly_ren["date_label"] = pd.to_datetime(
        monthly_ren[["year","month"]].assign(day=1))

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.fill_between(monthly_ren["date_label"], monthly_ren["renewable_share_pct"],
                    alpha=0.25, color=ACCENT)
    ax.plot(monthly_ren["date_label"], monthly_ren["renewable_share_pct"],
            color=ACCENT, lw=1.5)
    ax.axhline(50, color=ACCENT3, lw=1.2, ls="--", label="50% target line")
    ax.set_title("Germany Renewable Energy Share Over Time (%)", fontsize=13, pad=15)
    ax.set_ylabel("Renewable Share (%)"); ax.set_xlabel("")
    ax.yaxis.grid(True); ax.set_axisbelow(True); ax.legend()
    save(fig, "05_renewable_share_trend")

# ═══════════════════════════════════════════════════════════════════════════════
# CHART 6: Solar vs Wind by Season
# ═══════════════════════════════════════════════════════════════════════════════
if all(c in df.columns for c in ["solar_mwh","wind_onshore_mwh","wind_offshore_mwh"]):
    sv = df.groupby("season")[["solar_mwh","wind_onshore_mwh","wind_offshore_mwh"]].mean()
    sv = sv.reindex(season_order)

    x = np.arange(len(sv))
    w = 0.25
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(x - w,   sv["solar_mwh"],         w, color=ACCENT3, alpha=0.85, label="Solar")
    ax.bar(x,       sv["wind_onshore_mwh"],   w, color=ACCENT,  alpha=0.85, label="Wind Onshore")
    ax.bar(x + w,   sv["wind_offshore_mwh"],  w, color=BLUE,    alpha=0.85, label="Wind Offshore")
    ax.set_xticks(x); ax.set_xticklabels(sv.index)
    ax.set_title("Avg Daily Solar vs Wind Generation by Season (MWh)", fontsize=13, pad=15)
    ax.set_ylabel("Avg Daily MWh"); ax.legend()
    ax.yaxis.grid(True); ax.set_axisbelow(True)
    save(fig, "06_solar_vs_wind_season")

# ═══════════════════════════════════════════════════════════════════════════════
# CHART 7: 30-Day Rolling Average — Full Timeline
# ═══════════════════════════════════════════════════════════════════════════════
df["rolling_30d"] = df["consumption_mwh"].rolling(30, min_periods=1).mean()

fig, ax = plt.subplots(figsize=(14, 5))
ax.plot(df["date"], df["consumption_mwh"], color="#333333", lw=0.6, alpha=0.5, label="Daily")
ax.plot(df["date"], df["rolling_30d"],     color=ACCENT2,  lw=2,   label="30-Day Rolling Avg")
ax.set_title("Germany Daily Energy Consumption with 30-Day Rolling Average", fontsize=13, pad=15)
ax.set_ylabel("Consumption (MWh)"); ax.yaxis.grid(True); ax.set_axisbelow(True)
ax.legend(); ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"{x:,.0f}"))
save(fig, "07_rolling_average_timeline")

# ═══════════════════════════════════════════════════════════════════════════════
# CHART 8: YoY Comparison (all years on same monthly axis)
# ═══════════════════════════════════════════════════════════════════════════════
monthly = df.groupby(["year","month"])["consumption_mwh"].mean().reset_index()
year_colors = plt.cm.plasma(np.linspace(0.1, 0.9, monthly["year"].nunique()))

fig, ax = plt.subplots(figsize=(12, 5))
for (yr, grp), col in zip(monthly.groupby("year"), year_colors):
    lw = 2.5 if yr == monthly["year"].max() else 1.2
    ax.plot(grp["month"], grp["consumption_mwh"], "o-",
            color=col, lw=lw, ms=4, label=str(yr))
ax.set_xticks(range(1,13))
ax.set_xticklabels(["Jan","Feb","Mar","Apr","May","Jun",
                    "Jul","Aug","Sep","Oct","Nov","Dec"])
ax.set_title("Monthly Energy Consumption — Year-over-Year Comparison", fontsize=13, pad=15)
ax.set_ylabel("Avg Daily MWh"); ax.yaxis.grid(True); ax.set_axisbelow(True)
ax.legend(title="Year", bbox_to_anchor=(1.01, 1), loc="upper left")
save(fig, "08_yoy_monthly_comparison")

print("\n🎉 All charts generated!")
print(f"📁 Saved to: {OUT_DIR}/")
print("➡️  Next: run the Streamlit app with:  streamlit run streamlit_app/app.py")
