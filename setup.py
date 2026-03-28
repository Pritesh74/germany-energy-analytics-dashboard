"""
================================================
GERMANY ENERGY CONSUMPTION ANALYSIS
Setup Script — Downloads & prepares all data
================================================
Run this first: python setup.py
"""

import os
import urllib.request
import zipfile

# Create project folders
folders = [
    "data/raw",
    "data/processed",
    "outputs/charts",
    "outputs/sql_results",
    "streamlit_app",
]
for folder in folders:
    os.makedirs(folder, exist_ok=True)
    print(f"✅ Created folder: {folder}")

# -----------------------------------------------
# DATA SOURCE: SMARD — Bundesnetzagentur (Official)
# https://www.smard.de/en/downloadcenter/download-market-data
# -----------------------------------------------
# Manual download instructions (SMARD requires browser interaction):
print("""
========================================
📥 DATA DOWNLOAD INSTRUCTIONS
========================================

1. Go to: https://www.smard.de/en/downloadcenter/download-market-data

2. Select the following settings:
   - Category:     Electricity generation
   - Filter:       Total (all energy sources)
   - Resolution:   Quarterly (or Monthly)
   - Time range:   2018 – 2024
   - Format:       CSV

3. Also download:
   - Category:     Electricity consumption
   - Same settings

4. Save both CSVs into:  data/raw/

5. Rename them:
   - data/raw/energy_generation.csv
   - data/raw/energy_consumption.csv

Then run: python 01_clean_data.py
========================================

💡 Alternative: Use the pre-cleaned dataset from Open Power System Data:
   https://data.open-power-system-data.org/time_series/
   → Download "time_series_60min_singleindex.csv"
   → Save as: data/raw/opsd_germany.csv
   → Then run: python 01_clean_data.py

OPSD is easier and recommended for getting started quickly.
""")
