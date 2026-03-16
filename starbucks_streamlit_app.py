import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Starbucks Micro-Cafe Growth Model",
    page_icon="☕",
    layout="wide"
)

# -----------------------------
# BASE DATA (from Starbucks FY2025 10-K)
# -----------------------------
revenue_hist = pd.DataFrame({
    "Year": [2023, 2024, 2025],
    "Revenue": [35.98, 36.18, 37.18],          # billions
    "OperatingCashFlow": [6.01, 6.10, 4.75],   # billions
    "CapEx": [2.33, 2.78, 2.31]                # billions
})

# -----------------------------
# FIXED ASSUMPTIONS FOR PRESENTATION
# -----------------------------
current_revenue = 37.18           # FY2025 revenue, billions
total_locations = 40990           # 21,514 company-operated + 19,476 licensed
growth_gap_pct = 0.04             # 4% growth requirement
kiosk_productivity_pct = 0.165    # 16.5% of average location revenue

# -----------------------------
# DERIVED MODEL
# -----------------------------
avg_revenue_per_location = (current_revenue * 1_000_000_000) / total_locations
revenue_per_kiosk = avg_revenue_per_location * kiosk_productivity_pct
growth_needed = current_revenue * growth_gap_pct
kiosks_needed = (growth_needed * 1_000_000_000) / revenue_per_kiosk
modeled_kiosk_revenue = (round(kiosks_needed) * revenue_per_kiosk) / 1_000_000_000
free_cash_flow_2025 = 4.75 - 2.31

# -----------------------------
# TITLE
# -----------------------------
st.title("Starbucks Autonomous Micro-Cafe Model")
st.caption(
    "Source: Starbucks FY2025 Form 10-K. "
    "Store counts include both company-operated and licensed locations."
)

# -----------------------------
# KPI ROW
# -----------------------------
col1, col2, col3, col4 = st.columns(4)
col1.metric("Avg Revenue per Location (10-K)", f"${avg_revenue_per_location:,.0f}")
col2.metric("Revenue per Micro-Cafe", f"${revenue_per_kiosk:,.0f}")
col3.metric("Growth Needed", f"${growth_needed:,.2f}B")
col4.metric("Micro-Cafes Needed", f"{kiosks_needed:,.0f}")

# -----------------------------
# MODEL LOGIC
# -----------------------------
with st.expander("Model logic", expanded=True):
    st.markdown(
        f"""
- **Average location revenue** = FY2025 revenue / total locations  
  = **${current_revenue:.2f}B / {total_locations:,.0f} = ${avg_revenue_per_location:,.0f}**

- **Micro-cafe revenue assumption** = average location revenue × micro-cafe productivity  
  = **${avg_revenue_per_location:,.0f} × {kiosk_productivity_pct:.1%} = ${revenue_per_kiosk:,.0f}**

- **Growth gap required** = FY2025 revenue × growth target  
  = **${current_revenue:.2f}B × {growth_gap_pct:.1%} = ${growth_needed:.2f}B**

- **Micro-cafes needed** = growth gap / micro-cafe revenue  
  = **{kiosks_needed:,.0f}**

**10-K anchors used**
- FY2025 revenue: **$37.18B**
- Company-operated stores: **21,514**
- Licensed stores: **19,476**
- Total locations: **40,990**
        """
    )

st.success(
    "Key takeaway: Roughly 10,000 autonomous micro-cafes generating about $150K annually "
    "could close Starbucks' 4% revenue growth gap."
)

# -----------------------------
# CHART ROW 1
# -----------------------------
left, right = st.columns(2)

with left:
    growth_df = pd.DataFrame({
        "Scenario": ["Revenue Needed for 4% Growth", "Revenue from 10k Micro-Cafes"],
        "Revenue": [growth_needed, modeled_kiosk_revenue]
    })

    fig_growth = px.bar(
        growth_df,
        x="Scenario",
        y="Revenue",
        text="Revenue",
        title="Closing the Starbucks Growth Gap",
        labels={"Revenue": "Revenue ($ Billions)", "Scenario": ""}
    )
    fig_growth.update_traces(texttemplate="%{text:.2f}B", textposition="outside")
    fig_growth.update_layout(template="simple_white", height=450)
    st.plotly_chart(fig_growth, width="stretch")

with right:
    compare_df = pd.DataFrame({
        "Format": ["Traditional Location", "Micro-Cafe"],
        "Revenue": [avg_revenue_per_location / 1000, revenue_per_kiosk / 1000]
    })

    fig_compare = px.bar(
        compare_df,
        x="Format",
        y="Revenue",
        text="Revenue",
        title="Traditional Location vs Micro-Cafe Revenue",
        labels={"Revenue": "Annual Revenue ($ Thousands)", "Format": ""}
    )
    fig_compare.update_traces(texttemplate="$%{text:,.0f}K", textposition="outside")
    fig_compare.update_layout(template="simple_white", height=450)
    st.plotly_chart(fig_compare, width="stretch")

# -----------------------------
# CHART ROW 2
# -----------------------------
left2, right2 = st.columns(2)

with left2:
    fig_rev = px.line(
        revenue_hist,
        x="Year",
        y="Revenue",
        markers=True,
        title="Starbucks Revenue Trend",
        labels={"Revenue": "Revenue ($ Billions)", "Year": "Fiscal Year"}
    )
    fig_rev.update_traces(line=dict(width=4), marker=dict(size=10))
    fig_rev.update_layout(template="simple_white", height=450)
    st.plotly_chart(fig_rev, width="stretch")

with right2:
    capital_df = pd.DataFrame({
        "Metric": ["Operating Cash Flow", "CapEx", "Free Cash Flow"],
        "Value": [4.75, 2.31, free_cash_flow_2025]
    })

    fig_capital = px.bar(
        capital_df,
        x="Metric",
        y="Value",
        text="Value",
        title="Capital Allocation (FY2025)",
        labels={"Value": "Billions USD", "Metric": ""}
    )
    fig_capital.update_traces(texttemplate="%{text:.2f}", textposition="outside")
    fig_capital.update_layout(template="simple_white", height=450)
    st.plotly_chart(fig_capital, width="stretch")

# -----------------------------
# SUMMARY TABLE
# -----------------------------
st.subheader("Summary Table")

summary_table = pd.DataFrame({
    "Metric": [
        "FY2025 Revenue ($B)",
        "Company-Operated Stores",
        "Licensed Stores",
        "Total Locations",
        "Avg Revenue per Location ($)",
        "Micro-Cafe Productivity (%)",
        "Revenue per Micro-Cafe ($)",
        "Growth Gap ($B)",
        "Micro-Cafes Needed"
    ],
    "Value": [
        round(current_revenue, 2),
        "21,514",
        "19,476",
        f"{total_locations:,.0f}",
        f"{avg_revenue_per_location:,.0f}",
        f"{kiosk_productivity_pct:.1%}",
        f"{revenue_per_kiosk:,.0f}",
        round(growth_needed, 2),
        f"{kiosks_needed:,.0f}"
    ]
})

st.dataframe(summary_table, width="stretch", hide_index=True)