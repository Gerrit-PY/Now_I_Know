import os
import requests
import json

# Define the API endpoint and token
url = "https://researchbitcoin.net/bitlab-api"
token = "5095e872-71de-44c1-93df-7716b5b687db"  # Replace with your actual token

# Define the list of data fields you want to request
data_fields = ["MVRV_Z", "Liveliness", "SOPR", "Supply_LTH", "Supply_STH", "RealizedPrice_LTH", "RealizedPrice_STH"]  # Add more fields as needed

# Define the directory where the data should be saved
output_directory = '/Users/kimgrifhorst/Desktop/final charts 2024/repository/Now_I_Know/'

# Ensure the output directory exists
os.makedirs(output_directory, exist_ok=True)

# Print the output directory to verify it's correct
print(f"Saving files to: {output_directory}")

# Loop through each data field and request the data
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

        # Define the full path for the output file
        filename = os.path.join(output_directory, f'{data_field}.json')
        
        # Print the filename to check the path
        print(f"Attempting to save data to: {filename}")

        # Remove the old file if it exists
        if os.path.exists(filename):
            os.remove(filename)
            print(f"Old file {filename} removed.")

        # Save the data to the JSON file, overwriting the existing file
        with open(filename, 'w') as json_file:
            json.dump(data, json_file, indent=4)

        print(f"Data has been saved to {filename}")

    else:
        print(f"Failed to retrieve data for {data_field}. Status code: {response.status_code}")
        print("Response:", response.text)
