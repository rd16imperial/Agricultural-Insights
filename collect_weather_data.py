import requests
import pandas as pd
import datetime
import time

# OpenWeatherMap API Configuration
API_KEY = "81e2eb3c9c31fdbe05e78d34ebe53d55"  
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


LOCATION = {"lat": 37.7749, "lon": -122.4194} 

# Function to fetch weather data
def fetch_weather_data():
    params = {
        "lat": LOCATION["lat"],
        "lon": LOCATION["lon"],
        "appid": API_KEY,
        "units": "metric"  
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


columns = ["timestamp", "temperature", "humidity", "pressure", "weather"]
weather_data = pd.DataFrame(columns=columns)


try:
    for _ in range(10): 
        data = fetch_weather_data()
        if data:
            weather_data = weather_data._append(data, ignore_index=True)
            print(f"Data collected: {data}")
        time.sleep(60)  
except KeyboardInterrupt:
    print("Data collection interrupted.")


weather_data.to_csv("weather_data.csv", index=False)
print("Weather data saved to 'weather_data.csv'.")



