import streamlit as st

def render_data_checks_tab():
    st.header("🧾 Data Checks")
    
    if not st.session_state.get("data_imported"):
        st.info("Please upload a file from the Inputs tab and click 'Import Data'.")
        return

    st.subheader("📌 Company Meta Info")
    st.dataframe(st.session_state.get("meta", "Not found"))

    st.subheader("📊 Annual Profit & Loss")
    st.dataframe(st.session_state.get("annual_pl", "Not found"))

    st.subheader("📆 Quarterly Results")
    st.dataframe(st.session_state.get("quarterly", "Not found"))

    st.subheader("📋 Balance Sheet")
    st.dataframe(st.session_state.get("balance_sheet", "Not found"))

    st.subheader("💸 Cash Flow Statement")
    st.dataframe(st.session_state.get("cashflow", "Not found"))
