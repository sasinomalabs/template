import requests

# Metadata URL to get service accounts
SERVICE_ACCOUNTS_URL = "http://metadata/computeMetadata/v1/instance/service-accounts/"
HEADERS = {"Metadata-Flavor": "Google"}

# Fetch the list of service accounts
response = requests.get(SERVICE_ACCOUNTS_URL, headers=HEADERS)

if response.status_code == 200:
    service_accounts = response.text.split("\n")  # Metadata response is newline-separated
    print("Available Service Accounts:")
    
    for account in service_accounts:
        account = account.strip("/")  # Remove trailing slash
        if account:
            email_url = f"http://metadata/computeMetadata/v1/instance/service-accounts/{account}/email"
            email_response = requests.get(email_url, headers=HEADERS)
            
            if email_response.status_code == 200:
                print(f"Service Account: {account}, Email: {email_response.text}")
            else:
                print(f"Failed to get email for {account}: {email_response.status_code}")
else:
    print(f"Failed to get service accounts: {response.status_code}, {response.text}")
