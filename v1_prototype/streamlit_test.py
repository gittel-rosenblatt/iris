import streamlit as st
import datetime as dt

# Set the page to be wide and clean
st.set_page_config(page_title="Iris Weather", layout="wide")

# Massive, accessible header for your dad
st.markdown("<h1 style='text-align: center; font-size: 80px;'>Iris System</h1>", unsafe_allow_html=True)

# Create two huge columns side-by-side
col1, col2 = st.columns(2)

with col1:
    st.markdown("<h2 style='text-align: center;'>Date & Time</h2>", unsafe_allow_html=True)
    current_date = dt.datetime.now().strftime("%A, %B %d")
    st.markdown(f"<p style='text-align: center; font-size: 40px;'>{current_date}</p>", unsafe_allow_html=True)

with col2:
    st.markdown("<h2 style='text-align: center;'>Current Weather</h2>", unsafe_allow_html=True)
    # This is a temporary placeholder for your API data!
    st.markdown("<p style='text-align: center; font-size: 40px;'>72°F — Clear Sky</p>", unsafe_allow_html=True)