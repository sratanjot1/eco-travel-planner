import requests
import os
from dotenv import load_dotenv

load_dotenv()

def get_co2_emissions(distance_km):
    url = "https://www.carboninterface.com/api/v1/estimates"
    headers = {
        "Authorization": f"Bearer {os.getenv('CARBON_INTERFACE_API_KEY')}",
        "Content-Type": "application/json"
    }

    # You can use a fixed model like "medium-diesel-car" or fetch available IDs via their API
    payload = {
        "type": "vehicle",
        "distance_unit": "km",
        "distance_value": distance_km,
        "vehicle_model_id": "car-medium-diesel"
    }

    response = requests.post(url, json=payload, headers=headers)
    data = response.json()
    return round(data['data']['attributes']['carbon_kg'], 2)
