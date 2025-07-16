import streamlit as st
import pandas as pd
from calculations import calculate_dcf, dcf_fair_value
from assumption_builder import build_assumptions_from_data

if "initial_assumptions" not in st.session_state:
    st.error("Initial assumptions not found. Please upload data again from the Inputs tab.")
    return
defaults = st.session_state["initial_assumptions"]

def render_dcf_tab():
    st.header("💰 DCF Valuation")
    if not st.session_state.get("data_imported"):
        st.info("Please upload data first in the Inputs tab.")
        return

    df = st.session_state["annual_pl"].copy().set_index("Report Date")
    revenue_row = df.loc["Sales"].dropna()
    base_revenue = revenue_row.values[-1]

    with st.expander("📋 Assumptions", expanded=True):
        
        l_ebit_margin = defaults.get("ebit_margin", 20.0)
        l_depreciation_pct = defaults.get("depreciation_pct", 5.0)
        l_tax_rate = defaults.get("tax_rate", 25.0)
        l_capex_pct = defaults.get("capex_pct", 2.0)
        l_wc_change_pct = defaults.get("wc_change_pct", 2.0)
        l_interest_pct = defaults.get("interest_pct", 10.0)
        l_forecast_years = defaults.get("forecast_years", 20)
        l_growth_1_2 = defaults.get("user_growth_rate_yr_1_2", 10.0)
        l_growth_3_5 = defaults.get("user_growth_rate_yr_3_4_5", 10.0)
        l_growth_6 = defaults.get("user_growth_rate_yr_6_onwards", 4.0)
        if st.button("🔁 Reset to Default"):
            ebit_margin = l_ebit_margin
            depreciation_pct = l_depreciation_pct
            tax_rate = l_tax_rate
            capex_pct = l_capex_pct
            wc_change_pct = l_wc_change_pct
            interest_pct = l_interest_pct
            forecast_years = l_forecast_years
            growth_1_2 = l_growth_1_2
            growth_3_5 = l_growth_3_5
            growth_6 = l_growth_6

        col1, col2, col3 = st.columns(3)
        with col1:
            ebit_margin = st.number_input("EBIT Margin (%)", value=l_ebit_margin, step=0.1)
            depreciation_pct = st.number_input("Depreciation (% of Revenue)", value=l_depreciation_pct, step=0.1)
            tax_rate = st.number_input("Tax Rate (% of EBIT)", value=l_tax_rate, step=0.1)
        with col2:
            capex_pct = st.number_input("CapEx (% of Revenue)", value=l_capex_pct, step=0.1)
            wc_change_pct = st.number_input("Change in WC (% of Revenue)", value=l_wc_change_pct, step=0.1)
            interest_pct = st.number_input("WACC (%)", value=l_interest_pct, step=0.1)
        with col3:
            forecast_years = st.number_input("Forecast Years", value=l_forecast_years, min_value=1, max_value=30)
            growth_1_2 = st.number_input("Growth Rate Y1-2 (%)", value=l_growth_1_2, step=0.1)
            growth_3_5 = st.number_input("Growth Rate Y3-5 (%)", value=l_growth_3_5, step=0.1)
            growth_6 = st.number_input("Growth Rate Y6+ (%)", value=l_growth_6, step=0.1)
            shares = st.number_input("Shares Outstanding (Cr)", value=st.session_state.get("shares_outstanding", 0.0), step=0.01)
