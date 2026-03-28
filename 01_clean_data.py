"""
================================================
GERMANY ENERGY CONSUMPTION ANALYSIS
Script 01 — Data Cleaning & Preprocessing
================================================
Run: python 01_clean_data.py
Source: Open Power System Data (OPSD)
Download: https://data.open-power-system-data.org/time_series/
File: time_series_60min_singleindex.csv → save as data/raw/opsd_germany.csv
"""

import os
import sqlite3

import numpy as np
import pandas as pd

RAW_PATH = "data/raw/opsd_germany.csv"
DB_PATH = "data/processed/energy_germany.db"
CSV_OUT = "data/processed/energy_clean.csv"

print("📂 Loading raw data...")

# ── Load ──────────────────────────────────────────────────────────────────────
df = pd.read_csv(RAW_PATH, low_memory=False, parse_dates=["utc_timestamp"])

print(f"   Raw shape: {df.shape}")
print(f"   Columns: {list(df.columns[:15])}...")

# ── Select Germany-relevant columns ───────────────────────────────────────────
germany_cols = [c for c in df.columns if c.startswith("DE_")]
keep_cols = ["utc_timestamp"] + germany_cols
df = df[keep_cols].copy()

# Rename for readability
df.rename(columns={"utc_timestamp": "timestamp"}, inplace=True)

# ── Clean column names ─────────────────────────────────────────────────────────
df.columns = (
    df.columns
    .str.replace("DE_", "", regex=False)
    .str.lower()
    .str.replace(" ", "_")
    .str.replace("-", "_")
)

print(f"   Germany columns kept: {list(df.columns)}")

# ── Time features ──────────────────────────────────────────────────────────────
df["year"] = df["timestamp"].dt.year
df["month"] = df["timestamp"].dt.month
df["day"] = df["timestamp"].dt.day
df["hour"] = df["timestamp"].dt.hour
df["weekday"] = df["timestamp"].dt.day_name()
df["quarter"] = df["timestamp"].dt.quarter
df["date"] = df["timestamp"].dt.date.astype(str)

month_to_season = {
    12: "Winter", 1: "Winter", 2: "Winter",
    3: "Spring", 4: "Spring", 5: "Spring",
    6: "Summer", 7: "Summer", 8: "Summer",
    9: "Autumn", 10: "Autumn", 11: "Autumn",
}
df["season"] = df["month"].map(month_to_season)

# ── Filter to 2018–2024 ────────────────────────────────────────────────────────
df = df[(df["year"] >= 2018) & (df["year"] <= 2024)].copy()

# ── Handle missing values ──────────────────────────────────────────────────────
print("\n🔍 Missing values before cleaning:")
missing = df.isnull().sum()
print(missing[missing > 0].head(10))

df = df.sort_values("timestamp").copy()
numeric_cols = df.select_dtypes(include=np.number).columns
df[numeric_cols] = df[numeric_cols].ffill(limit=3)

main_load_col = "load_actual_entsoe_transparency"
if main_load_col not in df.columns:
    raise KeyError(
        f"Expected main load column '{main_load_col}' not found. "
        f"Available columns: {list(df.columns)}"
    )

df.dropna(subset=[main_load_col], inplace=True)

print("\n✅ After cleaning:")
print(f"   Shape: {df.shape}")
print(f"   Date range: {df['timestamp'].min()} → {df['timestamp'].max()}")
print(f"   Missing values remaining: {df.isnull().sum().sum()}")

# ── Derived metrics ────────────────────────────────────────────────────────────
if "load_actual_entsoe_transparency" in df.columns:
    df.rename(columns={"load_actual_entsoe_transparency": "consumption_mwh"}, inplace=True)

# Aggregate daily for SQL / dashboard friendliness
daily = (
    df.groupby("date")
    .agg(
        year=("year", "first"),
        month=("month", "first"),
        quarter=("quarter", "first"),
        season=("season", "first"),
        weekday=("weekday", "first"),
        consumption_mwh=("consumption_mwh", "sum"),
        solar_mwh=("solar_generation_actual", "sum") if "solar_generation_actual" in df.columns else 0,
        wind_onshore_mwh=("wind_onshore_generation_actual", "sum") if "wind_onshore_generation_actual" in df.columns else 0,
        wind_offshore_mwh=("wind_offshore_generation_actual", "sum") if "wind_offshore_generation_actual" in df.columns else 0,
    )
    .reset_index()
)

# ── Renewable metrics (IMPORTANT: before saving) ──────────────────────────────
renewable_cols = [
    c for c in ["solar_mwh", "wind_onshore_mwh", "wind_offshore_mwh"]
    if c in daily.columns
]

daily["renewable_total_mwh"] = daily[renewable_cols].sum(axis=1)
daily["renewable_share_pct"] = (
    daily["renewable_total_mwh"] / daily["consumption_mwh"] * 100
).round(2)

print(f"\n📊 Daily aggregated shape: {daily.shape}")

# ── Ensure output folder exists ────────────────────────────────────────────────
os.makedirs(os.path.dirname(CSV_OUT), exist_ok=True)

# ── Save CSV ───────────────────────────────────────────────────────────────────
hourly_out = CSV_OUT.replace("clean", "hourly_clean")
df.to_csv(hourly_out, index=False)
daily.to_csv(CSV_OUT, index=False)

print(f"\n💾 Saved hourly CSV: {hourly_out}")
print(f"💾 Saved daily CSV: {CSV_OUT}")

# ── Save to SQLite ─────────────────────────────────────────────────────────────
conn = sqlite3.connect(DB_PATH)
daily.to_sql("daily_energy", conn, if_exists="replace", index=False)
df.to_sql("hourly_energy", conn, if_exists="replace", index=False)
conn.close()

print(f"💾 SQLite DB saved: {DB_PATH}")
print("\n🎉 Data preparation complete! Run: python 02_sql_analysis.py")