import requests
import pandas as pd
import datetime
import time

# OpenWeatherMap API Configuration
API_KEY = "81e2eb3c9c31fdbe05e78d34ebe53d55"  # Replace with your OpenWeatherMap API key
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

# Define the location for weather data
LOCATION = {"lat": 37.7749, "lon": -122.4194}  # Example: San Francisco

# Function to fetch weather data
def fetch_weather_data():
    params = {
        "lat": LOCATION["lat"],
        "lon": LOCATION["lon"],
        "appid": API_KEY,
        "units": "metric"  # Use metric system for temperature in Celsius
    }
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        return {
            "timestamp": datetime.datetime.now().isoformat(),
            "temperature": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "pressure": data["main"]["pressure"],
            "weather": data["weather"][0]["description"],
        }
    else:
        print(f"Error fetching data: {response.status_code}")
        return None

# Initialize an empty DataFrame to store data
columns = ["timestamp", "temperature", "humidity", "pressure", "weather"]
weather_data = pd.DataFrame(columns=columns)

# Collect data periodically
try:
    for _ in range(10):  # Collect data 10 times (example)
        data = fetch_weather_data()
        if data:
            weather_data = weather_data._append(data, ignore_index=True)
            print(f"Data collected: {data}")
        time.sleep(60)  # Wait for 1 minute between requests
except KeyboardInterrupt:
    print("Data collection interrupted.")

# Save the data to a CSV file
weather_data.to_csv("weather_data.csv", index=False)
print("Weather data saved to 'weather_data.csv'.")



