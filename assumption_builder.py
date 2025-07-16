import pandas as pd
import streamlit as st
def build_assumptions_from_data():
    if not st.session_state.get("data_imported"):
        return

    # Extract and compute base values
    df = st.session_state["meta"].copy()
    df.columns = ["Label", "Value"]
    df = df.set_index("Label")
    current_price = float(df.loc["Current Price", "Value"])
    market_cap = float(df.loc["Market Capitalization", "Value"])

    df_bs = st.session_state["balance_sheet"].copy().set_index("Report Date")
    share_outstanding_row = df_bs.loc["No. of Equity Shares"].dropna()

    df_pl = st.session_state["annual_pl"].copy().set_index("Report Date")
    revenue_row = df_pl.loc["Sales"].dropna()
    tax_row = df_pl.loc["Tax"].dropna()
    depreciation_row = df_pl.loc["Depreciation"].dropna()

    try:
        calculated_ebit = revenue_row[-1] - sum(df_pl.loc[row].dropna()[-1] for row in [
            "Raw Material Cost", "Change in Inventory", "Power and Fuel",
            "Other Mfr. Exp", "Employee Cost", "Selling and admin", "Other Expenses"] if row in df_pl.index)
        latest_revenue = revenue_row[-1]
        calculated_ebit_margin = round((calculated_ebit / latest_revenue) * 100, 1)
        calculated_tax_rate = round((tax_row[-1]/calculated_ebit)*100, 1)
        calculated_depreciation_rate = round((depreciation_row[-1]/latest_revenue)*100, 1)
    except:
        calculated_ebit_margin = 0
        calculated_tax_rate = 0
        calculated_depreciation_rate = 0
    try:
        outstanding_shares = round(share_outstanding_row[-1]/10000000, 2)
    except:
        outstanding_shares = 0
    return {
        "ebit_margin": calculated_ebit_margin,
        "depreciation_pct": calculated_depreciation_rate,
        "tax_rate": calculated_tax_rate,
        "capex_pct": 2.0,
        "wc_change_pct": 2.0,
        "interest_pct": 10.0,
        "forecast_years": 20,
        "user_growth_rate_yr_1_2": 10.0,
        "user_growth_rate_yr_3_4_5": 10.0,
        "user_growth_rate_yr_6_onwards": 4.0
    }
