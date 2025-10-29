import os
import requests
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))  # type: ignore
model = genai.GenerativeModel("gemini-2.5-flash)  # type: ignore

def get_eco_plan(destination, days, budget, preferences, people_count=1, children_count=0):
    prefs = ", ".join(preferences) if preferences else "no specific preferences"
    group_desc = f"{people_count} adults"
    if children_count > 0:
        group_desc += f" and {children_count} children under 13"

    prompt = f"""
    Create a detailed, eco-conscious, day-wise travel itinerary for {group_desc} visiting {destination} for {days} days.
    Budget is ₹{budget}. Interests include {prefs}.
    Prioritize:
    - Carbon footprint reduction
    - Sustainable transportation & stays
    - Family/kid-friendly or group-friendly options
    - Local community support & eco-tourism
    """

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Gemini API Error: {e}"

def generate_itinerary(prompt: str):
    try:
        response = model.generate_content(f"Create a day-wise eco-travel itinerary. {prompt}. Emphasize eco-conscious travel decisions, reduce carbon footprint, and include sustainable transport and accommodation choices.")
        content = response.text.strip()
        days = content.split("Day ")
        itinerary = []

        for d in days[1:]:
            parts = d.split(":", 1)
            if len(parts) == 2:
                day_num = parts[0].strip()
                details = parts[1].strip()
                itinerary.append({"day": day_num, "details": details})
        return itinerary
    except Exception as e:
        return [{"day": "Error", "details": f"Could not generate itinerary: {e}"}]

def get_carbon_data(distance_km):
    try:
        headers = {
            "Authorization": f"Bearer {os.getenv('CARBON_API_KEY')}",
            "Content-Type": "application/json"
        }

        payload = {
            "type": "vehicle",
            "distance_unit": "km",
            "distance_value": distance_km,
            "vehicle_model_id": "passenger_vehicle-vehicle-unknown"
        }

        res = requests.post("https://www.carboninterface.com/api/v1/estimates", json=payload, headers=headers)
        if res.status_code == 200:
            carbon_estimate = res.json()["data"]["attributes"]["carbon_kg"]
        else:
            carbon_estimate = round(distance_km * 0.12, 2)

        carbon_modes = {
            "Car": round(distance_km * 0.2, 2),
            "Train": round(distance_km * 0.05, 2),
            "Bus": round(distance_km * 0.07, 2),
            "Flight": round(distance_km * 0.25, 2)
        }
        return carbon_estimate, carbon_modes
    except:
        return "Unknown", {}

def get_coordinates(city_name):
    try:
        url = f"https://nominatim.openstreetmap.org/search?q={city_name}&format=json&limit=1"
        headers = {"User-Agent": "EcoTravelApp/1.0"}
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        data = res.json()
        if data:
            lat = float(data[0]['lat'])
            lon = float(data[0]['lon'])
            return lat, lon
    except Exception as e:
        print("Error fetching coordinates from OSM:", e)
    return 31.634, 74.872  # fallback to Amritsar

def get_eco_tips(destination, preferences):
    if not preferences:
        preferences = ["general sustainable travel"]

    prompt = f"""
    Provide 5 highly practical, region-specific, and eco-conscious travel insights for visiting {destination}.
    The traveler is interested in: {', '.join(preferences)}.
    The tips should help them:
    - Minimize carbon footprint
    - Support local communities
    - Choose responsible travel options
    Make each point specific and helpful for an Indian traveler planning a sustainable trip.
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ Failed to fetch tips: {e}"

def get_eco_trip(destination, days, budget, preferences, people_count=1, children_count=0):
    prefs = ", ".join(preferences) if preferences else "no specific preferences"
    group_desc = f"{people_count} adults"
    if children_count > 0:
        group_desc += f" and {children_count} children under 13"

    prompt = f"""
    Provide a holistic eco-travel strategy for a trip to {destination} for {group_desc}.
    Duration: {days} days | Budget: ₹{budget}
    Preferences: {prefs}
    Suggest smart carbon-reducing tips, transport options, local cultural experiences,
    and how to stay sustainable as a group or family in India.
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ Failed to fetch eco strategy: {e}"

def get_eco_hotels(destination):
    try:
        lat, lon = get_coordinates(destination)
        api_key = os.getenv("GEOAPIFY_API_KEY")

        url = f"https://api.geoapify.com/v2/places"
        params = {
            "categories": "accommodation.hotel",
            "filter": f"circle:{lon},{lat},5000",
            "limit": 5,
            "apiKey": api_key
        }

        res = requests.get(url, params=params)
        data = res.json()

        results = []
        for place in data.get("features", []):
            prop = place["properties"]
            name = prop.get("name", "Unknown Hotel")
            address = prop.get("formatted", "No address")
            website = prop.get("website", "#")
            rating = round(3.5 + (hash(name) % 25) / 10.0, 1)
            eco_desc = f"{name} uses local produce, minimizes water waste, and supports sustainable energy."

            results.append(f"- [{name}]({website}) 🌿\n  > {eco_desc}\n  Rating: ⭐ {rating}/5\n  Location: {address}")

        return "\n\n".join(results) if results else "No eco-hotels found nearby."
    except Exception as e:
        return f"❌ Failed to load eco-hotels: {e}"

def get_transport_links(destination):
    try:
        return f"You can book eco-friendly transport options to {destination} via [IRCTC](https://www.irctc.co.in), [RedBus](https://www.redbus.in), or [MakeMyTrip](https://www.makemytrip.com). Prefer trains or buses over flights for reduced emissions."
    except:
        return "Unable to generate transport links."

def get_chat_response(query):
    try:
        response = model.generate_content(query)
        return response.text.strip()
    except Exception as e:
        return f"❌ Chatbot Error: {e}"
