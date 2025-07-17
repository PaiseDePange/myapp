import streamlit as st
import pandas as pd
from calculations import calculate_dcf, dcf_fair_value
from final_verdict import render_final_verdict




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
        
        l_growth_6 = defaults.get("user_growth_rate_yr_6_onwards", 4.0)
        l_shares = defaults.get("shares_outstanding", 0.0)
        if st.button("🔁 Reset to Default"):
            st.session_state["ebit_margin"] = l_ebit_margin
            st.session_state["depreciation_pct"] = l_depreciation_pct
            st.session_state["tax_rate"] = l_tax_rate
            st.session_state["capex_pct"] = l_capex_pct
            st.session_state["wc_change_pct"] = l_wc_change_pct
            st.session_state["interest_pct"] = l_interest_pct
            
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
                        # Removed: Growth Rate Y1-2 (%)
            # Removed: Growth Rate Y3-5 (%)
            # Removed duplicate to fix StreamlitDuplicateElementKey error
            shares = st.number_input("Shares Outstanding (Cr)", step=0.01, key="shares_outstanding")

    if st.button("🔄 Recalculate DCF"):
        ebit_margin = st.session_state["ebit_margin"]
        depreciation_pct = st.session_state["depreciation_pct"]
        tax_rate = st.session_state["tax_rate"]
        capex_pct = st.session_state["capex_pct"]
        wc_change_pct = st.session_state["wc_change_pct"]
        interest_pct = st.session_state["interest_pct"]
        
        growth_6 = st.session_state["user_growth_rate_yr_6_onwards"]
        shares = st.session_state["shares_outstanding"]

        fcf_data, fv, terminal_weight, phase1_pv, phase2_pv, pv_terminal = calculate_dcf(
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

        # Removed duplicate dcf_fair_value call to avoid redundant calculation

        st.metric("Fair Value per Share", f"₹{fv:,.2f}")

        meta_df = st.session_state["meta"].copy()
        if meta_df.shape[1] == 2:
            meta_df.columns = ["Label", "Value"]
        current_price = float(meta_df.set_index("Label").loc["Current Price", "Value"])
        render_final_verdict(fair_value=fv, current_price=current_price)
        st.caption("""
        💡 We determine the valuation status by comparing the calculated fair value with the current market price:
        - 🟢 **Undervalued** if fair value is more than 15% higher than the current price
        - ⚪ **Fairly Valued** if within ±15% of current price
        - 🔴 **Overvalued** if fair value is more than 15% below the current price

        📢 **Disclaimer:** Stock investment decisions are subject to market risks. Please do your own research and consult a SEBI-registered Research Analyst before making any investment decisions. This valuation is purely based on the uploaded financials and user-defined assumptions. Real-world performance can differ significantly. 

        However, for your assistance, a detailed scenario and sensitivity analysis is provided below.
        """)

        with st.expander("📘 How Fair Value is Calculated"):
            fv, terminal_weight, phase1_pv, phase2_pv, pv_terminal = dcf_fair_value(
                base_revenue=base_revenue,
                ebit_margin=ebit_margin,
                depreciation_pct=depreciation_pct,
                capex_pct=capex_pct,
                wc_change_pct=wc_change_pct,
                tax_rate=tax_rate,
                interest_pct=interest_pct,
                shares=shares,
                x_years=x_years,
                y_years=y_years,
                growth_rate_x=growth_x,
                growth_rate_y=growth_y,
                terminal_growth=growth_6
            )
            st.markdown(f"""
            **Fair Value per Share Calculation**

            **Phase Breakdown:**
            - Phase 1 (Years 1–{x_years}) PV: ₹{phase1_pv:,.2f}
            - Phase 2 (Years {x_years+1}–{y_years}) PV: ₹{phase2_pv:,.2f}
            - Terminal Value PV: ₹{pv_terminal:,.2f}  
              → Contributes **{terminal_weight:.1f}%** of total Enterprise Value

            **Enterprise Value = PV of All FCFs + Terminal Value**
            - EV = ₹{phase1_pv + phase2_pv:,.2f} + ₹{pv_terminal:,.2f} = ₹{phase1_pv + phase2_pv + pv_terminal:,.2f}

            **Fair Value/Share = EV ÷ Shares Outstanding ({shares:.2f} Cr)**
            - Fair Value/Share = ₹{fv:,.2f}
            """)
