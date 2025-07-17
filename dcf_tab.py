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
        if "initial_assumptions" not in st.session_state:
            st.error("Initial assumptions not found. Please upload data from the Inputs tab.")
            return
        # Load assumptions from initial assumptions (not session_state)
        defaults = st.session_state.get("initial_assumptions")
        if not isinstance(defaults, dict):
            st.error("Initial assumptions are not properly loaded. Please re-import the data.")
            return
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
        l_shares = defaults.get("shares_outstanding", 0.0)
        if st.button("🔁 Reset to Default"):
            st.session_state["ebit_margin"] = l_ebit_margin
            st.session_state["depreciation_pct"] = l_depreciation_pct
            st.session_state["tax_rate"] = l_tax_rate
            st.session_state["capex_pct"] = l_capex_pct
            st.session_state["wc_change_pct"] = l_wc_change_pct
            st.session_state["interest_pct"] = l_interest_pct
            st.session_state["forecast_years"] = l_forecast_years
            st.session_state["user_growth_rate_yr_1_2"] = l_growth_1_2
            st.session_state["user_growth_rate_yr_3_4_5"] = l_growth_3_5
            st.session_state["user_growth_rate_yr_6_onwards"] = l_growth_6
            st.session_state["shares_outstanding"] = l_shares

        col1, col2, col3 = st.columns(3)
        with col1:
            ebit_margin = st.number_input("EBIT Margin (%)", step=0.1, key="ebit_margin")
            depreciation_pct = st.number_input("Depreciation (% of Revenue)", step=0.1, key="depreciation_pct")
            tax_rate = st.number_input("Tax Rate (% of EBIT)", step=0.1, key="tax_rate")
            x_years = st.number_input("High Growth Period (X years)", min_value=1, max_value=30, value=5, step=1, key="x_years")
            growth_x = st.number_input("Growth Rate in X years (%)", step=0.1, value=20.0, key="growth_x")
        with col2:
            capex_pct = st.number_input("CapEx (% of Revenue)", step=0.1, key="capex_pct")
            wc_change_pct = st.number_input("Change in WC (% of Revenue)", step=0.1, key="wc_change_pct")
            interest_pct = st.number_input("WACC (%)", step=0.1, key="interest_pct")
            y_years = st.number_input("Total Projection Period (Y years)", min_value=5, max_value=40, value=15, step=1, key="y_years")
            growth_y = st.number_input("Growth Rate from X to Y years (%)", step=0.1, value=12.0, key="growth_y")
        with col3:
            growth_6 = st.number_input("Terminal Growth Rate (%)", step=0.1, key="user_growth_rate_yr_6_onwards")
            # Removed duplicate to fix StreamlitDuplicateElementKey error
            forecast_years = st.number_input("Forecast Years", min_value=1, max_value=30, key="forecast_years")
            growth_1_2 = st.number_input("Growth Rate Y1-2 (%)", step=0.1, key="user_growth_rate_yr_1_2")
            growth_3_5 = st.number_input("Growth Rate Y3-5 (%)", step=0.1, key="user_growth_rate_yr_3_4_5")
            # Removed duplicate to fix StreamlitDuplicateElementKey error
            shares = st.number_input("Shares Outstanding (Cr)", step=0.01, key="shares_outstanding")

    if st.button("🔄 Recalculate DCF"):
        ebit_margin = st.session_state["ebit_margin"]
        depreciation_pct = st.session_state["depreciation_pct"]
        tax_rate = st.session_state["tax_rate"]
        capex_pct = st.session_state["capex_pct"]
        wc_change_pct = st.session_state["wc_change_pct"]
        interest_pct = st.session_state["interest_pct"]
        forecast_years = st.session_state["forecast_years"]
        growth_1_2 = st.session_state["user_growth_rate_yr_1_2"]
        growth_3_5 = st.session_state["user_growth_rate_yr_3_4_5"]
        growth_6 = st.session_state["user_growth_rate_yr_6_onwards"]
        shares = st.session_state["shares_outstanding"]

        fcf_data = calculate_dcf(
            base_revenue=base_revenue,
            ebit_margin=ebit_margin,
            depreciation_pct=depreciation_pct,
            capex_pct=capex_pct,
            interest_pct=interest_pct,
            wc_change_pct=wc_change_pct,
            tax_rate=tax_rate,
            shares=shares,
            x_years=x_years,
            y_years=y_years,
            growth_rate_x=growth_x,
            growth_rate_y=growth_y,
            terminal_growth=growth_6
        )

        df_fcf = pd.DataFrame(fcf_data, columns=["Year", "Revenue", "EBIT", "Tax", "Net Operating PAT", "Depreciation", "CapEx", "Change in WC", "Free Cash Flow", "PV of FCF"])
        with st.expander("📊 Free Cash Flow Table"):
            st.dataframe(df_fcf.style.format({
                "Revenue": "{:.2f}", "EBIT": "{:.2f}", "Tax": "{:.2f}", "Net Operating PAT": "{:.2f}", "Depreciation": "{:.2f}",
                "CapEx": "{:.2f}", "Change in WC": "{:.2f}", "Free Cash Flow": "{:.2f}", "PV of FCF": "{:.2f}"
            }))

        final_fcf = fcf_data[-1][-2]
        terminal_value = (final_fcf * (1 + growth_6 / 100)) / ((interest_pct / 100) - (growth_6 / 100))
        pv_terminal = terminal_value / ((1 + interest_pct / 100) ** (len(fcf_data) - 1))
        total_pv_fcf = sum(row[-1] for row in fcf_data[1:])
        enterprise_value = total_pv_fcf + pv_terminal
        equity_value = enterprise_value
        fair_value_per_share = equity_value / shares if shares else 0

        st.metric("Fair Value per Share", f"₹{fair_value_per_share:,.2f}")

        with st.expander("📘 How Fair Value is Calculated"):
            st.markdown(f"""
            **Fair Value per Share Calculation**
            
            1. **FCF Projection**: Projected Free Cash Flows for {forecast_years} years.
            2. **Terminal Value**:
            \[ TV = FCF × (1 + g) / (r - g) \]
            Where:
              - FCF = ₹{final_fcf:,.2f}
              - g = {growth_6:.2f}% (Terminal Growth)
              - r = {interest_pct:.2f}% (WACC)
              - Terminal Value = ₹{terminal_value:,.2f}
              - Discounted Terminal Value = ₹{pv_terminal:,.2f}
            3. **Enterprise Value = PV of FCFs + PV of Terminal Value**  
               = ₹{total_pv_fcf:,.2f} + ₹{pv_terminal:,.2f} = ₹{enterprise_value:,.2f}
            4. **Equity Value = Enterprise Value** (assuming no debt/cash adjustment)
            5. **Fair Value per Share = Equity Value / Shares Outstanding ({shares:.2f} Cr)**
               = ₹{fair_value_per_share:,.2f} per share
            """)
