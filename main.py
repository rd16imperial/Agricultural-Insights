import requests
from google.cloud import firestore
from datetime import datetime, timedelta

# Initialize Firestore
db = firestore.Client()

# Weatherbit API configuration
API_KEY = "" # API KEY REMOVED FOR GIT, PLEASE ADD YOUR OWN API KEY OR FIND IT IN REPORT
LAT = "34.035" 
LON = "-117.846191"  
WEATHER_URL = "https://api.weatherbit.io/v2.0/history/hourly"
AGWEATHER_URL = "https://api.weatherbit.io/v2.0/history/agweather"


def fetch_weather_data():
    try:
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=5)
        params = {
            "lat": LAT,
            "lon": LON,
            "start_date": start_time.strftime("%Y-%m-%d:%H"),
            "end_date": end_time.strftime("%Y-%m-%d:%H"),
            "key": API_KEY,
        }
        response = requests.get(WEATHER_URL, params=params)
        response.raise_for_status()
        print(f"Weather API Response: {response.json()}")
        return response.json()["data"]
    except Exception as e:
        print(f"Error fetching weather data: {e}")
        return None


def fetch_soil_data():
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=7)
        params = {
            "lat": LAT,
            "lon": LON,
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "key": API_KEY,
        }
        response = requests.get(AGWEATHER_URL, params=params)
        response.raise_for_status()
        print(f"Agricultural Weather API Response: {response.json()}")
        return response.json()["data"]
    except Exception as e:
        print(f"Error fetching soil data: {e}")
        return None

# Save data to Firestore
def save_to_firestore(data, collection_name):
    try:
        for record in data:
            # Generate a unique document ID
            doc_id = f"{record['timestamp_local'].replace(' ', '_')}"

            # Create document data based on collection type
            document_data = {"timestamp": record["timestamp_local"]}
            if collection_name == "weather_data":
                document_data.update({
                    "temperature": record.get("temp"),
                    "humidity": record.get("rh"),
                    "pressure": record.get("pres"),
                    "wind_speed": record.get("wind_spd"),
                    "precipitation": record.get("precip"),
                })
            elif collection_name == "soil_data":
                document_data.update({
                    "soil_moisture": record.get("soil_moisture"),
                    "temp": record.get("temp"),
                    "precipitation": record.get("precip"),
                })

            # Save to Firestore
            db.collection(collection_name).document(doc_id).set(document_data)
            print(f"Saved data to {collection_name} for {record['timestamp_local']}")
    except Exception as e:
        print(f"Error saving data to Firestore: {e}")

# Entry point for weather data
def main(event, context):
    print("Fetching weather data...")
    weather_data = fetch_weather_data()
    if weather_data:
        print("Saving weather data to Firestore...")
        save_to_firestore(weather_data, "weather_data")
    else:
        print("No weather data fetched.")

# Entry point for soil data
def fetch_soil_data_main(event, context):
    print("Fetching soil data...")
    soil_data = fetch_soil_data()
    if soil_data:
        print("Saving soil data to Firestore...")
        save_to_firestore(soil_data, "soil_data")
    else:
        print("No soil data fetched.")

