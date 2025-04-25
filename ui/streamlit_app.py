# streamlit_app.py
import streamlit as st
import requests
import json
import os
import sys
import time


# Make sure the app directory is in the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Import directly from app modules - this ensures we can work without the API server
from app.data_loader import load_local_data
from app.groq_client import query_groq

# App title and configuration
st.set_page_config(
    page_title="Stadium Assistant",
    page_icon="🏟️",
    layout="wide"
)

# Initialize session state for chat history and connection status
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'api_connected' not in st.session_state:
    st.session_state.api_connected = None

def check_api_connection():
    """Check if the API server is running"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def direct_query(prompt):
    """Process query directly without API server - always use user role with Groq"""
    try:
        # Always use Groq for user queries
        return query_groq(prompt)
    except Exception as e:
        return f"Error processing request: {str(e)}"

def call_api(prompt):
    """Call the FastAPI backend or fallback to direct processing"""
    # If we already know API is down, go straight to direct processing
    if st.session_state.api_connected is False:
        result = direct_query(prompt)
        return {"response": result, "status": "success", "role": "user"}
        
    # Try the API first
    try:
        response = requests.post(
            "http://localhost:8000/chat",
            json={"message": prompt, "role": "user"},
            timeout=5  # Shorter timeout to avoid UI lag
        )
        st.session_state.api_connected = True
        response.raise_for_status()
        return response.json()
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        # Mark API as disconnected and fallback
        st.session_state.api_connected = False
        result = direct_query(prompt)
        return {"response": result, "status": "success", "role": "user"}
    except Exception as e:
        return {"response": f"Error: {str(e)}", "status": "error", "role": "user"}

# App UI
st.title("🏟️ Stadium Assistant")

# Check API connection on load
if st.session_state.api_connected is None:
    with st.spinner("Checking API connection..."):
        st.session_state.api_connected = check_api_connection()

# Sidebar
with st.sidebar:
    st.header("Stadium Information")
    
    # Show connection status
    if st.session_state.api_connected:
        st.success("API Server: Connected")
    else:
        st.warning("API Server: Disconnected (using direct model access)")
    
    # Retry connection button
    if not st.session_state.api_connected and st.button("Retry API Connection"):
        with st.spinner("Checking API connection..."):
            st.session_state.api_connected = check_api_connection()
            st.experimental_rerun()
    
    st.markdown("### Ask me about:")
    st.markdown("- Where is my gate/seat")
    st.markdown("- Event timing information")
    st.markdown("- Amenities locations")
    st.markdown("- Current crowd conditions")
    
    # Show example ticket format
    with st.expander("Ticket Format Information"):
        st.markdown("""
        **Ticket code format:** XX-YZ-NN
        
        - XX: Gate prefix (AA/BB/CC/DD)
        - Y: Section letter (A-F)
        - Z: Section number (1-9)
        - NN: Seat number (01-99)
        
        **Example:** BB-D1-11 = East entrance, Section D1, Seat 11
        """)

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Chat input
user_input = st.chat_input("اسأل عن أي شيء متعلق بالحدث أو الملعب...")

if user_input:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Display user message
    with st.chat_message("user"):
        st.write(user_input)
    
    # Show thinking indicator
    with st.chat_message("assistant"):
        thinking_placeholder = st.empty()
        thinking_placeholder.write("جاري التفكير...")
        
        # Call API or direct function - always as user role
        response_data = call_api(user_input)
        
        # Update assistant response
        thinking_placeholder.empty()
        
        if response_data["status"] == "success":
            st.write(response_data["response"])
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response_data["response"]})
        else:
            st.error(response_data["response"])
            # Add error to chat history
            st.session_state.messages.append({"role": "assistant", "content": f"⚠️ {response_data['response']}"})