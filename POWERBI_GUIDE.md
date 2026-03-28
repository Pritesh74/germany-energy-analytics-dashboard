# Power BI Setup Guide
## Germany Energy Consumption Dashboard

---

## STEP 1 — Import Data

1. Open Power BI Desktop
2. Click **Get Data → Text/CSV**
3. Load: `data/processed/energy_clean.csv`
4. Click **Transform Data** and verify column types:
   - `date` → Date
   - `consumption_mwh`, `renewable_share_pct`, `solar_mwh`, `wind_onshore_mwh` → Decimal Number
   - `year`, `month`, `quarter` → Whole Number
   - `season`, `weekday` → Text

---

## STEP 2 — Create a Date Table (Best Practice)

In Power Query or DAX, create a proper date table:

```dax
DateTable = 
ADDCOLUMNS(
    CALENDAR(DATE(2018,1,1), DATE(2024,12,31)),
    "Year",        YEAR([Date]),
    "Month",       MONTH([Date]),
    "MonthName",   FORMAT([Date], "MMM"),
    "Quarter",     QUARTER([Date]),
    "QuarterLabel", "Q" & QUARTER([Date]),
    "Weekday",     FORMAT([Date], "dddd"),
    "WeekdayNum",  WEEKDAY([Date], 2),
    "Season",      SWITCH(TRUE(),
                     MONTH([Date]) IN {12,1,2},  "Winter",
                     MONTH([Date]) IN {3,4,5},   "Spring",
                     MONTH([Date]) IN {6,7,8},   "Summer",
                     "Autumn"
                   )
)
```

Then create a relationship:  
`DateTable[Date]` → `energy_clean[date]`  (Many-to-one)

---

## STEP 3 — DAX Measures

Create these measures in a new **"Measures"** table:

### Core KPIs

```dax
Total Consumption TWh = 
DIVIDE(SUM(energy_clean[consumption_mwh]), 1000000)

Avg Daily Consumption MWh = 
AVERAGE(energy_clean[consumption_mwh])

Peak Day MWh = 
MAX(energy_clean[consumption_mwh])

Avg Renewable Share % = 
AVERAGE(energy_clean[renewable_share_pct])
```

---

### Year-over-Year Growth

```dax
Consumption Previous Year = 
CALCULATE(
    [Total Consumption TWh],
    SAMEPERIODLASTYEAR(DateTable[Date])
)

YoY Growth % = 
DIVIDE(
    [Total Consumption TWh] - [Consumption Previous Year],
    [Consumption Previous Year]
)

YoY Growth % Label = 
FORMAT([YoY Growth %], "+0.0%;-0.0%;0.0%")
```

---

### Renewable Analysis

```dax
Days Above 50pct Renewable = 
COUNTROWS(
    FILTER(energy_clean, energy_clean[renewable_share_pct] > 50)
)

Pct Days Green = 
DIVIDE(
    [Days Above 50pct Renewable],
    COUNTROWS(energy_clean)
)

Renewable Trend vs Prior Year = 
VAR CurrentYear = CALCULATE([Avg Renewable Share %])
VAR PriorYear = CALCULATE(
    [Avg Renewable Share %],
    SAMEPERIODLASTYEAR(DateTable[Date])
)
RETURN CurrentYear - PriorYear
```

---

### Rolling Average

```dax
Rolling 30 Day Avg MWh = 
AVERAGEX(
    DATESINPERIOD(DateTable[Date], LASTDATE(DateTable[Date]), -30, DAY),
    CALCULATE(AVERAGE(energy_clean[consumption_mwh]))
)
```

---

### Weekday vs Weekend

```dax
Weekday Avg MWh = 
CALCULATE(
    [Avg Daily Consumption MWh],
    FILTER(energy_clean, 
        NOT(energy_clean[weekday] IN {"Saturday", "Sunday"}))
)

Weekend Avg MWh = 
CALCULATE(
    [Avg Daily Consumption MWh],
    FILTER(energy_clean,
        energy_clean[weekday] IN {"Saturday", "Sunday"})
)

Weekday vs Weekend Diff % = 
DIVIDE([Weekday Avg MWh] - [Weekend Avg MWh], [Weekend Avg MWh])
```

---

## STEP 4 — Dashboard Layout

### Page 1: Executive Overview
- **4 KPI cards** (top row): Total TWh · Avg Daily MWh · Avg Renewable % · Days >50% Green
- **Line chart**: Annual total consumption with YoY % overlay
- **Card**: Peak day + date
- **Gauge**: Avg renewable share vs 80% Energiewende target

### Page 2: Consumption Patterns
- **Area chart**: Daily consumption timeline with 30-day rolling average
- **Bar chart**: Seasonal average comparison
- **Column chart**: Weekday vs weekend (Mon–Sun)
- **Matrix heatmap**: Year × Month average MWh

### Page 3: Renewable Energy
- **Line + fill**: Monthly renewable share trend (with 50% milestone line)
- **Bar chart**: Avg renewable share by year
- **Clustered bar**: Solar vs Wind Onshore vs Wind Offshore by season
- **Card**: Days with majority renewables this year

---

## STEP 5 — Formatting Tips for Professional Look

1. **Theme**: Use dark theme (View → Themes → Dark)
2. **Colors**: 
   - Consumption: `#4a9eff` (blue)
   - Renewable: `#00d4aa` (teal)
   - Solar: `#ffd93d` (yellow)
   - Wind: `#00d4aa` (teal)
   - Alert/Peak: `#ff6b6b` (coral)
3. **Font**: Segoe UI throughout
4. **Background**: `#0f1117` or `#1a1d27`
5. Add your **name + GitHub link** in the footer of each page

---

## STEP 6 — Publish & Share

1. **File → Publish → Publish to Power BI**
2. Sign in with a free Microsoft work/school account
3. In Power BI Service: click **Share → Copy link**
4. Add to your resume: *"View live dashboard: [your link]"*
5. Add to GitHub README as well

---

*Built as part of Germany Energy Analytics portfolio project*  
*Data: Open Power System Data · SMARD Bundesnetzagentur*
