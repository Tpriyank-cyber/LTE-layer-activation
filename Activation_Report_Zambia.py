import streamlit as st
import pandas as pd
import numpy as np
import re
from io import BytesIO
from openpyxl import load_workbook
from openpyxl.styles import PatternFill
from streamlit_option_menu import option_menu

favicon = "favicon.png"

st.set_page_config(
    page_title="LTE Layer Activation Report",
    page_icon=favicon,
    layout="wide"
)

background_text_color = "#001135"
background_header_text_color = "#a235b6"


with st.sidebar:
    selected = option_menu(
        menu_title="Airtel Zambia",
        options=["About", "BBH Tool", "Contact Us"],
        icons=["person", "slack", "telephone"],
        styles={
            "container": {"background-color": "transparent"},
            "nav-link": {
                "font-size": "17px",
                "font-weight": "bold",
                "font-family": "Nokia Pure Headline",
            },
            "nav-link-selected": {
                "background-image": "linear-gradient(to left, #a235b6, #a235b6)",
                "color": "white"
            },
        },
    )


def get_band(cell):
    cell = str(cell).upper()
    if "L800" in cell:
        return "L800"
    elif "L2600" in cell:
        return "L2600"
    elif "L2100" in cell:
        return "L2100"
    return "L1800"


def get_sector(cell):
    m = re.search(r"S([1-9])", str(cell).upper())
    return f"S{m.group(1)}" if m else "unknown"


def get_carrier(cell):
    m = re.search(r"F([0-9]+)", str(cell).upper())
    return f"F{m.group(1)}" if m else "NA"


def process_files(bbh_file, day_file, sector_file):

    df_bbh = pd.read_excel(bbh_file)
    df_day = pd.read_excel(day_file)
    df_sector = pd.read_excel(sector_file)

    for df in (df_bbh, df_day, df_sector):
        df["Period start time"] = pd.to_datetime(
            df["Period start time"], errors="coerce"
        )
        df["Date"] = df["Period start time"].dt.date

    for df in (df_bbh, df_day, df_sector):
        df["Band"] = df["LNCEL name"].apply(get_band)
        df["Sector"] = df["LNCEL name"].apply(get_sector)
        df["Carrier"] = df["LNCEL name"].apply(get_carrier)


    sheet = (
        df_bbh.groupby(["Band", "Date"])["Avg IP thp DL QCI9"]
        .mean()
        .reset_index()
    )

    pivot = sheet.pivot(index="Band", columns="Date", values="Avg IP thp DL QCI9")


    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        pivot.to_excel(writer, sheet_name="Band_Summary")

    output.seek(0)
    return output


if selected == "About":
    st.markdown(
        f"<h2 style='color:{background_header_text_color};'>Tool Introduction</h2>",
        unsafe_allow_html=True
    )
    st.write("LTE Band/Sector/LCEL wise report Generator.")


if selected == "BBH Tool":

    st.markdown(
        f"<h3 style='color:{background_text_color};'>Upload Input Files</h3>",
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        bbh_file = st.file_uploader("BBH File", type=["xlsx"])

    with col2:
        day_file = st.file_uploader("Daily File", type=["xlsx"])

    with col3:
        sector_file = st.file_uploader("Sector File", type=["xlsx"])

    st.markdown("---")

    # Styled Button
    st.markdown("""
        <style>
        div.stButton > button {
            background-color:#a235b6;
            color:white;
            width:180px;
        }
        </style>
    """, unsafe_allow_html=True)

    if st.button("Run Analysis"):

        if not (bbh_file and day_file and sector_file):
            st.warning("Please upload all files")
        else:
            with st.spinner("Processing..."):
                output = process_files(bbh_file, day_file, sector_file)

            st.success("Analysis completed ✅")

            st.download_button(
                "Download Output Excel",
                data=output,
                file_name="LTE Layer Activation_Output.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

if selected == "Contact Us":
    st.markdown(
        f"<h3 style='color:{background_header_text_color};'>Help us improve!</h3>",
        unsafe_allow_html=True
    )
    st.write("Reach out to developer for support @ tomar.priyank@nokia.com.")


st.markdown("""
<style>
MainMenu {visibility:hidden;}
footer {visibility:hidden;}
header {visibility:hidden;}
</style>
""", unsafe_allow_html=True)
