import streamlit as st
from langgraph_backend_database import chatbot, reytrive_all_threads
from langchain_core.messages import HumanMessage
import uuid

# -----------------------------
# Utility Functions
# -----------------------------
def generate_unique_thread_id():
    return str(uuid.uuid4())

def reset_chat():
    thread_id = generate_unique_thread_id()
    st.session_state['thread_id'] = thread_id
    add_thread_id(thread_id)
    st.session_state['message_history'] = []

def add_thread_id(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)

def load_chat_history(thread_id):
    """Load chat history safely for a given thread_id."""
    state = chatbot.get_state(config={'configurable': {'thread_id': thread_id}})
    messages = state.values.get('messages', [])
    formatted_messages = []

    for msg in messages:
        if isinstance(msg, HumanMessage):
            role = 'user'
        else:
            role = 'assistant'
        formatted_messages.append({'role': role, 'content': msg.content})
    
    return formatted_messages

# -----------------------------
# Initialize Streamlit session state
# -----------------------------
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_unique_thread_id()

if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = reytrive_all_threads()

add_thread_id(st.session_state['thread_id'])

# -----------------------------
# Sidebar UI
# -----------------------------
st.sidebar.title('LangGraph Chatbot')

if st.sidebar.button('New Chat'):
    reset_chat()

st.sidebar.header("My Conversations History")
for thread in st.session_state['chat_threads'][::-1]:
    if st.sidebar.button(thread):
        st.session_state['thread_id'] = thread
        st.session_state['message_history'] = load_chat_history(thread)

# -----------------------------
# Display existing chat messages
# -----------------------------
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

# -----------------------------
# Chat input
# -----------------------------
user_input = st.chat_input("Type your query here")

if user_input:
    # Append user message
    st.session_state['message_history'].append({
        'role': 'user',
        'content': user_input
    })

    with st.chat_message('user'):
        st.text(user_input)

    # LangGraph config
    config = {'configurable': {'thread_id': st.session_state['thread_id']}}

    # Stream AI response
    full_response = ""
    with st.chat_message('assistant'):
        response_placeholder = st.empty()
        for message_chunk, metadata in chatbot.stream(
            {'messages': [HumanMessage(content=user_input)]},
            config=config,
            stream_mode='messages'
        ):
            if hasattr(message_chunk, "content"):
                full_response += message_chunk.content
                response_placeholder.markdown(full_response)

    # Append AI message
    st.session_state['message_history'].append({
        'role': 'assistant',
        'content': full_response
    })
