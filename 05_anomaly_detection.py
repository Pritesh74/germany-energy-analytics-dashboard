import os
import numpy as np
import pandas as pd

df = pd.read_csv("data/processed/energy_clean.csv")

mean = df["consumption_mwh"].mean()
std = df["consumption_mwh"].std()

df["z_score"] = (df["consumption_mwh"] - mean) / std
df["anomaly"] = np.where(np.abs(df["z_score"]) > 1.8, 1, 0)

print("Anomaly counts:")
print(df["anomaly"].value_counts())

os.makedirs("outputs/anomalies", exist_ok=True)
df.to_csv("outputs/anomalies/anomalies.csv", index=False)

print("✅ Anomaly detection complete!")