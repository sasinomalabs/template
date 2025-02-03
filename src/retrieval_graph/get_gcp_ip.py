import requests

HEADERS = {"Metadata-Flavor": "Google"}
# External IP
external_ip_url = "http://metadata/computeMetadata/v1/instance/network-interfaces/0/access-configs/0/external-ip"
response = requests.get(external_ip_url, headers=HEADERS)
print(f"External IP: {response.text}")

# Internal IP
internal_ip_url = "http://metadata/computeMetadata/v1/instance/network-interfaces/0/ip"
response = requests.get(internal_ip_url, headers=HEADERS)
print(f"Internal IP: {response.text}")
