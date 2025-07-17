import streamlit as st
import pandas as pd
from calculations import calculate_dcf
from final_verdict import render_final_verdict
from disclaimer import render_disclaimer

def render_dcf_tab():
    col_header, col_button = st.columns([0.8, 0.2])
    with col_header:
        st.header("💰 DCF Valuation")
    with col_button:
        recalc = st.button("🔄 Recalculate DCF")

    if not st.session_state.get("data_imported"):
        st.info("Please upload data first in the Inputs tab.")
        return

    with st.expander("📋 Assumptions", expanded=True):
        if "initial_assumptions" not in st.session_state:
            st.error("Initial assumptions not found. Please upload data from the Inputs tab.")
            return

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
        l_growth_terminal = defaults.get("user_growth_rate_yr_6_onwards", 4.0)
        l_period_x = defaults.get("l_period_x", 5.0)
        l_period_y = defaults.get("l_period_y", 15.0)
        l_growth_x = defaults.get("l_growth_x", 20.0)
        l_growth_y = defaults.get("l_growth_y", 12.0)
        l_shares = defaults.get("shares_outstanding", 10.0)
        l_base_revenue = defaults.get("latest_revenue", 10.0)
        l_net_debt = defaults.get("net_debt", 0.0)

        if st.button("🔁 Reset to Default"):
            st.session_state.update({
                "ebit_margin": l_ebit_margin,
                "depreciation_pct": l_depreciation_pct,
                "tax_rate": l_tax_rate,
                "capex_pct": l_capex_pct,
                "wc_change_pct": l_wc_change_pct,
                "interest_pct": l_interest_pct,
                "growth_terminal": l_growth_terminal,
                "x_years": l_period_x,
                "y_years": l_period_y,
                "growth_x": l_growth_x,
                "growth_y": l_growth_y,
                "shares_outstanding": l_shares,
                "base_revenue": l_base_revenue,
                "net_debt": l_net_debt
            })

        col1, col2, col3 = st.columns(3)
        with col1:
            base_revenue = st.number_input("Latest Annual Revenue", step=10, key="base_revenue", help="Latest Revenue or Sales number")
            net_debt = st.number_input("Net Debt", step=10, key="net_debt", help="Total borrowings minus cash & investments")
            shares = st.number_input("Shares Outstanding (Cr)", step=0.01, key="shares_outstanding")
            ebit_margin = st.number_input("EBIT Margin (% of Revenue)", step=0.1, key="ebit_margin")
            depreciation_pct = st.number_input("Depreciation (% of Revenue)", step=0.1, key="depreciation_pct")
        with col2:
            capex_pct = st.number_input("CapEx (% of Revenue)", step=0.1, key="capex_pct")
            wc_change_pct = st.number_input("Change in WC (% of Revenue)", step=0.1, key="wc_change_pct")
            tax_rate = st.number_input("Tax Rate (% of EBIT)", step=0.1, key="tax_rate")
            interest_pct = st.number_input("WACC (%)", step=0.1, key="interest_pct")
        with col3:
            x_years = st.number_input("High Growth Period (X years)", min_value=1, max_value=30, step=1, key="x_years")
            growth_x = st.number_input("Growth Rate in X years (%)", step=0.1, key="growth_x")
            y_years = st.number_input("Total Projection Period (Y years)", min_value=5, max_value=40, step=1, key="y_years")
            growth_y = st.number_input("Growth Rate from X to Y years (%)", step=0.1, key="growth_y")
            growth_terminal = st.number_input("Terminal Growth Rate (%)", step=0.1, key="growth_terminal")

    if recalc:
        fcf_data, fv, terminal_weight, phase1_pv, phase2_pv, pv_terminal, enterprise_value, equity_value = calculate_dcf(
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
            terminal_growth=terminal_growth,
            net_Debt = net_debt
            

        )

        df_fcf = pd.DataFrame(fcf_data, columns=[
            "Year", "Revenue", "EBIT", "Tax", "Net Operating PAT",
            "Depreciation", "CapEx", "Change in WC", "Free Cash Flow", "PV of FCF"
        ])
        with st.expander("📊 Free Cash Flow Table"):
            st.dataframe(df_fcf.style.format("{:.2f}"))

        st.metric("Fair Value per Share", f"₹{fv:,.2f}")

        with st.expander("📢 Disclaimer"):
            render_disclaimer()

        try:
            meta_df = st.session_state["meta"].copy()
            if meta_df.shape[1] == 2:
                meta_df.columns = ["Label", "Value"]
            current_price = float(meta_df.set_index("Label").loc["Current Price", "Value"])
        except Exception:
            current_price = 0

        with st.expander("📍 Final Verdict"):
            render_final_verdict(fair_value=fv, current_price=current_price)

        with st.expander("📘 How Fair Value is Calculated"):
            st.markdown(f"""
            **Fair Value per Share Calculation**

            **Phase Breakdown:**
            - Phase 1 (Years 1–{x_years}) PV: ₹{phase1_pv:,.2f}
            - Phase 2 (Years {x_years+1}–{y_years}) PV: ₹{phase2_pv:,.2f}
            - Terminal Value PV: ₹{pv_terminal:,.2f}  
              → Contributes **{terminal_weight:.1f}%** of total Equity Value

            - Enterprise Value = ₹{enterprise_value:,.2f}
            - Equity Value = ₹{equity_value:,.2f}
            - Net Debt = ₹{st.session_state["net_debt"]:,.2f}

            **Fair Value/Share = Equity Value ÷ Shares Outstanding ({shares:.2f} Cr)**
            - Fair Value/Share = ₹{fv:,.2f}
            """)
