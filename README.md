# ⚡ Germany Energy Consumption Analysis Dashboard

## Live Demo
[Open the Streamlit App](https://germany-energy-analytics-dashboard-josb9hho5tdysusiidj3n9.streamlit.app/)

> End-to-end data analytics project using Python, SQL, Streamlit, forecasting, and anomaly detection.

[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?logo=streamlit)](https://streamlit.io)
[![SQLite](https://img.shields.io/badge/SQLite-SQL%20Analysis-07405E?logo=sqlite)](https://sqlite.org)
[![Plotly](https://img.shields.io/badge/Plotly-Interactive%20Charts-3F4F75?logo=plotly)](https://plotly.com)
[![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-150458?logo=pandas)](https://pandas.pydata.org)

---

## 📌 Project Overview

This project analyzes Germany’s electricity consumption and renewable energy trends using an end-to-end analytics workflow.

It combines:

- data cleaning with Python
- SQL analysis with SQLite
- interactive dashboarding with Streamlit
- forecasting with Prophet
- anomaly detection for unusual demand behavior

The dashboard is built on Germany electricity data from **2018 to 2020** and is designed as a portfolio-ready analytics project.

**Data sources:**  
[Open Power System Data (OPSD)](https://data.open-power-system-data.org/)  
[SMARD – Bundesnetzagentur](https://www.smard.de/)

---

## 🎯 Project Goals

This project was built to answer practical analytics questions such as:

- How does electricity consumption change over time?
- Which seasons have the highest demand?
- How does renewable share evolve month by month?
- What weekday and monthly demand patterns appear in the data?
- What are the top peak consumption days?
- Can future demand be forecasted?
- Can unusual consumption periods be detected automatically?

---

## 📊 Dashboard Features

The Streamlit dashboard includes:

- **KPI cards**
  - Total consumption
  - Average daily demand
  - Peak day
  - Average renewable share
  - Days with more than 50% renewable share

- **Tabs**
  - Consumption Trends
  - Renewable Energy
  - Time Patterns
  - SQL Insights

- **Advanced sections**
  - 365-day forecast
  - anomaly detection visualization

---

## 📈 Key Insights

Some of the main insights from the dashboard:

- Germany’s electricity demand shows strong seasonal variation, with higher demand in colder periods.
- Renewable share generally improves over time, with several periods crossing the 50% threshold.
- Weekday demand is consistently higher than weekend demand.
- Forecasting captures the broad consumption pattern and expected future movement.
- Anomaly detection highlights unusual demand periods, especially around major disruptions such as the 2020 COVID period.

---

## 🛠️ Tech Stack

| Layer | Tools |
|---|---|
| Data Processing | Python, Pandas, NumPy |
| Database | SQLite |
| SQL Analysis | SQLite queries, window functions |
| Visualization | Plotly, Matplotlib, Seaborn |
| Dashboard | Streamlit |
| Forecasting | Prophet |
| Anomaly Detection | Scikit-learn |
| Version Control | Git, GitHub |

---

## 📁 Project Structure

```text
germany-energy-analytics-dashboard/
│
├── app.py
├── 01_clean_data.py
├── 02_sql_analysis.py
├── 03_eda.py
├── 04_forecasting.py
├── 05_anomaly_detection.py
│
├── data/
│   ├── raw/
│   │   └── opsd_germany.csv
│   └── processed/
│       ├── energy_clean.csv
│       └── energy_germany.db
│
├── outputs/
│   ├── forecast/
│   │   └── forecast.csv
│   └── anomalies/
│       └── anomalies.csv
│
├── assets/
│   ├── dashboard-overview.png
│   ├── forecast-anomaly.png
│   ├── renewable-energy.png
│   └── sql-insights.png
│
├── POWERBI_GUIDE.md
├── README.md
├── requirements.txt
└── .gitignore