import requests

METADATA_URL = "http://metadata/computeMetadata/v1/instance/service-accounts/default/token"
HEADERS = {"Metadata-Flavor": "Google"}

response = requests.get(METADATA_URL, headers=HEADERS)

if response.status_code == 200:
    token = response.json().get("access_token")
    print(f"Access Token: {token}")
else:
    print(f"Failed to get token: {response.status_code} - {response.text}")
