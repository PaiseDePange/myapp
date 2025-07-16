import streamlit as st
import pandas as pd
import openpyxl
from assumption_builder import build_assumptions_from_data

def render_input_tab():
    st.header("📥 Upload Financial Data")
    uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

    if uploaded_file and st.button("📥 Import Data"):
        uploaded_file.seek(0)
        df_all = pd.read_excel(uploaded_file, sheet_name="Data Sheet", header=None, engine="openpyxl")
        st.session_state["company_name"] = df_all.iloc[0, 1] if pd.notna(df_all.iloc[0, 1]) else "Unknown Company"

        def extract_table(df, start_label, start_row_offset, col_count=11):
            start_row = df[df.iloc[:, 0] == start_label].index[0]
            header_row = start_row + start_row_offset
            headers_raw = df.iloc[header_row, 0:col_count].tolist()
            headers = [str(h) if pd.notna(h) else f"Unnamed_{i}" for i, h in enumerate(headers_raw)]
            data_rows = []
            for i in range(start_row + start_row_offset + 1, df.shape[0]):
                row = df.iloc[i, 0:col_count]
                if row.isnull().all():
                    break
                data_rows.append(row.tolist())
            return pd.DataFrame(data_rows, columns=headers).fillna(0)

        st.session_state["annual_pl"] = extract_table(df_all, "PROFIT & LOSS", 1)
        st.session_state["balance_sheet"] = extract_table(df_all, "BALANCE SHEET", 1)
        st.session_state["cashflow"] = extract_table(df_all, "CASH FLOW:", 1)
        st.session_state["quarterly"] = extract_table(df_all, "Quarters", 1)
        st.session_state["meta"] = extract_table(df_all, "META", 0, 2)

        assumptions = build_assumptions_from_data()
        st.session_state["initial_assumptions"] = assumptions
        st.session_state["data_imported"] = True

        st.success(f"✅ Data imported for {st.session_state['company_name']}")
