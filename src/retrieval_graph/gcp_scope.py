import requests

METADATA_URL = "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/langchain-prod.svc.id.goog/scopes"
HEADERS = {"Metadata-Flavor": "Google"}

response = requests.get(METADATA_URL, headers=HEADERS)

if response.status_code == 200:
    print("Available scopes:")
    print(response.text)
else:
    print(f"Failed to get service accounts: {response.status_code} - {response.text}")
