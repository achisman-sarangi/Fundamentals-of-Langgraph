from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.message import add_messages

from langchain_core.messages import BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI

# Define the state schema
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# Initialize the model
model = ChatOpenAI()

# Define the node function
def chat_node(state: ChatState):
    # Take user query from the state
    messages = state["messages"]

    # Send it to the LLM
    response = model.invoke(messages)

    # Store the responses back into the state
    return {"messages": [response]}

# Create a memory checkpoint
checkPointer = MemorySaver()

# Build the graph
graph = StateGraph(ChatState)

# Add nodes
graph.add_node("chat_node", chat_node)

# Add edges
graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)

# Compile the graph
chatbot = graph.compile(checkpointer=checkPointer)

# Run the chatbot with a sample input
for message_chunk, metadata in chatbot.stream(
    {"messages": [HumanMessage(content="give me ingredients required for making pasta")]},
    config={"configurable": {"thread_id": "thread-1"}},
    stream_mode="messages"
):
    if message_chunk.content:
        print(message_chunk.content, end=" ", flush=True)




