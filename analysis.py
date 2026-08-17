"""
Road Accident Risk Analysis — India (v2)
Python — reliability check, aggregations, chi-square tests, population normalization.

Requires: pandas, scipy, matplotlib
    pip install pandas scipy matplotlib
"""

import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import chi2_contingency

# ------------------------------------------------------------
# 0. LOAD DATA
# ------------------------------------------------------------
df = pd.read_csv("accident_prediction_india.csv")
df["Hour"] = df["Time of Day"].apply(lambda t: int(str(t).split(":")[0]))

# State population (2025 estimates — Govt. of India Technical Group
# Population Projection Report 2011-2036, via StatisticsTimes.com)
state_population = {
    "Jammu and Kashmir": 13831000, "Uttar Pradesh": 241265000, "Chhattisgarh": 30982000,
    "Sikkim": 703000, "Meghalaya": 3417000, "Himachal Pradesh": 7555000, "Rajasthan": 83060000,
    "Assam": 36493000, "Bihar": 131041000, "Telangana": 38499000, "Arunachal Pradesh": 1594000,
    "Andhra Pradesh": 53586000, "Karnataka": 68679000, "Madhya Pradesh": 88985000, "Puducherry": 1732000,
    "Maharashtra": 128659000, "Tamil Nadu": 77394000, "Chandigarh": 1259000, "Gujarat": 73513000,
    "Odisha": 46953000, "West Bengal": 100202000, "Kerala": 36111000, "Nagaland": 2279000,
    "Tripura": 4232000, "Uttarakhand": 11913000, "Haryana": 31057000, "Goa": 1593000,
    "Mizoram": 1264000, "Delhi": 22277000, "Jharkhand": 40626000, "Punjab": 31188000, "Manipur": 3289000,
}

fatal = df[df["Accident Severity"] == "Fatal"]


# ------------------------------------------------------------
# 1. DATASET RELIABILITY CHECK
# If every categorical column has near-equal category counts,
# the dataset is likely randomly generated rather than real.
# ------------------------------------------------------------
def uniformity_check(df, columns):
    print("=== Dataset Reliability Check ===")
    for col in columns:
        vc = df[col].value_counts()
        ratio = round(vc.max() / vc.min(), 2)
        print(f"{col:25s} min={vc.min():4d}  max={vc.max():4d}  ratio={ratio}")
    print()


categorical_cols = [
    "Weather Conditions", "Road Type", "Day of Week", "Month",
    "Accident Severity", "Road Condition", "Lighting Conditions",
]
uniformity_check(df, categorical_cols)

recs_per_state = df.groupby("State Name").size()
print(f"Records per state -> min={recs_per_state.min()}, max={recs_per_state.max()}")
print("(Real population range is ~7 lakh to ~24 crore — a 340x spread, "
      "not reflected in record counts)\n")


# ------------------------------------------------------------
# 2. CHI-SQUARE TESTS: does each factor relate to severity?
# ------------------------------------------------------------
def run_chi_square(df, factor_col, label):
    table = pd.crosstab(df[factor_col], df["Accident Severity"])
    chi2, p, dof, expected = chi2_contingency(table)
    sig = "SIGNIFICANT" if p < 0.05 else "not significant"
    print(f"{label:20s} X2={chi2:8.3f}  df={dof:3d}  p={p:.4f}  -> {sig}")
    return chi2, p, dof


print("=== Chi-square tests vs Accident Severity ===")
run_chi_square(df, "Hour", "Hour")
run_chi_square(df, "Weather Conditions", "Weather")
run_chi_square(df, "Road Type", "Road Type")
run_chi_square(df, "State Name", "State")
print()


# ------------------------------------------------------------
# 3. FATAL ACCIDENTS BY STATE — RAW vs POPULATION-NORMALIZED
# ------------------------------------------------------------
state_fatal = fatal.groupby("State Name").size().reset_index(name="Fatal_Count")
state_fatal["Population"] = state_fatal["State Name"].map(state_population)
state_fatal["Fatal_per_Crore"] = (
    state_fatal["Fatal_Count"] / (state_fatal["Population"] / 1e7)
).round(2)

print("=== Top 10 states — RAW COUNT ===")
print(state_fatal.sort_values("Fatal_Count", ascending=False)
      [["State Name", "Fatal_Count"]].head(10).to_string(index=False))

print("\n=== Top 10 states — RATE PER CRORE POPULATION ===")
print(state_fatal.sort_values("Fatal_per_Crore", ascending=False)
      [["State Name", "Fatal_Count", "Fatal_per_Crore"]].head(10).to_string(index=False))
print()


# ------------------------------------------------------------
# 4. OTHER AGGREGATIONS (hour, weather, road type, vehicle type)
# ------------------------------------------------------------
hour_fatal = fatal.groupby("Hour").size().sort_values(ascending=False)
weather_fatal = fatal.groupby("Weather Conditions").size().sort_values(ascending=False)
road_fatal = fatal.groupby("Road Type").size().sort_values(ascending=False)
# NOTE: "Vehicle Type Involved" does not separate cause vs. victim vehicle —
# treat as co-occurrence, not a causal safety ranking.
vehicle_fatal = fatal.groupby("Vehicle Type Involved").size().sort_values(ascending=False)

print("Fatal accidents by hour (top 5):\n", hour_fatal.head(5), "\n")
print("Fatal accidents by weather:\n", weather_fatal, "\n")
print("Fatal accidents by road type:\n", road_fatal, "\n")
print("Fatal accidents by vehicle type involved (cause/victim not distinguished):\n",
      vehicle_fatal, "\n")


# ------------------------------------------------------------
# 5. CHART — Fatal accidents by hour
# ------------------------------------------------------------
plt.figure(figsize=(10, 5))
df[df["Accident Severity"] == "Fatal"]["Hour"].value_counts().sort_index().plot(
    kind="bar", color="crimson"
)
plt.title("Fatal Accidents by Hour of Day")
plt.xlabel("Hour of Day (24-hour format)")
plt.ylabel("Fatal Accidents")
plt.tight_layout()
plt.savefig("fatal_by_hour.png", dpi=150)
print("Saved chart: fatal_by_hour.png")
