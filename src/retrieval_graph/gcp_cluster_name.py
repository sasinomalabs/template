import requests

METADATA_URL = "http://metadata/computeMetadata/v1/instance/attributes/cluster-name"
HEADERS = {"Metadata-Flavor": "Google"}

response = requests.get(METADATA_URL, headers=HEADERS)

if response.status_code == 200:
    print(f"Cluster Name: {response.text}")
else:
    print(f"Failed to get cluster name: {response.status_code} - {response.text}")
