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

    with st.expander("📋 Assumptions", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.number_input("EBIT Margin (%)", key="ebit_margin", value=st.session_state.get("ebit_margin", 0.0), step=0.1)
            st.number_input("Depreciation (% of Revenue)", key="depreciation_pct", value=st.session_state.get("depreciation_pct", 0.0), step=0.1)
            st.number_input("Tax Rate (% of EBIT)", key="tax_rate", value=st.session_state.get("tax_rate", 0.0), step=0.1)
        with col2:
            st.number_input("CapEx (% of Revenue)", key="capex_pct", value=st.session_state.get("capex_pct", 0.0), step=0.1)
            st.number_input("Change in WC (% of Revenue)", key="wc_change_pct", value=st.session_state.get("wc_change_pct", 0.0), step=0.1)
            st.number_input("WACC (%)", key="interest_pct", value=st.session_state.get("interest_pct", 0.0), step=0.1)
        with col3:
            st.number_input("Forecast Years", key="forecast_years", min_value=1, max_value=30, value=st.session_state.get("forecast_years", 20))
            st.number_input("Growth Rate Y1-2 (%)", key="user_growth_rate_yr_1_2", value=st.session_state.get("user_growth_rate_yr_1_2", 0.0), step=0.1)
            st.number_input("Growth Rate Y3-5 (%)", key="user_growth_rate_yr_3_4_5", value=st.session_state.get("user_growth_rate_yr_3_4_5", 0.0), step=0.1)
            st.number_input("Growth Rate Y6+ (%)", key="user_growth_rate_yr_6_onwards", value=st.session_state.get("user_growth_rate_yr_6_onwards", 0.0), step=0.1)

    if st.button("🔄 Recalculate DCF"):
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
