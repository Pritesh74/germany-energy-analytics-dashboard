import pandas as pd
from prophet import Prophet
import os

# Load cleaned data
df = pd.read_csv("data/processed/energy_clean.csv")

# Prepare for Prophet
df = df[['date', 'consumption_mwh']].copy()
df.columns = ['ds', 'y']
df['ds'] = pd.to_datetime(df['ds'])

# Initialize model
model = Prophet(
    daily_seasonality=False,
    weekly_seasonality=True,
    yearly_seasonality=True
)
model.fit(df)

# Future predictions
future = model.make_future_dataframe(periods=365)
forecast = model.predict(future)
forecast["yhat_smooth"] = forecast["yhat"].rolling(7).mean()

# Save forecast
os.makedirs("outputs/forecast", exist_ok=True)
forecast.to_csv("outputs/forecast/forecast.csv", index=False)

print("✅ Forecast generated and saved!")