import streamlit as st

st.set_page_config(page_title="📊Lenders Dashboard", layout="wide")

st.title("📊 Interactive Credit Dashboard")
st.markdown("This dashboard visualizes the overall credit profile of farmers across Nigeria.")

# Replace the URL below with your Power BI embed link
powerbi_url = "https://app.powerbi.com/view?r=eyJrIjoiNzRkYWM3MjAtODA2Zi00YzdiLWJjMTktMjdkODI4NGM3YTQwIiwidCI6IjhjNmEzZDFhLWY5N2ItNDBjMC05ZTgxLTMxYzEwOTQxMzU3NiJ9"

st.components.v1.iframe(powerbi_url, height=800, width=1200, scrolling=True)
