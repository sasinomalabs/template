import requests
import argparse

# Set metadata headers
HEADERS = {"Metadata-Flavor": "Google"}

def fetch_metadata(url):
    """Fetches data from the provided GCP metadata URL"""
    try:
        response = requests.get(url, headers=HEADERS)

        if response.status_code == 200:
            print("✅ Metadata Response:")
            print(response.text)
        else:
            print(f"❌ Failed to retrieve metadata. HTTP Status: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Error fetching metadata: {str(e)}")

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Fetch metadata from GCP Metadata Server.")
parser.add_argument("url", type=str, help="GCP Metadata URL (e.g., http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/)")
args = parser.parse_args()

# Fetch and print metadata
fetch_metadata(args.url)
