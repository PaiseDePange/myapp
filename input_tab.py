import streamlit as st
import pandas as pd
import openpyxl
from file_loader import extract_table



def render_input_tab():
    st.header("📥 Inputs")
    uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

    if uploaded_file and st.button("📥 Import Data"):
        uploaded_file.seek(0)  # Reset pointer for pandas
        try:
            wb = openpyxl.load_workbook(uploaded_file, data_only=True)
            sheet = wb["Data Sheet"]
            data = list(sheet.values)
            df_all = pd.DataFrame(data)
        except Exception as e:
            st.error(f"❌ Error reading Excel file: {e}")
            st.stop()

        if df_all.isna().sum().sum() > 50:
            st.warning("⚠️ Many empty cells found. If your sheet uses formulas, please ensure it was saved after calculation in Excel.")

        st.session_state["company_name"] = df_all.iloc[0, 1] if pd.notna(df_all.iloc[0, 1]) else "Unknown Company"
        st.session_state["annual_pl"] = extract_table(df_all, "PROFIT & LOSS", 1, 11)
        st.session_state["balance_sheet"] = extract_table(df_all, "BALANCE SHEET", 1, 11)
        st.session_state["cashflow"] = extract_table(df_all, "CASH FLOW:", 1, 11)
        st.session_state["quarterly"] = extract_table(df_all, "Quarters", 1, 11)
        st.session_state["meta"] = extract_table(df_all, "META", 0, 2)
        st.session_state["data_imported"] = True

assumptions = build_assumptions_from_data()
st.session_state["initial_assumptions"] = assumptions
