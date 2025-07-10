import streamlit as st
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.ai_module import (
    generate_itinerary, get_eco_plan, get_carbon_data,
    get_eco_tips, get_coordinates, get_eco_hotels,
    get_eco_trip, get_eco_hotels, get_transport_links,
    get_chat_response
)
from streamlit_lottie import st_lottie
import json
import requests
import time
import plotly.express as px

st.set_page_config(page_title="Eco Travel Planner", layout="wide")

# --- Load Lottie ---
def load_lottie(path):
    with open(path, "r") as f:
        return json.load(f)

# --- Sidebar ---
st.sidebar.markdown("## 🌍 Eco Travel Menu")
page = st.sidebar.radio("Navigate", ["🏠 Home", "🧳 Plan Trip", "📊 Insights & Booking", "🤖 Chat Bot"])

if "submitted" not in st.session_state:
    st.session_state.submitted = False

if "results" not in st.session_state:
    st.session_state.results = {}

# --- Home Page ---
if page == "🏠 Home":
    st.title("🌿 Welcome to Eco Travel Planner")
    col1, col2 = st.columns([1, 1])
    with col1:
        st_lottie(load_lottie(r"C:\Users\srata\OneDrive\Desktop\SAP Project\frontend\animations\eco_leaf.json"), height=400)
    with col2:
        st.markdown("""
        ### About Eco Travel Planner
        This app helps you plan **eco-conscious trips** that minimize your carbon footprint,
        support local communities, and ensure unforgettable, sustainable travel experiences.

        ✅ Personalized for solo, group, or family trips  
        ✅ AI-powered itinerary & tips from Gemini  
        ✅ Real eco-friendly hotels & travel options  
        ✅ Instant carbon insights & booking help
        """)
        st.info("Our mission is to help you **travel smarter**, **emit less**, and **experience more** – while being kind to the planet.")

# --- Plan Trip Page ---
elif page == "🧳 Plan Trip":
    st.header("📅 Plan Your Eco-Friendly Trip")

    col1, col2 = st.columns(2)
    with col1:
        start = st.text_input("🏠 Starting Location")
        destination = st.text_input("🌍 Destination")
        days = st.slider("📆 Trip Duration (days)", 1, 30, 5)
        budget = st.number_input("💰 Budget (in ₹)", min_value=1000, step=500)
    with col2:
        traveler_type = st.selectbox("👥 Who are you traveling with?", ["Solo", "Friends", "Family"])
        if traveler_type in ["Friends", "Family"]:
            people_count = st.number_input("🧑 Number of Adults", 2, 20, step=1)
        else:
            people_count = 1

        children_count = 0
        if traveler_type == "Family":
            children_count = st.number_input("👶 Children (under 13)", 0, 10, step=1)

        preferences = st.multiselect("🌱 Preferences", ["Nature", "Culture", "Adventure", "Relaxation", "Local Food", "Offbeat", "Wildlife"])

    if st.button("🚀 Generate Itinerary"):
        with st.spinner("Crafting your trip with AI magic..."):
            coords = get_coordinates(destination)
            hotels = get_eco_hotels(destination)
            plan_prompt = get_eco_plan(destination, days, budget, preferences, people_count, children_count)
            itinerary = generate_itinerary(plan_prompt)
            carbon_estimate, carbon_modes = get_carbon_data(100 * days)

            st.session_state.results = {
                "destination": destination,
                "days": days,
                "budget": budget,
                "preferences": preferences,
                "carbon_modes": carbon_modes,
                "itinerary": itinerary,
                "hotels": hotels,
                "eco_trip": get_eco_trip(destination, days, budget, preferences, people_count, children_count),
                "eco_tips": get_eco_tips(destination, preferences),
                "eco_hotels": get_eco_hotels(destination),
                "transport_links": get_transport_links(destination),
                "people": people_count,
                "children": children_count
            }
            st.session_state.submitted = True
        st.success("✅ Your sustainable itinerary is ready! Explore it in the Insights & Booking tab.")

# --- Insights & Booking ---
elif page == "📊 Insights & Booking":
    st.header("📈 Eco Insights & Booking Guide")

    if not st.session_state.submitted:
        st.warning("⚠️ Please generate an itinerary first in the Plan Trip tab.")
    else:
        st.subheader("🌿 Gemini's Eco Travel Strategy")
        st.markdown(st.session_state.results["eco_trip"])

        st.subheader("📌 Region-Specific Sustainable Travel Tips")
        st.markdown(st.session_state.results["eco_tips"])

        st.subheader("🏨 Eco-Conscious Hotel Suggestions")
        st.markdown(st.session_state.results["eco_hotels"])

        st.subheader("♻️ Carbon Emission Estimates (approx per person)")
        for mode, val in st.session_state.results["carbon_modes"].items():
            st.markdown(f"- {mode}: **{val} kg CO₂**")

        fig = px.pie(
            names=list(st.session_state.results["carbon_modes"].keys()),
            values=list(st.session_state.results["carbon_modes"].values()),
            title="Carbon Emission by Transport Mode"
        )
        st.plotly_chart(fig)

        st.subheader("📋 Day-wise Eco Itinerary")
        for day in st.session_state.results["itinerary"]:
            st.markdown(f"**Day {day['day']}**: {day['details']}")

        st.subheader("🚉 Transport Options to Reach Destination")
        st.markdown(st.session_state.results["transport_links"])

# --- Chat Bot Page ---
elif page == "🤖 Chat Bot":
    st.markdown("## 🤖 Ask Your Eco Travel Bot")
    st_lottie(load_lottie(r"C:\Users\srata\OneDrive\Desktop\SAP Project\frontend\animations\eco_leaf.json"), height=200)
    st.markdown("#### 🌿 How can I help with your sustainable trip today?")

    prompt = st.text_input("Type your eco travel question here...")

    if st.button("Send"):
        with st.spinner("EcoBot is thinking mindfully..."):
            itinerary_context = "\n".join([f"Day {d['day']}: {d['details']}" for d in st.session_state.results.get("itinerary", [])])
            prompt_with_context = f"Here is my itinerary:\n{itinerary_context}\nNow: {prompt}"
            response = get_chat_response(prompt_with_context)
        st.markdown("#### 🧠 EcoBot Says:")
        st.success(response)
