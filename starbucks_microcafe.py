import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

st.set_page_config(
    page_title="Starbucks AI Micro-Café Model",
    page_icon="☕",
    layout="wide"
)

# ─────────────────────────────────────────────
# ACTUAL DATA FROM FY2025 10-K
# ─────────────────────────────────────────────
fy25_revenue_m      = 37184.4
total_locations     = 40990
avg_rev_per_loc_m   = fy25_revenue_m / total_locations  # $M per location
fcf_2025            = 2440.0

revenue_hist = pd.DataFrame({
    "Year":            [2023,    2024,    2025],
    "Revenue":         [35975.6, 36176.2, 37184.4],
    "CompanyStores":   [29462.3, 29765.9, 30744.8],
    "LicensedStores":  [4512.7,  4505.1,  4350.4],
    "Other":           [2000.6,  1905.2,  2089.2],
    "OperatingIncome": [5870.8,  5408.8,  2936.6],
    "StoreOpEx":       [14720.3, 15286.5, 17058.9],  # from TABLE9
})

# Traditional store benchmarks from 10-K
trad_store_rev_k        = avg_rev_per_loc_m * 1e6 / 1e3   # ~$906K
trad_store_opex_pct     = 0.555   # 55.5% store OpEx as % of related revenues (TABLE9)
trad_labor_cost_k       = 400.0   # estimated annual labor per traditional store ($K)
trad_capex_k            = 750.0   # mid-range new store CapEx ($K)

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
st.sidebar.header("⚙️ Micro-Café Assumptions")
st.sidebar.markdown("**Growth Gap**")
growth_gap_pct = st.sidebar.slider("Revenue Growth Target (%)", 1.0, 10.0, 4.0, 0.5) / 100
kiosk_productivity_pct = st.sidebar.slider("Micro-Café Revenue (% of avg location)", 5.0, 40.0, 16.5, 0.5) / 100

st.sidebar.markdown("---")
st.sidebar.markdown("**AI / Automation Levers**")
ai_opex_pct       = st.sidebar.slider("AI Kiosk OpEx margin (%)", 25, 70, 45, 5) / 100
labor_savings_pct = st.sidebar.slider("Labor cost reduction vs traditional (%)", 50, 99, 95, 1) / 100
uptime_mult       = st.sidebar.slider("24/7 revenue uplift multiplier", 1.0, 1.5, 1.2, 0.05)
ai_capex_k        = st.sidebar.slider("CapEx per AI kiosk ($K)", 50, 400, 150, 10)
ramp_years        = st.sidebar.slider("Deployment period (years)", 1, 5, 3, 1)

st.sidebar.markdown("---")
st.sidebar.caption("Source: Starbucks FY2025 10-K  \nFiled Nov 14, 2025")

# ─────────────────────────────────────────────
# DERIVED MODEL
# ─────────────────────────────────────────────
# Base micro-café revenue (before AI uplift)
base_rev_per_kiosk_m    = avg_rev_per_loc_m * kiosk_productivity_pct
# AI 24/7 uplift
ai_rev_per_kiosk_m      = base_rev_per_kiosk_m * uptime_mult
ai_rev_per_kiosk_k      = ai_rev_per_kiosk_m * 1e6 / 1e3

# Growth gap
growth_needed_m         = fy25_revenue_m * growth_gap_pct
kiosks_needed           = int(round(growth_needed_m / ai_rev_per_kiosk_m))
total_kiosk_rev_m       = kiosks_needed * ai_rev_per_kiosk_m

# Traditional store comparisons
trad_opex_k             = trad_store_rev_k * trad_store_opex_pct
trad_ebitda_k           = trad_store_rev_k - trad_opex_k
trad_payback_yrs        = trad_capex_k / trad_ebitda_k if trad_ebitda_k > 0 else 99

# AI kiosk unit economics
ai_opex_k               = ai_rev_per_kiosk_k * ai_opex_pct
ai_labor_k              = trad_labor_cost_k * (1 - labor_savings_pct)
ai_ebitda_k             = ai_rev_per_kiosk_k - ai_opex_k
ai_payback_yrs          = ai_capex_k / ai_ebitda_k if ai_ebitda_k > 0 else 99

# Program-level
total_capex_m           = kiosks_needed * ai_capex_k * 1e3 / 1e6
pct_of_fcf              = total_capex_m / fcf_2025 * 100

# Margin impact on Starbucks overall
ai_total_ebitda_m       = kiosks_needed * ai_ebitda_k / 1e3
combined_rev_m          = fy25_revenue_m + total_kiosk_rev_m
combined_opincome_m     = 2936.6 + ai_total_ebitda_m
combined_margin         = combined_opincome_m / combined_rev_m
current_margin          = 2936.6 / fy25_revenue_m

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.title("☕ Starbucks AI Micro-Café: Growth Gap & Automation Economics")
st.caption("All base financials from Starbucks FY2025 Form 10-K (period end Sep 28, 2025). Dollar figures in millions unless noted.")

# ─────────────────────────────────────────────
# TOP KPIs
# ─────────────────────────────────────────────
k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("FY2025 Revenue",          f"${fy25_revenue_m/1000:.2f}B")
k2.metric("Growth Gap",              f"${growth_needed_m/1000:.2f}B", delta=f"{growth_gap_pct:.0%} target")
k3.metric("AI Kiosks Needed",        f"{kiosks_needed:,}")
k4.metric("Revenue per AI Kiosk",    f"${ai_rev_per_kiosk_k:,.0f}K", delta=f"{uptime_mult:.1f}x 24/7 uplift")
k5.metric("AI Kiosk OpEx Margin",    f"{ai_opex_pct:.0%}", delta=f"vs {trad_store_opex_pct:.0%} traditional", delta_color="inverse")
k6.metric("AI Payback Period",       f"{ai_payback_yrs:.1f} yrs", delta=f"vs {trad_payback_yrs:.1f} traditional", delta_color="inverse")

st.divider()

# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📐 Growth Gap & AI Case",
    "🤖 AI vs Traditional Store",
    "💰 Unit Economics",
    "📊 Sensitivity Analysis",
    "🗓️ Deployment Timeline",
])

# ══════════════════════════════════════════════
# TAB 1 — GROWTH GAP & AI CASE
# ══════════════════════════════════════════════
with tab1:
    st.subheader("The Problem: Starbucks Needs New Revenue")

    col1, col2 = st.columns([1.1, 1])

    with col1:
        # Revenue + growth gap bar
        fig_gap = go.Figure()
        fig_gap.add_trace(go.Bar(
            name="FY2025 Revenue", x=["FY2025"], y=[fy25_revenue_m/1000],
            marker_color="#1E3932", text=[f"${fy25_revenue_m/1000:.1f}B"], textposition="inside",
        ))
        fig_gap.add_trace(go.Bar(
            name=f"Growth Gap ({growth_gap_pct:.0%})", x=["FY2025"], y=[growth_needed_m/1000],
            marker_color="#CBA258", text=[f"+${growth_needed_m/1000:.2f}B needed"], textposition="outside",
        ))
        fig_gap.add_trace(go.Bar(
            name="AI Micro-Café Revenue", x=["With AI Kiosks"], y=[total_kiosk_rev_m/1000],
            marker_color="#00704A", text=[f"${total_kiosk_rev_m/1000:.2f}B"], textposition="outside",
        ))
        fig_gap.update_layout(
            barmode="stack", title="Revenue Gap vs AI Kiosk Solution ($B)",
            template="simple_white", height=400,
            yaxis_title="Revenue ($B)", showlegend=True,
            legend=dict(orientation="h", y=-0.2)
        )
        st.plotly_chart(fig_gap, use_container_width=True)

    with col2:
        st.markdown("### Why AI Kiosks Close the Gap")
        st.markdown(f"""
| Factor | Value |
|---|---|
| FY2025 Revenue | **${fy25_revenue_m/1000:.2f}B** |
| Growth target | **{growth_gap_pct:.0%}** |
| New revenue needed | **${growth_needed_m/1000:.2f}B** |
| Base kiosk revenue | ${base_rev_per_kiosk_m*1e6/1e3:,.0f}K |
| **+ 24/7 AI uplift ({uptime_mult:.1f}×)** | **${ai_rev_per_kiosk_k:,.0f}K** |
| Kiosks needed | **{kiosks_needed:,}** |
| Total kiosk revenue | **${total_kiosk_rev_m/1000:.2f}B** |
""")
        surplus = total_kiosk_rev_m - growth_needed_m
        if surplus >= 0:
            st.success(f"✅ AI kiosks generate **${total_kiosk_rev_m/1000:.2f}B** — exceeds the gap by **${surplus/1000:.2f}B**")
        else:
            st.warning(f"⚠️ AI kiosks generate **${total_kiosk_rev_m/1000:.2f}B** — still **${abs(surplus)/1000:.2f}B** short of the gap")

    st.divider()
    st.subheader("Why AI — Not Just More Stores")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("#### 🏪 Traditional Store")
        st.markdown(f"""
- Revenue: **${trad_store_rev_k:,.0f}K/yr**
- OpEx margin: **{trad_store_opex_pct:.0%}**
- Labor cost: **${trad_labor_cost_k:,.0f}K/yr**
- CapEx to build: **${trad_capex_k:,.0f}K**
- Operating hours: **~17 hrs/day**
- Payback: **{trad_payback_yrs:.1f} years**
""")
    with c2:
        st.markdown("#### 🤖 AI Micro-Café")
        st.markdown(f"""
- Revenue: **${ai_rev_per_kiosk_k:,.0f}K/yr** ({uptime_mult:.1f}× uplift)
- OpEx margin: **{ai_opex_pct:.0%}**
- Labor cost: **${ai_labor_k:,.0f}K/yr** (remote tech only)
- CapEx to build: **${ai_capex_k:,}K**
- Operating hours: **24/7 = 24 hrs/day**
- Payback: **{ai_payback_yrs:.1f} years**
""")
    with c3:
        st.markdown("#### 📈 AI Advantage")
        capex_saving_pct = (1 - ai_capex_k / trad_capex_k) * 100
        labor_saving_k = trad_labor_cost_k - ai_labor_k
        opex_saving_pp = (trad_store_opex_pct - ai_opex_pct) * 100
        pb_improvement = trad_payback_yrs - ai_payback_yrs
        st.markdown(f"""
- Revenue uplift: **+{(uptime_mult-1)*100:.0f}%** from 24/7 ops
- OpEx saving: **{opex_saving_pp:+.0f} percentage points**
- Labor saving: **${labor_saving_k:,.0f}K/yr per unit**
- CapEx saving: **{capex_saving_pct:.0f}% less** to deploy
- Payback faster: **{pb_improvement:.1f} years** sooner
- Scale: **{kiosks_needed:,} units** fundable from FCF
""")

    st.divider()
    st.subheader("Overall Margin Impact on Starbucks")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Current Op. Income",  f"${2936.6:,.0f}M",  delta=f"{current_margin:.1%} margin")
    m2.metric("AI Kiosk EBITDA",     f"${ai_total_ebitda_m:,.0f}M", delta=f"from {kiosks_needed:,} kiosks")
    m3.metric("Combined Op. Income", f"${combined_opincome_m:,.0f}M")
    m4.metric("New Margin",          f"{combined_margin:.1%}", delta=f"{(combined_margin-current_margin)*100:+.1f}pp vs today", delta_color="normal")

    fig_margin = go.Figure()
    fig_margin.add_trace(go.Bar(
        x=["Current Starbucks", "With AI Kiosks"],
        y=[current_margin*100, combined_margin*100],
        marker_color=["#1E3932", "#00704A"],
        text=[f"{current_margin:.1%}", f"{combined_margin:.1%}"],
        textposition="outside",
    ))
    fig_margin.update_layout(
        title="Operating Margin: Before vs After AI Micro-Cafés",
        yaxis_title="Operating Margin (%)",
        template="simple_white", height=350, showlegend=False,
    )
    st.plotly_chart(fig_margin, use_container_width=True)

# ══════════════════════════════════════════════
# TAB 2 — AI VS TRADITIONAL
# ══════════════════════════════════════════════
with tab2:
    st.subheader("🤖 AI Kiosk vs Traditional Store — Head to Head")

    metrics_df = pd.DataFrame({
        "Metric":            ["Annual Revenue ($K)", "OpEx ($K)", "Labor Cost ($K)", "EBITDA ($K)", "CapEx ($K)", "Payback (yrs)"],
        "Traditional Store": [trad_store_rev_k, trad_opex_k, trad_labor_cost_k, trad_ebitda_k, trad_capex_k, round(trad_payback_yrs, 1)],
        "AI Micro-Café":     [ai_rev_per_kiosk_k, ai_opex_k, ai_labor_k, ai_ebitda_k, ai_capex_k, round(ai_payback_yrs, 1)],
    })
    metrics_df["AI Advantage"] = metrics_df.apply(
        lambda r: f"{((r['AI Micro-Café']/r['Traditional Store'])-1)*100:+.0f}%" if r["Traditional Store"] != 0 else "—", axis=1
    )
    st.dataframe(metrics_df.style.format({"Traditional Store": "{:,.1f}", "AI Micro-Café": "{:,.1f}"}),
                 use_container_width=True, hide_index=True)

    c1, c2 = st.columns(2)
    with c1:
        # Revenue + EBITDA comparison
        comp_fig = go.Figure()
        cats = ["Revenue", "OpEx", "EBITDA"]
        trad_vals = [trad_store_rev_k, trad_opex_k, trad_ebitda_k]
        ai_vals   = [ai_rev_per_kiosk_k, ai_opex_k, ai_ebitda_k]
        comp_fig.add_trace(go.Bar(name="Traditional Store", x=cats, y=trad_vals, marker_color="#6B6B6B"))
        comp_fig.add_trace(go.Bar(name="AI Micro-Café",     x=cats, y=ai_vals,   marker_color="#00704A"))
        comp_fig.update_layout(barmode="group", title="Unit P&L Comparison ($K)",
                               template="simple_white", height=400, yaxis_title="$K")
        st.plotly_chart(comp_fig, use_container_width=True)

    with c2:
        # OpEx breakdown — where AI saves
        opex_breakdown = pd.DataFrame({
            "Cost Line":       ["Labor", "Rent/Lease", "Other OpEx"],
            "Traditional ($K)": [trad_labor_cost_k, 220, trad_opex_k - trad_labor_cost_k - 220],
            "AI Kiosk ($K)":   [ai_labor_k, 40, ai_opex_k - ai_labor_k - 40],
        })
        fig_opex = go.Figure()
        for col, color in [("Traditional ($K)", "#6B6B6B"), ("AI Kiosk ($K)", "#00704A")]:
            fig_opex.add_trace(go.Bar(name=col, x=opex_breakdown["Cost Line"],
                                      y=opex_breakdown[col], marker_color=color))
        fig_opex.update_layout(barmode="group", title="Operating Cost Breakdown ($K)",
                               template="simple_white", height=400, yaxis_title="$K")
        st.plotly_chart(fig_opex, use_container_width=True)

    # 24/7 revenue visualization
    st.subheader("The 24/7 AI Revenue Uplift")
    hours_traditional = 17
    hours_ai = 24
    hourly_rev_k = (trad_store_rev_k / 365 / hours_traditional)

    hours = list(range(25))
    traditional_curve = [min(h, hours_traditional) * hourly_rev_k * 365 / 1000 for h in hours]
    ai_curve          = [h * hourly_rev_k * 365 / 1000 * uptime_mult for h in hours]

    fig_24 = go.Figure()
    fig_24.add_trace(go.Scatter(x=hours, y=traditional_curve, name="Traditional Store",
                                 line=dict(color="#6B6B6B", width=3, dash="dash"), mode="lines"))
    fig_24.add_trace(go.Scatter(x=hours, y=ai_curve, name="AI Kiosk (24/7)",
                                 line=dict(color="#00704A", width=3), mode="lines"))
    fig_24.add_vline(x=hours_traditional, line_dash="dot", line_color="#C0392B",
                     annotation_text="Traditional closes", annotation_position="top right")
    fig_24.update_layout(title="Annual Revenue Potential by Operating Hours ($K)",
                          xaxis_title="Daily Operating Hours", yaxis_title="Annual Revenue ($K)",
                          template="simple_white", height=380)
    st.plotly_chart(fig_24, use_container_width=True)

# ══════════════════════════════════════════════
# TAB 3 — UNIT ECONOMICS
# ══════════════════════════════════════════════
with tab3:
    st.subheader("💰 AI Kiosk Unit Economics")
    u1, u2, u3, u4 = st.columns(4)
    u1.metric("Annual Revenue", f"${ai_rev_per_kiosk_k:,.0f}K")
    u2.metric("Annual OpEx",    f"${ai_opex_k:,.0f}K", delta=f"{ai_opex_pct:.0%} margin", delta_color="inverse")
    u3.metric("EBITDA",         f"${ai_ebitda_k:,.0f}K", delta=f"{(1-ai_opex_pct):.0%} EBITDA margin")
    u4.metric("Payback",        f"{ai_payback_yrs:.1f} yrs")

    c1, c2 = st.columns(2)
    with c1:
        fig_wf = go.Figure(go.Waterfall(
            orientation="v",
            measure=["absolute", "relative", "relative", "relative", "total"],
            x=["Revenue", "Rent/Lease", "Labor (AI)", "Other OpEx", "EBITDA"],
            y=[ai_rev_per_kiosk_k, -40, -ai_labor_k, -(ai_opex_k - ai_labor_k - 40), ai_ebitda_k],
            connector={"line": {"color": "#888888"}},
            increasing={"marker": {"color": "#00704A"}},
            decreasing={"marker": {"color": "#C0392B"}},
            totals={"marker": {"color": "#CBA258"}},
            texttemplate="%{y:,.0f}K",
            textposition="outside",
        ))
        fig_wf.update_layout(title="AI Kiosk P&L Waterfall ($K)", template="simple_white", height=420)
        st.plotly_chart(fig_wf, use_container_width=True)

    with c2:
        yrs = np.arange(0, 8.1, 0.25)
        fig_pb = go.Figure()
        fig_pb.add_hline(y=ai_capex_k, line_dash="dash", line_color="#C0392B",
                         annotation_text=f"AI CapEx = ${ai_capex_k}K")
        fig_pb.add_hline(y=trad_capex_k, line_dash="dot", line_color="#888888",
                         annotation_text=f"Traditional CapEx = ${trad_capex_k}K")
        fig_pb.add_trace(go.Scatter(x=yrs, y=yrs * ai_ebitda_k, name="AI Kiosk Cumulative EBITDA",
                                     line=dict(color="#00704A", width=3)))
        fig_pb.add_trace(go.Scatter(x=yrs, y=yrs * trad_ebitda_k, name="Traditional Store Cumulative EBITDA",
                                     line=dict(color="#888888", width=2, dash="dash")))
        fig_pb.update_layout(title="CapEx Payback Comparison", xaxis_title="Years",
                              yaxis_title="Cumulative EBITDA ($K)", template="simple_white", height=420)
        st.plotly_chart(fig_pb, use_container_width=True)

    st.subheader("Program-Level CapEx vs Free Cash Flow")
    p1, p2, p3 = st.columns(3)
    p1.metric("Total Program CapEx", f"${total_capex_m:,.0f}M")
    p2.metric("FY2025 Free Cash Flow", f"${fcf_2025:,.0f}M")
    p3.metric("CapEx as % of FCF", f"{pct_of_fcf:.0f}%",
              delta="Manageable" if pct_of_fcf <= 100 else "Needs phasing", delta_color="normal" if pct_of_fcf <= 100 else "inverse")

    fig_fcf = go.Figure(go.Bar(
        x=["AI Program CapEx", "FY2025 FCF"],
        y=[total_capex_m, fcf_2025],
        marker_color=["#C0392B" if total_capex_m > fcf_2025 else "#00704A", "#00704A"],
        text=[f"${total_capex_m:,.0f}M", f"${fcf_2025:,.0f}M"],
        textposition="outside",
    ))
    fig_fcf.update_layout(title="Total Program CapEx vs Available FCF ($M)",
                          template="simple_white", height=350, yaxis_title="$M", showlegend=False)
    st.plotly_chart(fig_fcf, use_container_width=True)

# ══════════════════════════════════════════════
# TAB 4 — SENSITIVITY
# ══════════════════════════════════════════════
with tab4:
    st.subheader("📊 Sensitivity: AI Kiosks Needed")
    st.caption("Rows = growth target; Columns = kiosk productivity (% of avg location revenue)")

    growth_targets  = [0.02, 0.03, 0.04, 0.05, 0.06, 0.08, 0.10]
    productivities  = [0.08, 0.10, 0.125, 0.165, 0.20, 0.25, 0.30]

    mat_k  = pd.DataFrame(index=[f"{g:.0%}" for g in growth_targets], columns=[f"{p:.1%}" for p in productivities])
    mat_pb = pd.DataFrame(index=[f"{g:.0%}" for g in growth_targets], columns=[f"{p:.1%}" for p in productivities])

    for g in growth_targets:
        for p in productivities:
            rk = avg_rev_per_loc_m * p * uptime_mult
            n  = int(round(fy25_revenue_m * g / rk)) if rk > 0 else 0
            mat_k.loc[f"{g:.0%}", f"{p:.1%}"] = n
            rev_k  = rk * 1e6 / 1e3
            ebitda = rev_k * (1 - ai_opex_pct)
            pb = round(ai_capex_k / ebitda, 1) if ebitda > 0 else 99
            mat_pb.loc[f"{g:.0%}", f"{p:.1%}"] = pb

    st.markdown("**Kiosks needed (with AI 24/7 uplift applied)**")
    st.dataframe(mat_k.astype(int).style.background_gradient(cmap="RdYlGn_r", axis=None), use_container_width=True)

    st.markdown("**Payback period (years) per AI kiosk**")
    st.dataframe(mat_pb.astype(float).style.background_gradient(cmap="RdYlGn_r", axis=None), use_container_width=True)

    z = mat_k.astype(int).values.tolist()
    fig_heat = go.Figure(go.Heatmap(
        z=z, x=[f"{p:.1%}" for p in productivities], y=[f"{g:.0%}" for g in growth_targets],
        colorscale="RdYlGn_r", text=[[f"{v:,}" for v in row] for row in z],
        texttemplate="%{text}", colorbar=dict(title="# Kiosks"),
    ))
    fig_heat.update_layout(title="AI Kiosks Needed (24/7 uplift baked in)",
                           xaxis_title="Kiosk Productivity", yaxis_title="Growth Target",
                           template="simple_white", height=420)
    st.plotly_chart(fig_heat, use_container_width=True)

    # OpEx sensitivity — how much does margin assumption matter?
    st.subheader("OpEx Margin vs EBITDA per Kiosk ($K)")
    opex_range = np.arange(0.30, 0.76, 0.05)
    ebitda_range = [ai_rev_per_kiosk_k * (1 - o) for o in opex_range]
    fig_opex_sens = go.Figure(go.Scatter(
        x=[f"{o:.0%}" for o in opex_range], y=ebitda_range,
        mode="lines+markers", line=dict(color="#00704A", width=3),
        text=[f"${e:,.0f}K" for e in ebitda_range], textposition="top center",
    ))
    # add_vline doesn't work on categorical axes — use a scatter trace instead
    current_opex_label = f"{ai_opex_pct:.0%}"
    if current_opex_label in [f"{o:.0%}" for o in opex_range]:
        fig_opex_sens.add_trace(go.Scatter(
            x=[current_opex_label, current_opex_label],
            y=[0, max(ebitda_range)],
            mode="lines",
            line=dict(color="#CBA258", dash="dash", width=2),
            name="Current assumption",
            showlegend=True,
        ))
    fig_opex_sens.update_layout(title="EBITDA per Kiosk at Different OpEx Margins",
                                xaxis_title="OpEx Margin (%)", yaxis_title="EBITDA ($K)",
                                template="simple_white", height=360)
    st.plotly_chart(fig_opex_sens, use_container_width=True)

# ══════════════════════════════════════════════
# TAB 5 — DEPLOYMENT TIMELINE
# ══════════════════════════════════════════════
with tab5:
    st.subheader(f"🗓️ {ramp_years}-Year AI Kiosk Deployment Ramp")

    def make_ramp(weights_fn):
        w = np.array(weights_fn(ramp_years), dtype=float)
        w /= w.sum()
        vals = [int(round(x * kiosks_needed)) for x in w]
        vals[-1] += kiosks_needed - sum(vals)
        return vals

    profiles = {
        "Linear":       make_ramp(lambda n: [1]*n),
        "Front-Loaded": make_ramp(lambda n: [max(1, n-i) for i in range(n)]),
        "Back-Loaded":  make_ramp(lambda n: [i+1 for i in range(n)]),
    }
    yrs_labels = [f"Year {i+1}" for i in range(ramp_years)]

    rows = []
    for profile, vals in profiles.items():
        cum = np.cumsum(vals)
        for i, yr in enumerate(yrs_labels):
            cum_ebitda = cum[i] * ai_ebitda_k / 1e3
            rows.append({
                "Year": yr, "Profile": profile,
                "New Kiosks": vals[i],
                "Cumulative Kiosks": int(cum[i]),
                "Cumulative Revenue ($M)": round(cum[i] * ai_rev_per_kiosk_k / 1e3, 1),
                "Cumulative EBITDA ($M)":  round(cum_ebitda, 1),
                "Annual CapEx ($M)":       round(vals[i] * ai_capex_k / 1e3, 1),
            })
    ramp_df = pd.DataFrame(rows)

    choice = st.radio("Ramp profile:", list(profiles.keys()), horizontal=True)
    sel = ramp_df[ramp_df["Profile"] == choice].reset_index(drop=True)

    c1, c2 = st.columns(2)
    with c1:
        fig_r = go.Figure()
        fig_r.add_trace(go.Bar(x=sel["Year"], y=sel["New Kiosks"], name="New / Year", marker_color="#CBA258"))
        fig_r.add_trace(go.Scatter(x=sel["Year"], y=sel["Cumulative Kiosks"],
                                    name="Cumulative", yaxis="y2",
                                    mode="lines+markers", line=dict(color="#00704A", width=3)))
        fig_r.update_layout(title=f"{choice} Deployment", yaxis=dict(title="New Kiosks"),
                            yaxis2=dict(title="Cumulative", overlaying="y", side="right"),
                            template="simple_white", height=400, legend=dict(orientation="h"))
        st.plotly_chart(fig_r, use_container_width=True)

    with c2:
        fig_e = go.Figure()
        fig_e.add_trace(go.Bar(x=sel["Year"], y=sel["Annual CapEx ($M)"],
                                name="Annual CapEx Spend", marker_color="#C0392B"))
        fig_e.add_trace(go.Scatter(x=sel["Year"], y=sel["Cumulative EBITDA ($M)"],
                                    name="Cumulative EBITDA", yaxis="y2",
                                    mode="lines+markers", line=dict(color="#00704A", width=3)))
        fig_e.update_layout(title="CapEx Spend vs Cumulative EBITDA ($M)",
                            yaxis=dict(title="Annual CapEx ($M)"),
                            yaxis2=dict(title="Cumulative EBITDA ($M)", overlaying="y", side="right"),
                            template="simple_white", height=400, legend=dict(orientation="h"))
        st.plotly_chart(fig_e, use_container_width=True)

    st.dataframe(
        sel[["Year", "New Kiosks", "Cumulative Kiosks", "Cumulative Revenue ($M)", "Cumulative EBITDA ($M)", "Annual CapEx ($M)"]],
        use_container_width=True, hide_index=True
    )

    # Break-even year highlight
    st.subheader("When Does the Program Pay Back?")
    for profile in profiles:
        s = ramp_df[ramp_df["Profile"] == profile]
        cum_capex = s["Annual CapEx ($M)"].cumsum().values
        cum_ebitda = s["Cumulative EBITDA ($M)"].values
        payback_yr = next((s["Year"].iloc[i] for i, (c, e) in enumerate(zip(cum_capex, cum_ebitda)) if e >= c), "Beyond ramp")
        st.write(f"**{profile}**: program break-even at **{payback_yr}**")