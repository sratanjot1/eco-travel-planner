from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from backend.routing import geocode_location, get_route_data
from backend.ai_module import get_carbon_data, get_hotels, generate_itinerary
import os
import requests
from dotenv import load_dotenv

import google.generativeai as genai

load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TripRequest(BaseModel):
    source: str
    destination: str
    budget: int
    duration: str
    preferences: list[str]

def get_eco_plan(prompt: str):
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Gemini API Error: {e}"

@app.post("/plan_trip/")
async def plan_trip(request: TripRequest):
    try:
        start_coords = geocode_location(request.source)
        end_coords = geocode_location(request.destination)

        if not start_coords or not end_coords:
            raise HTTPException(status_code=400, detail="Could not geocode location(s).")

        route = get_route_data(start_coords, end_coords)

        user_prompt = (
            f"You are planning a trip from {request.source} to {request.destination}. "
            f"The distance is around {route['distance_km']} km and will take about {route['duration_mins']} minutes. "
            f"Your budget is ₹{request.budget} for a duration of {request.duration}. "
            f"Your preferences include: {', '.join(request.preferences)}. "
            "Suggest an eco-friendly travel plan with CO₂-saving tips, sustainable stay, food, and transport. ignore the duration give holistic report on what can be done at the destination?"
        )

        plan = get_eco_plan(user_prompt)
        carbon_kg, carbon_modes = get_carbon_data(route['distance_km'])
        hotels = get_hotels(end_coords)
        itinerary = generate_itinerary(user_prompt)

        return {
            "plan": plan,
            "distance_km": route["distance_km"],
            "duration_mins": route["duration_mins"],
            "carbon_estimate_kg": carbon_kg,
            "carbon_modes": carbon_modes,
            "hotels": hotels,
            "itinerary": itinerary
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
