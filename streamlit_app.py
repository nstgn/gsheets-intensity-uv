import streamlit as st
from streamlit_gsheets import GSheetsConnection

conn = st.connection("gsheets", type=GSheetsConnection)

data = conn.read(worksheet="Intensity1")
st.dataframe(data)