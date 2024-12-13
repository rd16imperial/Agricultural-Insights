import requests
import csv
from datetime import datetime, timedelta

# Weatherbit API Configuration
API_KEY = "3a224b3e590541ecb4e1e7a85b34e929" 
BASE_URL = "https://api.weatherbit.io/v2.0/history/agweather"
LAT = "34.035"  
LON = "-117.846191"  


def fetch_agweather_data():
    try:
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=7)

        # Format the dates as required by the API (YYYY-MM-DD)
        params = {
            "lat": LAT,
            "lon": LON,
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "key": API_KEY,
        }

        # Make the API request
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()  # Raise exception for HTTP errors

        # Parse and return the response JSON data
        data = response.json()
        return data["data"]

    except Exception as e:
        print(f"Error fetching agricultural weather data: {e}")
        return None

# Function to save data to CSV
def save_to_csv(data, filename="agweather_data.csv"):
    try:
        # Open the CSV file for writing
        with open(filename, mode="w", newline="") as file:
            writer = csv.writer(file)

            # Write the header row
            header = [
                "timestamp_local", "timestamp_utc", "bulk_soil_density", 
                "skin_temp_max", "skin_temp_avg", "skin_temp_min", 
                "temp_2m_avg", "precip", "specific_humidity", 
                "evapotranspiration", "pres_avg", "wind_10m_spd_avg", 
                "soilm_0_10cm", "soilm_10_40cm", "soilm_40_100cm", 
                "soilm_100_200cm", "soilt_0_10cm", "soilt_10_40cm", 
                "soilt_40_100cm", "soilt_100_200cm"
            ]
            writer.writerow(header)

            # Write the data rows
            for record in data:
                writer.writerow([
                    record.get("timestamp_local"),
                    record.get("timestamp_utc"),
                    record.get("bulk_soil_density"),
                    record.get("skin_temp_max"),
                    record.get("skin_temp_avg"),
                    record.get("skin_temp_min"),
                    record.get("temp_2m_avg"),
                    record.get("precip"),
                    record.get("specific_humidity"),
                    record.get("evapotranspiration"),
                    record.get("pres_avg"),
                    record.get("wind_10m_spd_avg"),
                    record.get("soilm_0_10cm"),
                    record.get("soilm_10_40cm"),
                    record.get("soilm_40_100cm"),
                    record.get("soilm_100_200cm"),
                    record.get("soilt_0_10cm"),
                    record.get("soilt_10_40cm"),
                    record.get("soilt_40_100cm"),
                    record.get("soilt_100_200cm"),
                ])
        print(f"Data saved to {filename}")
    except Exception as e:
        print(f"Error saving data to CSV: {e}")

# Main execution
if __name__ == "__main__":
    print("Fetching agricultural weather data...")
    agweather_data = fetch_agweather_data()
    if agweather_data:
        print("Saving data to CSV...")
        save_to_csv(agweather_data)
    else:
        print("No data fetched.")
