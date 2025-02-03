import requests

METADATA_URL = "http://metadata.google.internal/computeMetadata/v1/project/project-id"
HEADERS = {"Metadata-Flavor": "Google"}

response = requests.get(METADATA_URL, headers=HEADERS)

if response.status_code == 200:
    print("Available Service Accounts:")
    print(response.text)
else:
    print(f"Failed to get service accounts: {response.status_code} - {response.text}")
