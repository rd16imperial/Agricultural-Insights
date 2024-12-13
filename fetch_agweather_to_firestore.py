import csv
import requests
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timedelta

# Initialize Firebase Admin SDK with your credentials file
cred = credentials.Certificate("crop-yeild-project-firebase-adminsdk-rqplp-e61c3c5737.json")  # Your credentials file
firebase_admin.initialize_app(cred)

# Firestore client
db = firestore.client()

# Weatherbit API configuration
API_KEY = "3a224b3e590541ecb4e1e7a85b34e929"  # Your Weatherbit API key
BASE_URL = "https://api.weatherbit.io/v2.0/history/agweather"
LAT = "34.035"  # Latitude of the location
LON = "-117.846191"  # Longitude of the location

# Function to fetch data from Weatherbit API
def fetch_agweather_data():
    csv_data = []  # To store data for the CSV file

    # Iterate through the past 10 days
    for day_offset in range(10):
        # Calculate the start and end times for the day
        end_time = datetime.utcnow() - timedelta(days=day_offset)
        start_time = end_time - timedelta(hours=5)
        start_date_str = start_time.strftime("%Y-%m-%d:%H")
        end_date_str = end_time.strftime("%Y-%m-%d:%H")

        # API request parameters
        params = {
            "lat": LAT,
            "lon": LON,
            "start_date": start_date_str,
            "end_date": end_date_str,
            "key": API_KEY,
        }

        try:
            # Fetch data from the Weatherbit API
            response = requests.get(BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()["data"]
            csv_data.extend(data)  # Add the data to the CSV list

            print(f"Data fetched for {start_date_str} to {end_date_str}")
        except Exception as e:
            print(f"Error fetching data for {start_date_str} to {end_date_str}: {e}")

    return csv_data

# Function to save data to a CSV file
def save_to_csv(data, filename):
    if not data:
        print("No data to save.")
        return

    # Write data to a CSV file
    with open(filename, mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

    print(f"Data saved to CSV file: {filename}")

# Function to upload CSV data to Firestore
def upload_csv_to_firestore(csv_file, collection_name):
    try:
        # Open the CSV file
        with open(csv_file, mode="r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Use a unique ID for each document in the collection
                doc_id = row["timestamp_local"].replace(" ", "_").replace(":", "-")  # Example: timestamp as ID

                # Add the document to Firestore
                db.collection(collection_name).document(doc_id).set(row)

                print(f"Uploaded document with ID: {doc_id}")

        print(f"All data from {csv_file} has been uploaded to {collection_name}.")
    except Exception as e:
        print(f"Error uploading data: {e}")

# Main function
if __name__ == "__main__":
    # Fetch the last 10 days of agweather data
    agweather_data = fetch_agweather_data()

    # Save the data to a CSV file
    csv_filename = "agweather_data_10days.csv"  # New CSV file name
    save_to_csv(agweather_data, csv_filename)

    # Upload the CSV data to Firestore
    collection_name = "agweather_data_10days"  # Specify your Firestore collection name
    upload_csv_to_firestore(csv_filename, collection_name)
