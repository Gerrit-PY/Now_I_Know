import requests
import json

# Define the API endpoint and parameters
url = "https://researchbitcoin.net/bitlab-api"
token = "5095e872-71de-44c1-93df-7716b5b687db"  # Replace with your actual token
data_field = "Active_Realized_Price"

# Define the payload
payload = {
    'token': token,
    'data_field': data_field
}

# Send the POST request with JSON payload
response = requests.post(url, json=payload)

# Check if the request was successful
if response.status_code == 200:
    print("Success! Here is the data:")
    data = response.json()
    print(data)

    # Save the data to a JSON file
    with open('data.json', 'w') as json_file:
        json.dump(data, json_file, indent=4)

    print("Data has been saved to data.json")
else:
    print(f"Failed to retrieve data. Status code: {response.status_code}")
    print("Response:", response.text)
