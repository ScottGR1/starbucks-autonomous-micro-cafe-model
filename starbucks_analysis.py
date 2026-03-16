import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set(style="whitegrid")

# -----------------------------
# DATA (from Starbucks FY2025 10-K)
# -----------------------------

data = {
    "Year": [2023, 2024, 2025],
    "Revenue": [35.98, 36.18, 37.18],  # billions
    "OperatingCashFlow": [6.01, 6.10, 4.75],  # billions
    "CapEx": [2.33, 2.78, 2.31]  # billions
}

df = pd.DataFrame(data)

# -----------------------------
# ASSUMPTIONS / DERIVED MODEL
# -----------------------------

total_stores = 40990
current_revenue = 37.18  # billions
growth_needed = current_revenue * 0.04

# derive avg revenue per store
avg_revenue_per_store = (current_revenue * 1_000_000_000) / total_stores

# assume kiosk does 16.5% of a full store
kiosk_productivity_pct = 0.165
revenue_per_kiosk = avg_revenue_per_store * kiosk_productivity_pct
kiosks_needed = growth_needed * 1_000_000_000 / revenue_per_kiosk

# convert to billions for charting
kiosk_model_revenue = (round(kiosks_needed) * revenue_per_kiosk) / 1_000_000_000

print("Average revenue per store: ${:,.0f}".format(avg_revenue_per_store))
print("Revenue per kiosk: ${:,.0f}".format(revenue_per_kiosk))
print("Kiosks needed: {:,.0f}".format(kiosks_needed))
print("Growth needed: ${:.2f}B".format(growth_needed))

# -----------------------------
# 1. Revenue Growth Chart
# -----------------------------

plt.figure(figsize=(8,5))
plt.plot(df["Year"], df["Revenue"], marker="o", linewidth=3)
plt.title("Starbucks Revenue Growth")
plt.ylabel("Revenue ($ Billions)")
plt.xlabel("Year")
plt.tight_layout()
plt.savefig("revenue_growth.png", dpi=300)
plt.show()

# -----------------------------
# 2. Capital Allocation Chart
# -----------------------------

latest = df[df["Year"] == 2025]

values = [
    latest["OperatingCashFlow"].values[0],
    latest["CapEx"].values[0],
    latest["OperatingCashFlow"].values[0] - latest["CapEx"].values[0]
]

labels = ["Operating Cash Flow", "CapEx", "Free Cash Flow"]

plt.figure(figsize=(8,5))
sns.barplot(x=labels, y=values)
plt.title("Starbucks Capital Allocation (FY2025)")
plt.ylabel("Billions USD")
plt.tight_layout()
plt.savefig("capital_allocation.png", dpi=300)
plt.show()

# -----------------------------
# 3. Growth Gap vs Kiosk Model
# -----------------------------

labels = ["Revenue Needed (4% Growth)", "Micro-Cafe Model"]
values = [growth_needed, kiosk_model_revenue]

plt.figure(figsize=(8,5))
sns.barplot(x=labels, y=values)
plt.title("Closing the Starbucks Growth Gap")
plt.ylabel("Revenue ($ Billions)")
plt.tight_layout()
plt.savefig("growth_gap_solution.png", dpi=300)
plt.show()

# -----------------------------
# 4. OPTIONAL: Derivation Chart
# -----------------------------

labels = ["Avg Revenue per Store", "Revenue per Kiosk"]
values = [avg_revenue_per_store / 1000, revenue_per_kiosk / 1000]

plt.figure(figsize=(8,5))
sns.barplot(x=labels, y=values)
plt.title("Traditional Store vs Micro-Cafe Revenue")
plt.ylabel("Annual Revenue ($ Thousands)")
plt.tight_layout()
plt.savefig("kiosk_revenue_derivation.png", dpi=300)
plt.show()

print("Charts generated successfully.")