import requests

# Metadata server headers
HEADERS = {"Metadata-Flavor": "Google"}

# Metadata URL to get all service accounts
SERVICE_ACCOUNTS_URL = "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/"

# Fetch all service accounts
response = requests.get(SERVICE_ACCOUNTS_URL, headers=HEADERS)

if response.status_code == 200:
    service_accounts = response.text.split("\n")  # Metadata response is newline-separated
    service_accounts = [account.strip("/") for account in service_accounts if account.strip()]
else:
    print(f"❌ Failed to get Service Accounts: {response.status_code}, {response.text}")
    exit(1)

# ✅ Print all service accounts
print("\n✅ Available Service Accounts:")
for account in service_accounts:
    print(f"  - {account}")

# ✅ Fetch and print OAuth scopes for each service account
print("\n✅ OAuth Scopes for Each Service Account:")
for account in service_accounts:
    scopes_url = f"http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/{account}/scopes"
    scopes_response = requests.get(scopes_url, headers=HEADERS)

    if scopes_response.status_code == 200:
        scopes = scopes_response.text.split("\n")  # Scopes are newline-separated
        print(f"\n🔹 Service Account: {account}")
        for scope in scopes:
            print(f"   - {scope}")
    else:
        print(f"❌ Failed to get scopes for {account}: {scopes_response.status_code}")
