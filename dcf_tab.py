import streamlit as st
import pandas as pd
from calculations import calculate_dcf, dcf_fair_value

def render_dcf_tab():
    st.header("💰 DCF Valuation")
    if not st.session_state.get("data_imported"):
        st.info("Please upload data first in the Inputs tab.")
        return

    df = st.session_state["annual_pl"].copy().set_index("Report Date")
    revenue_row = df.loc["Sales"].dropna()
    base_revenue = revenue_row.values[-1]

    st.subheader("📋 Assumptions")
    st.write(f"**Base Revenue:** {base_revenue:,.2f}")
    st.write(f"**EBIT Margin (%):** {st.session_state['ebit_margin']}")
    st.write(f"**Tax Rate (% of EBIT):** {st.session_state['tax_rate']}")
    st.write(f"**Depreciation (% of Revenue):** {st.session_state['depreciation_pct']}")
    st.write(f"**CapEx (% of Revenue):** {st.session_state['capex_pct']}")
    st.write(f"**Change in WC (% of Revenue):** {st.session_state['wc_change_pct']}")
    st.write(f"**WACC (%):** {st.session_state['interest_pct']}")
    st.write(f"**Forecast Years:** {st.session_state['forecast_years']}")
    st.write(f"**Growth Rates:** Y1-2: {st.session_state['user_growth_rate_yr_1_2']}%, Y3-5: {st.session_state['user_growth_rate_yr_3_4_5']}%, Y6+: {st.session_state['user_growth_rate_yr_6_onwards']}%")

    fcf_data = calculate_dcf(
        base_revenue=base_revenue,
        forecast_years=st.session_state["forecast_years"],
        ebit_margin=st.session_state["ebit_margin"],
        depreciation_pct=st.session_state["depreciation_pct"],
        capex_pct=st.session_state["capex_pct"],
        interest_pct=st.session_state["interest_pct"],
        wc_change_pct=st.session_state["wc_change_pct"],
        tax_rate=st.session_state["tax_rate"],
        shares=st.session_state["shares_outstanding"],
        growth_rate_1_2=st.session_state["user_growth_rate_yr_1_2"],
        growth_rate_3_4_5=st.session_state["user_growth_rate_yr_3_4_5"],
        growth_rate_6=st.session_state["user_growth_rate_yr_6_onwards"]
    )

    df_fcf = pd.DataFrame(fcf_data, columns=["Year", "Revenue", "EBIT", "Tax", "Net Operating PAT", "Depreciation", "CapEx", "Change in WC", "Free Cash Flow", "PV of FCF"])
    st.dataframe(df_fcf.style.format({
        "Revenue": "{:.2f}", "EBIT": "{:.2f}", "Tax": "{:.2f}", "Net Operating PAT": "{:.2f}", "Depreciation": "{:.2f}",
        "CapEx": "{:.2f}", "Change in WC": "{:.2f}", "Free Cash Flow": "{:.2f}", "PV of FCF": "{:.2f}"
    }))

    final_fcf = fcf_data[-1][-2]
    terminal_growth = st.session_state["user_growth_rate_yr_6_onwards"]
    interest_pct = st.session_state["interest_pct"]
    forecast_years = min(st.session_state["forecast_years"], 20)
    shares = st.session_state["shares_outstanding"]

    terminal_value = (final_fcf * (1 + terminal_growth / 100)) / ((interest_pct / 100) - (terminal_growth / 100))
    pv_terminal = terminal_value / ((1 + interest_pct / 100) ** forecast_years)
    total_pv_fcf = sum(row[-1] for row in fcf_data[1:])
    enterprise_value = total_pv_fcf + pv_terminal
    equity_value = enterprise_value
    fair_value_per_share = equity_value / shares if shares else 0

    st.metric("Fair Value per Share", f"₹{fair_value_per_share:,.2f}")
