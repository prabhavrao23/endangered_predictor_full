import os
import requests
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="Endangered Species Explorer", layout="wide")
st.title("🚎 Endangered Species Risk and Data Explorer")

# Load pinned species data from the API
try:
    pinned_response = requests.get(f"{API_URL}/pinned", timeout=10)
    pinned_response.raise_for_status()
    pinned_species = pinned_response.json()
except Exception:
    st.error("Failed to load pinned species data. Please ensure the API is running.")
    pinned_species = []

# Display pinned species section
st.header("📍 Pinned Endangered Species")
if pinned_species:
    species_options = [item.get("common_name") or item["species"] for item in pinned_species]
    selected_species = st.selectbox("Select a species", species_options)
    selected_data = next((item for item in pinned_species if (item.get("common_name") or item["species"]) == selected_species), None)
    if selected_data:
        # Show IUCN info if available
        iucn = selected_data.get("iucn")
        if iucn:
            st.markdown(f"**Scientific Name:** {iucn.get('scientific_name','N/A')}")
            st.markdown(f"**Common Name:** {iucn.get('common_name','N/A')}")
            st.markdown(f"**IUCN Status:** {iucn.get('status','N/A')}")
            st.markdown(f"**Population Trend:** {iucn.get('population_trend','N/A')}")
            st.markdown(f"**Habitat:** {iucn.get('habitat','N/A')}")
            st.markdown(f"**Threats:** {iucn.get('threats','N/A')}")
        else:
            st.write("No IUCN data available for this species.")

        # Show risk curve if available
        risk_curve = selected_data.get("risk_curve")
        if risk_curve:
            years = [point["year"] for point in risk_curve]
            probs = [point["p"] for point in risk_curve]
            fig = go.Figure(go.Scatter(x=years, y=probs, mode="lines+markers"))
            fig.update_layout(title="Extinction Risk Projection", yaxis_title="Probability of Quasi-Extinction", xaxis_title="Year")
            fig.update_yaxes(range=[0,1], tickformat=".0%")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.write("No extinction risk projection available for this species.")
else:
    st.write("No pinned species found.")

# Search section
st.header("🔍 Search the IUCN Red List")
query = st.text_input("Enter a species name to search")
if st.button("Search") and query.strip():
    with st.spinner("Searching..."):
        try:
            search_response = requests.get(f"{API_URL}/search", params={"query": query.strip()}, timeout=15)
            search_response.raise_for_status()
            search_results = search_response.json()
            st.subheader(f"Results for '{query.strip()}'")
            st.json(search_results)
        except Exception:
            st.error("Failed to perform search. Please check the API and your internet connection.")
