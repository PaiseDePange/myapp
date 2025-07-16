import streamlit as st
from input_tab import render_input_tab
from dcf_tab import render_dcf_tab
from data_checks_tab import render_data_checks_tab
from assumption_builder import build_assumptions_from_data


st.set_page_config(page_title="Smart Investing App", layout="wide")

st.title("🤖 Smart Investing App to model DCF and EPS")
st.caption("📦 Version: 1.0 Stable")

tabs = st.tabs(["📥 Inputs", "💰 DCF Valuation", "📈 EPS Projection", "🧾 Data Checks"])

with tabs[0]:
    render_input_tab()


if st.session_state.get("data_imported"):
    build_assumptions_from_data()

with tabs[1]:
    render_dcf_tab()

# EPS and Data Checks tabs can be added below
with tabs[3]:
    render_data_checks_tab()
