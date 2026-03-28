"""
================================================
GERMANY ENERGY CONSUMPTION ANALYSIS
Script 02 — SQL Case Study (15 Business Questions)
================================================
Run: python 02_sql_analysis.py
"""

import sqlite3
import pandas as pd
import os

DB_PATH = "data/processed/energy_germany.db"
OUT_DIR = "outputs/sql_results"
os.makedirs(OUT_DIR, exist_ok=True)

conn = sqlite3.connect(DB_PATH)

def run_query(title, question, sql, insight=""):
    """Run a SQL query, print results, save to CSV."""
    print(f"\n{'='*60}")
    print(f"📌 {title}")
    print(f"❓ Business Question: {question}")
    print(f"{'='*60}")
    df = pd.read_sql_query(sql, conn)
    print(df.to_string(index=False))
    if insight:
        print(f"\n💡 Insight: {insight}")
    safe_title = title.replace(" ", "_").replace("/", "_").lower()[:40]
    df.to_csv(f"{OUT_DIR}/{safe_title}.csv", index=False)
    return df


# ──────────────────────────────────────────────────────────────────────────────
# Q1: OVERALL ANNUAL CONSUMPTION TREND
# ──────────────────────────────────────────────────────────────────────────────
run_query(
    title="Q1: Annual Energy Consumption Trend",
    question="How has total energy consumption changed year over year in Germany?",
    sql="""
        SELECT
            year,
            ROUND(SUM(consumption_mwh) / 1e6, 2)    AS total_twh,
            ROUND(AVG(consumption_mwh), 0)           AS avg_daily_mwh,
            ROUND(MAX(consumption_mwh), 0)           AS peak_daily_mwh,
            ROUND(MIN(consumption_mwh), 0)           AS min_daily_mwh
        FROM daily_energy
        GROUP BY year
        ORDER BY year;
    """,
    insight="Identify if Germany's consumption is declining (efficiency gains, deindustrialisation) or growing."
)

# ──────────────────────────────────────────────────────────────────────────────
# Q2: YEAR-OVER-YEAR GROWTH RATE
# ──────────────────────────────────────────────────────────────────────────────
run_query(
    title="Q2: Year-over-Year Consumption Growth Rate",
    question="What is the YoY growth rate of energy consumption?",
    sql="""
        WITH yearly AS (
            SELECT year, SUM(consumption_mwh) AS total_mwh
            FROM daily_energy
            GROUP BY year
        )
        SELECT
            year,
            ROUND(total_mwh / 1e6, 2)                                         AS total_twh,
            ROUND((total_mwh - LAG(total_mwh) OVER (ORDER BY year))
                  / LAG(total_mwh) OVER (ORDER BY year) * 100, 2)             AS yoy_growth_pct
        FROM yearly
        ORDER BY year;
    """,
    insight="Negative YoY in 2022/2023 likely reflects the energy crisis response and efficiency measures."
)

# ──────────────────────────────────────────────────────────────────────────────
# Q3: SEASONAL CONSUMPTION PATTERNS
# ──────────────────────────────────────────────────────────────────────────────
run_query(
    title="Q3: Seasonal Consumption Patterns",
    question="Which season has the highest energy demand and by how much?",
    sql="""
        SELECT
            season,
            ROUND(AVG(consumption_mwh), 0)  AS avg_daily_mwh,
            ROUND(SUM(consumption_mwh)/1e6, 2) AS total_twh,
            COUNT(*)                         AS days
        FROM daily_energy
        GROUP BY season
        ORDER BY avg_daily_mwh DESC;
    """,
    insight="Winter typically peaks due to heating demand and shorter daylight hours."
)

# ──────────────────────────────────────────────────────────────────────────────
# Q4: MONTHLY CONSUMPTION BREAKDOWN
# ──────────────────────────────────────────────────────────────────────────────
run_query(
    title="Q4: Monthly Consumption Breakdown",
    question="Which months are peak vs. low demand periods for grid planning?",
    sql="""
        SELECT
            month,
            ROUND(AVG(consumption_mwh), 0)  AS avg_daily_mwh,
            ROUND(MIN(consumption_mwh), 0)  AS min_mwh,
            ROUND(MAX(consumption_mwh), 0)  AS max_mwh
        FROM daily_energy
        GROUP BY month
        ORDER BY month;
    """,
    insight="December/January = highest demand. July/August = lowest (warm weather, industrial holidays)."
)

# ──────────────────────────────────────────────────────────────────────────────
# Q5: WEEKDAY VS WEEKEND CONSUMPTION
# ──────────────────────────────────────────────────────────────────────────────
run_query(
    title="Q5: Weekday vs Weekend Consumption",
    question="Is there a significant difference between weekday and weekend energy use?",
    sql="""
        SELECT
            CASE WHEN weekday IN ('Saturday','Sunday') THEN 'Weekend' ELSE 'Weekday' END AS day_type,
            ROUND(AVG(consumption_mwh), 0)  AS avg_daily_mwh,
            COUNT(*)                         AS total_days
        FROM daily_energy
        GROUP BY day_type
        ORDER BY avg_daily_mwh DESC;
    """,
    insight="Weekdays are ~15-20% higher — industrial and commercial activity drives the gap."
)

# ──────────────────────────────────────────────────────────────────────────────
# Q6: TOP 10 HIGHEST CONSUMPTION DAYS
# ──────────────────────────────────────────────────────────────────────────────
run_query(
    title="Q6: Top 10 Peak Consumption Days",
    question="Which specific days had the highest energy demand — and what caused the spikes?",
    sql="""
        SELECT
            date, year, month, season, weekday,
            ROUND(consumption_mwh, 0) AS consumption_mwh
        FROM daily_energy
        ORDER BY consumption_mwh DESC
        LIMIT 10;
    """,
    insight="Peak days are almost always cold winter weekdays — validate against historical cold snaps."
)

# ──────────────────────────────────────────────────────────────────────────────
# Q7: TOP 10 LOWEST CONSUMPTION DAYS
# ──────────────────────────────────────────────────────────────────────────────
run_query(
    title="Q7: Top 10 Lowest Consumption Days",
    question="Which days had the lowest demand — are they holidays or summer weekends?",
    sql="""
        SELECT
            date, year, month, season, weekday,
            ROUND(consumption_mwh, 0) AS consumption_mwh
        FROM daily_energy
        ORDER BY consumption_mwh ASC
        LIMIT 10;
    """,
    insight="Low-demand days often fall on public holidays (Christmas, Easter) — useful for grid balancing."
)

# ──────────────────────────────────────────────────────────────────────────────
# Q8: RENEWABLE ENERGY SHARE BY YEAR
# ──────────────────────────────────────────────────────────────────────────────
run_query(
    title="Q8: Renewable Energy Share by Year",
    question="Is Germany's renewable energy share growing — and how fast?",
    sql="""
        SELECT
            year,
            ROUND(AVG(renewable_share_pct), 1) AS avg_renewable_share_pct,
            ROUND(MAX(renewable_share_pct), 1) AS max_renewable_share_pct,
            ROUND(MIN(renewable_share_pct), 1) AS min_renewable_share_pct
        FROM daily_energy
        GROUP BY year
        ORDER BY year;
    """,
    insight="Germany's Energiewende target: 80% renewables by 2030. Track progress here."
)

# ──────────────────────────────────────────────────────────────────────────────
# Q9: SOLAR vs WIND CONTRIBUTION BY SEASON
# ──────────────────────────────────────────────────────────────────────────────
run_query(
    title="Q9: Solar vs Wind by Season",
    question="Which renewable source dominates in each season — solar or wind?",
    sql="""
        SELECT
            season,
            ROUND(AVG(solar_mwh), 0)          AS avg_solar_mwh,
            ROUND(AVG(wind_onshore_mwh), 0)   AS avg_wind_onshore_mwh,
            ROUND(AVG(wind_offshore_mwh), 0)  AS avg_wind_offshore_mwh
        FROM daily_energy
        GROUP BY season
        ORDER BY avg_solar_mwh DESC;
    """,
    insight="Solar peaks in summer; wind peaks in winter — they naturally complement each other."
)

# ──────────────────────────────────────────────────────────────────────────────
# Q10: DAYS WITH >50% RENEWABLE SHARE
# ──────────────────────────────────────────────────────────────────────────────
run_query(
    title="Q10: Days with >50% Renewable Share",
    question="How many days per year does Germany run on majority renewables?",
    sql="""
        SELECT
            year,
            COUNT(*) AS days_above_50pct_renewable,
            ROUND(COUNT(*) * 100.0 / 365, 1) AS pct_of_year
        FROM daily_energy
        WHERE renewable_share_pct > 50
        GROUP BY year
        ORDER BY year;
    """,
    insight="An increasing trend signals Germany's grid is genuinely decarbonising."
)

# ──────────────────────────────────────────────────────────────────────────────
# Q11: CONSUMPTION BEFORE/AFTER 2022 ENERGY CRISIS
# ──────────────────────────────────────────────────────────────────────────────
run_query(
    title="Q11: Impact of 2022 Energy Crisis",
    question="Did Germany's energy consumption measurably drop after the 2022 gas crisis?",
    sql="""
        SELECT
            CASE WHEN year < 2022 THEN 'Pre-Crisis (2018-2021)' ELSE 'Post-Crisis (2022-2024)' END AS period,
            ROUND(AVG(consumption_mwh), 0)       AS avg_daily_mwh,
            ROUND(SUM(consumption_mwh)/1e6, 2)   AS total_twh,
            COUNT(DISTINCT year)                  AS years_in_period
        FROM daily_energy
        GROUP BY period;
    """,
    insight="Post-2022 consumption drop reflects both efficiency mandates and economic slowdown."
)

# ──────────────────────────────────────────────────────────────────────────────
# Q12: MONTHLY RENEWABLE SHARE HEATMAP DATA
# ──────────────────────────────────────────────────────────────────────────────
run_query(
    title="Q12: Monthly Renewable Share by Year (Heatmap Data)",
    question="How does renewable share vary month-by-month across years?",
    sql="""
        SELECT
            year,
            month,
            ROUND(AVG(renewable_share_pct), 1) AS avg_renewable_share_pct
        FROM daily_energy
        GROUP BY year, month
        ORDER BY year, month;
    """,
    insight="Reveals structural shift — summer months progressively greener each year."
)

# ──────────────────────────────────────────────────────────────────────────────
# Q13: ROLLING 30-DAY AVERAGE CONSUMPTION
# ──────────────────────────────────────────────────────────────────────────────
run_query(
    title="Q13: Rolling 30-Day Average Consumption",
    question="What does smoothed consumption look like — removing daily noise?",
    sql="""
        SELECT
            date,
            year,
            month,
            ROUND(consumption_mwh, 0) AS daily_mwh,
            ROUND(AVG(consumption_mwh) OVER (
                ORDER BY date
                ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
            ), 0) AS rolling_30d_avg_mwh
        FROM daily_energy
        ORDER BY date;
    """,
    insight="Rolling average is clean for executive dashboards — removes holiday/weekend spikes."
)

# ──────────────────────────────────────────────────────────────────────────────
# Q14: CONSUMPTION PERCENTILE RANKING
# ──────────────────────────────────────────────────────────────────────────────
run_query(
    title="Q14: Consumption Percentile by Day",
    question="How does each day rank in the overall consumption distribution?",
    sql="""
        SELECT
            date, year, season, weekday,
            ROUND(consumption_mwh, 0) AS consumption_mwh,
            ROUND(PERCENT_RANK() OVER (ORDER BY consumption_mwh) * 100, 1) AS percentile
        FROM daily_energy
        ORDER BY percentile DESC
        LIMIT 20;
    """,
    insight="Top percentile days are your grid stress events — critical for infrastructure planning."
)

# ──────────────────────────────────────────────────────────────────────────────
# Q15: EXECUTIVE KPI SUMMARY
# ──────────────────────────────────────────────────────────────────────────────
run_query(
    title="Q15: Executive KPI Summary Dashboard",
    question="What are the headline KPIs for the full analysis period?",
    sql="""
        SELECT
            MIN(year)                                    AS data_from,
            MAX(year)                                    AS data_to,
            COUNT(*)                                     AS total_days,
            ROUND(SUM(consumption_mwh)/1e6, 1)          AS total_consumption_twh,
            ROUND(AVG(consumption_mwh), 0)               AS avg_daily_mwh,
            ROUND(MAX(consumption_mwh), 0)               AS peak_day_mwh,
            ROUND(AVG(renewable_share_pct), 1)           AS avg_renewable_share_pct,
            ROUND(MAX(renewable_share_pct), 1)           AS max_renewable_share_pct,
            SUM(CASE WHEN renewable_share_pct > 50
                THEN 1 ELSE 0 END)                       AS days_majority_renewable
        FROM daily_energy;
    """,
    insight="These are your headline numbers — put them at the top of your README and Streamlit app."
)

conn.close()
print("\n\n🎉 SQL Analysis complete!")
print(f"📁 Results saved to: {OUT_DIR}/")
print("➡️  Next: python 03_eda.py")
