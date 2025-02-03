import requests

API_SERVER = "https://192.168.64.1:443"
TOKEN_PATH = "/var/run/secrets/kubernetes.io/serviceaccount/token"

# Load token (if running inside a pod)
with open(TOKEN_PATH, "r") as file:
    TOKEN = file.read().strip()

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/json"
}

# Make a request to get Kubernetes nodes
response = requests.get(f"{API_SERVER}/api/v1/nodes", headers=HEADERS, verify=False)
print(response.json())
