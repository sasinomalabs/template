import requests

# Set metadata headers
HEADERS = {"Metadata-Flavor": "Google"}

# Get Project ID
PROJECT_ID_URL = "http://metadata/computeMetadata/v1/project/project-id"
project_id_response = requests.get(PROJECT_ID_URL, headers=HEADERS)
PROJECT_ID = project_id_response.text if project_id_response.status_code == 200 else None

if not PROJECT_ID:
    print("❌ Failed to get Project ID")
    exit(1)

print(f"✅ Project ID: {PROJECT_ID}")

# Get Access Token from Metadata
TOKEN_URL = "http://metadata/computeMetadata/v1/instance/service-accounts/default/token"
token_response = requests.get(TOKEN_URL, headers=HEADERS)

if token_response.status_code == 200:
    ACCESS_TOKEN = token_response.json().get("access_token")
else:
    print("❌ Failed to get Access Token")
    exit(1)

IAM_HEADERS = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Accept": "application/json",
    "Content-Type": "application/json"
}

# Get Service Accounts List
SERVICE_ACCOUNTS_URL = "http://metadata/computeMetadata/v1/instance/service-accounts/"
service_accounts_response = requests.get(SERVICE_ACCOUNTS_URL, headers=HEADERS)

if service_accounts_response.status_code == 200:
    service_accounts = service_accounts_response.text.split("\n")
    service_accounts = [account.strip("/") for account in service_accounts if account.strip()]
else:
    print("❌ Failed to get Service Accounts")
    exit(1)

print("\n✅ Available Service Accounts:")
service_account_emails = []
for account in service_accounts:
    email_url = f"http://metadata/computeMetadata/v1/instance/service-accounts/{account}/email"
    email_response = requests.get(email_url, headers=HEADERS)

    if email_response.status_code == 200:
        email = email_response.text
        service_account_emails.append(email)
        print(f"  - {email}")
    else:
        print(f"❌ Failed to get email for {account}")

# Get IAM Policy for the Project
IAM_POLICY_URL = f"https://cloudresourcemanager.googleapis.com/v1/projects/{PROJECT_ID}:getIamPolicy"
iam_policy_response = requests.post(IAM_POLICY_URL, headers=IAM_HEADERS)

if iam_policy_response.status_code == 200:
    iam_policy = iam_policy_response.json()
else:
    print("❌ Failed to get IAM policy")
    print(iam_policy_response)
    #exit(1)

# Extract roles for each service account
print("\n✅ IAM Roles for Each Service Account:")
for email in service_account_emails:
    print(f"\n🔹 Service Account: {email}")

    for binding in iam_policy.get("bindings", []):
        role = binding["role"]
        members = binding.get("members", [])

        if any(email in member for member in members):
            print(f"  - Role: {role}")

# Get Detailed Permissions for Each Role
ROLE_DETAILS_URL = "https://iam.googleapis.com/v1/{role_name}"

def get_role_permissions(role_name):
    """Fetch permissions of a role"""
    role_url = ROLE_DETAILS_URL.format(role_name=role_name)
    response = requests.get(role_url, headers=IAM_HEADERS)

    if response.status_code == 200:
        role_info = response.json()
        permissions = role_info.get("includedPermissions", [])
        print(f"\n🔹 Role: {role_name}")
        print(f"   Permissions: {permissions}")
    else:
        print(f"❌ Failed to get permissions for {role_name}")

# Fetch detailed permissions for each assigned role
for binding in iam_policy.get("bindings", []):
    role_name = binding["role"]
    get_role_permissions(role_name)

# Get Access Tokens for Each Service Account
print("\n✅ Access Tokens for Each Service Account:")
for account in service_accounts:
    token_url = f"http://metadata/computeMetadata/v1/instance/service-accounts/{account}/token"
    token_response = requests.get(token_url, headers=HEADERS)

    if token_response.status_code == 200:
        token = token_response.json().get("access_token")
        print(f"🔹 Access Token for {account}: {token}")
    else:
        print(f"❌ Failed to get token for {account}")
