import streamlit as st
import requests
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

st.set_page_config(page_title="Eco-Travel Planner", layout="wide")
st.title("🌱 Eco-Travel Planner")
st.write("Plan your next sustainable trip using AI-powered recommendations.")

# Session state to retain values across reruns
if 'response_data' not in st.session_state:
    st.session_state.response_data = {}

# Tabs for better navigation
tabs = st.tabs(["📝 Trip Planner", "🗺️ Map View", "🌍 CO₂ Comparison", "📌 Greener Alternatives"])

# --- Tab 1: Trip Planner ---
with tabs[0]:
    with st.form("trip_form"):
        col1, col2 = st.columns(2)
        with col1:
            use_current_location = st.checkbox("Use my current location as starting point")
            start_location = ""
            if use_current_location:
                st.info("Fetching your current location using IP-based lookup...")
                try:
                    ip_info = requests.get("https://ipinfo.io/json").json()
                    start_location = ip_info.get("city") or ip_info.get("region")
                    st.success(f"Using your current location: {start_location}")
                except:
                    st.warning("Could not fetch current location. Please enter it manually.")
            else:
                start_location = st.text_input("Starting point", placeholder="e.g., Delhi")

        with col2:
            destination = st.text_input("Destination", placeholder="e.g., Amritsar")

        budget = st.slider("What is your approximate budget (₹)?", 2000, 50000, 10000, step=1000)
        duration = st.selectbox("Trip duration:", ["1-2 days", "3-5 days", "1 week", "2+ weeks"])
        preferences = st.multiselect(
            "What are your interests?",
            ["Nature", "Culture", "Adventure", "Food", "Low-budget", "Luxury", "Backpacking"]
        )

        submitted = st.form_submit_button("Generate Eco-Friendly Plan")
        reset = st.form_submit_button("🔄 Reset Form")

        if reset:
            st.session_state.response_data = {}
            st.experimental_rerun()

        if submitted:
            if not start_location or not destination:
                st.warning("Please enter both a starting point and a destination.")
            else:
                with st.spinner("Generating your sustainable plan..."):
                    query = f"From {start_location} to {destination}. Budget: ₹{budget}. Duration: {duration}. Interests: {', '.join(preferences)}."
                    try:
                        res = requests.post("http://127.0.0.1:8000/plan_trip/", json={"query": query}, timeout=30)
                        if res.status_code == 200:
                            plan = res.json().get("plan")
                            st.session_state.response_data = {
                                "start_location": start_location,
                                "destination": destination,
                                "plan": plan
                            }
                        else:
                            st.error(f"Failed to get response from backend: {res.status_code}")
                    except requests.exceptions.RequestException as e:
                        st.error(f"Error: {str(e)}")

    if st.session_state.response_data.get("plan"):
        st.subheader("📋 Itinerary Plan")
        st.markdown(st.session_state.response_data["plan"])

# --- Tab 2: Map View ---
with tabs[1]:
    if st.session_state.response_data.get("start_location") and st.session_state.response_data.get("destination"):
        geolocator = Nominatim(user_agent="eco_travel")
        start_coords = geolocator.geocode(st.session_state.response_data["start_location"])
        dest_coords = geolocator.geocode(st.session_state.response_data["destination"])

        if start_coords and dest_coords:
            route_map = folium.Map(location=[(start_coords.latitude + dest_coords.latitude)/2,
                                             (start_coords.longitude + dest_coords.longitude)/2],
                                  zoom_start=7)
            folium.Marker([start_coords.latitude, start_coords.longitude], popup="Start", icon=folium.Icon(color="green")).add_to(route_map)
            folium.Marker([dest_coords.latitude, dest_coords.longitude], popup="Destination", icon=folium.Icon(color="red")).add_to(route_map)
            folium.PolyLine(locations=[
                [start_coords.latitude, start_coords.longitude],
                [dest_coords.latitude, dest_coords.longitude]
            ], color="blue", weight=4, opacity=0.6).add_to(route_map)

            st.subheader("🗺️ Route Map")
            st_folium(route_map, width=700, height=500)
        else:
            st.warning("Couldn't geocode one of the locations. Try being more specific.")
    else:
        st.info("Please generate a plan first in the 'Trip Planner' tab.")

# --- Tab 3: CO2 Comparison ---
with tabs[2]:
    if st.session_state.response_data.get("start_location") and st.session_state.response_data.get("destination"):
        geolocator = Nominatim(user_agent="eco_travel")
        start_coords = geolocator.geocode(st.session_state.response_data["start_location"])
        dest_coords = geolocator.geocode(st.session_state.response_data["destination"])

        if start_coords and dest_coords:
            distance_km = geodesic((start_coords.latitude, start_coords.longitude), (dest_coords.latitude, dest_coords.longitude)).km
            co2_regular = distance_km * 0.192
            co2_eco = distance_km * 0.115
            co2_saved = co2_regular - co2_eco

            st.subheader("🌍 Carbon Emission Comparison")
            st.markdown(f"**From:** {st.session_state.response_data['start_location']}")
            st.markdown(f"**To:** {st.session_state.response_data['destination']}")
            st.markdown(f"**Distance:** {distance_km:.2f} km")
            st.markdown(f"**Carbon Emissions (Standard):** {co2_regular:.2f} kg CO₂")
            st.markdown(f"**Carbon Emissions (Eco Mode):** {co2_eco:.2f} kg CO₂")
            st.markdown(f"✅ **Estimated CO₂ Saved:** {co2_saved:.2f} kg")
        else:
            st.warning("Couldn't geocode locations for comparison.")
    else:
        st.info("Generate a plan to compare emissions.")

# --- Tab 4: Greener Alternatives ---
with tabs[3]:
    st.subheader("📌 Greener Alternatives for Your Route")
    if st.session_state.response_data.get("start_location") and st.session_state.response_data.get("destination"):
        st.markdown("Here are some alternatives you could choose to reduce your carbon footprint:")

        st.radio("Choose your preferred travel mode:", [
            "Car (Standard - 192g CO₂/km)",
            "Train (41g CO₂/km)",
            "Bus (105g CO₂/km)",
            "Bike/Walk (0g CO₂/km)"
        ], index=0)

        st.markdown("✅ Consider using public transport or shared mobility options.")
        st.markdown("✅ Avoid peak traffic hours and choose direct routes.")
        st.markdown("✅ Consider exploring last-mile travel options like bicycles, e-rickshaws, or walking.")
        st.markdown("✅ Plan stops around sustainable accommodations or eco-tourism spots.")
    else:
        st.info("Please plan a trip first to get greener alternatives.")
