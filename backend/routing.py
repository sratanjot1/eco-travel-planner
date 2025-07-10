import openrouteservice
import os
from dotenv import load_dotenv
from geopy.geocoders import Nominatim

load_dotenv()

client = openrouteservice.Client(key=os.getenv("OPENROUTESERVICE_API_KEY"))
geolocator = Nominatim(user_agent="eco_travel_app")

def geocode_location(place):
    location = geolocator.geocode(place)
    if location:
        return (location.latitude, location.longitude)
    return None

def get_route_data(start_coords, end_coords):
    coords = [start_coords[::-1], end_coords[::-1]]  # (lng, lat)
    result = client.directions(coords, profile='driving-car')
    distance_km = result['routes'][0]['summary']['distance'] / 1000
    duration_mins = result['routes'][0]['summary']['duration'] / 60
    return {
        "distance_km": round(distance_km, 2),
        "duration_mins": int(duration_mins)
    }
