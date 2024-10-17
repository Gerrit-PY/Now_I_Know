import requests
import json
import os

# Define the API endpoint and your token
url = "https://researchbitcoin.net/bitlab-api"
token = "5095e872-71de-44c1-93df-7716b5b687db"  # Replace with your actual token

# List of data fields you want to retrieve
data_fields = ["Active_MVRV", "Active_Realized_Price", "Price", "MVRV_Z", "RealizedPrice"]  # Add as many fields as you want

# Loop over each data field
for data_field in data_fields:
    # Define the payload for each request
    payload = {
        'token': token,
        'data_field': data_field
    }

    # Send the POST request with JSON payload
    response = requests.post(url, json=payload)

    # Check if the request was successful
    if response.status_code == 200:
        print(f"Success! Retrieved data for {data_field}.")
        data = response.json()

        # Create the filename based on the data_field
        filename = f"{data_field}.json"

        # Check if the file already exists and delete it if it does
        if os.path.exists(filename):
            os.remove(filename)
            print(f"Old file {filename} has been deleted.")

        # Save the new data to a JSON file with the new filename
        with open(filename, 'w') as json_file:
            json.dump(data, json_file, indent=4)

        print(f"Data for {data_field} has been saved to {filename}")
    else:
        print(f"Failed to retrieve data for {data_field}. Status code: {response.status_code}")
        print("Response:", response.text)
